---
id: SEG-HKD
used_by: [Propagation, Product-Impact, Inside-out Monitor]
steps: [2, 3, 4]
depends_on: [core/01_risk_codes.md, core/03_linkage_graph.md]
load_when: Sự kiện chạm hộ kinh doanh, sức mua địa phương, thuế HKD, hoặc lan qua L03, L06, L07
version: v1.2
updated: 2026-10-26
---

# Phân khúc: Hộ kinh doanh (HKD) – nút lai

> Cấu trúc: (a) Chân dung → (b) Động lực rủi ro → (c) Bảng độ nhạy sản phẩm → (d) Tín hiệu sớm nội bộ → (e) Lan ra phân khúc khác → (f) Danh mục sản phẩm & URL nguồn


## (a) Chân dung
- Chủ hộ là cá nhân, thường đồng thời là KHCN (một CIF hoặc hai CIF liên kết).
- Mô hình: tạp hóa, ăn uống, bán lẻ online, dịch vụ nhỏ; doanh thu nhận qua QR, Soundbox, POS, phần mềm bán hàng.
- Đang trong giai đoạn **chuyển đổi thuế** và có lộ trình **chuyển lên doanh nghiệp** (cạnh `L07`).

## (b) Động lực rủi ro chính
1. **Chi tiêu của KHCN tại địa bàn** (cạnh `L06`) – nguồn doanh thu trực tiếp
2. **Chính sách thuế/hóa đơn** cho HKD – thay đổi chi phí tuân thủ, minh bạch doanh thu
3. **Chuỗi cung ứng / nhà phân phối** (cạnh `L03`) – điều khoản công nợ, giá nhập
4. **Sức khỏe & biến cố của chủ hộ** – dừng kinh doanh ngay lập tức
5. **Thiên tai, dịch bệnh, giải tỏa mặt bằng, quy hoạch chợ**
6. **Cạnh tranh từ thương mại điện tử / chuỗi bán lẻ**
7. **Lừa đảo nhắm vào chủ shop** (QR giả, mạo danh cơ quan thuế)

## (c) Bảng độ nhạy sản phẩm HKD
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `HKD-ACC-01` | Tài khoản Hộ kinh doanh | `LQ` `CO` `FR` | Thuế, AML (tách bạch dòng tiền), lừa đảo | Doanh thu về TK giảm; dấu hiệu dùng TK cá nhân thay TK HKD |
| `HKD-REV-01` | Soundbox | `OR` `BR` | Sự cố thiết bị/mạng, doanh thu giảm | Giảm số giao dịch/ngày |
| `HKD-REV-02` | Liên kết phần mềm bán hàng (QR liên kết) | `OR` `BR` | Sự cố đối tác phần mềm, thay đổi đối tác | Mất dữ liệu doanh thu, gián đoạn nhận tiền |
| `HKD-REV-03` | Nhận thanh toán thẻ: SoftPOS / SmartPOS / SoundPOS | `OR` `FR` `BR` | Gian lận thẻ tại điểm bán, sự cố | Tra soát, chargeback |
| `HKD-LN-01` | Vay tín chấp kinh doanh ShopCash (hạn mức cấp sẵn) | `CR` | Doanh thu giảm, biến cố chủ hộ | Sử dụng hạn mức tăng khi doanh thu giảm = tín hiệu căng thẳng |
| `HKD-LN-02` | Vay thế chấp kinh doanh ShopCredit | `CR` `CL` | Giá BĐS (TSBĐ thường là nhà ở/mặt bằng), doanh thu | DPD; TSBĐ giảm giá |
| `HKD-LN-03` | Vay trả góp tín chấp cho chủ HKD | `CR` | Doanh thu, thu nhập chủ hộ | DPD sớm |
| `HKD-CARD-01` | Thẻ thanh toán Techcombank Visa Seller | `FR` `BR` | Gian lận, chi tiêu nhập hàng | Giảm chi tiêu nhập hàng = HKD thu hẹp |
| `HKD-DEP-01` | Tiền gửi HKD; Sinh lời tự động | `LQ` | Doanh thu, nhu cầu vốn | Số dư nhàn rỗi giảm |
| `HKD-INS-01` | BH sức khỏe nhóm; BH toàn diện HKD & DN | `INS` | Dịch bệnh, cháy nổ, thiên tai | Claim tăng |
| `HKD-DIG-01` | Techcombank Mobile (cho HKD) | `OR` `FR` | Sự cố app | Mất doanh thu trực tiếp trong thời gian gián đoạn |
| `HKD-SVC-01` | Dịch vụ qua CDM | `OR` | Sự cố máy | Không nộp được tiền mặt doanh thu |

## (d) Tín hiệu sớm nội bộ – HKD
- Số giao dịch QR/Soundbox/POS **theo ngày** giảm so với cùng kỳ, theo địa bàn và MCC
- Số lượng người trả tiền khác nhau (unique payers) giảm → mất khách
- Doanh thu chuyển sang TK cá nhân thay vì TK HKD (né thuế hoặc rủi ro AML)
- Hạn mức ShopCash bị rút tối đa, trả chậm
- Chi tiêu thẻ Visa Seller cho nhập hàng giảm
- Ngắt liên kết phần mềm bán hàng

## (e) Lan ra phân khúc khác
- **→ KHCN (cùng chủ hộ)**: hop 0 – rủi ro HKD là rủi ro cá nhân chủ hộ (các khoản vay tiêu dùng, mua nhà, thẻ của chủ hộ).
- **→ DN lớn / nhà phân phối** (cạnh `L03` ngược): HKD giảm nhập hàng, chậm thanh toán công nợ → nhà phân phối SCF.
- **→ SME** (cạnh `L07`): HKD chuyển đổi lên DN mang theo rủi ro tín dụng cũ.


## (f) Danh mục sản phẩm & URL nguồn (chốt 26/10/2026)

Nguồn: https://techcombank.com/ho-kinh-doanh-va-doanh-nghiep-nho/ho-kinh-doanh

- Tài khoản Hộ kinh doanh
- Quản lý doanh thu: Soundbox · Liên kết phần mềm bán hàng · (SoftPOS/SmartPOS/SoundPOS theo chương trình ưu đãi)
- Vay: ShopCash (tín chấp) · ShopCredit (thế chấp) · Vay trả góp tín chấp cho chủ HKD
- Techcombank Mobile · Thẻ thanh toán Techcombank Visa Seller · Tiền gửi (Sinh lời tự động)
- Bảo hiểm: Bảo hiểm sức khỏe nhóm · Bảo hiểm toàn diện
- Dịch vụ khác: CDM · Đặt lịch hẹn
- Lộ trình: Chuyển đổi HKD lên doanh nghiệp
