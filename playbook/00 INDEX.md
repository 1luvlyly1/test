---
id: INDEX
used_by: [Orchestrator, ALL]
steps: [0]
depends_on: []
load_when: Luôn nạp đầu tiên – file định tuyến, cho biết cần đọc file nào tiếp theo
version: v1.0
updated: 2026-10-26
---

# PLAYBOOK SUY LUẬN LAN TRUYỀN RỦI RO – TECHCOMBANK (INDEX)

Bộ playbook được tách thành các module nhỏ. **Agent không đọc toàn bộ thư mục.** Mỗi agent chỉ nạp `00_INDEX.md` + các file trong "gói ngữ cảnh" của mình (bảng 3), rồi nạp thêm file phân khúc theo bộ định tuyến (bảng 4).

Phạm vi: 5 nhóm khách hàng (Cá nhân · Hộ kinh doanh · DN vừa và nhỏ · DN lớn & ĐCTC · Nhà đầu tư). Danh mục sản phẩm chốt ngày 26/10/2026 từ techcombank.com.

## 1. Quy tắc chung (bắt buộc với mọi agent)

1. Mỗi sự kiện **luôn** đi qua quy trình 10 bước (`core/04_reasoning_procedure.md`). Không nhảy thẳng tới sản phẩm.
2. **Khách hàng trước, sản phẩm sau:** chỉ tra bảng sản phẩm sau khi đã xác định phân khúc bị chạm và cạnh truyền dẫn.
3. Tra sản phẩm bằng **mã sản phẩm** (ví dụ `CN-LN-05`, `HKD-LN-01`, `CIB-TF-02`) trong file phân khúc tương ứng.
4. Mọi kết luận phải ghi: **kênh truyền dẫn**, **số hop**, **độ tin cậy**, **tín hiệu nội bộ cần kiểm chứng**.
5. Không bịa số liệu. Thiếu dữ liệu nội bộ thì ghi `exposure: "unknown – cần truy vấn"`.
6. Ghi kết quả đúng schema chung (`scoring/output_schema.md`).

## 2. Cấu trúc thư mục

| File | ID | Nội dung | Kích thước |
|---|---|---|---|
| `00_INDEX.md` | INDEX | File này – định tuyến | nhỏ |
| `guardrails.md` | GUARDRAILS | 10 ràng buộc bắt buộc | nhỏ |
| `core/01_risk_codes.md` | CORE-RISK-CODES | Mã rủi ro `CR` `CL` `LQ` `MR` `OR` `FR` `CO` `RP` `BR` `INS` | nhỏ |
| `core/02_concepts_patterns.md` | CORE-CONCEPTS | Outside-in/Inside-out, mẫu P1/P2/P3, nút lai HKD, vòng phản hồi | nhỏ |
| `core/03_linkage_graph.md` | CORE-LINKAGE-GRAPH | 12 cạnh liên kết `L01`–`L12`, quy tắc duyệt, độ trễ | nhỏ |
| `core/04_reasoning_procedure.md` | CORE-PROCEDURE | Quy trình 10 bước & agent phụ trách | nhỏ |
| `events/event_matrix.md` | EVENT-MATRIX | 22 nhóm sự kiện `E01`–`E22` → mẫu → nút chạm → sản phẩm | vừa |
| `segments/seg_01_KHCN.md` | SEG-KHCN | Khách hàng cá nhân | lớn nhất |
| `segments/seg_02_HKD.md` | SEG-HKD | Hộ kinh doanh (nút lai) | vừa |
| `segments/seg_03_SME.md` | SEG-SME | DN vừa và nhỏ | vừa |
| `segments/seg_04_CIB.md` | SEG-CIB | DN lớn & ĐCTC | vừa |
| `segments/seg_05_NDT.md` | SEG-NDT | Nhà đầu tư | vừa |
| `inside_out/signals.md` | IO-SIGNALS | 16 tín hiệu nội bộ `S01`–`S16` | nhỏ |
| `inside_out/bank_response_risks.md` | IO-BANK-RESPONSE | Rủi ro bậc 2 do phản ứng của ngân hàng | nhỏ |
| `scoring/scoring.md` | SCORING | Công thức điểm, ngưỡng cảnh báo, độ tin cậy theo hop | nhỏ |
| `scoring/output_schema.md` | OUTPUT-SCHEMA | Schema JSON đầu ra | nhỏ |
| `examples/ex_P1_doanh_nghiep_truoc.md` | EX-P1 | Few-shot mẫu P1 | nhỏ |
| `examples/ex_P2_ca_nhan_truoc.md` | EX-P2 | Few-shot mẫu P2 | nhỏ |
| `examples/ex_P3_toan_he_thong.md` | EX-P3 | Few-shot mẫu P3 (inside-out) | nhỏ |

Mỗi file có front-matter `id`, `used_by`, `steps`, `depends_on`, `load_when` để orchestrator lọc tự động.

## 3. Gói ngữ cảnh theo agent (nạp sẵn)

| Agent | Bước | Luôn nạp | Nạp theo điều kiện |
|---|---|---|---|
| Orchestrator | 0–10 | `00_INDEX.md`, `core/04_reasoning_procedure.md`, `guardrails.md` | – |
| Ingest | 1 | `guardrails.md`, `scoring/output_schema.md` | – |
| Classifier | 2–3 | `core/02_concepts_patterns.md`, `events/event_matrix.md`, `guardrails.md` | – |
| Propagation | 3–4, 9 | `core/02_concepts_patterns.md`, `core/03_linkage_graph.md`, `guardrails.md` | File phân khúc (bảng 4), 1 file example đúng mẫu P |
| Product-Impact | 5, 7 | `core/01_risk_codes.md`, `scoring/scoring.md`, `guardrails.md` | **Chỉ** các file phân khúc nằm trong `propagation_path` |
| Inside-out Monitor | 6, 8 | `inside_out/signals.md`, `inside_out/bank_response_risks.md`, `core/03_linkage_graph.md` | Phần (d) của file phân khúc liên quan |
| Critic | 10 | `guardrails.md`, `scoring/scoring.md`, `core/02_concepts_patterns.md` | Output JSON của các agent trước |

## 4. Bộ định tuyến phân khúc

Nạp file phân khúc khi phân khúc đó là nút chạm đầu tiên **hoặc** xuất hiện trong `propagation_path`.

| Tín hiệu trong sự kiện / đường lan truyền | Nạp file |
|---|---|
| Cá nhân, hộ gia đình, người lao động, chủ DN với tư cách cá nhân; cạnh `L01` `L02` `L04` `L05` `L06` hướng về cá nhân | `segments/seg_01_KHCN.md` |
| Cửa hàng, tiểu thương, bán lẻ nhỏ, thuế HKD, sức mua địa phương; cạnh `L03` `L06` `L07` | `segments/seg_02_HKD.md` **và** `seg_01_KHCN.md` (nút lai) |
| DN vừa và nhỏ, nhà cung cấp, nhà thầu mua sắm công; cạnh `L01` `L02` `L03` `L07` `L12` | `segments/seg_03_SME.md` |
| Tập đoàn, ngành, xuất nhập khẩu, chủ đầu tư BĐS, tổ chức phát hành trái phiếu, anchor chuỗi cung ứng; cạnh `L03` `L04` `L05` `L08` | `segments/seg_04_CIB.md` |
| Cổ phiếu TCB, xếp hạng tín nhiệm, rủi ro tập trung, sự cố danh tiếng ngân hàng, mẫu P3; cạnh `L10` `L11` | `segments/seg_05_NDT.md` |

Giới hạn: một lượt suy luận nạp tối đa **3 file phân khúc**. Nếu cần nhiều hơn (thường là P3), tách thành nhiều lượt Product-Impact, mỗi lượt một phân khúc, rồi orchestrator gộp kết quả.

## 5. Bảng tra nhanh tiền tố mã

| Tiền tố | Ý nghĩa | File |
|---|---|---|
| `CN-` | Sản phẩm KHCN | `segments/seg_01_KHCN.md` |
| `HKD-` | Sản phẩm hộ kinh doanh | `segments/seg_02_HKD.md` |
| `SME-` | Sản phẩm DN vừa và nhỏ | `segments/seg_03_SME.md` |
| `CIB-` | Sản phẩm DN lớn & ĐCTC | `segments/seg_04_CIB.md` |
| `IR-` | Kênh nhà đầu tư | `segments/seg_05_NDT.md` |
| `L01`–`L12` | Cạnh liên kết | `core/03_linkage_graph.md` |
| `E01`–`E22` | Nhóm sự kiện | `events/event_matrix.md` |
| `S01`–`S16` | Tín hiệu nội bộ | `inside_out/signals.md` |
| `P1` `P2` `P3` | Mẫu lan truyền | `core/02_concepts_patterns.md` |

## 6. Quy tắc bảo trì

- Không đổi hoặc tái sử dụng mã cũ (sản phẩm, cạnh, sự kiện, tín hiệu). Sản phẩm ngừng bán thì đánh dấu `(ngừng)` thay vì xóa.
- Sản phẩm mới: thêm dòng vào bảng (c) **và** danh mục (f) của file phân khúc, cập nhật trường `updated` ở front-matter.
- Thêm cạnh/sự kiện/tín hiệu mới: cập nhật file gốc tương ứng và bảng 5 ở file này.
- Giữ mỗi file dưới ~12 KB. Nếu file phân khúc vượt ngưỡng, tách bảng (c) theo nhóm sản phẩm (ví dụ `seg_01_KHCN_vay.md`) và thêm dòng định tuyến tương ứng ở bảng 4.
