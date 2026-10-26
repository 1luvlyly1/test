---
id: SEG-SME
used_by: [Propagation, Product-Impact, Inside-out Monitor]
steps: [2, 3, 4]
depends_on: [core/01_risk_codes.md, core/03_linkage_graph.md]
load_when: Sự kiện chạm DN vừa và nhỏ, mua sắm công, hoặc lan qua L01, L02, L03, L07, L12
version: v1.2
updated: 2026-10-26
---

# Phân khúc: Doanh nghiệp vừa và nhỏ (SME)

> Cấu trúc: (a) Chân dung → (b) Động lực rủi ro → (c) Bảng độ nhạy sản phẩm → (d) Tín hiệu sớm nội bộ → (e) Lan ra phân khúc khác → (f) Danh mục sản phẩm & URL nguồn


## (a) Chân dung
- Quy mô vừa/nhỏ, quản trị phụ thuộc chủ sở hữu (cạnh `L01` rất mạnh).
- Dùng gói BusinessOne / MerchantOne; vay dựa trên dữ liệu (Misa Lending, Hybrid, B1CP); tham gia mua sắm công.

## (b) Động lực rủi ro chính
1. **Dòng tiền ngắn hạn** – SME ít đệm thanh khoản; chậm thu tiền khách hàng là nguy cơ lớn nhất
2. **Phụ thuộc khách hàng/nhà cung cấp lớn** (cạnh `L03`)
3. **Chủ sở hữu** – biến cố cá nhân của chủ = biến cố DN
4. **Thuế, hóa đơn, kế toán** (dữ liệu từ phần mềm kế toán ảnh hưởng hạn mức vay)
5. **Thanh toán chậm từ ngân sách / chủ đầu tư công** (cạnh `L12`)
6. **Tỷ giá** với SME có nhập khẩu nguyên liệu
7. **Lừa đảo chiếm đoạt tài khoản DN, giả mạo email đối tác (BEC)**

## (c) Bảng độ nhạy sản phẩm SME
**Tài khoản & Gói giải pháp**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `SME-ACC-01` | Tài khoản doanh nghiệp | `LQ` `FR` `CO` | Dòng tiền, lừa đảo BEC, AML | Số dư giảm; giao dịch bất thường |
| `SME-ACC-02` | Tài khoản vốn | `CO` `MR` | Quy định đầu tư nước ngoài, ngoại hối | Dòng vốn FDI/góp vốn dừng |
| `SME-ACC-03` | Tài khoản giữ hộ thương mại | `RP` `CO` | Tranh chấp hợp đồng mua bán | Tranh chấp giải ngân giữ hộ |
| `SME-ACC-04` | Tài khoản giữ hộ bất động sản | `RP` `CO` | Pháp lý giao dịch BĐS | Tranh chấp, phong tỏa |
| `SME-ACC-05` | Tài khoản ký quỹ | `CO` `MR` | Bảo lãnh, giao dịch có điều kiện | Ký quỹ bị phong tỏa/giải tỏa đột ngột |
| `SME-PKG-01` | BusinessOne Plus / Connect / Premium | `BR` | Hoạt động DN giảm | Hạ gói, đóng gói |
| `SME-PKG-02` | MerchantOne | `BR` `OR` | Doanh thu bán lẻ (cạnh `L06`) | Giảm giao dịch nhận tiền |
| `SME-REV-01` | SoftPOS; liên kết phần mềm bán hàng | `OR` `FR` | Sự cố, gian lận thẻ | Chargeback, gián đoạn |

**Thanh toán**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `SME-PAY-01` | Thanh toán tiền hàng hóa, dịch vụ | `FR` `OR` | BEC, sự cố | Chuyển nhầm/lừa đảo |
| `SME-PAY-02` | Thẻ tín dụng DN (Visa Business Platinum) | `CR` `FR` | Dòng tiền DN | Dư nợ thẻ tăng, chậm trả |
| `SME-PAY-03` | Thẻ thanh toán DN | `FR` | Gian lận | |
| `SME-PAY-04` | Giao dịch ngoại tệ | `MR` `CO` | Tỷ giá, quy định ngoại hối | Chi phí nhập khẩu tăng |
| `SME-PAY-05` | Thanh toán hóa đơn | `OR` | Sự cố | |
| `SME-PAY-06` | Thanh toán lương | `CR` (gián tiếp) `BR` | **Tín hiệu then chốt cạnh `L02`** | Trả lương trễ/giảm = DN căng thẳng + rủi ro lan sang nhân viên |
| `SME-PAY-07` | Chuyển tiền đi nước ngoài | `CO` `MR` | Trừng phạt, AML, tỷ giá | Giao dịch bị giữ lại |
| `SME-PAY-08` | Chuyển tiền nộp ngân sách nhà nước | `CO` | Thay đổi thuế | Nộp thuế chậm = dấu hiệu thiếu tiền |

**Tiền gửi, Ngân hàng số, Vay, Bảo lãnh, Bảo hiểm**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `SME-DEP-01` | Tiền gửi có kỳ hạn / linh hoạt | `LQ` | Nhu cầu vốn lưu động | Tất toán sớm |
| `SME-DEP-02` | Chứng chỉ tiền gửi Bảo Lộc | `LQ` `MR` | Lãi suất | |
| `SME-DIG-01` | Techcombank Business; F@st EBank | `OR` `FR` | Sự cố, chuyển đổi nền tảng, chiếm đoạt quyền truy cập | Không chi lương/thanh toán đúng hạn |
| `SME-LN-01` | Giải pháp tín dụng linh hoạt (Hybrid) | `CR` `CL` | Doanh thu, TSBĐ | DPD |
| `SME-LN-02` | Tín dụng kết nối Misa Lending | `CR` `OR` | Chất lượng dữ liệu kế toán, sự cố đối tác dữ liệu | Hạn mức dựa trên dữ liệu có thể sai lệch nếu dữ liệu bị thao túng |
| `SME-LN-03` | Giải pháp tín dụng B1CP | `CR` | Dòng tiền | DPD |
| `SME-GTE-01` | Bảo lãnh mua sắm công | `CR` `CO` | Chậm giải ngân vốn đầu tư công, vi phạm đấu thầu (cạnh `L12`) | Bị yêu cầu thực hiện bảo lãnh |
| `SME-INS-01` | BH sức khỏe nhóm; BH toàn diện | `INS` | Dịch bệnh, cháy nổ | Claim |

## (d) Tín hiệu sớm nội bộ – SME
- Lô chi lương **trễ ngày**, **giảm số nhân viên** hoặc **giảm tổng quỹ lương**
- Nộp NSNN trễ; tần suất thanh toán hóa đơn (điện, nước) giảm → sản xuất giảm
- Dòng tiền vào giảm, tập trung từ ít khách hàng hơn
- Sử dụng hạn mức Hybrid/B1CP tối đa liên tục
- Chủ DN rút tiết kiệm cá nhân, tăng thấu chi cá nhân (cạnh `L01`)
- Thay đổi đột ngột người đại diện pháp luật / chủ sở hữu
- Đăng nhập Techcombank Business từ thiết bị/IP lạ, thay đổi người thụ hưởng (BEC)

## (e) Lan ra phân khúc khác
- **→ KHCN** qua `L01` (chủ DN) và `L02` (nhân viên)
- **→ HKD** (là nhà cung cấp hoặc khách hàng của SME)
- **→ DN lớn** (SME là spoke trong chuỗi SCF – cạnh `L03`)


## (f) Danh mục sản phẩm & URL nguồn (chốt 26/10/2026)

Nguồn: https://techcombank.com/ho-kinh-doanh-va-doanh-nghiep-nho/doanh-nghiep-nho

- Tài khoản: Tài khoản DN · Tài khoản vốn · Giữ hộ thương mại · Giữ hộ BĐS · Ký quỹ
- Gói giải pháp: BusinessOne Plus · BusinessOne Connect · BusinessOne Premium · MerchantOne
- Quản lý doanh thu: SoftPOS · Liên kết phần mềm bán hàng
- Thanh toán: Hàng hóa dịch vụ · Thẻ tín dụng DN (Visa Business Platinum) · Thẻ thanh toán DN · Giao dịch ngoại tệ · Thanh toán hóa đơn · Thanh toán lương · Chuyển tiền đi nước ngoài · Nộp NSNN
- Tiền gửi: Có kỳ hạn · Linh hoạt · CCTG Bảo Lộc
- Ngân hàng số: Techcombank Business · F@st EBank
- Vay: Tín dụng linh hoạt (Hybrid) · Kết nối Misa Lending · B1CP
- Bảo lãnh: Bảo lãnh mua sắm công
- Bảo hiểm: Sức khỏe nhóm · Toàn diện
- Dịch vụ khác: CDM · Đặt lịch hẹn
