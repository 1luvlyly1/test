---
id: OUTPUT-SCHEMA
used_by: [ALL]
steps: [1-10]
depends_on: []
load_when: Khi ghi kết quả – mọi agent ghi vào đúng trường của schema chung
version: v1.0
updated: 2026-10-26
---

# Schema đầu ra (JSON)

```json
{
  "event": {
    "id": "EVT-2026-xxxx",
    "title": "string",
    "description": "string",
    "source": "string",
    "source_reliability": "A|B|C|D",
    "event_date": "YYYY-MM-DD",
    "geography": ["string"],
    "sectors_vsic": ["string"]
  },
  "classification": {
    "direction": "outside_in|inside_out|both",
    "event_category": "E01..E22",
    "pattern": ["P1", "P2", "P3"],
    "hybrid_node_involved": true
  },
  "first_hit_segments": ["KHCN|HKD|SME|CIB|NDT"],
  "propagation_path": [
    {
      "hop": 1,
      "from": "CIB",
      "to": "KHCN",
      "edge": "L02",
      "mechanism": "Cắt giảm nhân sự → thu nhập nhân viên giảm",
      "lag": "1-3 tháng",
      "confidence": 0.75
    }
  ],
  "product_impacts": [
    {
      "segment": "KHCN",
      "product_code": "CN-LN-06",
      "product_name": "Vay tiêu dùng tín chấp trả góp",
      "risk_types": ["CR"],
      "direction": "negative",
      "rationale": "string",
      "exposure": "unknown – cần truy vấn",
      "hop": 1
    }
  ],
  "signals_to_check": [
    { "signal_id": "S01", "query_hint": "Lô lương của DN thuộc ngành X tại tỉnh Y, so sánh 3 tháng gần nhất" }
  ],
  "bank_response_risks": ["string"],
  "feedback_loops": ["string"],
  "score": {
    "severity": 4, "likelihood": 3, "breadth": 2, "urgency": 2,
    "risk_score": 48, "alert_level": "Vàng"
  },
  "critic_notes": {
    "weakest_assumption": "string",
    "missed_segments_check": "string",
    "data_gaps": ["string"]
  },
  "final_confidence": 0.6,
  "recommended_actions": ["string"]
}
```
