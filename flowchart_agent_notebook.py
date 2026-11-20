# Databricks notebook source
# MAGIC %md
# MAGIC # 🪙 Flowchart Agent · Techcom Wealth style
# MAGIC
# MAGIC Nhập mô tả quy trình bằng ngôn ngữ tự nhiên → **Claude Sonnet 5.5** (Databricks Foundation Model endpoint) dựng flowchart
# MAGIC theo bộ entity draw.io (start/end, process, decision, data, document, database...) → xuất:
# MAGIC
# MAGIC | File | Dùng để |
# MAGIC |---|---|
# MAGIC | `*.html` | Flowchart động (dựng dần + dòng chảy), mở offline, có nút tải SVG/PNG |
# MAGIC | `*.gif`  | Chèn vào PowerPoint (Insert → Pictures) – tự chạy khi trình chiếu |
# MAGIC | `*.svg`  | Bản vector tĩnh – chèn PowerPoint vẫn sắc nét, có thể *Convert to Shape* để sửa |
# MAGIC | `*.json` | Spec của sơ đồ – dùng cho bước **Chỉnh sửa** bên dưới |
# MAGIC
# MAGIC **Cách dùng:** chỉnh widget phía trên → sửa ô *① Mô tả quy trình* → `Run all`. Muốn sửa sơ đồ, điền ô *④ Chỉnh sửa* rồi chạy riêng ô đó.

# COMMAND ----------

# MAGIC %run ./flowchart_agent_lib

# COMMAND ----------

# Widgets cấu hình (chỉ tạo một lần; đổi giá trị trên thanh widget ở đầu notebook)
dbutils.widgets.text("endpoint", "databricks-claude-sonnet-5-5", "Endpoint / model")
dbutils.widgets.dropdown("backend", "serving", ["serving", "anthropic"], "API")
dbutils.widgets.text("output_dir", "", "Thư mục lưu (trống = /Workspace/Users/<bạn>/flowcharts)")
dbutils.widgets.text("chart_name", "", "Tên file (trống = theo tiêu đề)")
dbutils.widgets.dropdown("direction", "auto", ["auto", "LR", "TB"], "Hướng")
dbutils.widgets.dropdown("theme", "wealth_light", list(THEMES.keys()), "Theme")
dbutils.widgets.dropdown("gif_mode", "build_flow", ["build_flow", "flow", "build"], "Kiểu GIF")
dbutils.widgets.dropdown("gif_aspect", "auto", ["auto", "16:9", "4:3", "none"], "Khung GIF")
dbutils.widgets.dropdown("gif_title", "yes", ["yes", "no"], "Tiêu đề trong GIF")

# COMMAND ----------

# MAGIC %md ## ① Mô tả quy trình (context)
# MAGIC Viết tự do: các bước, ai làm (để agent chia swimlane), điều kiện rẽ nhánh, vòng lặp, hệ thống/tài liệu liên quan, SLA.

# COMMAND ----------

USER_CONTEXT = """
Quy trình đầu tư trái phiếu cho khách hàng Techcom Wealth.
Khách hàng gửi yêu cầu mua trái phiếu trên app hoặc qua RM.
RM kiểm tra hồ sơ khẩu vị rủi ro của khách hàng; nếu hồ sơ đã hết hạn thì khách hàng làm lại bài đánh giá trên app rồi RM kiểm tra lại.
Hệ thống kiểm tra số dư tài khoản. Nếu không đủ, hệ thống gửi thông báo nạp tiền và chờ tối đa 24h; quá hạn thì huỷ yêu cầu.
Nếu đủ, hệ thống đặt lệnh và phong toả tiền; Back-office xác nhận lệnh với tổ chức phát hành.
Hệ thống xuất hợp đồng điện tử, khách hàng ký bằng OTP.
Sau khi ký, hệ thống ghi nhận vào danh mục đầu tư (core banking) và gửi email xác nhận cho khách hàng.
"""

# COMMAND ----------

# MAGIC %md ## ② Chạy agent

# COMMAND ----------

import os, base64

def _w(name):
    return dbutils.widgets.get(name).strip()

def resolve_output_dir():
    d = _w("output_dir")
    if not d:
        user = spark.sql("SELECT current_user()").first()[0]
        d = f"/Workspace/Users/{user}/flowcharts"
    try:
        os.makedirs(d, exist_ok=True)
        probe = os.path.join(d, ".write_test")
        open(probe, "w").write("ok"); os.remove(probe)
        return d
    except Exception as ex:
        print(f"⚠ Không ghi được vào {d} ({ex}). Tạm lưu ở /tmp/flowcharts – nên đặt output_dir là một Volume, "
              f"vd /Volumes/<catalog>/<schema>/<volume>/flowcharts")
        os.makedirs("/tmp/flowcharts", exist_ok=True)
        return "/tmp/flowcharts"

def make_llm():
    endpoint, backend = _w("endpoint"), _w("backend")
    if backend == "anthropic" and endpoint.startswith("databricks-claude-"):
        endpoint = "system.ai.claude-" + endpoint[len("databricks-claude-"):]   # databricks-claude-sonnet-5-5 → system.ai.claude-sonnet-5-5
    return DatabricksClaude(endpoint=endpoint, backend=backend)

def run(context=USER_CONTEXT, previous_spec=None, revision=None):
    aspect = _w("gif_aspect")
    return run_flowchart_agent(
        context=context, llm=make_llm(), out_dir=OUTPUT_DIR, name=_w("chart_name") or None,
        direction=_w("direction"), theme=_w("theme"), gif_mode=_w("gif_mode"),
        gif_aspect=None if aspect == "none" else aspect, gif_title=_w("gif_title") == "yes",
        previous_spec=previous_spec, revision=revision)

OUTPUT_DIR = resolve_output_dir()
result = run()
if result.warnings:
    print("Cảnh báo:", *result.warnings, sep="\n  • ")

# COMMAND ----------

# MAGIC %md ## ③ Xem kết quả

# COMMAND ----------

def show(res):
    displayHTML(res.html)

def show_gif(res, max_mb=12):
    if not res.gif_path:
        return
    raw = open(res.gif_path, "rb").read()
    size = len(raw) / 1e6
    links = (f'<p style="font-family:sans-serif;font-size:13px;color:#7A7062">'
             f'HTML: <code>{res.html_path}</code><br>GIF: <code>{res.gif_path}</code> ({size:.1f} MB)<br>'
             f'SVG: <code>{res.svg_path}</code><br>Tải về: mở thư mục trong Workspace / Catalog Explorer → ⋮ → Download.</p>')
    if size > max_mb:
        displayHTML(links + "<p>GIF lớn, không hiển thị inline.</p>")
        return
    b64 = base64.b64encode(raw).decode()
    name = os.path.basename(res.gif_path)
    displayHTML(f'<div style="background:#F3EEE4;padding:12px;border-radius:12px">'
                f'<img src="data:image/gif;base64,{b64}" style="max-width:100%;border-radius:8px;box-shadow:0 8px 24px rgba(60,40,10,.15)">'
                f'<p><a download="{name}" href="data:image/gif;base64,{b64}" style="color:#7D6136;font-family:sans-serif">⬇ Tải GIF</a></p>{links}</div>')

show(result)

# COMMAND ----------

show_gif(result)

# COMMAND ----------

# MAGIC %md ## ④ Chỉnh sửa sơ đồ (tuỳ chọn)
# MAGIC Mô tả thay đổi bằng lời – agent sửa trên spec hiện tại (giữ nguyên các bước không liên quan) và xuất bộ file mới.

# COMMAND ----------

REVISION = ""   # vd: "Thêm bước Phòng Tuân thủ duyệt nếu giá trị lệnh trên 5 tỷ; đổi lane Back-office thành 'Vận hành'"

if REVISION.strip():
    result = run(previous_spec=result.spec, revision=REVISION)
    show(result)
    show_gif(result)
else:
    print("REVISION đang trống – bỏ qua.")

# COMMAND ----------

# MAGIC %md ## ⑤ Thư viện entity mẫu (draw.io) & bảng màu
# MAGIC Sinh từ `SHAPES` / `THEMES` trong `flowchart_agent_lib` – cũng là danh sách entity mà prompt cho phép model dùng.

# COMMAND ----------

catalog_html = build_entity_catalog_html(_w("theme"))
catalog_path = os.path.join(OUTPUT_DIR, "flowchart_entities.html")
with open(catalog_path, "w", encoding="utf-8") as f:
    f.write(catalog_html)
print("Đã lưu:", catalog_path)
displayHTML(catalog_html)

# COMMAND ----------

# MAGIC %md ## ⑥ (Tuỳ chọn) Render lại từ JSON có sẵn – không gọi model
# MAGIC Hữu ích khi muốn sửa tay spec (đổi nhãn, tone, lane) rồi xuất lại HTML/GIF.

# COMMAND ----------

# import json
# spec = json.load(open(result.json_path, encoding="utf-8"))
# spec["nodes"][0]["label"] = "Nhãn mới"
# result = run_flowchart_agent(spec=spec, out_dir=OUTPUT_DIR, direction=_w("direction"), theme=_w("theme"),
#                              gif_mode=_w("gif_mode"), gif_aspect=_w("gif_aspect"))
# show(result); show_gif(result)
