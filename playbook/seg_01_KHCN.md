---
id: SEG-KHCN
used_by: [Propagation, Product-Impact, Inside-out Monitor]
steps: [2, 3, 4]
depends_on: [core/01_risk_codes.md, core/03_linkage_graph.md]
load_when: Sự kiện chạm cá nhân/hộ gia đình, hoặc lan tới KHCN qua L01, L02, L04, L05, L06
version: v1.2
updated: 2026-10-26
---

# Phân khúc: Khách hàng cá nhân (KHCN)

> Cấu trúc: (a) Chân dung → (b) Động lực rủi ro → (c) Bảng độ nhạy sản phẩm → (d) Tín hiệu sớm nội bộ → (e) Lan ra phân khúc khác → (f) Danh mục sản phẩm & URL nguồn


## (a) Chân dung & phân hạng
| Phân hạng | Đặc điểm | Ý nghĩa cho suy luận |
|---|---|---|
| Đại chúng | Người làm công ăn lương, thu nhập chủ yếu qua TK thanh toán | Nhạy với việc làm, lương, lạm phát, lừa đảo |
| Inspire | Khách hàng trẻ, số hóa cao, dùng thẻ/app nhiều | Nhạy với sự cố app, lừa đảo số, tín dụng tiêu dùng |
| Priority | Khách hàng giàu có, nhiều sản phẩm đầu tư/bảo hiểm | Nhạy với thị trường vốn, BĐS; **thường là chủ DN/HKD (cạnh L01)** |
| Private / Techcom Wealth | Khách hàng siêu giàu, quản lý gia sản | Tập trung rủi ro lớn, liên kết chặt với DN sở hữu, nhạy với tin pháp lý cá nhân |

## (b) Động lực rủi ro chính
1. **Thu nhập & việc làm** (sa thải, giảm lương, ngành gặp khó)
2. **Lãi suất** (khoản vay thả nổi mua nhà/ô tô; hấp dẫn của tiết kiệm vs đầu tư)
3. **Giá tài sản** (BĐS, chứng khoán, trái phiếu, vàng)
4. **Sức khỏe & thiên tai** (bệnh tật, dịch bệnh, bão lũ)
5. **Lừa đảo & an ninh số** (mạo danh, chiếm đoạt tài khoản)
6. **Pháp lý cá nhân** (khởi tố, phong tỏa tài sản, tranh chấp)
7. **Quy định** (xác thực sinh trắc, hạn mức giao dịch, thuế thu nhập)

## (c) Bảng độ nhạy sản phẩm KHCN

**Nhóm Chi tiêu – Tài khoản, Thẻ, Dịch vụ**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CN-ACC-01` | Tài khoản thanh toán | `LQ` `FR` `OR` `CO` | Lương giảm, lừa đảo, sự cố app, quy định sinh trắc | Số dư CASA giảm; tăng khóa TK; tăng khiếu nại |
| `CN-ACC-02` | Tài khoản ngoại tệ | `MR` `CO` | Tỷ giá, quy định ngoại hối, kiều hối | Dịch chuyển số dư ngoại tệ/VND |
| `CN-ACC-03` | Sinh lời tự động | `LQ` `MR` `RP` | Lãi suất thị trường, so sánh với đối thủ | Dòng tiền rút nhanh nếu lợi suất kém hấp dẫn |
| `CN-CARD-01` | Thẻ tín dụng | `CR` `FR` | Thu nhập giảm, lạm phát, gian lận thẻ, du lịch | Tăng dư nợ quay vòng, tăng DPD; tăng giao dịch gian lận |
| `CN-CARD-02` | Thẻ thanh toán (ghi nợ quốc tế/nội địa) | `FR` `OR` `BR` | Gian lận, sự cố hệ thống thẻ, chi tiêu giảm | Giảm doanh số thẻ; tăng tra soát |
| `CN-PAY-01` | Chuyển tiền quốc tế | `CO` `MR` | Trừng phạt, AML, tỷ giá, kiều hối, du học | Tăng giao dịch cần rà soát; biến động dòng kiều hối |
| `CN-PAY-02` | Dịch vụ qua CDM (nộp/rút 24/7) | `OR` `LQ` | Sự cố máy, thiên tai, tâm lý rút tiền mặt | Rút tiền mặt tăng đột biến là tín hiệu hoảng loạn |
| `CN-LOY-01` | OneU (khách hàng thân thiết) | `BR` `FR` | Lạm dụng ưu đãi, thay đổi chương trình | Gian lận điểm thưởng; giảm tương tác |

**Nhóm Tiết kiệm**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CN-DEP-01` | Tiền gửi tiết kiệm có kỳ hạn | `LQ` `MR` | Lãi suất đối thủ, tin đồn ngân hàng, nhu cầu tiền mặt | Tất toán trước hạn, không tái tục |
| `CN-DEP-02` | Tích lũy Như Ý | `LQ` | Thu nhập giảm | Ngừng nộp định kỳ |
| `CN-DEP-03` | Tiền gửi rút gốc linh hoạt | `LQ` | Cú sốc thu nhập, sức khỏe | Rút gốc từng phần tăng |
| `CN-DEP-04` | Chứng chỉ tiền gửi Bảo Lộc | `LQ` `MR` `RP` | Lãi suất, niềm tin ngân hàng | Bán lại/không mua mới |

**Nhóm Vay**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CN-LN-01` | Vay mua nhà dự án trực tiếp từ Chủ đầu tư | `CR` `CL` `RP` | Pháp lý dự án, tiến độ CĐT, hết ưu đãi lãi suất, giá BĐS | DPD tăng khi hết ân hạn; tranh chấp với CĐT (cạnh `L04`) |
| `CN-LN-02` | Vay mua BĐS có Giấy chứng nhận | `CR` `CL` | Lãi suất, giá BĐS, thu nhập | LTV xấu đi; DPD |
| `CN-LN-03` | Vay nhận chuyển nhượng | `CR` `CL` | Thanh khoản thị trường BĐS thứ cấp | Khó bán TS để trả nợ |
| `CN-LN-04` | Vay mua ô tô đi lại | `CR` `CL` | Thu nhập, giá xe cũ, chính sách thuế phí trước bạ | Giá trị xe giảm nhanh hơn dư nợ |
| `CN-LN-05` | Tài khoản thấu chi MyCash | `CR` | Thu nhập giảm, chi tiêu khẩn cấp | Sử dụng hạn mức tăng vọt = tín hiệu căng thẳng |
| `CN-LN-06` | Vay tiêu dùng tín chấp trả góp | `CR` | Mất việc, giảm lương (cạnh `L02`) | DPD sớm nhất trong danh mục |
| `CN-LN-07` | Vay cầm cố tiền gửi | `CR` (thấp) `LQ` | Nhu cầu tiền mặt gấp | Tăng khoản vay cầm cố = khách cần tiền nhưng không muốn tất toán |
| `CN-LN-08` | Vay xây dựng / sửa chữa nhà ở | `CR` `CL` | Giá vật liệu, thiên tai | Đội chi phí, chậm trả |
| `CN-LN-09` | Thấu chi có TSBĐ | `CR` `CL` | Giá TSBĐ, dòng tiền cá nhân/chủ DN | Sử dụng hạn mức tăng, thường để bơm vốn cho DN (cạnh `L01`) |
| `CN-LN-10` | Thấu chi không TSBĐ | `CR` | Thu nhập | Tương tự MyCash |

**Nhóm Đầu tư**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CN-INV-01` | Trái phiếu DN iBond (iBond Pro – dòng tiền định sẵn; iBond Prix – đầu tư linh hoạt; iBond Prix – tích lũy bền vững) | `MR` `RP` `LQ` `CO` | Sự cố tổ chức phát hành, quy định trái phiếu, lãi suất | Yêu cầu bán lại tăng; khiếu nại bán hàng; rủi ro danh tiếng lớn (cạnh `L05`) |
| `CN-INV-02a` | Quỹ trái phiếu Techcom (TCBF) | `MR` `LQ` | Lãi suất, tín dụng DN phát hành | NAV giảm, rút vốn |
| `CN-INV-02b` | Quỹ cổ phiếu Techcom Top 30 (TCEF) | `MR` | Thị trường chứng khoán | NAV giảm; khách Priority tái cơ cấu tài sản |
| `CN-INV-02c` | Quỹ cổ phiếu Ngân hàng & Tài chính (TCFIN) | `MR` | Tin ngành ngân hàng, quy định NHNN | Nhạy kép: tin xấu ngành ngân hàng vừa hạ NAV vừa hạ niềm tin |
| `CN-INV-02d` | Quỹ cổ phiếu DN vừa và nhỏ (TCSME) | `MR` | Sức khỏe SME, thanh khoản thị trường | Biến động mạnh khi SME gặp khó |
| `CN-INV-02e` | Quỹ cổ phiếu Bất động sản (TCRES) | `MR` | Chính sách BĐS, tín dụng BĐS | Nhạy trực tiếp với sự kiện BĐS (cạnh `L04`) |
| `CN-INV-02f` | Quỹ Cân bằng Linh hoạt (TCFF) | `MR` | Cả cổ phiếu và trái phiếu | Biến động vừa phải |
| `CN-INV-03` | Chứng chỉ tiền gửi (kênh đầu tư) | Xem `CN-DEP-04` | | |

**Nhóm Bảo hiểm**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CN-INS-01` | BH sức khỏe: Song An, Global Prime, An tâm đồng hành, Chăm sóc sức khỏe toàn diện | `INS` `RP` | Dịch bệnh, ô nhiễm, chi phí y tế | Claim tăng; tranh chấp từ chối bồi thường |
| `CN-INS-02` | BH tích lũy & đầu tư: Techcom Life Max Chủ Động, Max Vững Vàng, Khỏe trọn vẹn vượt trội, Khỏe bình an vượt trội, Vững tương lai vượt trội | `RP` `LQ` `CO` | Thu nhập giảm (ngừng đóng phí), quy định bancassurance, khủng hoảng niềm tin bảo hiểm | Hủy hợp đồng sớm, khiếu nại tư vấn sai |
| `CN-INS-03` | BH khác: nhà tư nhân, ô tô, du lịch toàn cầu TechCare Travel | `INS` | Bão lũ, cháy nổ, tai nạn, gián đoạn đi lại | Claim tăng theo địa bàn |

**Nhóm Ngân hàng số**
| Mã | Sản phẩm | Rủi ro chính | Nhạy với sự kiện | Chiều tác động khi sự kiện xấu |
|---|---|---|---|---|
| `CN-DIG-01` | Techcombank Mobile, Online Banking | `OR` `FR` `RP` | Sự cố hệ thống, tấn công mạng, lừa đảo, quy định xác thực | Gián đoạn mọi sản phẩm khác (P3); bùng nổ khiếu nại mạng xã hội |

## (d) Tín hiệu sớm nội bộ – KHCN
- Lương về tài khoản giảm/không về (theo DN trả lương – cạnh `L02`)
- Tỷ lệ sử dụng hạn mức MyCash / thẻ tín dụng tăng nhanh; chuyển từ trả toàn bộ sang trả tối thiểu
- Tất toán tiết kiệm trước hạn, vay cầm cố tiền gửi tăng
- Rút tiền mặt qua CDM tăng bất thường theo địa bàn
- Bán lại iBond/iFund hàng loạt, nhất là theo một tổ chức phát hành/một ngành
- Hủy hợp đồng bảo hiểm sớm, ngừng đóng phí
- Đổi thiết bị/đăng nhập bất thường, chuyển tiền tới tài khoản mới lần đầu với giá trị lớn (lừa đảo)

## (e) Lan ra phân khúc khác
- **→ HKD/SME bán lẻ** (cạnh `L06`): chi tiêu thẻ/QR giảm = doanh thu HKD giảm (P2).
- **→ DN** (cạnh `L01`): biến cố của chủ DN (pháp lý, sức khỏe, nợ cá nhân) → DN mất người ra quyết định, mất bảo lãnh, mất TSBĐ.
- **→ Nhà đầu tư** (cạnh `L10`): rút tiền gửi diện rộng, khủng hoảng iBond → thanh khoản và danh tiếng ngân hàng.


## (f) Danh mục sản phẩm & URL nguồn (chốt 26/10/2026)

Nguồn: https://techcombank.com/khach-hang-ca-nhan

- **Phân hạng:** Inspire · Priority · Private · Techcom Wealth
- **Chi tiêu – Tài khoản:** Tài khoản thanh toán · Tài khoản ngoại tệ · Tài khoản thấu chi MyCash · Sinh lời tự động
- **Chi tiêu – Thẻ:** Thẻ tín dụng · Thẻ thanh toán (quốc tế & nội địa)
- **Chi tiêu – Dịch vụ khác:** Chuyển tiền quốc tế · Dịch vụ qua CDM · Đặt lịch hẹn chi nhánh
- **Tiết kiệm:** Tiền gửi tiết kiệm có kỳ hạn · Tích lũy Như Ý · Tiền gửi rút gốc linh hoạt · Chứng chỉ tiền gửi Bảo Lộc
- **Vay mua nhà:** Vay mua nhà dự án trực tiếp từ CĐT · Vay mua BĐS có Giấy chứng nhận · Vay nhận chuyển nhượng
- **Vay mua ô tô:** Vay mua ô tô đi lại
- **Vay tiêu dùng:** MyCash · Vay tín chấp trả góp · Vay cầm cố tiền gửi · Vay xây dựng/sửa chữa nhà · Thấu chi có TSBĐ · Thấu chi không TSBĐ
- **Đầu tư – iBond:** iBond Pro (dòng tiền định sẵn) · iBond Prix (đầu tư linh hoạt) · iBond Prix (tích lũy bền vững)
- **Đầu tư – iFund:** TCBF · TCEF · TCFIN · TCSME · TCRES · TCFF
- **Bảo hiểm sức khỏe:** Song An · Global Prime · An tâm đồng hành · Chăm sóc sức khỏe toàn diện
- **Bảo hiểm tích lũy & đầu tư:** Techcom Life Max Chủ Động · Techcom Life Max Vững Vàng · Khỏe trọn vẹn vượt trội · Khỏe bình an vượt trội · Vững tương lai vượt trội
- **Bảo hiểm khác:** Bảo hiểm nhà tư nhân · Bảo hiểm ô tô · TechCare Travel
- **Ngân hàng số:** Techcombank Mobile · Techcombank Online Banking · Techcombank OneU
