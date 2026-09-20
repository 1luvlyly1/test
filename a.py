# Databricks notebook source
# MAGIC %md
# MAGIC # Tóm tắt thông tin doanh nghiệp — call AI endpoint (Databricks)
# MAGIC
# MAGIC **Kiến trúc:**
# MAGIC
# MAGIC - **Luồng 1 — Đăng ký kinh doanh:** bảng (CREATE TABLE + select) đối chiếu với các PDF ĐKKD
# MAGIC   (tên file YYYYMM_...): so tên đại diện theo cùng thời điểm + so ngày lớn nhất.
# MAGIC - **Luồng 2 — Tình hình quan hệ:**
# MAGIC   1. Excel 3 sheet → JSON = **HIỆN TẠI** (AI dò schema → Python đọc).
# MAGIC   2. AI **thống kê context hiện tại** từ JSON (chưa so sánh).
# MAGIC   3. PDF báo cáo **CŨ** → khối chân dung (ngành nghề → quy trình SX) = **QUÁ KHỨ**.
# MAGIC   4. AI **tự do so sánh** hiện tại vs quá khứ, trình bày **theo format các mục chân dung của OCR cũ**.
# MAGIC
# MAGIC **Output Markdown:**
# MAGIC - `bao_cao_tong_hop.md` — chính: OCR quá khứ + thống kê hiện tại + so sánh QK↔HT.
# MAGIC - `du_lieu_excel.md` — dữ liệu Excel dạng bảng (tách riêng).
# MAGIC
# MAGIC Nội dung AI ghi thẳng ra file text → xuống dòng thật, không còn `\n` literal.

# COMMAND ----------

# MAGIC %pip install openpyxl pdfplumber
# dbutils.library.restartPython()

# COMMAND ----------

# ============================================================
# CẤU HÌNH
# ============================================================
CONFIG = {
    "endpoint_name": "databricks-meta-llama-3-3-70b-instruct",  # đổi thành endpoint của bạn
    "max_tokens": 4096,
    "temperature": 0.0,

    "enterprise_table": "main.default.enterprise_info",

    "dkkd_folder": "/Volumes/main/default/reports/dkkd",          # folder PDF ĐKKD
    "report_pdf_path": "/Volumes/main/default/reports/bao_cao_cu.pdf",  # PDF báo cáo CŨ (tự khai tên)
    "excel_path": "/Volumes/main/default/reports/Book1.xlsx",     # Excel HIỆN TẠI

    "schema_scan_rows": 25,
    "schema_cache_path": "/Volumes/main/default/reports/_schema_cache.json",
    "use_schema_cache": True,

    "out_main_md": "/Volumes/main/default/reports/bao_cao_tong_hop.md",
    "out_excel_md": "/Volumes/main/default/reports/du_lieu_excel.md",

    "portrait_fields": ["ngành nghề", "hoạt động kinh doanh", "quy trình sản xuất"],
}

# COMMAND ----------

import re, os, json, unicodedata
import openpyxl, pdfplumber
from datetime import datetime

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s))
                   if unicodedata.category(c) != "Mn").lower().strip()

def _to_local(path: str) -> str:
    """Chuẩn hóa path đọc bằng Python file API (dbfs: -> /dbfs)."""
    if path.startswith("dbfs:/"):
        return "/dbfs/" + path[len("dbfs:/"):]
    return path

# COMMAND ----------

# ============================================================
# BẢNG DOANH NGHIỆP — tạo bừa 1 bảng + function select
# ============================================================
# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS main.default.enterprise_info (
# MAGIC   tax_code            STRING COMMENT 'mã số thuế',
# MAGIC   representative_name STRING COMMENT 'tên đại diện',
# MAGIC   updated_date        STRING COMMENT 'ngày cập nhật (YYYYMM hoặc YYYY-MM-DD)'
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- dữ liệu mẫu (thay bằng dữ liệu thật, hoặc trỏ enterprise_table sang bảng có sẵn)
# MAGIC INSERT INTO main.default.enterprise_info VALUES
# MAGIC   ('0101234567', 'Nguyễn Văn A', '202511'),
# MAGIC   ('0101234567', 'Nguyễn Văn A', '202601'),
# MAGIC   ('0101234567', 'Trần Thị B',   '202603');

# COMMAND ----------

def get_enterprise_rows() -> list:
    df = spark.sql(f"""
        SELECT tax_code, representative_name, updated_date
        FROM {CONFIG['enterprise_table']}
        ORDER BY updated_date
    """)
    return [r.asDict() for r in df.collect()]

# COMMAND ----------

# ============================================================
# CALL AI ENDPOINT
# ============================================================
from mlflow.deployments import get_deploy_client
_deploy_client = get_deploy_client("databricks")

def call_ai(system_prompt: str, user_prompt: str,
            max_tokens: int = None, temperature: float = None) -> str:
    resp = _deploy_client.predict(
        endpoint=CONFIG["endpoint_name"],
        inputs={
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens or CONFIG["max_tokens"],
            "temperature": temperature if temperature is not None else CONFIG["temperature"],
        },
    )
    return resp["choices"][0]["message"]["content"]

def _parse_json(out: str):
    out = re.sub(r"^```(?:json)?|```$", "", out.strip(), flags=re.MULTILINE).strip()
    return json.loads(out)

# COMMAND ----------

# ============================================================
# PDF: đọc text
# ============================================================
def extract_pdf_text(pdf_path: str) -> str:
    local = _to_local(pdf_path)
    chunks = []
    with pdfplumber.open(local) as pdf:
        for page in pdf.pages:
            chunks.append(page.extract_text() or "")
    return "\n".join(chunks)

# COMMAND ----------

# ============================================================
# LUỒNG 1 — ĐĂNG KÝ KINH DOANH
# ============================================================
def _period_to_yyyymm(s: str) -> str:
    digits = re.sub(r"\D", "", str(s))
    return digits[:6] if len(digits) >= 6 else digits

def list_dkkd_files(folder: str) -> list:
    """Liệt kê PDF trong folder ĐKKD, lấy period YYYYMM từ đầu tên file.
    Dùng f.path trực tiếp (đã đầy đủ), KHÔNG tự ghép chuỗi -> tránh lỗi path."""
    files = []
    for f in dbutils.fs.ls(folder):
        if not f.name.lower().endswith(".pdf"):
            continue
        m = re.match(r"^(\d{6})_", f.name)
        if m:
            files.append({"period": m.group(1), "name": f.name, "path": f.path})
    return sorted(files, key=lambda x: x["period"])

def ai_extract_legal_reps(pdf_text: str) -> list:
    system = ("Bạn bóc tách thông tin từ giấy đăng ký kinh doanh tiếng Việt. "
              "Chỉ trả JSON hợp lệ, không giải thích.")
    user = f"""Từ nội dung giấy ĐKKD dưới đây, liệt kê TÊN NHỮNG NGƯỜI ĐẠI DIỆN PHÁP LUẬT.
Trả JSON: {{"legal_representatives": ["...", "..."]}}

--- NỘI DUNG ---
{pdf_text}
"""
    try:
        return _parse_json(call_ai(system, user)).get("legal_representatives", [])
    except Exception:
        return []

def _name_match(a: str, b: str) -> bool:
    return _strip_accents(a) == _strip_accents(b)

def run_dkkd_flow() -> dict:
    rows = get_enterprise_rows()
    files = list_dkkd_files(CONFIG["dkkd_folder"])

    file_reps = []
    for fi in files:
        text = extract_pdf_text(fi["path"])
        file_reps.append({**fi, "legal_representatives": ai_extract_legal_reps(text)})

    period_matches = []
    for fr in file_reps:
        p = fr["period"]
        table_names = [r["representative_name"] for r in rows
                       if _period_to_yyyymm(r["updated_date"]) == p]
        matched = any(_name_match(tn, fn)
                      for tn in table_names for fn in fr["legal_representatives"])
        period_matches.append({
            "period": p, "file": fr["name"],
            "ten_trong_file": fr["legal_representatives"],
            "ten_trong_bang": table_names,
            "trung_khop": matched if table_names else None,
        })

    max_file = max((fr["period"] for fr in file_reps), default=None)
    max_tbl = max((_period_to_yyyymm(r["updated_date"]) for r in rows), default=None)

    return {
        "so_dong_bang": len(rows),
        "so_file_dkkd": len(files),
        "doi_chieu_theo_thoi_diem": period_matches,
        "ngay_lon_nhat": {
            "max_file_period": max_file, "max_table_period": max_tbl,
            "trung_khop": (max_file == max_tbl) if (max_file and max_tbl) else None,
        },
    }

# COMMAND ----------

# ============================================================
# LUỒNG 2 — PDF CŨ: khối "a. Phương án" / chân dung (QUÁ KHỨ)
# ============================================================
def slice_phuong_an(raw_text: str) -> str:
    start = re.search(r"ng[àa]nh\s*ngh[eề]", raw_text, flags=re.IGNORECASE)
    end = re.search(r"quy\s*tr[ìi]nh\s*s[aả]n\s*xu[aấ]t.*", raw_text, flags=re.IGNORECASE)
    if start and end: return raw_text[start.start(): end.end()].strip()
    if start:         return raw_text[start.start():].strip()
    return raw_text.strip()

def ai_extract_portrait(phuong_an_text: str) -> dict:
    fields = CONFIG["portrait_fields"]
    system = ("Bạn bóc tách báo cáo doanh nghiệp tiếng Việt. Chỉ trả JSON hợp lệ, không markdown.")
    user = f"""Nội dung bảng 'chân dung | nội dung đánh giá' (phần a. Phương án).
Trích NGUYÊN VĂN nội dung đánh giá cho từng chân dung: {fields}. Không có -> "".
Trả JSON: {{{", ".join(f'"{f}": "..."' for f in fields)}}}

--- NỘI DUNG ---
{phuong_an_text}
"""
    try:
        return _parse_json(call_ai(system, user))
    except Exception:
        return {f: "" for f in fields}

# COMMAND ----------

# ============================================================
# LUỒNG 2 — EXCEL HIỆN TẠI: AI dò schema -> Python đọc -> JSON
# (đã BỎ compare đầu kỳ/cuối kỳ & highlight theo yêu cầu)
# ============================================================
def sheet_to_grid_text(ws, max_rows: int) -> str:
    lines = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i >= max_rows: break
        cells = [f"C{j}={v!r}" for j, v in enumerate(row) if v is not None]
        lines.append(f"R{i}: " + " | ".join(cells))
    return "\n".join(lines)

def ai_detect_schema(ws, sheet_name: str) -> dict:
    grid = sheet_to_grid_text(ws, CONFIG["schema_scan_rows"])
    system = ("Bạn phân tích layout sheet Excel tiếng Việt có header nhiều tầng và dòng rác. "
              "Chỉ trả JSON, KHÔNG giải thích, KHÔNG trả giá trị, chỉ trả index.")
    user = f"""Sheet '{sheet_name}'. Lưới (Rn=dòng, Cn=cột, index từ 0):
{grid}

Xác định cấu trúc bảng chính, bỏ dòng/cột rác. Header nhiều tầng: nhóm thời điểm
(đầu kỳ/nhập/xuất/tồn/phát sinh/cuối kỳ) + cột con (thành tiền/số lượng hoặc nợ/có).

Trả JSON:
{{
  "data_start_row": <int>,
  "columns": {{
     "ten": <int>, "ma": <int hoặc null>,
     "groups": {{ "<ten_nhom>": {{"<con>": <int>, ...}}, ... }}
  }}
}}
Tên nhóm/con: thường, không dấu, gạch dưới (dau_ky, cuoi_ky, phat_sinh, nhap, xuat, ton; no, co, thanh_tien, so_luong).
"""
    return _parse_json(call_ai(system, user))

def validate_schema(ws, schema: dict) -> None:
    assert "columns" in schema and "data_start_row" in schema, "Thiếu khóa schema"
    cols = schema["columns"]; maxc, maxr = ws.max_column, ws.max_row
    dsr = schema["data_start_row"]
    assert isinstance(dsr, int) and 0 <= dsr < maxr, f"data_start_row sai: {dsr}"
    assert isinstance(cols.get("ten"), int) and 0 <= cols["ten"] < maxc, "col 'ten' sai"
    if cols.get("ma") is not None:
        assert 0 <= cols["ma"] < maxc, "col 'ma' sai"
    assert cols.get("groups"), "thiếu groups"
    for g, subs in cols["groups"].items():
        for sub, idx in subs.items():
            assert idx is None or (isinstance(idx, int) and 0 <= idx < maxc), f"col {g}.{sub} sai"

def read_by_schema(ws, schema: dict) -> list:
    rows = list(ws.iter_rows(values_only=True))
    cols = schema["columns"]; recs = []
    for r in rows[schema["data_start_row"]:]:
        if cols["ten"] >= len(r): continue
        name = r[cols["ten"]]
        if name in (None, ""): continue
        rec = {"ten": str(name).strip(),
               "ma": r[cols["ma"]] if cols.get("ma") is not None and cols["ma"] < len(r) else None,
               "groups": {}}
        for g, subs in cols["groups"].items():
            rec["groups"][g] = {sub: (r[idx] if idx is not None and idx < len(r) else None)
                                for sub, idx in subs.items()}
        recs.append(rec)
    return recs

def _load_cache():
    if CONFIG["use_schema_cache"] and os.path.exists(_to_local(CONFIG["schema_cache_path"])):
        try:
            with open(_to_local(CONFIG["schema_cache_path"]), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: return {}
    return {}

def _save_cache(cache):
    if not CONFIG["use_schema_cache"]: return
    p = _to_local(CONFIG["schema_cache_path"])
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_schema(ws, sheet_name, cache):
    if sheet_name in cache:
        try:
            validate_schema(ws, cache[sheet_name]); return cache[sheet_name]
        except AssertionError:
            pass
    schema = ai_detect_schema(ws, sheet_name)
    validate_schema(ws, schema)
    cache[sheet_name] = schema
    return schema

def _classify_sheet(name):
    k = _strip_accents(name)
    if "ton" in k: return "hang_ton"
    if "thu" in k: return "phai_thu"
    if "tra" in k: return "phai_tra"
    return k.replace(" ", "_")

def load_excel(path):
    wb = openpyxl.load_workbook(_to_local(path), data_only=True)
    cache = _load_cache(); data, schemas = {}, {}
    for name in wb.sheetnames:
        ws = wb[name]; schema = get_schema(ws, name, cache)
        data[_classify_sheet(name)] = read_by_schema(ws, schema)
        schemas[_classify_sheet(name)] = schema
    _save_cache(cache)
    return data, schemas

# COMMAND ----------

# ============================================================
# AI — (1) THỐNG KÊ CONTEXT HIỆN TẠI  (2) SO SÁNH TỰ DO QK vs HT
# ============================================================
def ai_thongke_hientai(excel_json: dict) -> str:
    """Bước 1: AI thống kê / mô tả tình hình HIỆN TẠI từ JSON Excel — CHƯA so sánh."""
    system = ("Bạn là chuyên viên phân tích tín dụng. Từ dữ liệu Excel (hàng tồn kho, phải thu, phải trả), "
              "hãy THỐNG KÊ và MÔ TẢ tình hình HIỆN TẠI của doanh nghiệp bằng tiếng Việt: quy mô, cơ cấu, "
              "các con số nổi bật, điểm cần lưu ý. CHƯA so sánh với bất kỳ mốc nào. Viết đoạn văn mạch lạc, có số liệu.")
    user = f"""DỮ LIỆU HIỆN TẠI (JSON từ Excel):
{json.dumps(excel_json, ensure_ascii=False, indent=2)}

Hãy thống kê tình hình hiện tại về: hàng tồn kho, công nợ phải thu, công nợ phải trả."""
    return call_ai(system, user).strip()

def ai_sosanh_tudo(portrait_cu: dict, thongke_hientai: str, excel_json: dict) -> str:
    """Bước 2: AI TỰ DO so sánh HIỆN TẠI (Excel) vs QUÁ KHỨ (chân dung PDF cũ),
    trình bày THEO FORMAT các mục chân dung của OCR cũ."""
    fields = CONFIG["portrait_fields"]
    system = ("Bạn là chuyên viên phân tích tín dụng. So sánh tình hình HIỆN TẠI (từ Excel) với "
              "báo cáo QUÁ KHỨ (các mục chân dung trong PDF cũ). Được TỰ DO nhận định, không bị định hướng. "
              "Lưu ý: báo cáo cũ có thể THIẾU thông tin mà dữ liệu mới có, và ngược lại có thông tin mới phát sinh — "
              "hãy nêu rõ khi gặp. Trình bày kết quả THEO ĐÚNG CÁC MỤC của báo cáo cũ.")
    sections = "\n".join(f"### {f}\n- Quá khứ (PDF): {portrait_cu.get(f) or '(không có trong báo cáo cũ)'}"
                         for f in fields)
    user = f"""BÁO CÁO QUÁ KHỨ — các mục chân dung (OCR PDF cũ):
{json.dumps(portrait_cu, ensure_ascii=False, indent=2)}

THỐNG KÊ HIỆN TẠI (đã tổng hợp từ Excel):
{thongke_hientai}

DỮ LIỆU HIỆN TẠI CHI TIẾT (JSON Excel):
{json.dumps(excel_json, ensure_ascii=False, indent=2)}

YÊU CẦU: Với TỪNG MỤC của báo cáo cũ dưới đây, viết phần "Quá khứ" (nguyên văn OCR cũ) và
phần "Hiện tại & so sánh" (dựa trên Excel + thống kê). Nếu mục cũ trống -> ghi rõ là thông tin mới phát sinh.
Khung mục cần bám theo:
{sections}

Với mỗi mục, xuất ra dạng Markdown:
#### <tên mục>
**Quá khứ:** <nội dung OCR cũ hoặc 'không có trong báo cáo cũ'>
**Hiện tại & so sánh:** <nhận định>
"""
    return call_ai(system, user).strip()

# COMMAND ----------

# ============================================================
# XUẤT MARKDOWN
# ============================================================
def _fmt(v):
    if v is None: return ""
    if isinstance(v, float) and v.is_integer(): v = int(v)
    if isinstance(v, (int, float)): return f"{v:,}"
    return str(v)

def _write(path, text):
    local = _to_local(path)
    os.makedirs(os.path.dirname(local), exist_ok=True)
    with open(local, "w", encoding="utf-8") as f:
        f.write(text)

def md_excel_file(excel_data: dict) -> str:
    L = ["# Dữ liệu Excel — Tình hình hiện tại", ""]
    label = {"hang_ton": "Hàng tồn kho", "phai_thu": "Công nợ phải thu", "phai_tra": "Công nợ phải trả"}
    for key, records in excel_data.items():
        L += [f"## {label.get(key, key)}", ""]
        if records:
            groups = list(records[0]["groups"].keys())
            subs = {g: list(records[0]["groups"][g].keys()) for g in groups}
            head = ["Tên", "Mã"] + [f"{g}.{s}" for g in groups for s in subs[g]]
            L.append("| " + " | ".join(head) + " |")
            L.append("| " + " | ".join(["---"] * len(head)) + " |")
            for r in records:
                cells = [r["ten"], _fmt(r["ma"])] + [_fmt(r["groups"][g].get(s))
                                                     for g in groups for s in subs[g]]
                L.append("| " + " | ".join(cells) + " |")
        L.append("")
    return "\n".join(L)

def md_main_file(dkkd: dict, portrait_cu: dict, thongke_ht: str, sosanh: str) -> str:
    L = ["# Báo cáo tóm tắt thông tin doanh nghiệp", "",
         f"*Tạo lúc: {datetime.now().strftime('%Y-%m-%d %H:%M')} — Endpoint: {CONFIG['endpoint_name']}*", ""]

    # 1. ĐKKD
    L += ["## 1. Đối chiếu Đăng ký kinh doanh", "",
          f"- Số dòng trong bảng: **{dkkd['so_dong_bang']}**",
          f"- Số file ĐKKD: **{dkkd['so_file_dkkd']}**", "",
          "### 1.1. Đối chiếu tên đại diện theo cùng thời điểm", "",
          "| Kỳ (YYYYMM) | File | Tên trong file | Tên trong bảng | Trùng khớp |",
          "| --- | --- | --- | --- | --- |"]
    for m in dkkd["doi_chieu_theo_thoi_diem"]:
        tk = "✅" if m["trung_khop"] else ("❌" if m["trung_khop"] is False else "—")
        L.append(f"| {m['period']} | {m['file']} | {', '.join(m['ten_trong_file']) or '—'} "
                 f"| {', '.join(m['ten_trong_bang']) or '—'} | {tk} |")
    nn = dkkd["ngay_lon_nhat"]
    tk = "✅ khớp" if nn["trung_khop"] else ("❌ lệch" if nn["trung_khop"] is False else "—")
    L += ["", "### 1.2. So sánh ngày lớn nhất", "",
          f"- Ngày lớn nhất từ tên file: **{nn['max_file_period'] or '—'}**",
          f"- Ngày lớn nhất trong bảng: **{nn['max_table_period'] or '—'}**",
          f"- Kết quả: **{tk}**", ""]

    # 2. OCR quá khứ (nguyên văn chân dung PDF cũ)
    L += ["## 2. Báo cáo quá khứ (OCR PDF cũ)", ""]
    for f in CONFIG["portrait_fields"]:
        L += [f"### {f.capitalize()}", "", (portrait_cu.get(f) or "_(không có trong báo cáo cũ)_"), ""]

    # 3. Thống kê hiện tại
    L += ["## 3. Thống kê tình hình hiện tại (từ Excel)", "", thongke_ht, "",
          "> Dữ liệu chi tiết dạng bảng xem file `du_lieu_excel.md`.", ""]

    # 4. So sánh quá khứ ↔ hiện tại (theo format mục chân dung cũ)
    L += ["## 4. So sánh quá khứ ↔ hiện tại", "", sosanh, ""]
    return "\n".join(L)

# COMMAND ----------

# ============================================================
# PIPELINE CHÍNH
# ============================================================
# Luồng 1
dkkd = run_dkkd_flow()

# Luồng 2 — quá khứ (PDF) & hiện tại (Excel)
portrait_cu = ai_extract_portrait(slice_phuong_an(extract_pdf_text(CONFIG["report_pdf_path"])))
excel_data, schemas = load_excel(CONFIG["excel_path"])

# Bước 1: thống kê hiện tại  ->  Bước 2: so sánh tự do
thongke_ht = ai_thongke_hientai(excel_data)
sosanh = ai_sosanh_tudo(portrait_cu, thongke_ht, excel_data)

# Xuất 2 file
_write(CONFIG["out_main_md"], md_main_file(dkkd, portrait_cu, thongke_ht, sosanh))
_write(CONFIG["out_excel_md"], md_excel_file(excel_data))

print("Đã xuất:")
print(" -", CONFIG["out_main_md"])
print(" -", CONFIG["out_excel_md"])
print("=" * 60)
print(md_main_file(dkkd, portrait_cu, thongke_ht, sosanh))
