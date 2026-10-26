---
id: EX-P2
used_by: [Propagation, Product-Impact, Critic]
steps: [3-9]
depends_on: [core/03_linkage_graph.md]
load_when: Few-shot khi sự kiện thuộc mẫu P2
version: v1.0
updated: 2026-10-26
---

# Ví dụ P2 – Cá nhân trước: lãnh đạo một tập đoàn bị khởi tố

> Kịch bản giả định để minh họa cách suy luận, không phản ánh dữ liệu thực. Dùng làm few-shot khi cần.



**Bước 1–3:** E06, outside-in, P2. Chạm đầu tiên: cá nhân (khách hàng Private).

**Bước 4 – Đường lan truyền:**
```
Cá nhân lãnh đạo (KHCN Private) ─ hop0: tài khoản/tài sản có thể bị phong tỏa (CO)
 ├─ L01 ─► Tập đoàn (CIB) ─ hop1: khủng hoảng niềm tin, mất bảo lãnh cá nhân, TSBĐ bên thứ ba bị phong tỏa
 │          ├─ L05 ─► NĐT cá nhân nắm trái phiếu của tập đoàn qua iBond ─ hop2: yêu cầu bán lại hàng loạt
 │          ├─ L04 ─► Người mua nhà tại dự án của tập đoàn ─ hop2: lo ngại tiến độ, ngừng trả nợ
 │          └─ L02 ─► Nhân viên tập đoàn ─ hop2
 └─ L10 ─► Nhà đầu tư TCB ─ hop2–3: lo ngại rủi ro tập trung
```

**Sản phẩm ưu tiên:** `CN-*` của cá nhân (CO) → `CIB-LN-02` `CIB-INV-01` `CIB-ACC-04` → `CN-INV-01` `CN-LN-01` `CN-INV-02e` → `IR-EQ-01`.

**Tín hiệu:** `S08` (bán lại iBond theo issuer), `S14` (khiếu nại), `S07` (rút tiền mặt), `S12`.

**Phản ứng ngân hàng cần cân nhắc:** Tạm dừng phân phối iBond của issuer có thể bị đọc là tín hiệu xấu (`inside_out/bank_response_risks.md`) → cần truyền thông phối hợp.
