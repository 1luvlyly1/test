---
id: EVENT-MATRIX
used_by: [Classifier, Propagation]
steps: [2, 3]
depends_on: [core/02_concepts_patterns.md, core/03_linkage_graph.md]
load_when: Ngay sau khi chuẩn hóa sự kiện – để gán mã E01–E22, mẫu lan truyền và danh sách sản phẩm ưu tiên
version: v1.0
updated: 2026-10-26
---

# Ma trận sự kiện → nút chạm đầu tiên → sản phẩm

| # | Nhóm sự kiện | Ví dụ | Hướng | Mẫu | Chạm đầu tiên | Lan tiếp (cạnh) | Sản phẩm ưu tiên kiểm tra |
|---|---|---|---|---|---|---|---|
| E01 | Lãi suất điều hành / lãi suất thị trường tăng | NHNN điều chỉnh lãi suất, thanh khoản hệ thống căng | Out-in | P3 | Tất cả | `L09` `L10` | `CN-LN-01..04` `CN-ACC-03` `CN-DEP-*` `CIB-LN-02` `CIB-CM-01` `CN-INV-02a` |
| E02 | Tỷ giá biến động mạnh | VND mất giá nhanh | Out-in | P3 | CIB, SME XNK | `L08` `L02` | `CIB-TF-01` `CIB-FX-01` `CIB-CM-02` `SME-PAY-04` `CN-ACC-02` `CN-PAY-01` |
| E03 | Thuế quan / rào cản thương mại | Thuế nhập khẩu cao vào thị trường XK chính | Out-in | P1 | CIB/SME xuất khẩu | `L02` `L03` `L01` `L06` | `CIB-TF-02` `CIB-LN-01` `CIB-PAY-06` → `CN-LN-05/06` `CN-CARD-01` |
| E04 | Suy yếu ngành BĐS / pháp lý dự án | Dự án bị dừng, siết tín dụng BĐS | Out-in | P1 | CĐT (CIB) | `L04` `L05` `L01` | `CIB-LN-02` `CIB-ACC-04` `CIB-INV-01` → `CN-LN-01..03` `CN-INV-01` `CN-INV-02e` |
| E05 | Sự cố trái phiếu DN | Chậm trả lãi/gốc trái phiếu | Out-in | P1 | Tổ chức phát hành | `L05` `L10` | `CIB-INV-01` `CN-INV-01` `CN-INV-02a` `IR-EQ-01` |
| E06 | Biến cố pháp lý lãnh đạo / chủ DN | Khởi tố, phong tỏa tài sản | Out-in | P2 | Cá nhân (Private/Priority) | `L01` `L05` `L10` | `CN-*` của cá nhân → `CIB-*`/`SME-*` của DN → `CN-INV-01` |
| E07 | Sa thải hàng loạt / đóng cửa nhà máy | KCN cắt giảm lao động | Out-in | P1 | DN | `L02` `L06` | `CIB-PAY-06` `SME-PAY-06` → `CN-LN-05/06/10` `CN-CARD-01` → `HKD-LN-01` |
| E08 | Lạm phát / giá tiêu dùng tăng | Giá xăng, điện, lương thực tăng | Out-in | P2 | Hộ gia đình | `L06` | `CN-CARD-01` `CN-LN-05/06` `CN-DEP-02` → `HKD-REV-*` |
| E09 | Chính sách thuế/hóa đơn cho HKD | Bỏ thuế khoán, bắt buộc hóa đơn điện tử | Out-in | P2+P1 (lai) | HKD | `L07` `L06` | `HKD-ACC-01` `HKD-REV-*` `HKD-LN-01/02` → `SME-*` mới chuyển đổi |
| E10 | Thiên tai diện rộng | Bão, lũ, ngập | Out-in | P3 (khu vực) | Tất cả tại địa bàn | `L06` `L03` | `CN-INS-03` `HKD-INS-01` `CIB-INS-01` `CN-LN-02/08` `HKD-LN-*` `CN-PAY-02` |
| E11 | Dịch bệnh | Dịch lây lan, giãn cách | Out-in | P2→P3 | Cá nhân | `L06` `L02` | `CN-INS-01` `HKD-*` `SME-*` `CIB-SCF-01` (hàng không) |
| E12 | Làn sóng lừa đảo / an ninh mạng ngoài | Mạo danh ngân hàng, mã độc | Out-in | P2 | KHCN, HKD | `L09` `L10` | `CN-DIG-01` `CN-ACC-01` `HKD-ACC-01` `SME-DIG-01` |
| E13 | Quy định NHNN / pháp luật ngân hàng | Room tín dụng, xác thực sinh trắc, giới hạn sở hữu | Out-in | P3 | Tất cả + NĐT | `L09` `L10` | Mọi nhóm vay; `CN-DIG-01`; `IR-*` |
| E14 | Sự cố tại anchor chuỗi cung ứng | Anchor tạm dừng sản xuất/đổi chính sách đại lý | Out-in | P1 | Anchor (CIB) | `L03` | `CIB-SCF-01` → `SME-LN-*` `HKD-LN-*` |
| E15 | Khủng hoảng ngành hàng không / du lịch | Giá nhiên liệu tăng, tạm dừng đường bay | Out-in | P1 | Hãng bay / đại lý | `L03` `L02` | `CIB-SCF-01` (đại lý vé, vận chuyển hàng hóa) `CN-INS-03` (TechCare Travel) |
| E16 | Chậm giải ngân đầu tư công | Dự án công chậm thanh toán | Out-in | P1 | SME/CIB nhà thầu | `L12` `L02` | `SME-GTE-01` `CIB-TF-04` `SME-LN-*` `CIB-LN-01` |
| E17 | Thị trường chứng khoán giảm mạnh | Chỉ số giảm sâu | Out-in | P3 | NĐT cá nhân, NĐT TCB | `L10` `L11` | `CN-INV-02*` `IR-EQ-01` `IR-ECO-01` |
| E18 | Sự cố hệ thống Techcombank | App/Business/thẻ/POS gián đoạn | **In-out** | P3 | Tất cả | `L09` `L10` | `CN-DIG-01` `HKD-DIG-01` `HKD-REV-*` `SME-DIG-01` `CIB-DIG-01` `CIB-COL-01` |
| E19 | Thay đổi lãi suất/phí/khẩu vị của chính Techcombank | Tăng lãi suất cho vay, siết hạn mức tín chấp | **In-out** | P3 | Phân khúc bị áp dụng | `L09` | Theo sản phẩm bị thay đổi + bậc 2 (`inside_out/bank_response_risks.md`) |
| E20 | Sự cố danh tiếng / bán hàng sai | Khiếu nại tập thể iBond, bảo hiểm | **In-out** | P2→P3 | KHCN Priority | `L10` `L11` | `CN-INV-01` `CN-INS-02` `IR-EQ-01` |
| E21 | Rò rỉ dữ liệu khách hàng | Lộ thông tin tài khoản | **In-out** | P3 | Tất cả | `L09` `L10` | `CN-DIG-01` `CO` toàn hệ thống, `FR` tăng sau rò rỉ |
| E22 | Quy định ESG / thuế carbon tại thị trường XK | Yêu cầu báo cáo phát thải | Out-in | P1 | CIB ngành phát thải cao | `L08` | `CIB-TF-02` `CIB-LN-02` `CIB-DEP-01` (tiền gửi xanh – cơ hội) |
