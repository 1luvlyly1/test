---
id: INDEX
used_by: [Orchestrator, ALL]
steps: [0]
depends_on: []
load_when: Luôn nạp đầu tiên – file định tuyến, cho biết cần đọc file nào tiếp theo
version: v1.2
updated: 2026-10-26
---

# PLAYBOOK SUY LUẬN LAN TRUYỀN RỦI RO – TECHCOMBANK (INDEX)

Bộ playbook gồm các module nhỏ. **Agent không đọc toàn bộ thư mục.** Mỗi agent chỉ nạp `00_INDEX.md` + gói ngữ cảnh của mình (mục 3), rồi nạp thêm file phân khúc theo bộ định tuyến (mục 4).

Phạm vi: 5 nhóm khách hàng (Cá nhân · Hộ kinh doanh · DN vừa và nhỏ · DN lớn & ĐCTC · Nhà đầu tư). Danh mục sản phẩm chốt ngày 26/10/2026 từ techcombank.com.

## 1. Quy tắc chung

1. **Đầu vào là sự kiện đã được người dùng sàng lọc.** Agent không lọc, không phân loại, không tự tìm thêm tin; chỉ lấy thông tin sự kiện để suy luận.
2. Mỗi sự kiện đi qua quy trình 6 bước (`core/04_reasoning_procedure.md`). Không nhảy thẳng tới sản phẩm.
3. **Khách hàng trước, sản phẩm sau:** chỉ tra sản phẩm sau khi đã biết phân khúc nào bị chạm và qua kênh nào.
4. Kết quả cuối cùng là **một bài văn xuôi** theo mẫu `core/05_output_prose.md`. Không cần JSON, không chấm điểm.
5. Mỗi nhận định phải nói rõ: lan qua kênh nào, sau bao lâu, mức chắc chắn (có khả năng cao / có thể / giả thuyết), và tín hiệu nội bộ nào để kiểm chứng.
6. Không bịa số liệu. Thiếu dữ liệu thì viết rõ là chưa có.

## 2. Cấu trúc thư mục

| File | Nội dung |
|---|---|
| `00_INDEX.md` | File này – định tuyến |
| `guardrails.md` | 10 ràng buộc bắt buộc |
| `core/01_risk_codes.md` | Mã loại rủi ro `CR` `CL` `LQ` `MR` `OR` `FR` `CO` `RP` `BR` `INS` |
| `core/02_concepts_patterns.md` | Outside-in/Inside-out, mẫu P1/P2/P3, nút lai HKD, vòng phản hồi |
| `core/03_linkage_graph.md` | 12 kênh liên kết `L01`–`L12`, độ trễ |
| `core/04_reasoning_procedure.md` | Quy trình 6 bước, mức chắc chắn |
| `core/05_output_prose.md` | Mẫu viết kết luận bằng văn xuôi |
| `segments/seg_01_KHCN.md` | Khách hàng cá nhân |
| `segments/seg_02_HKD.md` | Hộ kinh doanh (nút lai) |
| `segments/seg_03_SME.md` | DN vừa và nhỏ |
| `segments/seg_04_CIB.md` | DN lớn & ĐCTC |
| `segments/seg_05_NDT.md` | Nhà đầu tư |
| `inside_out/signals.md` | 16 tín hiệu nội bộ `S01`–`S16` |
| `inside_out/bank_response_risks.md` | Rủi ro do chính phản ứng của ngân hàng |
| `examples/ex_P1_doanh_nghiep_truoc.md` | Bài mẫu P1 |
| `examples/ex_P2_ca_nhan_truoc.md` | Bài mẫu P2 |
| `examples/ex_P3_toan_he_thong.md` | Bài mẫu P3 (inside-out) |

## 3. Gói ngữ cảnh theo agent

| Agent | Bước | Luôn nạp | Nạp theo điều kiện |
|---|---|---|---|
| Orchestrator | 1–6 | `00_INDEX.md`, `core/04_reasoning_procedure.md`, `guardrails.md` | – |
| Propagation | 1–2 | `core/02_concepts_patterns.md`, `core/03_linkage_graph.md` | File phân khúc (mục 4); 1 bài mẫu đúng mẫu P |
| Product-Impact | 3 | `core/01_risk_codes.md` | **Chỉ** các file phân khúc nằm trên đường lan truyền |
| Inside-out Monitor | 4–5 | `inside_out/signals.md`, `inside_out/bank_response_risks.md` | Phần (d) của file phân khúc liên quan |
| Critic (viết kết luận) | 6 | `guardrails.md`, `core/05_output_prose.md` | 1 bài mẫu đúng mẫu P; ghi chú của các agent trước |

## 4. Bộ định tuyến phân khúc

Nạp file phân khúc khi phân khúc đó bị chạm đầu tiên **hoặc** nằm trên đường lan truyền.

| Dấu hiệu trong sự kiện / đường lan truyền | Nạp file |
|---|---|
| Cá nhân, hộ gia đình, người lao động, chủ DN với tư cách cá nhân; kênh `L01` `L02` `L04` `L05` `L06` hướng về cá nhân | `segments/seg_01_KHCN.md` |
| Cửa hàng, tiểu thương, bán lẻ nhỏ, thuế HKD, sức mua địa phương; kênh `L03` `L06` `L07` | `segments/seg_02_HKD.md` **và** `seg_01_KHCN.md` (nút lai) |
| DN vừa và nhỏ, nhà cung cấp, nhà thầu mua sắm công; kênh `L01` `L02` `L03` `L07` `L12` | `segments/seg_03_SME.md` |
| Tập đoàn, ngành, xuất nhập khẩu, chủ đầu tư BĐS, tổ chức phát hành trái phiếu, doanh nghiệp đầu chuỗi cung ứng; kênh `L03` `L04` `L05` `L08` | `segments/seg_04_CIB.md` |
| Cổ phiếu TCB, xếp hạng tín nhiệm, rủi ro tập trung, sự cố danh tiếng ngân hàng, mẫu P3; kênh `L10` `L11` | `segments/seg_05_NDT.md` |

Mỗi lượt nạp tối đa **3 file phân khúc**. Sự kiện P3 cần nhiều hơn thì tách thành nhiều lượt, mỗi lượt một phân khúc, rồi Critic viết gộp.

## 5. Tra nhanh tiền tố mã

| Tiền tố | Ý nghĩa | File |
|---|---|---|
| `CN-` | Sản phẩm KHCN | `segments/seg_01_KHCN.md` |
| `HKD-` | Sản phẩm hộ kinh doanh | `segments/seg_02_HKD.md` |
| `SME-` | Sản phẩm DN vừa và nhỏ | `segments/seg_03_SME.md` |
| `CIB-` | Sản phẩm DN lớn & ĐCTC | `segments/seg_04_CIB.md` |
| `IR-` | Kênh nhà đầu tư | `segments/seg_05_NDT.md` |
| `L01`–`L12` | Kênh liên kết | `core/03_linkage_graph.md` |
| `S01`–`S16` | Tín hiệu nội bộ | `inside_out/signals.md` |
| `P1` `P2` `P3` | Mẫu lan truyền | `core/02_concepts_patterns.md` |

## 6. Quy tắc bảo trì

- Không đổi hoặc tái sử dụng mã cũ. Sản phẩm ngừng bán thì đánh dấu `(ngừng)` thay vì xóa.
- Sản phẩm mới: thêm vào bảng (c) **và** danh mục (f) của file phân khúc, cập nhật `updated` ở front-matter.
- Giữ mỗi file dưới ~12 KB. File phân khúc vượt ngưỡng thì tách bảng (c) theo nhóm sản phẩm và thêm dòng định tuyến ở mục 4.
