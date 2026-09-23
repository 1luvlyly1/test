# Databricks notebook source
# MAGIC %md
# MAGIC # Rà soát hồ sơ vay → báo cáo Markdown
# MAGIC Gọi trực tiếp REST API của Model Serving (không cần thư viện openai)

# COMMAND ----------

# MAGIC %pip install pymupdf markdown --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# ================== CẤU HÌNH ==================
ENDPOINT   = "databricks-claude-sonnet-4-5"
IMAGE_DIR  = "/Volumes/main/credit/loan_docs/images"
PDF_PATH   = "/Volumes/main/credit/loan_docs/ho_so_vay.pdf"
CONTEXT    = None   # vd: "Công ty ABC, MST 0101234567, đề nghị vay 5 tỷ bổ sung vốn lưu động"
OUTPUT_MD  = "/Volumes/main/credit/loan_docs/reports/bao_cao_tham_dinh.md"
IMG_EXTS   = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

# COMMAND ----------

import os, io, time, base64, html, requests
import markdown as mdlib
from datetime import datetime
from PIL import Image
import fitz

ctx   = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
HOST  = ctx.apiUrl().get()
TOKEN = ctx.apiToken().get()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def img_to_b64(img):
    img = img.convert("RGB")
    img.thumbnail((1568, 1568))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode()


def ask(prompt, image=None, max_tokens=4096):
    """Gửi 1 prompt (kèm 1 ảnh nếu có) tới endpoint, trả về text."""
    if image is None:
        content = prompt
    else:
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url",
             "image_url": {"url": "data:image/jpeg;base64," + img_to_b64(image)}},
        ]
    body = {"messages": [{"role": "user", "content": content}],
            "max_tokens": max_tokens, "temperature": 0}

    for attempt in range(5):
        r = requests.post(f"{HOST}/serving-endpoints/{ENDPOINT}/invocations",
                          headers=HEADERS, json=body, timeout=300)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        if r.status_code in (429, 500, 503):
            time.sleep(5 * (attempt + 1))
            continue
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
    raise RuntimeError("Hết số lần thử lại")


def card(title, image, text):
    """Tạo khối HTML: ảnh bên trái, kết quả phân tích bên phải."""
    thumb = image.copy()
    thumb.thumbnail((700, 700))
    body = mdlib.markdown(text, extensions=["tables"]) if text else ""
    return f"""
    <div style="border:1px solid #ccc;border-radius:8px;padding:12px;margin:10px 0;font-family:sans-serif">
      <h3 style="margin-top:0">{html.escape(title)}</h3>
      <div style="display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap">
        <img src="data:image/jpeg;base64,{img_to_b64(thumb)}"
             style="max-width:45%;min-width:280px;border:1px solid #eee"/>
        <div style="flex:1;min-width:300px;font-size:14px;line-height:1.5">{body}</div>
      </div>
    </div>"""

# COMMAND ----------

# MAGIC %md ### Kiểm tra kết nối (chạy cell này trước)

# COMMAND ----------

try:
    print(ask("Trả lời đúng 1 từ: OK"))
except Exception as e:
    print("LỖI:", e)
    # Liệt kê các endpoint Claude có trong workspace để kiểm tra đúng tên
    eps = requests.get(f"{HOST}/api/2.0/serving-endpoints", headers=HEADERS).json()
    print("Endpoint Claude hiện có:",
          [e["name"] for e in eps.get("endpoints", []) if "claude" in e["name"].lower()])

# COMMAND ----------

# MAGIC %md ## Bước 1: Từng ảnh → mô tả, OCR, dấu hiệu bất thường

# COMMAND ----------

IMAGE_PROMPT = """Đây là một ảnh trong hồ sơ vay của doanh nghiệp. Hãy trả lời theo đúng cấu trúc:

**Mô tả:** loại tài liệu/ảnh và nội dung chính

**Những gì xuất hiện trong ảnh:**
- liệt kê từng thành phần nhìn thấy được (vd: tiêu đề, bảng số liệu, con dấu, chữ ký, logo, người, máy móc, hàng hóa, biển hiệu...)

**OCR:**
chép lại toàn bộ chữ trong ảnh

**Dấu hiệu bất thường:** các điểm đáng ngờ (chỉnh sửa, số liệu vô lý, con dấu/chữ ký lạ...), hoặc "Không thấy" """

image_paths = sorted(
    os.path.join(root, f)
    for root, _, files in os.walk(IMAGE_DIR)
    for f in files if os.path.splitext(f)[1].lower() in IMG_EXTS
)

image_results, cards = [], []
for i, path in enumerate(image_paths, 1):
    name = os.path.basename(path)
    print(f"[{i}/{len(image_paths)}] {name}")
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            result = ask(IMAGE_PROMPT, img)
            cards.append(card(f"[{i}/{len(image_paths)}] {name}", img, result))
    except Exception as e:
        result = f"(Lỗi xử lý: {e})"
        print(result)
    image_results.append((name, result))

displayHTML("".join(cards))

# COMMAND ----------

# MAGIC %md ## Bước 2: OCR PDF

# COMMAND ----------

pdf_name = os.path.basename(PDF_PATH)
pdf_texts, cards = [], []
with fitz.open(PDF_PATH) as doc:
    for i, page in enumerate(doc, 1):
        print(f"PDF trang {i}/{doc.page_count}")
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        text = ask("Chép lại toàn bộ chữ trong trang tài liệu này.", img)
        pdf_texts.append(text)
        cards.append(card(f"PDF {pdf_name} – trang {i}", img, text))

displayHTML("".join(cards))

# COMMAND ----------

# MAGIC %md ## Bước 3: Rà soát tổng thể → báo cáo

# COMMAND ----------

data = "# Context đề xuất vay\n" + (CONTEXT.strip() if CONTEXT and CONTEXT.strip() else "(Không có)")
data += f"\n\n# File PDF: {pdf_name}\n" + "\n".join(f"\n## Trang {i}\n{t}" for i, t in enumerate(pdf_texts, 1))
data += "\n\n# Kết quả phân tích từng ảnh\n" + "\n".join(f"\n## {n}\n{r}" for n, r in image_results)

REVIEW_PROMPT = """Bạn là chuyên viên thẩm định tín dụng. Dưới đây là toàn bộ hồ sơ vay của một doanh nghiệp
(context, nội dung PDF, kết quả phân tích từng ảnh). Hãy rà soát tổng thể, đối chiếu chéo giữa các tài liệu
để tìm dấu hiệu gian lận hoặc bất thường. Chỉ dựa trên dữ liệu có sẵn, ghi rõ nguồn; thiếu thông tin thì nói là thiếu.

Viết báo cáo Markdown tiếng Việt gồm:
## 1. Tóm tắt hồ sơ
## 2. Dấu hiệu bất thường (bảng: Dấu hiệu | Bằng chứng | Nguồn | Mức độ)
## 3. Thông tin còn thiếu
## 4. Kết luận (mức rủi ro Thấp / Trung bình / Cao và lý do)
## 5. Đề xuất xác minh

HỒ SƠ:
""" + data

report = ask(REVIEW_PROMPT, max_tokens=8192)

# COMMAND ----------

# MAGIC %md ## Bước 4: Xuất file .md

# COMMAND ----------

md = f"""# Báo cáo rà soát hồ sơ vay

- Thời gian: {datetime.now():%d/%m/%Y %H:%M}
- PDF: `{pdf_name}` ({len(pdf_texts)} trang) | Số ảnh: {len(image_results)}
- Context: {CONTEXT or "(Không có)"}

---

{report}

---

# Phụ lục: Phân tích từng ảnh
""" + "\n".join(f"\n### {n}\n\n{r}\n" for n, r in image_results)

os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write(md)

print("Đã lưu:", OUTPUT_MD)
displayHTML("<div style='font-family:sans-serif'>" + mdlib.markdown(report, extensions=["tables"]) + "</div>")
