---
id: SEG-NDT
used_by: [Propagation, Product-Impact, Inside-out Monitor]
steps: [4, 5, 6]
depends_on: [core/01_risk_codes.md, core/03_linkage_graph.md]
load_when: Rủi ro đủ lớn ở cấp danh mục (P3 hoặc cộng dồn), hoặc tín hiệu inside-out từ thị trường vốn (L10, L11)
version: v1.0
updated: 2026-10-26
---

# Phân khúc: Nhà đầu tư (cổ đông, trái chủ, tổ chức xếp hạng)

> Cấu trúc: (a) Chân dung → (b) Động lực rủi ro → (c) Bảng độ nhạy sản phẩm → (d) Tín hiệu sớm nội bộ → (e) Lan ra phân khúc khác → (f) Danh mục sản phẩm & URL nguồn


> Nhà đầu tư **không dùng sản phẩm ngân hàng theo nghĩa bán lẻ** mà nắm giữ chứng khoán của chính ngân hàng. Họ là **nút cuối của outside-in** và **nút đầu của inside-out**.

## (a) Chân dung
| Nhóm | Mối quan tâm | Kênh thông tin |
|---|---|---|
| Cổ đông tổ chức & cá nhân | Lợi nhuận, chất lượng tài sản, cổ tức, giá cổ phiếu | Báo cáo tài chính, sự kiện công bố KQKD hàng quý, ĐHĐCĐ, công bố thông tin |
| Trái chủ / đối tác vốn | Thanh khoản, an toàn vốn, xếp hạng | Báo cáo xếp hạng, báo cáo thường niên |
| Tổ chức xếp hạng | Chất lượng tín dụng, vốn, thanh khoản, hỗ trợ hệ thống | Moody's, S&P, Fitch, FiinRatings |

**Ảnh chụp tham chiếu (cần xác minh trước khi dùng):** trang Nhà đầu tư tại thời điểm 26/10/2026 liệt kê Moody's Ba3 triển vọng Tích cực (3/2026), S&P BB/Ổn định (8/2025), Fitch BB-/Tích cực (11/2025), FiinRatings AA-/Ổn định (12/2024); lưu ý dành cho cổ đông về Luật các TCTD 2024 (người có liên quan, giới hạn sở hữu, công bố thông tin).

## (b) Động lực rủi ro chính
1. Chất lượng tài sản (nợ xấu, cơ cấu nợ) – tổng hợp từ 4 phân khúc trên
2. Tập trung tín dụng (BĐS, nhóm khách hàng liên quan)
3. Thanh khoản & huy động (CASA, tiền gửi, CCTG)
4. Danh tiếng (iBond, bảo hiểm, sự cố hệ thống, lừa đảo)
5. Quy định (room tín dụng, tỷ lệ an toàn vốn, giới hạn sở hữu)
6. Thị trường chứng khoán chung & dòng vốn ngoại
7. Hoạt động hệ sinh thái (chứng khoán, quản lý quỹ, bảo hiểm)

## (c) Bảng độ nhạy “sản phẩm” nhà đầu tư
| Mã | Đối tượng / Kênh | Rủi ro chính | Nhạy với sự kiện | Chiều tác động |
|---|---|---|---|---|
| `IR-EQ-01` | Cổ phiếu TCB | `MR` `RP` | KQKD, tin danh tiếng, chính sách NHNN, dòng vốn ngoại | Giá giảm → vốn hóa giảm → khó tăng vốn |
| `IR-RT-01` | Xếp hạng tín nhiệm | `MR` `LQ` | Chất lượng tài sản, vốn, rủi ro tập trung | Hạ hạng → chi phí vốn quốc tế tăng |
| `IR-DIS-01` | Công bố thông tin, báo cáo tài chính | `CO` `RP` | Chậm/sai công bố | Phạt, mất niềm tin |
| `IR-AGM-01` | ĐHĐCĐ, cổ tức, chính sách vốn | `RP` | Cổ đông phản đối | |
| `IR-ECO-01` | Hệ sinh thái (TCBS, Techcom Capital, bảo hiểm) | `RP` `MR` | Sự cố tại công ty con/đối tác | Lan danh tiếng về ngân hàng mẹ (cạnh `L11`) |

## (d) Tín hiệu sớm
- Khối lượng bán ròng cổ phiếu bất thường, tin đồn trên mạng xã hội
- Báo cáo xếp hạng chuyển triển vọng
- Chênh lệch lợi suất trái phiếu/CDS (nếu có) mở rộng
- Câu hỏi của nhà đầu tư tập trung vào một chủ đề (BĐS, iBond…) tại sự kiện KQKD

## (e) Lan ngược (Inside-out)
- Giá cổ phiếu/xếp hạng giảm → chi phí vốn tăng → ngân hàng tăng lãi suất cho vay/giảm ưu đãi → **mọi phân khúc** (P3).
- Áp lực nhà đầu tư → ngân hàng siết khẩu vị rủi ro → SME/HKD khó tiếp cận vốn → rủi ro tín dụng bậc 2.


## (f) Danh mục sản phẩm & URL nguồn (chốt 26/10/2026)

Nguồn: https://techcombank.com/nha-dau-tu

- Thông tin tài chính (chỉ số nổi bật, công bố KQKD, báo cáo tài chính, báo cáo thường niên)
- Đại hội đồng cổ đông
- Tin tức & sự kiện nhà đầu tư
- Công bố thông tin (tài liệu doanh nghiệp)
- Xếp hạng tín nhiệm (Moody's, S&P, Fitch, FiinRatings)
- Lưu ý cổ đông theo Luật các TCTD 2024
- Hệ sinh thái liên quan: Techcom Securities (TCBS), Techcom Capital
