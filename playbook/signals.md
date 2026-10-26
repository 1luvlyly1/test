---
id: IO-SIGNALS
used_by: [Inside-out Monitor, Product-Impact]
steps: [6]
depends_on: [core/03_linkage_graph.md]
load_when: Liệt kê tín hiệu nội bộ (S01–S16) cần truy vấn để xác nhận/bác bỏ giả thuyết
version: v1.0
updated: 2026-10-26
---

# Inside-out: thư viện tín hiệu nội bộ

| ID | Tín hiệu | Nguồn dữ liệu | Báo trước điều gì | Phân khúc |
|---|---|---|---|---|
| `S01` | Lô chi lương trễ / giảm tổng quỹ / giảm số người | Thanh toán lương | DN căng dòng tiền; nhân viên sắp giảm thu nhập | SME, CIB → KHCN |
| `S02` | Doanh thu QR/Soundbox/POS giảm theo địa bàn, MCC | Quản lý doanh thu HKD/SME | Sức mua địa phương giảm | HKD, SME |
| `S03` | Unique payers giảm | Giao dịch nhận tiền | Mất khách | HKD |
| `S04` | Sử dụng hạn mức MyCash/thẻ/ShopCash tăng nhanh | Hệ thống thẻ/thấu chi | Căng thẳng thanh khoản cá nhân/hộ | KHCN, HKD |
| `S05` | Chuyển từ trả toàn bộ sang trả tối thiểu thẻ tín dụng | Hệ thống thẻ | Sắp DPD | KHCN |
| `S06` | Tất toán tiết kiệm trước hạn, vay cầm cố tiền gửi tăng | Core banking | Cần tiền gấp | KHCN, SME |
| `S07` | Rút tiền mặt CDM tăng đột biến | CDM | Hoảng loạn/tin đồn | Tất cả |
| `S08` | Bán lại iBond/rút iFund theo một tổ chức phát hành/ngành | Hệ thống đầu tư | Mất niềm tin vào issuer/ngành | KHCN Priority |
| `S09` | Hủy bảo hiểm sớm, ngừng đóng phí | Đối tác bảo hiểm | Thu nhập giảm hoặc khủng hoảng niềm tin | KHCN |
| `S10` | Nộp NSNN trễ, hóa đơn điện/cảng giảm | Thanh toán | Sản xuất/xuất khẩu giảm | SME, CIB |
| `S11` | Spoke SCF cùng anchor đồng loạt chậm trả | Tài trợ chuỗi cung ứng | Anchor gặp vấn đề | CIB → SME/HKD |
| `S12` | Chủ DN rút tiết kiệm cá nhân & DN tăng sử dụng hạn mức cùng lúc | Liên kết CIF (`L01`) | Chủ đang bơm tiền cứu DN | SME, CIB ↔ KHCN |
| `S13` | Đăng nhập lạ, đổi thiết bị, người thụ hưởng mới giá trị lớn | Ngân hàng số | Lừa đảo/chiếm đoạt | Tất cả |
| `S14` | Khiếu nại tăng theo chủ đề | CRM, tổng đài | Rủi ro danh tiếng | Tất cả |
| `S15` | Giá trị thị trường âm lớn trên vị thế FX/phái sinh của khách | Treasury | Rủi ro đối tác | CIB |
| `S16` | Doanh thu HKD chảy về TK cá nhân thay vì TK HKD | Giao dịch | Né thuế / rủi ro AML | HKD |
