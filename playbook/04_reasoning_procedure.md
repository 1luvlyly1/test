---
id: CORE-PROCEDURE
used_by: [Orchestrator, ALL]
steps: [1-10]
depends_on: [00_INDEX.md]
load_when: Orchestrator luôn nạp; agent con nạp khi cần biết vai trò của mình
version: v1.0
updated: 2026-10-26
---

# Quy trình suy luận 10 bước (bắt buộc)

| Bước | Tên | Agent phụ trách | Việc phải làm | Đầu ra |
|---|---|---|---|---|
| 1 | Chuẩn hóa sự kiện | Ingest | Ai/cái gì, ở đâu, khi nào, quy mô, nguồn, độ tin cậy nguồn (A–D) | `event` object |
| 2 | Phân loại | Classifier | Outside-in / Inside-out / cả hai; nhóm sự kiện (`events/event_matrix.md`); ngành (VSIC); địa bàn | `classification` |
| 3 | Xác định nút chạm đầu tiên & mẫu lan truyền | Propagation | Chọn P1 / P2 / P3; đánh dấu nút lai HKD | `pattern`, `first_hit_segments` |
| 4 | Duyệt đồ thị | Propagation | Đi theo cạnh `L01`–`L12`, ghi cơ chế, độ trễ, hop | `propagation_path[]` |
| 5 | Ánh xạ sản phẩm | Product-Impact | Với mỗi phân khúc bị chạm: tra bảng độ nhạy ở `segments/` (file của phân khúc tương ứng) → mã sản phẩm, loại rủi ro, chiều tác động | `product_impacts[]` |
| 6 | Tín hiệu kiểm chứng | Inside-out Monitor | Liệt kê tín hiệu nội bộ cần truy vấn để xác nhận/bác bỏ (`inside_out/`) | `signals_to_check[]` |
| 7 | Chấm điểm | Product-Impact | Mức độ × khả năng × độ phủ × thời gian (`scoring/scoring.md`) | `score` |
| 8 | Kiểm tra phản ứng ngân hàng | Inside-out Monitor | Nếu ngân hàng phản ứng (siết tín dụng, tăng lãi suất, khóa tài khoản), có tạo rủi ro bậc 2 không? | `bank_response_risks[]` |
| 9 | Vòng phản hồi | Propagation | Kiểm tra ít nhất 1 vòng lặp (`core/02_concepts_patterns.md` (phần Vòng phản hồi)) | `feedback_loops[]` |
| 10 | Phản biện | Critic | Kiểm tra: có bỏ sót phân khúc? có suy luận quá đà? có bịa số? giả định nào yếu nhất? | `critic_notes`, `confidence` cuối |

**Câu hỏi kiểm tra nhanh ở bước 3:**
- Sự kiện có làm thay đổi **doanh thu/chi phí/pháp lý của một tổ chức** trước không? → P1.
- Sự kiện có làm thay đổi **thu nhập/sức khỏe/tài sản/hành vi của con người** trước không? → P2.
- Sự kiện có tác động **cùng lúc** tới mọi khách hàng qua giá cả vĩ mô, quy định hay hạ tầng ngân hàng không? → P3.
- Nếu đối tượng là HKD → luôn ghi cả P1 và P2 (nút lai).
