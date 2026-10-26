---
id: SCORING
used_by: [Product-Impact, Critic]
steps: [7, 10]
depends_on: []
load_when: Chấm điểm mức độ cảnh báo và hiệu chỉnh độ tin cậy theo hop
version: v1.0
updated: 2026-10-26
---

# Chấm điểm mức độ & độ tin cậy

## 7.1 Công thức
```
risk_score = Severity (1–5) × Likelihood (1–5) × Breadth (1–3) × Urgency (1–3)
Thang tối đa = 225
```

| Thành phần | 1 | 3 | 5 |
|---|---|---|---|
| **Severity** (mức thiệt hại nếu xảy ra) | Ảnh hưởng nhỏ, phí/doanh thu | DPD tăng ở một nhóm sản phẩm | Tổn thất tín dụng lớn, khủng hoảng thanh khoản/danh tiếng |
| **Likelihood** | Suy đoán, ≥3 hop, nguồn yếu | 2 hop, có cơ chế rõ | Đã có tín hiệu nội bộ xác nhận |

| Thành phần | 1 | 2 | 3 |
|---|---|---|---|
| **Breadth** (độ phủ) | Một khách hàng/nhóm nhỏ | Một phân khúc hoặc một địa bàn | Nhiều phân khúc / toàn hệ thống |
| **Urgency** (thời gian tới tác động) | > 6 tháng | 1–6 tháng | < 1 tháng |

**Phân loại cảnh báo:** `≥ 120` Đỏ · `60–119` Cam · `20–59` Vàng · `< 20` Theo dõi

## 7.2 Độ tin cậy theo hop
| Hop | Hệ số tin cậy mặc định |
|---|---|
| 0 (nút chạm đầu tiên / nút lai HKD) | 0.9 |
| 1 | 0.75 |
| 2 | 0.55 |
| 3 | 0.35 |
| ≥ 4 | ≤ 0.2 – chỉ ghi nhận như giả thuyết |

Điều chỉnh: +0.15 nếu có tín hiệu nội bộ (`inside_out/signals.md`) xác nhận; −0.2 nếu nguồn sự kiện xếp hạng C/D; trần 0.95.
