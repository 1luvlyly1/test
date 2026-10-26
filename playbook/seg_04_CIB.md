---
id: SEG-CIB
used_by: [Propagation, Product-Impact, Inside-out Monitor]
steps: [4, 5, 6]
depends_on: [core/01_risk_codes.md, core/03_linkage_graph.md]
load_when: Sự kiện chạm DN lớn, ngành, thương mại quốc tế, BĐS, trái phiếu, hoặc lan qua L03, L04, L05, L08
version: v1.0
updated: 2026-10-26
---

# Phân khúc: Doanh nghiệp lớn & Định chế tài chính (CIB)

> Cấu trúc: (a) Chân dung → (b) Động lực rủi ro → (c) Bảng độ nhạy sản phẩm → (d) Tín hiệu sớm nội bộ → (e) Lan ra phân khúc khác → (f) Danh mục sản phẩm & URL nguồn


## (a) Chân dung
- DN quy mô lớn, tập đoàn, FDI, định chế tài chính.
- Dư nợ tập trung lớn; dùng sản phẩm phức tạp (tài trợ thương mại, FX, phái sinh, trái phiếu); là **anchor** trong chuỗi cung ứng và là **CĐT BĐS / tổ chức phát hành trái phiếu** (cạnh `L04`, `L05`).

## (b) Động lực rủi ro chính
1. **Ngành** (BĐS, thép, dệt may, gỗ, thủy sản, hàng không, ô tô, tiêu dùng nhanh…)
2. **Thương mại quốc tế** – thuế quan, trừng phạt, đứt gãy vận tải (cạnh `L08`)
3. **Tỷ giá & lãi suất** – nợ ngoại tệ, vị thế phái sinh
4. **Pháp lý doanh nghiệp & lãnh đạo** – thanh tra, khởi tố, tranh chấp
5. **Thị trường vốn** – đáo hạn trái phiếu, khả năng huy động mới
6. **Rủi ro tập trung theo nhóm khách hàng liên quan**
7. **ESG** – quy định phát thải, CBAM, tín dụng xanh

## (c) Bảng độ nhạy sản phẩm CIB
**Quản trị hàng ngày**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CIB-PKG-01` | BusinessOne Connect / Plus / Premium | `BR` | Hoạt động DN | |
| `CIB-DIG-01` | Techcombank Business; F@st EBank (đang chuyển đổi sang Techcombank Business); Chữ ký số | `OR` `FR` | Sự cố, rủi ro trong giai đoạn chuyển đổi nền tảng, chiếm đoạt chữ ký số | Gián đoạn thanh toán quy mô lớn |
| `CIB-ACC-01` | Tài khoản thanh toán | `LQ` `CO` | Dòng tiền, AML | Số dư lớn rút đột ngột |
| `CIB-ACC-02` | Tài khoản vốn | `CO` `MR` | Quy định FDI, ngoại hối | |
| `CIB-ACC-03` | Tài khoản giữ hộ thương mại | `RP` `CO` | Tranh chấp M&A, mua bán | |
| `CIB-ACC-04` | Tài khoản giữ hộ bất động sản | `RP` `CO` `CR` | Pháp lý dự án, tiến độ (cạnh `L04`) | Tranh chấp với người mua nhà |
| `CIB-PAY-01` | Thanh toán hàng hóa dịch vụ trong nước | `FR` `OR` | | |
| `CIB-PAY-02` | Chuyển tiền đi nước ngoài | `CO` `MR` | Trừng phạt, AML | |
| `CIB-PAY-03` | Nộp ngân sách nhà nước | `CO` | Thuế, hải quan | |
| `CIB-PAY-04` | Thẻ dành cho DN | `CR` `FR` | | |
| `CIB-PAY-05` | Thanh toán hóa đơn | `OR` | | Hóa đơn điện/cảng giảm = sản xuất/xuất khẩu giảm |
| `CIB-PAY-06` | Thanh toán lương | `BR` | **Cạnh `L02`** – quy mô lớn | Cắt giảm nhân sự lan tới hàng nghìn KHCN |
| `CIB-COL-01` | Thu hộ: TK định danh, POS, QR, Payment Gateway, tiền mặt tại quầy, tại địa điểm KH, qua quầy đối tác | `OR` `FR` `BR` | Doanh thu bán lẻ, sự cố cổng thanh toán | Thu hộ giảm = doanh thu DN giảm |
| `CIB-LIQ-01` | Báo cáo tổng hợp dòng tiền | – | Công cụ quan sát | Nguồn tín hiệu sớm |
| `CIB-DEP-01` | CCTG Bảo Lộc; Tiền gửi xanh | `LQ` `MR` | Lãi suất, nhu cầu vốn | Rút tiền gửi lớn ảnh hưởng thanh khoản ngân hàng |

**Vay**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CIB-LN-01` | Vay vốn lưu động: theo món, theo hạn mức, theo ngành, thấu chi | `CR` `CL` | Doanh thu, vòng quay hàng tồn, ngành | DPD, xin cơ cấu |
| `CIB-LN-02` | Vay trung dài hạn: theo món, theo dự án, theo ngành, mua ô tô DN | `CR` `CL` `MR` | Lãi suất, tiến độ dự án, pháp lý dự án | Dự án chậm → dòng tiền trả nợ chậm |
| `CIB-SCF-01` | Tài trợ chuỗi cung ứng: kinh doanh ô tô; đại lý bán vé hàng không; vận chuyển hàng hóa hàng không; nhà phân phối Masan | `CR` | **Sức khỏe anchor** + nhu cầu cuối (cạnh `L03`) | Anchor gặp khó → toàn bộ spoke bị ảnh hưởng đồng thời |

**Thương mại (Trade)**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CIB-TF-01` | Nhập khẩu: L/C nhập khẩu, nhờ thu | `CR` `MR` `CO` | Tỷ giá, giá hàng hóa, trừng phạt | Ngân hàng phải thanh toán thay khi DN thiếu tiền |
| `CIB-TF-02` | Xuất khẩu: L/C xuất khẩu, nhờ thu, tài trợ thương mại | `CR` `CO` | Thuế quan, rủi ro quốc gia người mua, chứng từ bất hợp lệ | Hủy đơn, chậm thu tiền |
| `CIB-TF-03` | Nội địa: L/C nội địa, tài trợ thương mại, tài trợ chuỗi cung ứng | `CR` `FR` | Gian lận chứng từ, chuỗi cung ứng | |
| `CIB-TF-04` | Bảo lãnh; L/C UPAS | `CR` `CO` | Vi phạm hợp đồng, tranh chấp | Bị gọi bảo lãnh |

**Nguồn vốn (Treasury & Markets)**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CIB-FX-01` | Giao dịch ngoại tệ: giao ngay, kỳ hạn, hoán đổi | `MR` `CR` (đối tác) | Biến động tỷ giá | Lỗ vị thế của khách → rủi ro đối tác |
| `CIB-CM-01` | Phái sinh lãi suất | `MR` `CR` | Thay đổi lãi suất | Giá trị thị trường âm lớn với khách |
| `CIB-CM-02` | Phái sinh tỷ giá | `MR` `CR` | Tỷ giá | |
| `CIB-CM-03` | Sản phẩm cấu trúc | `MR` `RP` | Biến động thị trường | Tranh chấp về tính phù hợp sản phẩm |
| `CIB-INV-01` | Trái phiếu doanh nghiệp (phát hành/thu xếp) | `CR` `RP` `CO` | Đáo hạn, quy định phát hành | **Lan sang nhà đầu tư cá nhân qua iBond (cạnh `L05`)** |
| `CIB-INS-01` | Bảo hiểm phi nhân thọ cho DN | `INS` | Cháy nổ, thiên tai, gián đoạn kinh doanh | Claim lớn |

## (d) Tín hiệu sớm nội bộ – CIB
- Báo cáo tổng hợp dòng tiền: dòng vào giảm, dòng ra tăng; tiền thu hộ giảm
- Sử dụng hạn mức vốn lưu động tăng liên tục; đề nghị gia hạn/cơ cấu
- L/C nhập khẩu tăng nhưng thanh toán chậm; chứng từ xuất khẩu bất hợp lệ tăng
- Vị thế FX/phái sinh của khách có giá trị thị trường âm lớn
- Lô lương giảm quy mô (cạnh `L02`)
- Spoke SCF cùng một anchor đồng loạt chậm trả
- Bán ra tài sản bảo đảm, chuyển nhượng cổ phần lớn của lãnh đạo

## (e) Lan ra phân khúc khác
- **→ KHCN** qua `L02` (nhân viên quy mô lớn), `L01` (lãnh đạo/cổ đông Private), `L04` (người mua nhà), `L05` (trái chủ iBond, NĐT iFund)
- **→ SME/HKD** qua `L03` (nhà phân phối, đại lý, nhà cung cấp)
- **→ Nhà đầu tư** qua `L10` (rủi ro tập trung lớn ảnh hưởng trực tiếp chất lượng tài sản ngân hàng)


## (f) Danh mục sản phẩm & URL nguồn (chốt 26/10/2026)

Nguồn: https://techcombank.com/khach-hang-doanh-nghiep

- **Quản trị hàng ngày:** Gói BusinessOne (Connect/Plus/Premium) · Techcombank Business · F@st EBank (đang chuyển đổi) · Chữ ký số · TK thanh toán · TK vốn · Giữ hộ thương mại · Giữ hộ BĐS · Thanh toán trong nước · Chuyển tiền nước ngoài · Nộp NSNN · Thẻ DN · Hóa đơn · Lương · Thu hộ (TK định danh, POS, QR, Payment Gateway, tiền mặt tại quầy / tại địa điểm KH / qua đối tác) · Báo cáo tổng hợp dòng tiền · CDM · Tổng đài · CCTG Bảo Lộc · Tiền gửi xanh
- **Vay:** Vốn lưu động (theo món, hạn mức, theo ngành, thấu chi) · Trung dài hạn (theo món, theo dự án, theo ngành, mua ô tô DN) · Tài trợ chuỗi cung ứng (kinh doanh ô tô, đại lý bán vé hàng không, vận chuyển hàng hóa hàng không, nhà phân phối Masan)
- **Thương mại:** L/C nhập khẩu · Nhờ thu NK · L/C xuất khẩu · Nhờ thu XK · Tài trợ thương mại · L/C nội địa · Tài trợ chuỗi cung ứng nội địa · Bảo lãnh · L/C UPAS
- **Nguồn vốn:** FX giao ngay · Kỳ hạn · Hoán đổi · Phái sinh lãi suất · Phái sinh tỷ giá · Sản phẩm cấu trúc · Trái phiếu doanh nghiệp
- **Bảo hiểm:** Bảo hiểm phi nhân thọ cho DN
