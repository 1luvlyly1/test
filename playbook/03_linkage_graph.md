---
id: CORE-LINKAGE-GRAPH
used_by: [Propagation, Inside-out Monitor]
steps: [4, 6]
depends_on: [core/02_concepts_patterns.md]
load_when: Duyệt đường lan truyền giữa các phân khúc (cạnh L01–L12)
version: v1.0
updated: 2026-10-26
---

# Đồ thị liên kết khách hàng (Customer Linkage Graph)

Đây là “bản đồ đường đi” để agent Propagation duyệt. Mỗi cạnh có **khóa liên kết dữ liệu** để truy vấn nội bộ.

| ID | Cạnh | Cơ chế truyền dẫn | Khóa liên kết dữ liệu nội bộ (gợi ý) | Hướng mạnh |
|---|---|---|---|---|
| `L01` | DN ↔ Chủ DN / cổ đông | Bảo lãnh cá nhân, TSBĐ là BĐS cá nhân, rút tiết kiệm cá nhân bù vốn DN, cổ tức | CIF chủ sở hữu/người đại diện pháp luật, hợp đồng bảo lãnh, TSBĐ bên thứ ba | 2 chiều |
| `L02` | DN → Nhân viên | Chi lương qua Techcombank; giảm lương/sa thải → thu nhập nhân viên | Lô chi lương (Thanh toán lương), mã DN trả lương trên TK nhân viên | DN → CN |
| `L03` | DN lớn → Nhà phân phối / đại lý (SME, HKD) | Tài trợ chuỗi cung ứng, công nợ, chính sách chiết khấu | Chương trình SCF (ô tô, đại lý vé/vận chuyển hàng không, nhà phân phối Masan…), anchor ID | Anchor → spoke |
| `L04` | Chủ đầu tư BĐS → Người mua nhà | Vay mua nhà dự án, TK giữ hộ BĐS, tiến độ bàn giao, hỗ trợ lãi suất | Mã dự án, TK giữ hộ BĐS, khoản vay `CN-LN-01` gắn dự án | 2 chiều |
| `L05` | Tổ chức phát hành → Nhà đầu tư cá nhân | Trái phiếu phân phối qua iBond; chứng chỉ quỹ iFund | Mã trái phiếu/tổ chức phát hành, danh mục iFund theo ngành | Issuer → CN |
| `L06` | KHCN ↔ HKD / SME bán lẻ | Chi tiêu thẻ/QR của KHCN là doanh thu của HKD | Giao dịch QR/POS/Soundbox nhận tiền, MCC, địa bàn | CN → HKD |
| `L07` | HKD → SME | Chuyển đổi HKD lên DN (chính sách thuế), tăng trưởng quy mô | Cờ chuyển đổi, cùng chủ sở hữu (CIF chủ hộ = đại diện DN) | HKD → SME |
| `L08` | DN XNK → Thị trường quốc tế | L/C, nhờ thu, FX, phái sinh tỷ giá | Hồ sơ L/C, đối tác nước ngoài, quốc gia, HS code | Ngoài → DN |
| `L09` | Techcombank → Tất cả khách hàng | Lãi suất, phí, khẩu vị tín dụng, hệ thống số, danh tiếng | Thay đổi biểu phí/lãi suất, log sự cố, khiếu nại | Bank → KH |
| `L10` | Khách hàng → Nhà đầu tư | Chất lượng danh mục, lợi nhuận, thanh khoản → giá cổ phiếu, xếp hạng | Chỉ số nợ xấu, CASA, LNTT, công bố thông tin | KH → NĐT |
| `L11` | Hệ sinh thái tài chính → KH | Công ty con/đối tác: chứng khoán (TCBS), quản lý quỹ (Techcom Capital), bảo hiểm (Techcom Life, đối tác phi nhân thọ) | Mã sản phẩm phân phối, đối tác | 2 chiều |
| `L12` | Nhà nước → DN (mua sắm công, NSNN) | Bảo lãnh mua sắm công, thanh toán chậm từ ngân sách, nộp thuế | Bảo lãnh dự thầu/thực hiện HĐ, giao dịch nộp NSNN | Nhà nước → DN |

**Quy tắc duyệt:**
- Tối đa **3 hop** theo mặc định. Hop 4+ chỉ khi có bằng chứng định lượng.
- Mỗi hop giảm độ tin cậy (xem `scoring/scoring.md`).
- Cạnh `L01` và nút HKD có **độ trễ gần bằng 0** (cùng một túi tiền).
- Cạnh `L02`, `L06` có độ trễ **1–3 tháng** (chu kỳ lương, chu kỳ chi tiêu).
- Cạnh `L04`, `L05` có độ trễ **3–12 tháng** (tiến độ dự án, kỳ trả lãi/gốc).
