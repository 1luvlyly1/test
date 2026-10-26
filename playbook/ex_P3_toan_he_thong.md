---
id: EX-P3
used_by: [Propagation, Product-Impact, Critic]
steps: [3-9]
depends_on: [core/03_linkage_graph.md]
load_when: Few-shot khi sự kiện thuộc mẫu P3
version: v1.0
updated: 2026-10-26
---

# Ví dụ P3 – Toàn hệ thống (Inside-out): gián đoạn ngân hàng số kéo dài

> Kịch bản giả định để minh họa cách suy luận, không phản ánh dữ liệu thực. Dùng làm few-shot khi cần.



**Bước 1–3:** E18, inside-out, P3. Chạm đồng thời mọi phân khúc.

| Phân khúc | Tác động trực tiếp | Mã sản phẩm | Rủi ro |
|---|---|---|---|
| KHCN | Không chuyển tiền, không thanh toán | `CN-DIG-01` `CN-CARD-02` `CN-ACC-01` | `OR` `RP` |
| HKD | Không nhận được tiền QR/Soundbox → **mất doanh thu trực tiếp** | `HKD-DIG-01` `HKD-REV-01/02/03` | `OR` `BR` `RP` |
| SME | Không chi lương/thanh toán nhà cung cấp đúng hạn | `SME-DIG-01` `SME-PAY-06` | `OR` |
| CIB | Gián đoạn thu hộ, thanh toán lớn | `CIB-DIG-01` `CIB-COL-01` | `OR` |
| Nhà đầu tư | Lan truyền mạng xã hội → lo ngại năng lực công nghệ | `IR-EQ-01` | `RP` |

**Rủi ro bậc 2:** kẻ gian lợi dụng sự cố gửi tin nhắn mạo danh “khắc phục sự cố” (`FR` tăng – `S13`); HKD chuyển sang nhận tiền qua ngân hàng khác (`BR` dài hạn).
