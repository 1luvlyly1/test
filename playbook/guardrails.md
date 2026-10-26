---
id: GUARDRAILS
used_by: [ALL]
steps: [1-6]
depends_on: []
load_when: Luôn nạp – ràng buộc bắt buộc cho mọi agent
version: v1.2
updated: 2026-10-26
---

# Guardrails cho agent

1. **Khách hàng trước, sản phẩm sau.** Không được liệt kê sản phẩm khi chưa xác định nút khách hàng và cạnh truyền dẫn.
2. **Không bịa số liệu.** Không tự tạo dư nợ, số khách hàng, tỷ lệ nợ xấu. Khi thiếu dữ liệu, viết rõ “chưa có số liệu – cần truy vấn nội bộ”.
3. **Không bịa tên khách hàng/DN cụ thể** là khách hàng của ngân hàng nếu dữ liệu nội bộ chưa xác nhận.
4. **Bảo vệ dữ liệu cá nhân:** đầu ra chỉ dùng mã CIF/ID đã ẩn danh; không đưa tên, số tài khoản, số điện thoại vào báo cáo tổng hợp.
5. **Tách bạch giả thuyết và xác nhận:** mọi tác động hop ≥ 2 mặc định là giả thuyết cho đến khi có tín hiệu nội bộ.
6. **Không suy diễn quá 3 hop** nếu không có bằng chứng định lượng.
7. **Chỉ suy luận từ sự kiện được giao.** Sự kiện đã được người dùng sàng lọc: không đánh giá lại có đáng xử lý hay không, không tự tìm thêm tin, không thêm tình tiết. Thiếu chi tiết quan trọng thì nêu rõ giả định. Với sự kiện pháp lý về cá nhân, không suy đoán ngoài nội dung đã cho.
8. **Luôn chạy bước phản biện (bước 6)** trước khi chốt kết luận.
9. **Danh mục sản phẩm có thể thay đổi:** nếu sự kiện liên quan tới sản phẩm không có trong phần (f) của file phân khúc, ghi rõ “sản phẩm chưa có trong danh mục playbook”.
10. **Không đưa khuyến nghị đầu tư** cho nhà đầu tư; chỉ đánh giá rủi ro.
