# Databricks notebook source
# MAGIC %md
# MAGIC # Rà soát hồ sơ vay → báo cáo HTML (ảnh trái – text phải) + Markdown
# MAGIC Gọi trực tiếp REST API của Model Serving

# COMMAND ----------

# MAGIC %pip install pymupdf markdown --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# ================== CẤU HÌNH ==================
ENDPOINT    = "databricks-claude-sonnet-4-5"
IMAGE_DIR   = "/Volumes/main/credit/loan_docs/images"
PDF_PATH    = "/Volumes/main/credit/loan_docs/ho_so_vay.pdf"
CONTEXT     = None   # vd: "Công ty ABC, MST 0101234567, đề nghị vay 5 tỷ bổ sung vốn lưu động"
OUTPUT_DIR  = "/Volumes/main/credit/loan_docs/reports"
REPORT_NAME = "bao_cao_tham_dinh"          # -> .html và .md
IMG_EXTS    = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

# COMMAND ----------

import os, io, re, time, base64, html, textwrap, requests
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image, ImageOps
from IPython.display import display, Markdown, Image as IPImage
import markdown as mdlib
import fitz

ctx     = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
HOST    = ctx.apiUrl().get()
HEADERS = {"Authorization": f"Bearer {ctx.apiToken().get()}"}


def load_image(path):
    """Đọc ảnh về RGB, xoay đúng chiều EXIF, nền trong suốt -> trắng."""
    img = ImageOps.exif_transpose(Image.open(path))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img)
    return img.convert("RGB")


def to_b64(img, size, quality=88):
    img = img.copy()
    img.thumbnail((size, size))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode()


def ask(prompt, image=None, max_tokens=4096):
    content = prompt if image is None else [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + to_b64(image, 1568)}},
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


def preview(title, image, text, max_lines=80, wrap=85):
    """Xem trong notebook: ảnh trái - text phải, vẽ thành 1 hình PNG nên đúng màu cả ở theme tối."""
    clean = re.sub(r"\*\*|__|`|^#+\s*", "", text or "", flags=re.M)
    lines = []
    for line in clean.splitlines():
        lines += textwrap.wrap(line, wrap, subsequent_indent="  ") or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines] + ["", "... (xem đầy đủ trong file HTML)"]

    thumb = image.copy()
    thumb.thumbnail((1000, 1000))
    height = max(6, len(lines) * 0.19 + 1)

    fig, (ax_img, ax_txt) = plt.subplots(
        1, 2, figsize=(16, height), gridspec_kw={"width_ratios": [1, 1.15]})
    fig.patch.set_facecolor("white")
    ax_img.imshow(thumb)
    ax_img.set_anchor("N")
    ax_img.axis("off")
    ax_txt.axis("off")
    ax_txt.text(0, 1, "\n".join(lines), va="top", ha="left",
                fontsize=10, family="DejaVu Sans", transform=ax_txt.transAxes)
    fig.suptitle(title, x=0.01, ha="left", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.show()
    plt.close(fig)

# COMMAND ----------

# MAGIC %md ### Kiểm tra kết nối

# COMMAND ----------

try:
    print(ask("Trả lời đúng 1 từ: OK"))
except Exception as e:
    print("LỖI:", e)
    eps = requests.get(f"{HOST}/api/2.0/serving-endpoints", headers=HEADERS).json()
    print("Endpoint Claude hiện có:",
          [x["name"] for x in eps.get("endpoints", []) if "claude" in x["name"].lower()])

# COMMAND ----------

# MAGIC %md ## Bước 1: Từng ảnh → mô tả, những gì xuất hiện, OCR, dấu hiệu bất thường

# COMMAND ----------

IMAGE_PROMPT = """Đây là một ảnh trong hồ sơ vay của doanh nghiệp. Hãy trả lời theo đúng cấu trúc:

**Mô tả:** loại tài liệu/ảnh và nội dung chính

**Những gì xuất hiện trong ảnh:**
- liệt kê từng thành phần nhìn thấy được (tiêu đề, bảng số liệu, con dấu, chữ ký, logo, người, máy móc, hàng hóa, biển hiệu...)

**OCR:**
chép lại toàn bộ chữ trong ảnh

**Dấu hiệu bất thường:** các điểm đáng ngờ (chỉnh sửa, số liệu vô lý, con dấu/chữ ký lạ...), hoặc "Không thấy" """

image_paths = sorted(
    os.path.join(root, f)
    for root, _, files in os.walk(IMAGE_DIR)
    for f in files if os.path.splitext(f)[1].lower() in IMG_EXTS
)

image_results = []   # (tên, kết quả, ảnh base64 thu nhỏ)
for i, path in enumerate(image_paths, 1):
    name = os.path.basename(path)
    print(f"[{i}/{len(image_paths)}] {name}")
    try:
        img = load_image(path)
        result = ask(IMAGE_PROMPT, img)
        image_results.append((name, result, to_b64(img, 900)))
        preview(f"[{i}/{len(image_paths)}] {name}", img, result)
    except Exception as e:
        print("   Lỗi:", e)
        image_results.append((name, f"(Lỗi xử lý: {e})", None))

# COMMAND ----------

# MAGIC %md ## Bước 2: OCR PDF

# COMMAND ----------

pdf_name = os.path.basename(PDF_PATH)
pdf_results = []     # (trang, text, ảnh base64 thu nhỏ)
with fitz.open(PDF_PATH) as doc:
    for i, page in enumerate(doc, 1):
        print(f"PDF trang {i}/{doc.page_count}")
        pix = page.get_pixmap(dpi=150)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        text = ask("Chép lại toàn bộ chữ trong trang tài liệu này.", img)
        pdf_results.append((i, text, to_b64(img, 900)))
        preview(f"PDF {pdf_name} – trang {i}", img, text)

# COMMAND ----------

# MAGIC %md ## Bước 3: Rà soát tổng thể

# COMMAND ----------

data = "# Context đề xuất vay\n" + (CONTEXT.strip() if CONTEXT and CONTEXT.strip() else "(Không có)")
data += f"\n\n# File PDF: {pdf_name}\n" + "\n".join(f"\n## Trang {p}\n{t}" for p, t, _ in pdf_results)
data += "\n\n# Kết quả phân tích từng ảnh\n" + "\n".join(f"\n## {n}\n{r}" for n, r, _ in image_results)

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
display(Markdown(report))

# COMMAND ----------

# MAGIC %md ## Bước 4: Xuất báo cáo HTML (ảnh trái – text phải) và Markdown

# COMMAND ----------

def md2html(text):
    return mdlib.markdown(html.escape(text or "", quote=False), extensions=["tables"])


def row(title, b64, text):
    img = (f'<img src="data:image/jpeg;base64,{b64}"/>' if b64
           else '<div class="noimg">Không có ảnh</div>')
    return f"""
<section class="item">
  <h3>{html.escape(title)}</h3>
  <div class="grid">
    <div class="pic">{img}</div>
    <div class="txt">{md2html(text)}</div>
  </div>
</section>"""


now = datetime.now()
meta = (f"Thời gian: {now:%d/%m/%Y %H:%M} &nbsp;|&nbsp; PDF: {html.escape(pdf_name)} "
        f"({len(pdf_results)} trang) &nbsp;|&nbsp; Số ảnh: {len(image_results)}<br>"
        f"Context: {html.escape(CONTEXT or '(Không có)')}")

html_doc = f"""<!DOCTYPE html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Báo cáo rà soát hồ sơ vay</title>
<style>
  body {{ font-family: "Segoe UI", Arial, sans-serif; font-size: 14px; line-height: 1.55;
         color: #222; background: #f5f6f8; margin: 0; padding: 24px; }}
  .wrap {{ max-width: 1280px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin: 0 0 6px; }}
  h2 {{ font-size: 18px; margin: 28px 0 10px; border-bottom: 2px solid #2b5797; padding-bottom: 4px; }}
  h3 {{ font-size: 15px; margin: 0 0 10px; color: #2b5797; }}
  .meta {{ color: #666; font-size: 13px; margin-bottom: 16px; }}
  .card, .item {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
  .grid {{ display: grid; grid-template-columns: 45% 1fr; gap: 20px; align-items: start; }}
  .pic img {{ width: 100%; border: 1px solid #e3e3e3; border-radius: 4px; }}
  .noimg {{ padding: 40px; text-align: center; color: #999; border: 1px dashed #ccc; }}
  .txt {{ max-height: 900px; overflow: auto; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 13px; margin: 8px 0; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; vertical-align: top; }}
  th {{ background: #eef2f8; }}
  p, ul {{ margin: 6px 0; }}
  @media (max-width: 800px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style></head>
<body><div class="wrap">
  <h1>Báo cáo rà soát hồ sơ vay</h1>
  <div class="meta">{meta}</div>

  <div class="card">{md2html(report)}</div>

  <h2>Phụ lục A – Ảnh đính kèm</h2>
  {"".join(row(n, b, r) for n, r, b in image_results)}

  <h2>Phụ lục B – File PDF: {html.escape(pdf_name)}</h2>
  {"".join(row(f"Trang {p}", b, t) for p, t, b in pdf_results)}
</div></body></html>"""

md_doc = f"""# Báo cáo rà soát hồ sơ vay

- Thời gian: {now:%d/%m/%Y %H:%M}
- PDF: `{pdf_name}` ({len(pdf_results)} trang) | Số ảnh: {len(image_results)}
- Context: {CONTEXT or "(Không có)"}

---

{report}

---

# Phụ lục: Phân tích từng ảnh
""" + "\n".join(f"\n### {n}\n\n{r}\n" for n, r, _ in image_results)

os.makedirs(OUTPUT_DIR, exist_ok=True)
html_path = os.path.join(OUTPUT_DIR, REPORT_NAME + ".html")
md_path   = os.path.join(OUTPUT_DIR, REPORT_NAME + ".md")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_doc)
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_doc)

print("Đã lưu HTML:", html_path)
print("Đã lưu MD:  ", md_path)
