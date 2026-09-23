# Databricks notebook source
# MAGIC %md
# MAGIC # Quét hồ sơ vay → báo cáo Markdown
# MAGIC Claude Sonnet 4.5 qua Databricks Foundation Model API

# COMMAND ----------

# MAGIC %pip install pymupdf pillow openai --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# ================== CẤU HÌNH ==================
ENDPOINT   = "databricks-claude-sonnet-4-5"
IMAGE_DIR  = "/Volumes/main/credit/loan_docs/images"
PDF_PATH   = "/Volumes/main/credit/loan_docs/ho_so_vay.pdf"
CONTEXT    = None   # vd: "Công ty ABC, MST 0101234567, đề nghị vay 5 tỷ bổ sung vốn lưu động"
OUTPUT_MD  = "/Volumes/main/credit/loan_docs/reports/bao_cao_tham_dinh.md"

INCLUDE_APPENDIX = True   # đính kèm mô tả + OCR từng tài liệu ở cuối báo cáo
MAX_WORKERS = 4
MAX_SIDE    = 1568
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

# COMMAND ----------

import os, io, time, base64
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import fitz
from PIL import Image
from databricks.sdk import WorkspaceClient

client = WorkspaceClient().serving_endpoints.get_open_ai_client()


def to_data_url(img):
    img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def ask(prompt, image=None, max_tokens=4096, retries=5):
    content = [{"type": "text", "text": prompt}]
    if image is not None:
        content.append({"type": "image_url", "image_url": {"url": to_data_url(image)}})
    for i in range(retries):
        try:
            r = client.chat.completions.create(
                model=ENDPOINT, max_tokens=max_tokens, temperature=0,
                messages=[{"role": "user", "content": content}])
            c = r.choices[0].message.content
            return c if isinstance(c, str) else "".join(p.get("text", "") for p in c)
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2 ** i * 3)

# COMMAND ----------

# MAGIC %md ## 1. Mô tả + OCR ảnh

# COMMAND ----------

IMAGE_PROMPT = """Mô tả ngắn ảnh này (loại tài liệu, nội dung chính), sau đó chép lại toàn bộ chữ trong ảnh.
Nếu thấy dấu hiệu chỉnh sửa hoặc bất thường (chữ/số ghi đè, con dấu, chữ ký lạ...) thì ghi thêm.
Trả lời theo dạng:
**Mô tả:** ...
**OCR:** ...
**Bất thường:** ... (hoặc "Không thấy")"""


def process_image(path):
    try:
        with Image.open(path) as img:
            return path, ask(IMAGE_PROMPT, img)
    except Exception as e:
        return path, f"(Lỗi: {e})"


image_paths = sorted(
    os.path.join(root, f)
    for root, _, files in os.walk(IMAGE_DIR)
    for f in files if os.path.splitext(f)[1].lower() in IMG_EXTS
)
print(f"{len(image_paths)} ảnh")

with ThreadPoolExecutor(MAX_WORKERS) as ex:
    image_results = list(ex.map(process_image, image_paths))

# COMMAND ----------

# MAGIC %md ## 2. OCR PDF

# COMMAND ----------

PDF_PROMPT = "Chép lại toàn bộ chữ trong trang tài liệu này. Nếu thấy dấu hiệu chỉnh sửa bất thường thì ghi thêm ở cuối."

doc = fitz.open(PDF_PATH)
pdf_meta = {k: v for k, v in doc.metadata.items() if v}
pages = []
for p in doc:
    pix = p.get_pixmap(dpi=150)
    pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
doc.close()

with ThreadPoolExecutor(MAX_WORKERS) as ex:
    pdf_texts = list(ex.map(lambda im: ask(PDF_PROMPT, im), pages))
print(f"PDF: {len(pdf_texts)} trang | metadata: {pdf_meta}")

# COMMAND ----------

# MAGIC %md ## 3. Phân tích & viết báo cáo

# COMMAND ----------

pdf_name = os.path.basename(PDF_PATH)
data = f"""# Context đề xuất vay
{CONTEXT.strip() if CONTEXT and CONTEXT.strip() else "(Không có)"}

# File PDF: {pdf_name}
Metadata: {pdf_meta}
""" + "\n".join(f"\n## Trang {i+1}\n{t}" for i, t in enumerate(pdf_texts)) + \
"\n\n# Ảnh đính kèm\n" + "\n".join(f"\n## {os.path.basename(p)}\n{r}" for p, r in image_results)

REPORT_PROMPT = """Bạn là chuyên viên thẩm định tín dụng. Dựa trên dữ liệu hồ sơ vay bên dưới, viết báo cáo Markdown bằng tiếng Việt
chỉ ra các dấu hiệu gian lận hoặc bất thường của doanh nghiệp. Chỉ dựa trên dữ liệu có sẵn, ghi rõ nguồn (tên file/trang);
thông tin nào thiếu thì nói là thiếu, không suy đoán.

Cấu trúc:
## 1. Tóm tắt hồ sơ
## 2. Dấu hiệu bất thường (bảng: Dấu hiệu | Bằng chứng | Nguồn | Mức độ)
## 3. Thông tin còn thiếu
## 4. Kết luận (mức rủi ro: Thấp / Trung bình / Cao, kèm lý do)
## 5. Đề xuất xác minh

DỮ LIỆU:
""" + data

report = ask(REPORT_PROMPT, max_tokens=8192)

# COMMAND ----------

# MAGIC %md ## 4. Xuất file .md

# COMMAND ----------

md = f"""# Báo cáo thẩm định dấu hiệu bất thường hồ sơ vay

- Thời gian: {datetime.now():%d/%m/%Y %H:%M}
- File PDF: `{pdf_name}` ({len(pdf_texts)} trang)
- Số ảnh: {len(image_results)}
- Context: {CONTEXT or "(Không có)"}

---

{report}
"""

if INCLUDE_APPENDIX:
    md += "\n\n---\n\n# Phụ lục: Nội dung tài liệu\n"
    md += "\n".join(f"\n### PDF – trang {i+1}\n\n{t}\n" for i, t in enumerate(pdf_texts))
    md += "\n".join(f"\n### Ảnh – {os.path.basename(p)}\n\n{r}\n" for p, r in image_results)

os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write(md)
print("Đã lưu:", OUTPUT_MD)

displayHTML(f"<pre style='white-space:pre-wrap'>{report}</pre>")
