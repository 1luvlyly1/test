# Databricks notebook source
# MAGIC %md
# MAGIC # rmd_llm · Quickstart
# MAGIC Gọi Claude Sonnet 5.5 qua model service `analytics_ai.rmd_bau.claude-sonnet-5-5-rmd_bau` (Unity AI Gateway).

# COMMAND ----------

# MAGIC %pip install /Volumes/analytics_ai/rmd_bau/libs/rmd_llm-0.1.0-py3-none-any.whl

# COMMAND ----------

from rmd_llm import Connect, CallModel, GatewayError

# COMMAND ----------

# MAGIC %md ## 1. Kiểm tra kết nối

# COMMAND ----------

call_model = CallModel()
call_model.test_connection()

# COMMAND ----------

# MAGIC %md ## 2. Hỏi một câu (lớp test CallModel)

# COMMAND ----------

answer = call_model("Giải thích ngắn gọn khẩu vị rủi ro (risk appetite) trong cho vay cá nhân, tối đa 4 câu.")

# COMMAND ----------

# MAGIC %md ## 3. Dùng Connect trong code của usecase

# COMMAND ----------

llm = Connect(system="Bạn là chuyên viên quản trị rủi ro tín dụng. Trả lời ngắn gọn bằng tiếng Việt.")

print(llm.ask("Ba tiêu chí chính để route hồ sơ vay sang Expert-led là gì?"))

# COMMAND ----------

# Trả lời dạng luồng
for chunk in llm.stream("Viết 5 gạch đầu dòng về quy trình thẩm định khoản vay mua nhà."):
    print(chunk, end="")

# COMMAND ----------

# Nhận JSON có cấu trúc
steps = llm.ask_json("Trả về JSON dạng {\"steps\": [{\"name\": str, \"owner\": str}]} cho quy trình mở tài khoản thanh toán.")
display(steps["steps"])

# COMMAND ----------

# Hỏi nhiều prompt song song
questions = ["Định nghĩa LTV?", "Định nghĩa DSCR?", "Định nghĩa PD?", "Định nghĩa LGD?"]
for q, a in zip(questions, llm.ask_many(questions, max_workers=4)):
    print(f"• {q}\n  {a}\n")

# COMMAND ----------

# Hội thoại nhiều lượt
chat = llm.conversation()
print(chat.send("Tôi có khách hàng thu nhập 40 triệu/tháng, muốn vay mua nhà 3 tỷ."))
print(chat.send("Với lãi suất 9%/năm, 20 năm thì trả góp mỗi tháng khoảng bao nhiêu?"))

# COMMAND ----------

# Bắt lỗi
try:
    Connect(model_service="analytics_ai.rmd_bau.khong_ton_tai", retries=0).ask("hi")
except GatewayError as e:
    print("Status:", e.status)
    print("Gợi ý:", e.hint)
