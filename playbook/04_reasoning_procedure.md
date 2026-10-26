---
id: CORE-PROCEDURE
used_by: [Orchestrator, ALL]
steps: [1-6]
depends_on: [00_INDEX.md]
load_when: Orchestrator luôn nạp; agent con nạp khi cần biết vai trò của mình
version: v1.2
updated: 2026-10-26
---

# Quy trình suy luận 6 bước (bắt buộc)

**Đầu vào:** thông tin một sự kiện **đã được người dùng sàng lọc**. Agent không lọc, không đánh giá sự kiện có đáng xử lý hay không, không tự tìm thêm tin. Agent chỉ suy luận từ nội dung sự kiện và playbook.

**Đầu ra:** một bài văn xuôi theo mẫu `core/05_output_prose.md`.

| Bước | Câu hỏi phải trả lời | Agent phụ trách | File cần dùng |
|---|---|---|---|
| 1 | Sự kiện chạm ai đầu tiên? Outside-in hay inside-out? Lan theo mẫu nào (P1 / P2 / P3)? Có dính nút lai HKD không? | Propagation | `core/02_concepts_patterns.md` |
| 2 | Rủi ro lan sang ai tiếp theo, qua kênh nào (`L01`–`L12`), sau bao lâu? Có vòng phản hồi nào không? | Propagation | `core/03_linkage_graph.md`, file phân khúc phần (e) |
| 3 | Ở mỗi phân khúc bị chạm, sản phẩm nào bị ảnh hưởng và loại rủi ro gì? | Product-Impact | File phân khúc phần (c), `core/01_risk_codes.md` |
| 4 | Cần kiểm tra tín hiệu nội bộ nào (`S01`–`S16`) để xác nhận hay bác bỏ? | Inside-out Monitor | `inside_out/signals.md`, file phân khúc phần (d) |
| 5 | Nếu ngân hàng phản ứng (siết tín dụng, đổi lãi suất, khóa tài khoản…), có tạo rủi ro mới không? | Inside-out Monitor | `inside_out/bank_response_risks.md` |
| 6 | Lập luận có bỏ sót phân khúc, suy diễn quá đà hay bịa số không? Giả định nào yếu nhất? Viết kết luận. | Critic | `guardrails.md`, `core/05_output_prose.md` |

## Câu hỏi kiểm tra nhanh ở bước 1
- Sự kiện làm thay đổi **doanh thu, chi phí hoặc pháp lý của một tổ chức** trước? → P1.
- Sự kiện làm thay đổi **thu nhập, sức khỏe, tài sản hoặc hành vi của con người** trước? → P2.
- Sự kiện tác động **cùng lúc** tới mọi khách hàng qua giá cả vĩ mô, quy định hay hạ tầng ngân hàng? → P3.
- Sự kiện bắt nguồn từ **bên trong ngân hàng** (hệ thống, chính sách, dữ liệu, sản phẩm) → inside-out; còn lại → outside-in.
- Đối tượng là hộ kinh doanh → luôn xét cả P1 và P2 (nút lai).

## Mức chắc chắn
Không dùng điểm số. Khi viết, gắn mỗi nhận định với một trong ba mức:
- **Có khả năng cao:** nút chạm đầu tiên hoặc hop 1, cơ chế rõ ràng.
- **Có thể:** hop 2, hoặc hop 1 nhưng cơ chế còn phụ thuộc điều kiện.
- **Giả thuyết, cần kiểm chứng:** hop 3 trở lên, hoặc phải dựa vào giả định do sự kiện thiếu chi tiết.

Nếu đã có tín hiệu nội bộ xác nhận, được nâng lên một mức và phải nói rõ tín hiệu nào.
