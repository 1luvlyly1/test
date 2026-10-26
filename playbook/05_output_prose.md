---
id: CORE-OUTPUT-PROSE
used_by: [Critic, Orchestrator]
steps: [6]
depends_on: [core/04_reasoning_procedure.md, guardrails.md]
load_when: Khi viết kết luận cuối cùng của một lượt suy luận
version: v1.2
updated: 2026-10-26
---

# Mẫu viết kết luận bằng văn xuôi

Kết luận là một bài viết ngắn, đọc liền mạch, **250–500 từ**. Không dùng bảng, không dùng JSON. Mã (`L..`, `CN-..`, `S..`) chỉ đặt trong ngoặc sau cụm từ tiếng Việt để tra cứu, câu văn vẫn phải đọc hiểu được khi bỏ mã đi.

## Bố cục 6 đoạn

1. **Sự kiện và hướng tác động.** Một đến hai câu: tóm tắt lại sự kiện được giao; outside-in hay inside-out; theo mẫu lan truyền nào.
2. **Ai bị chạm đầu tiên và vì sao.** Nêu phân khúc khách hàng và cơ chế cụ thể (mất doanh thu, mất thu nhập, bị phong tỏa…).
3. **Rủi ro lan đi như thế nào.** Kể theo từng nhánh, mỗi nhánh nói: từ ai sang ai, qua kênh gì, sau khoảng bao lâu, mức chắc chắn. Nếu có vòng phản hồi thì nói ở cuối đoạn này.
4. **Sản phẩm nào chịu ảnh hưởng.** Đi theo thứ tự phân khúc như ở đoạn 3; với mỗi phân khúc nêu các sản phẩm chính và loại rủi ro (tín dụng, thanh khoản, gian lận…).
5. **Cần kiểm tra gì trong dữ liệu nội bộ.** Nêu tín hiệu cụ thể sẽ xác nhận hoặc bác bỏ các nhận định ở đoạn 3–4. Nếu chưa có số liệu, nói thẳng là chưa có.
6. **Phản ứng của ngân hàng và điểm còn chưa chắc.** Phản ứng nào của ngân hàng có thể làm rủi ro nặng thêm; giả định yếu nhất của lập luận là gì.

## Quy tắc viết
- Viết như một chuyên viên rủi ro báo cáo cho trưởng phòng: rõ, cụ thể, không rào đón.
- Mỗi nhận định ở hop 2 trở đi phải kèm từ chỉ mức chắc chắn (“có thể”, “giả thuyết”).
- Chỉ dùng thông tin có trong sự kiện được giao và trong playbook. Không viết số liệu không có cơ sở. Không nêu tên khách hàng cụ thể.
- Ưu tiên chiều sâu ở 2–3 nhánh quan trọng nhất thay vì liệt kê mọi nhánh có thể.

## Khung câu gợi ý
> [Sự kiện] là sự kiện [outside-in/inside-out], lan theo mẫu [P..]. Bên chịu tác động đầu tiên là [phân khúc], vì [cơ chế]. Từ đó, rủi ro có khả năng cao lan sang [phân khúc] qua [kênh] ([L..]) trong khoảng [độ trễ]… Ở phía sản phẩm, đáng lo nhất là [sản phẩm] ([mã]) do [rủi ro]… Để xác nhận, cần kiểm tra [tín hiệu] ([S..])… Điểm cần lưu ý là nếu ngân hàng [phản ứng], rủi ro có thể [hệ quả]. Giả định yếu nhất của lập luận này là […].
