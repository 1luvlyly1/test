---
id: CORE-CONCEPTS
used_by: [Classifier, Propagation, Critic]
steps: [2, 3, 9]
depends_on: []
load_when: Phân loại hướng (outside-in/inside-out), chọn mẫu P1/P2/P3, kiểm tra vòng phản hồi
version: v1.0
updated: 2026-10-26
---

# Khung khái niệm: Outside-in, Inside-out, 3 mẫu lan truyền

## 1.1 Hai hướng phát hiện

| Hướng | Định nghĩa | Nguồn đầu vào điển hình | Câu hỏi agent phải trả lời |
|---|---|---|---|
| **Outside-in** | Sự kiện bên ngoài ngân hàng tác động vào khách hàng → vào danh mục sản phẩm của ngân hàng | Tin tức, chính sách (NHNN, Bộ Tài chính, thuế), thị trường (lãi suất, tỷ giá, vàng, chứng khoán, BĐS), thiên tai, dịch bệnh, thương mại quốc tế, sự cố của DN/đối tác | “Sự kiện này chạm ai đầu tiên, lan sang ai tiếp theo, rơi vào sản phẩm nào?” |
| **Inside-out** | Tín hiệu/biến cố phát sinh **bên trong** ngân hàng (dữ liệu giao dịch, quyết định chính sách, sự cố hệ thống) lan ra khách hàng, thị trường và nhà đầu tư | Dữ liệu giao dịch nội bộ, DPD, dòng tiền lương, doanh thu QR/POS, sự cố hệ thống, thay đổi lãi suất/phí/khẩu vị tín dụng, khiếu nại | “Tín hiệu nội bộ này báo trước điều gì ở khách hàng?” và “Hành động của ngân hàng có tạo rủi ro thứ cấp không?” |

> Một sự kiện có thể có **cả hai chiều**: ví dụ ngành BĐS suy yếu (outside-in) → ngân hàng siết cho vay mua nhà (inside-out) → chủ đầu tư thiếu dòng tiền bán hàng → rủi ro quay lại danh mục CIB.

## 1.2 Ba mẫu lan truyền (Propagation Patterns)

```
P1 – DOANH NGHIỆP TRƯỚC
  Sự kiện ─► Doanh nghiệp ─┬─► Chủ DN / cổ đông (KHCN Priority/Private)
                           ├─► Nhân viên (qua chi lương)
                           ├─► Nhà cung cấp / nhà phân phối (SME, HKD)
                           └─► Khách hàng của DN (người mua nhà, trái chủ iBond)

P2 – CÁ NHÂN TRƯỚC
  Sự kiện ─► Cá nhân / hộ gia đình ─┬─► Chi tiêu giảm ─► HKD, SME bán lẻ, DN tiêu dùng
                                    ├─► Chủ DN gặp biến cố ─► DN mình sở hữu/bảo lãnh
                                    └─► Hành vi tài chính thay đổi (rút tiền, bán iFund…)

P3 – TOÀN HỆ THỐNG (TRỰC TIẾP MỌI PHÂN KHÚC)
  Sự kiện ─► KHCN + HKD + SME + CIB đồng thời ─► Nhà đầu tư (giá cổ phiếu, xếp hạng)
  (lãi suất điều hành, tỷ giá, sự cố hệ thống Techcombank, quy định NHNN, thiên tai diện rộng)
```

**Nút lai – Hộ kinh doanh (HKD):** pháp lý và tài chính của HKD **không tách bạch** với chủ hộ. Mọi sự kiện chạm chủ hộ = chạm HKD ở cùng bước (hop 0), và ngược lại. Agent phải gắn cờ `hybrid_node: true`.

**Nút cuối – Nhà đầu tư:** nhận tác động khi rủi ro đủ lớn ở cấp danh mục ngân hàng (P3, hoặc P1/P2 cộng dồn). Đồng thời là **nguồn inside-out**: biến động giá cổ phiếu, xếp hạng tín nhiệm → chi phí vốn → lãi suất sản phẩm → khách hàng.

## 1.3 Vòng phản hồi (bậc 2+)
Agent phải kiểm tra vòng lặp sau tối thiểu 1 lần:
- DN sa thải → thu nhập nhân viên giảm → chi tiêu giảm → HKD/SME bán lẻ giảm doanh thu → HKD giảm nhập hàng → nhà phân phối (SCF) chậm thanh toán → DN lớn.
- Giá BĐS giảm → TSBĐ giảm → ngân hàng siết tín dụng → người mua không vay được → CĐT bán chậm → CĐT chậm tiến độ/chậm trả trái phiếu → nhà đầu tư iBond/TCRES.
