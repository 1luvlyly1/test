---
id: EX-P1
used_by: [Propagation, Product-Impact, Critic]
steps: [3-9]
depends_on: [core/03_linkage_graph.md]
load_when: Few-shot khi sự kiện thuộc mẫu P1
version: v1.0
updated: 2026-10-26
---

# Ví dụ P1 – Doanh nghiệp trước: thuế quan cao lên hàng dệt may xuất khẩu

> Kịch bản giả định để minh họa cách suy luận, không phản ánh dữ liệu thực. Dùng làm few-shot khi cần.



**Bước 1–3:** Sự kiện thương mại (E03), outside-in, P1. Chạm đầu tiên: CIB/SME dệt may xuất khẩu.

**Bước 4 – Đường lan truyền:**
```
DN dệt may (CIB/SME) ─ hop0: đơn hàng XK giảm, giá bán giảm
 ├─ L02 ─► Công nhân (KHCN) ─ hop1: giảm ca, sa thải (1–3 tháng)
 │          └─ L06 ─► HKD quanh KCN (nhà trọ, ăn uống, tạp hóa) ─ hop2: doanh thu QR giảm
 ├─ L01 ─► Chủ DN (KHCN Priority) ─ hop1: rút tiết kiệm, tăng thấu chi có TSBĐ để bơm vốn
 └─ L03 ─► Nhà cung cấp phụ liệu (SME) ─ hop1: bị chậm thanh toán
```

**Bước 5 – Sản phẩm:**
| Hop | Phân khúc | Mã sản phẩm | Rủi ro |
|---|---|---|---|
| 0 | CIB/SME | `CIB-TF-02` `CIB-LN-01` `CIB-FX-01` `SME-LN-01` | `CR` `MR` |
| 1 | KHCN (công nhân) | `CN-LN-06` `CN-LN-05` `CN-CARD-01` | `CR` |
| 1 | KHCN (chủ DN) | `CN-DEP-01` `CN-LN-09` | `LQ` `CR` `CL` |
| 1 | SME nhà cung cấp | `SME-LN-03` `SME-PAY-06` | `CR` |
| 2 | HKD | `HKD-REV-01/02` `HKD-LN-01` | `BR` `CR` |

**Bước 6 – Tín hiệu:** `S01` (lô lương DN dệt may), `S10` (hóa đơn điện giảm), `S12` (chủ DN rút tiết kiệm), `S02` (QR quanh KCN), chứng từ L/C xuất khẩu giảm.

**Bước 8 – Phản ứng ngân hàng:** Nếu siết hạn mức vốn lưu động ngành dệt may → DN cắt giảm sâu hơn → `S01` xấu nhanh hơn.

**Bước 9 – Vòng phản hồi:** Công nhân giảm chi tiêu → HKD giảm nhập hàng → nhà phân phối hàng tiêu dùng (SCF) chậm thu tiền.
