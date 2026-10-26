---
id: EX-P1
used_by: [Propagation, Product-Impact, Critic]
steps: [1-6]
depends_on: [core/05_output_prose.md]
load_when: Few-shot khi sự kiện thuộc mẫu P1 (doanh nghiệp bị chạm trước)
version: v1.2
updated: 2026-10-26
---

# Ví dụ P1 – Doanh nghiệp trước: thuế quan cao lên hàng dệt may xuất khẩu

> Kịch bản giả định để minh họa cách suy luận, không phản ánh dữ liệu thực.

Một thị trường nhập khẩu lớn công bố mức thuế cao với hàng dệt may Việt Nam. Đây là sự kiện outside-in, lan theo mẫu doanh nghiệp trước (P1).

Bên chịu tác động đầu tiên là các doanh nghiệp dệt may xuất khẩu, cả khách hàng doanh nghiệp lớn lẫn SME. Đơn hàng bị cắt hoặc bị ép giá, nên doanh thu và dòng tiền giảm gần như ngay khi thuế có hiệu lực.

Từ doanh nghiệp, rủi ro đi theo ba nhánh. Nhánh mạnh nhất là người lao động: để giảm chi phí, doanh nghiệp giảm ca hoặc cắt giảm nhân sự, nên thu nhập của công nhân nhận lương qua Techcombank có khả năng cao sụt giảm trong một đến ba tháng (L02). Nhánh thứ hai là chủ doanh nghiệp, thường là khách hàng Priority: họ có khả năng cao rút tiết kiệm cá nhân hoặc dùng thấu chi có tài sản bảo đảm để bơm vốn cho công ty (L01), và việc này diễn ra gần như tức thì. Nhánh thứ ba là các nhà cung cấp phụ liệu, đa số là SME, có thể bị chậm thanh toán (L03). Cuối cùng có một vòng phản hồi: khi công nhân chi tiêu ít đi, các hộ kinh doanh quanh khu công nghiệp như nhà trọ, quán ăn, tạp hóa có thể mất doanh thu (L06). Đây là hop 2, nên mới ở mức có thể.

Về sản phẩm, ở doanh nghiệp đáng chú ý nhất là tài trợ xuất khẩu và L/C xuất khẩu (CIB-TF-02) cùng vay vốn lưu động (CIB-LN-01, SME-LN-01), với rủi ro tín dụng. Ở người lao động, các khoản dễ trễ hạn sớm nhất là vay tín chấp trả góp (CN-LN-06), thấu chi MyCash (CN-LN-05) và thẻ tín dụng (CN-CARD-01). Ở chủ doanh nghiệp, rủi ro là rút tiền gửi (CN-DEP-01) và dư nợ thấu chi có tài sản bảo đảm tăng (CN-LN-09). Ở hộ kinh doanh, doanh thu qua QR và Soundbox giảm, kéo theo việc dùng hạn mức ShopCash tăng (HKD-LN-01).

Để xác nhận, cần kiểm tra các lô chi lương của doanh nghiệp dệt may xem có trễ hoặc giảm quy mô không (S01), hóa đơn điện của nhà máy có giảm không (S10), có trường hợp chủ doanh nghiệp rút tiết kiệm cùng lúc với việc doanh nghiệp dùng kín hạn mức không (S12), và doanh thu QR quanh các khu công nghiệp dệt may (S02). Hiện chưa có số liệu dư nợ theo ngành, cần truy vấn nội bộ.

Nếu ngân hàng siết hạn mức vốn lưu động với ngành dệt may quá sớm, doanh nghiệp có thể phải cắt giảm nhân sự mạnh hơn, khiến nhánh người lao động xấu đi nhanh hơn. Giả định yếu nhất là doanh nghiệp không tìm được thị trường thay thế trong ngắn hạn. Nếu họ chuyển hướng được, nhánh người lao động sẽ nhẹ hơn nhiều.
