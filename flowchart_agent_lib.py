# Databricks notebook source
# =============================================================================
#  Flowchart Agent – thư viện
#  Dùng trong notebook chính bằng:  %run ./flowchart_agent_lib
#
#  Luồng xử lý:
#    context người dùng ──► Claude Sonnet 5.5 qua model service Unity AI Gateway
#        (analytics_ai.rmd_bau.claude-sonnet-5-5-rmd_bau – không gọi trực tiếp model)
#        ──► JSON spec (nodes/edges/lanes) ──► validate + tự sửa (agent loop)
#        ──► layout tự động (layered / Sugiyama rút gọn, định tuyến vuông góc)
#        ──► HTML động (SVG + CSS/SMIL, không JS ngoài)  +  GIF (Pillow)  +  SVG tĩnh
#
#  Phụ thuộc: requests, Pillow, (matplotlib chỉ để lấy font DejaVu) – có sẵn trên
#  Databricks Runtime. databricks-sdk (có sẵn trên DBR 13+) dùng để xác thực.
# =============================================================================

import base64
import datetime as _dt
import html as _html
import json
import math
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

# -----------------------------------------------------------------------------
# 1. THEME – phong cách Techcom Wealth (ngà / mực / vàng ánh kim, điểm đỏ Techcombank)
#    Mã màu là ước lượng theo nhận diện thương hiệu; thay bằng mã chính thức nếu có.
# -----------------------------------------------------------------------------
THEMES: Dict[str, Dict[str, str]] = {
    "wealth_light": {
        "page_bg": "#F3EEE4", "card": "#FBF8F2", "ink": "#1D1B18", "muted": "#7A7062",
        "rule": "#E3D8C4", "edge": "#B9A987", "edge_strong": "#8C7A5B",
        "gold": "#B08D57", "gold_soft": "#F1E7D5", "gold_deep": "#7D6136",
        "red": "#D3202A", "red_soft": "#F8E3E1", "green": "#2F6B5A", "green_soft": "#E0EDE7",
        "node_fill": "#FFFFFF", "node_stroke": "#CDB894",
        "start_fill": "#B08D57", "start_text": "#FFFFFF",
        "end_fill": "#1D1B18", "end_text": "#F1E7D5",
        "lane_alt": "#F5EEE1", "lane_head": "#EFE4CF", "lane_line": "#E1D3BA",
        "shadow": "#5A4320", "token": "#B08D57", "token_ring": "#FFFFFF",
    },
    "wealth_dark": {
        "page_bg": "#0C0B0A", "card": "#14120F", "ink": "#F3EDE2", "muted": "#A59A88",
        "rule": "#2E2921", "edge": "#5C513F", "edge_strong": "#8E7B5A",
        "gold": "#C9A46A", "gold_soft": "#2A2318", "gold_deep": "#E2C48E",
        "red": "#E0464D", "red_soft": "#3A1D1D", "green": "#6FB59A", "green_soft": "#16302A",
        "node_fill": "#1C1915", "node_stroke": "#6E5E45",
        "start_fill": "#C9A46A", "start_text": "#15120D",
        "end_fill": "#F3EDE2", "end_text": "#15120D",
        "lane_alt": "#181510", "lane_head": "#211C15", "lane_line": "#2E2921",
        "shadow": "#000000", "token": "#E2C48E", "token_ring": "#14120F",
    },
}

FONT_STACK = "'Segoe UI','SF Pro Text','Helvetica Neue',Arial,'DejaVu Sans',sans-serif"
SERIF_STACK = "'Cormorant Garamond','Playfair Display',Georgia,'Times New Roman','DejaVu Serif',serif"

# -----------------------------------------------------------------------------
# 2. ENTITY / SHAPE REGISTRY (tương đương thư viện Flowchart của draw.io)
#    Đây là nguồn duy nhất: dùng cho prompt LLM, file catalog HTML, renderer SVG & GIF.
# -----------------------------------------------------------------------------
SHAPES: Dict[str, Dict[str, str]] = {
    "start":        {"vi": "Bắt đầu",            "drawio": "Terminator",        "use": "Điểm khởi đầu quy trình. Thường có đúng 1."},
    "end":          {"vi": "Kết thúc",           "drawio": "Terminator",        "use": "Điểm kết thúc (có thể nhiều: hoàn tất, từ chối, huỷ...)."},
    "process":      {"vi": "Xử lý / Hành động",  "drawio": "Process",           "use": "Một bước công việc, hành động do người hoặc hệ thống thực hiện."},
    "decision":     {"vi": "Điều kiện",          "drawio": "Decision",          "use": "Câu hỏi Có/Không hoặc rẽ nhiều nhánh; mỗi nhánh ra phải có nhãn."},
    "io":           {"vi": "Nhập / Xuất dữ liệu", "drawio": "Data",             "use": "Dữ liệu vào/ra: form, file, API request/response."},
    "document":     {"vi": "Tài liệu",           "drawio": "Document",          "use": "Văn bản, hợp đồng, báo cáo, chứng từ được tạo hoặc dùng."},
    "database":     {"vi": "Cơ sở dữ liệu",      "drawio": "Database",          "use": "Lưu trữ / truy vấn dữ liệu: CRM, core banking, data lake."},
    "subprocess":   {"vi": "Quy trình con",      "drawio": "Predefined Process", "use": "Một quy trình đã định nghĩa ở nơi khác (gọi lại)."},
    "manual_input": {"vi": "Nhập thủ công",      "drawio": "Manual Input",      "use": "Nhân viên/khách hàng nhập liệu bằng tay."},
    "manual_op":    {"vi": "Thao tác thủ công",  "drawio": "Manual Operation",  "use": "Bước làm thủ công, không tự động hoá (ký, kiểm đếm...)."},
    "preparation":  {"vi": "Chuẩn bị",           "drawio": "Preparation",       "use": "Khởi tạo, chuẩn bị điều kiện, cấu hình trước khi xử lý."},
    "delay":        {"vi": "Chờ / Trì hoãn",     "drawio": "Delay",             "use": "Thời gian chờ, SLA, hàng đợi phê duyệt."},
    "display":      {"vi": "Hiển thị",           "drawio": "Display",           "use": "Thông tin hiển thị trên màn hình / app / dashboard."},
    "event":        {"vi": "Sự kiện",            "drawio": "Ellipse",           "use": "Sự kiện, thông báo, trigger (email, SMS, webhook)."},
    "connector":    {"vi": "Điểm nối",           "drawio": "On-page Reference", "use": "Điểm nối/nhảy (A, B...) khi luồng quá xa. Hạn chế dùng."},
    "note":         {"vi": "Ghi chú",            "drawio": "Note",              "use": "Chú thích bổ sung, nối bằng cạnh style=dotted."},
}
SHAPE_ORDER = list(SHAPES.keys())

TONES = ("default", "gold", "red", "green", "muted")

TYPE_ALIASES = {
    "terminator": "start", "begin": "start", "stop": "end", "finish": "end",
    "rect": "process", "rectangle": "process", "action": "process", "task": "process", "step": "process", "activity": "process",
    "diamond": "decision", "condition": "decision", "gateway": "decision", "if": "decision", "rhombus": "decision",
    "data": "io", "input": "io", "output": "io", "parallelogram": "io", "input_output": "io",
    "doc": "document", "report": "document", "contract": "document",
    "cylinder": "database", "db": "database", "storage": "database", "datastore": "database",
    "predefined_process": "subprocess", "sub_process": "subprocess", "predefined": "subprocess",
    "manualinput": "manual_input", "manual_operation": "manual_op", "manual": "manual_op",
    "hexagon": "preparation", "prepare": "preparation",
    "wait": "delay", "timer": "delay",
    "circle": "event", "ellipse": "event", "notification": "event",
    "screen": "display", "ui": "display",
    "reference": "connector", "jump": "connector",
    "annotation": "note", "comment": "note",
}

# Kích thước chữ (đơn vị px của SVG)
FS, LH = 14, 18          # nhãn node
EFS, ELH = 12, 15        # nhãn cạnh
WRAP = {"process": 150, "decision": 104, "start": 150, "end": 150, "io": 140, "document": 140,
        "database": 130, "subprocess": 140, "manual_input": 140, "manual_op": 140, "preparation": 130,
        "delay": 130, "display": 140, "event": 110, "connector": 40, "note": 160}

# -----------------------------------------------------------------------------
# 3. FONT & ĐO CHỮ (dùng chung cho layout, SVG và GIF để kết quả nhất quán)
# -----------------------------------------------------------------------------
_FONT_FILES = {
    "sans": "DejaVuSans.ttf", "sans_bold": "DejaVuSans-Bold.ttf",
    "serif": "DejaVuSerif.ttf", "serif_bold": "DejaVuSerif-Bold.ttf",
}
_font_path_cache: Dict[str, Optional[str]] = {}
_font_cache: Dict[Tuple[str, int], object] = {}


def _font_path(kind: str) -> Optional[str]:
    if kind in _font_path_cache:
        return _font_path_cache[kind]
    fname = _FONT_FILES[kind]
    cands = []
    try:
        import matplotlib
        cands.append(os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", fname))
    except Exception:
        pass
    cands += [f"/usr/share/fonts/truetype/dejavu/{fname}", f"/usr/share/fonts/dejavu/{fname}",
              f"/Library/Fonts/{fname}", f"C:/Windows/Fonts/{fname}"]
    path = next((p for p in cands if os.path.exists(p)), None)
    _font_path_cache[kind] = path
    return path


def get_font(size: float, kind: str = "sans"):
    from PIL import ImageFont
    size = max(6, int(round(size)))
    key = (kind, size)
    if key not in _font_cache:
        p = _font_path(kind)
        if p:
            _font_cache[key] = ImageFont.truetype(p, size)
        else:  # fallback (không hỗ trợ đủ tiếng Việt)
            try:
                _font_cache[key] = ImageFont.load_default(size=size)
            except TypeError:
                _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def text_w(s: str, size: float = FS, kind: str = "sans") -> float:
    f = get_font(size, kind)
    try:
        return float(f.getlength(s))
    except AttributeError:
        return float(f.getsize(s)[0])


def wrap_text(s: str, max_w: float, size: float = FS, kind: str = "sans") -> List[str]:
    out: List[str] = []
    for para in str(s).replace("\\n", "\n").split("\n"):
        words = para.split()
        if not words:
            continue
        line = words[0]
        for w in words[1:]:
            cand = line + " " + w
            if text_w(cand, size, kind) <= max_w:
                line = cand
            else:
                out.append(line)
                line = w
        out.append(line)
    return out or [""]


# -----------------------------------------------------------------------------
# 4. HÌNH HỌC CÁC SHAPE (toạ độ tương đối quanh tâm 0,0)
# -----------------------------------------------------------------------------
def _arc(cx, cy, rx, ry, a0, a1, n=10):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _rrect(w, h, r, n=6):
    r = max(0.0, min(r, w / 2, h / 2))
    x0, y0, x1, y1 = -w / 2, -h / 2, w / 2, h / 2
    if r < 0.5:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    pts += _arc(x1 - r, y0 + r, r, r, -math.pi / 2, 0, n)
    pts += _arc(x1 - r, y1 - r, r, r, 0, math.pi / 2, n)
    pts += _arc(x0 + r, y1 - r, r, r, math.pi / 2, math.pi, n)
    pts += _arc(x0 + r, y0 + r, r, r, math.pi, 1.5 * math.pi, n)
    return pts


def shape_geometry(t: str, w: float, h: float):
    """Trả về (polygon tô nền, [các polyline phụ chỉ vẽ nét])."""
    hw, hh = w / 2, h / 2
    if t in ("start", "end"):
        return _rrect(w, h, h / 2, 10), []
    if t == "process":
        return _rrect(w, h, 8), []
    if t == "decision":
        return [(0, -hh), (hw, 0), (0, hh), (-hw, 0)], []
    if t == "io":
        k = h * 0.35
        return [(-hw + k, -hh), (hw, -hh), (hw - k, hh), (-hw, hh)], []
    if t == "document":
        a = min(9.0, h * 0.16)
        pts = [(-hw, -hh), (hw, -hh), (hw, hh - a)]
        n = 24
        for i in range(n + 1):
            u = i / n
            pts.append((hw - u * w, hh - a + a * math.sin(u * 2 * math.pi)))
        return pts, []
    if t == "database":
        ry = min(9.0, h * 0.16)
        pts = _arc(0, -hh + ry, hw, ry, math.pi, 2 * math.pi, 20) + _arc(0, hh - ry, hw, ry, 0, math.pi, 20)
        rim = _arc(0, -hh + ry, hw, ry, 0, math.pi, 20)
        return pts, [rim]
    if t == "subprocess":
        b = 10
        return _rrect(w, h, 3), [[(-hw + b, -hh), (-hw + b, hh)], [(hw - b, -hh), (hw - b, hh)]]
    if t == "manual_input":
        k = h * 0.28
        return [(-hw, -hh + k), (hw, -hh), (hw, hh), (-hw, hh)], []
    if t == "manual_op":
        k = h * 0.3
        return [(-hw, -hh), (hw, -hh), (hw - k, hh), (-hw + k, hh)], []
    if t == "preparation":
        k = h * 0.35
        return [(-hw + k, -hh), (hw - k, -hh), (hw, 0), (hw - k, hh), (-hw + k, hh), (-hw, 0)], []
    if t == "delay":
        r = hh
        return [(-hw, -hh)] + _arc(hw - r, 0, r, hh, -math.pi / 2, math.pi / 2, 16) + [(-hw, hh)], []
    if t == "display":
        k, r = h * 0.35, h * 0.35
        return [(-hw, 0), (-hw + k, -hh)] + _arc(hw - r, 0, r, hh, -math.pi / 2, math.pi / 2, 16) + [(-hw + k, hh)], []
    if t in ("event", "connector"):
        return _arc(0, 0, hw, hh, 0, 2 * math.pi, 48)[:-1], []
    if t == "note":
        f = 12
        return [(-hw, -hh), (hw - f, -hh), (hw, -hh + f), (hw, hh), (-hw, hh)], [[(hw - f, -hh), (hw - f, -hh + f), (hw, -hh + f)]]
    return _rrect(w, h, 8), []


def node_box(t: str, tw: float, th: float) -> Tuple[float, float, float]:
    """Kích thước (w, h) của node từ kích thước khối chữ, và độ lệch dọc của chữ."""
    px, py = 16, 11
    dy = 0.0
    if t in ("start", "end"):
        h = max(42, th + 2 * py); w = max(120, tw + h * 0.9)
    elif t == "decision":
        w = max(140, tw * 1.9 + 30); h = max(76, th * 2.0 + 26)
    elif t in ("io", "manual_op", "preparation", "display"):
        h = max(48, th + 2 * py); w = max(132, tw + 2 * px + h * 0.7)
        if t == "display":
            dy = 0
    elif t == "manual_input":
        h = max(56, th + 2 * py + 12); w = max(124, tw + 2 * px); dy = h * 0.14
    elif t == "document":
        h = max(56, th + 2 * py + 10); w = max(124, tw + 2 * px); dy = -4
    elif t == "database":
        h = max(62, th + 2 * py + 18); w = max(124, tw + 2 * px); dy = 6
    elif t == "subprocess":
        h = max(48, th + 2 * py); w = max(140, tw + 2 * px + 20)
    elif t == "delay":
        h = max(48, th + 2 * py); w = max(120, tw + 2 * px + h * 0.35)
    elif t == "event":
        w = max(110, tw * 1.42 + 24); h = max(56, th * 1.42 + 20)
    elif t == "connector":
        d = max(40, max(tw, th) * 1.42 + 14); w = h = d
    elif t == "note":
        h = max(46, th + 2 * py); w = max(130, tw + 2 * px + 8)
    else:
        h = max(48, th + 2 * py); w = max(124, tw + 2 * px)
    return float(w), float(h), float(dy)


def node_colors(theme: Dict[str, str], t: str, tone: str) -> Dict[str, object]:
    th = theme
    if t == "start":
        return {"fill": th["start_fill"], "stroke": th["start_fill"], "text": th["start_text"], "sw": 1.6, "dash": None, "bold": True}
    if t == "end":
        if tone == "red":
            return {"fill": th["red"], "stroke": th["red"], "text": "#FFFFFF", "sw": 1.6, "dash": None, "bold": True}
        if tone == "green":
            return {"fill": th["green"], "stroke": th["green"], "text": "#FFFFFF", "sw": 1.6, "dash": None, "bold": True}
        return {"fill": th["end_fill"], "stroke": th["end_fill"], "text": th["end_text"], "sw": 1.6, "dash": None, "bold": True}
    if tone == "default" and t == "decision":
        tone = "gold"
    if tone == "default" and t == "note":
        tone = "muted"
    base = {"fill": th["node_fill"], "stroke": th["node_stroke"], "text": th["ink"], "sw": 1.6, "dash": None, "bold": False}
    if tone == "gold":
        base.update(fill=th["gold_soft"], stroke=th["gold"])
    elif tone == "red":
        base.update(fill=th["red_soft"], stroke=th["red"])
    elif tone == "green":
        base.update(fill=th["green_soft"], stroke=th["green"])
    elif tone == "muted":
        base.update(fill=th["card"], stroke=th["edge"], text=th["muted"], dash=(4, 3))
    return base


def edge_label_tone(label: str) -> str:
    s = (label or "").strip().lower()
    if re.match(r"^(không|ko|no|sai|fail|thất bại|từ chối|không đạt|chưa|reject|lỗi|false)\b", s):
        return "red"
    if re.match(r"^(có|yes|đúng|ok|pass|đạt|đồng ý|hợp lệ|thành công|approve|true|đã)\b", s):
        return "green"
    return "default"


# -----------------------------------------------------------------------------
# 5. SPEC: chuẩn hoá & kiểm tra
# -----------------------------------------------------------------------------
@dataclass
class SpecCheck:
    spec: dict
    errors: List[str] = field(default_factory=list)      # cần LLM sửa
    warnings: List[str] = field(default_factory=list)    # đã tự sửa / chấp nhận được
    fatal: bool = False                                    # không thể render


def _slug_id(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_\-]", "_", str(s)).strip("_")
    return s or "n"


def normalize_spec(raw) -> SpecCheck:
    errors, warnings = [], []
    if not isinstance(raw, dict):
        return SpecCheck({}, ["JSON gốc phải là một object {...}."], [], True)
    spec = {
        "title": str(raw.get("title") or "Quy trình").strip(),
        "subtitle": str(raw.get("subtitle") or "").strip(),
        "direction": str(raw.get("direction") or "auto").upper(),
        "lanes": [str(x).strip() for x in (raw.get("lanes") or []) if str(x).strip()],
        "nodes": [], "edges": [],
    }
    if spec["direction"] not in ("TB", "LR"):
        spec["direction"] = "AUTO"
    nodes_in = raw.get("nodes")
    if not isinstance(nodes_in, list) or not nodes_in:
        return SpecCheck(spec, ["Thiếu mảng 'nodes' hoặc rỗng."], [], True)
    seen = set()
    for i, n in enumerate(nodes_in):
        if not isinstance(n, dict):
            errors.append(f"nodes[{i}] không phải object."); continue
        nid = _slug_id(n.get("id") or f"n{i+1}")
        if nid in seen:
            errors.append(f"id node bị trùng: '{nid}'."); nid = f"{nid}_{i}"
        seen.add(nid)
        t = str(n.get("type") or "process").strip().lower().replace("-", "_").replace(" ", "_")
        t = TYPE_ALIASES.get(t, t)
        if t not in SHAPES:
            warnings.append(f"Node '{nid}': type '{t}' không hợp lệ → dùng 'process'."); t = "process"
        tone = str(n.get("tone") or "default").lower()
        if tone not in TONES:
            tone = "default"
        label = str(n.get("label") or n.get("text") or nid).strip()
        spec["nodes"].append({"id": nid, "type": t, "label": label, "lane": str(n.get("lane") or "").strip(), "tone": tone})
    ids = {n["id"] for n in spec["nodes"]}
    for i, e in enumerate(raw.get("edges") or []):
        if not isinstance(e, dict):
            errors.append(f"edges[{i}] không phải object."); continue
        u = _slug_id(e.get("from") or e.get("source") or "")
        v = _slug_id(e.get("to") or e.get("target") or "")
        if u not in ids or v not in ids:
            errors.append(f"edges[{i}] tham chiếu node không tồn tại: {u} → {v}."); continue
        if u == v:
            warnings.append(f"Bỏ cạnh tự lặp {u} → {v}."); continue
        style = str(e.get("style") or "solid").lower()
        if style not in ("solid", "dashed", "dotted"):
            style = "solid"
        spec["edges"].append({"from": u, "to": v, "label": str(e.get("label") or "").strip(), "style": style})

    # lanes
    if spec["lanes"]:
        lane_set = list(spec["lanes"])
        for n in spec["nodes"]:
            if n["lane"] and n["lane"] not in lane_set:
                lane_set.append(n["lane"]); warnings.append(f"Thêm lane '{n['lane']}'.")
        spec["lanes"] = lane_set
        by_id = {n["id"]: n for n in spec["nodes"]}
        for n in spec["nodes"]:
            if not n["lane"]:
                nb = [by_id[e["from"]]["lane"] for e in spec["edges"] if e["to"] == n["id"] and by_id[e["from"]]["lane"]]
                nb += [by_id[e["to"]]["lane"] for e in spec["edges"] if e["from"] == n["id"] and by_id[e["to"]]["lane"]]
                n["lane"] = nb[0] if nb else spec["lanes"][0]
    else:
        lanes_used = []
        for n in spec["nodes"]:
            if n["lane"] and n["lane"] not in lanes_used:
                lanes_used.append(n["lane"])
        if len(lanes_used) >= 2:
            spec["lanes"] = lanes_used
            for n in spec["nodes"]:
                n["lane"] = n["lane"] or lanes_used[0]
        else:
            for n in spec["nodes"]:
                n["lane"] = ""

    # chất lượng
    types = {n["id"]: n["type"] for n in spec["nodes"]}
    outs: Dict[str, list] = {i: [] for i in ids}
    ins: Dict[str, list] = {i: [] for i in ids}
    for e in spec["edges"]:
        outs[e["from"]].append(e); ins[e["to"]].append(e)
    starts = [i for i, t in types.items() if t == "start"]
    if not starts:
        errors.append("Thiếu node type 'start'.")
    if not any(t == "end" for t in types.values()):
        errors.append("Thiếu node type 'end'.")
    for nid, t in types.items():
        if t == "decision":
            if len(outs[nid]) < 2:
                errors.append(f"Decision '{nid}' cần ít nhất 2 cạnh ra (hiện có {len(outs[nid])}).")
            elif any(not e["label"] for e in outs[nid]):
                errors.append(f"Các cạnh ra của decision '{nid}' phải có label (vd 'Có'/'Không').")
        if t == "end" and outs[nid]:
            warnings.append(f"Node end '{nid}' có cạnh ra.")
        if t not in ("end", "note", "connector") and not outs[nid]:
            warnings.append(f"Node '{nid}' ({t}) không có cạnh ra.")
    if starts:
        seen_r, stack = set(starts), list(starts)
        while stack:
            u = stack.pop()
            for e in outs[u]:
                if e["to"] not in seen_r:
                    seen_r.add(e["to"]); stack.append(e["to"])
        unreached = [i for i in ids if i not in seen_r and types[i] != "note"]
        if unreached:
            errors.append("Các node không đi tới được từ start: " + ", ".join(sorted(unreached)) + ".")
    if len(spec["nodes"]) > 60:
        errors.append(f"Quá nhiều node ({len(spec['nodes'])}); hãy gộp còn ≤ 40.")
    return SpecCheck(spec, errors, warnings, fatal=False)


def extract_json(text: str) -> dict:
    t = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j <= i:
        raise ValueError("Không tìm thấy object JSON trong phản hồi.")
    body = t[i:j + 1]
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        body2 = re.sub(r",\s*([}\]])", r"\1", body)
        try:
            return json.loads(body2)
        except json.JSONDecodeError as ex:
            raise ValueError(f"JSON không hợp lệ: {ex}") from None


# -----------------------------------------------------------------------------
# 6. LLM CLIENT – Claude Sonnet 5.5 qua model service (Unity AI Gateway)
# -----------------------------------------------------------------------------
DEFAULT_MODEL_SERVICE = "analytics_ai.rmd_bau.claude-sonnet-5-5-rmd_bau"


class DatabricksClaude:
    """
    Gọi Claude THÔNG QUA model service của Unity AI Gateway (không gọi trực tiếp serving endpoint/model).

    model_service : tên đầy đủ <catalog>.<schema>.<service>, mặc định analytics_ai.rmd_bau.claude-sonnet-5-5-rmd_bau
    api="gateway"   : POST {host}/ai-gateway/mlflow/v1/chat/completions   (OpenAI-compatible, model=<model_service>)
    api="anthropic" : POST {host}/ai-gateway/anthropic/v1/messages        (Anthropic Messages native, model=<model_service>)
    Xác thực: databricks-sdk WorkspaceClient (tự động trong notebook) → DATABRICKS_HOST/DATABRICKS_TOKEN → tham số host/token.
    Quyền cần có: được phép query model service này (Workspace/Consumer access + quyền trên service trong Unity Catalog).
    """

    ROUTES = {"gateway": "/ai-gateway/mlflow/v1/chat/completions",
              "anthropic": "/ai-gateway/anthropic/v1/messages"}

    def __init__(self, model_service: str = DEFAULT_MODEL_SERVICE, api: str = "gateway",
                 host: Optional[str] = None, token: Optional[str] = None,
                 max_tokens: int = 8000, timeout: int = 240, retries: int = 3):
        if api not in self.ROUTES:
            raise ValueError(f"api phải là một trong {list(self.ROUTES)} (chỉ gọi qua AI Gateway).")
        if model_service.count(".") < 2:
            raise ValueError(f"model_service phải là tên đầy đủ <catalog>.<schema>.<service>, nhận được: '{model_service}'")
        self.model_service, self.api = model_service.strip(), api
        self.host, self.token = host, token
        self.max_tokens, self.timeout, self.retries = max_tokens, timeout, retries
        self.resolved_url = ""

    @staticmethod
    def _nb_globals():
        """Lấy spark / dbutils của notebook (có khi chạy qua %run hoặc databricks.sdk.runtime)."""
        sp = dbu = None
        try:
            from databricks.sdk.runtime import spark as sp, dbutils as dbu  # type: ignore
        except Exception:
            pass
        g = globals()
        sp = sp or g.get("spark")
        dbu = dbu or g.get("dbutils")
        if sp is None:
            try:
                from pyspark.sql import SparkSession
                sp = SparkSession.getActiveSession()
            except Exception:
                pass
        return sp, dbu

    def _resolve_host(self) -> str:
        # Thứ tự giống cell test chạy được: DATABRICKS_HOST → spark.databricks.workspaceUrl.
        # KHÔNG dùng host của databricks-sdk trong notebook: nó có thể là host vùng
        # (vd https://singapore.cloud.databricks.com) – route /ai-gateway/... không có ở đó → HTTP 404.
        host = self.host or os.environ.get("DATABRICKS_HOST")
        if not host:
            sp, _ = self._nb_globals()
            try:
                host = sp.conf.get("spark.databricks.workspaceUrl") if sp is not None else None
            except Exception:
                host = None
        if not host:
            try:
                from databricks.sdk import WorkspaceClient
                host = WorkspaceClient().config.host
            except Exception:
                host = None
        if not host:
            raise RuntimeError("Không xác định được URL workspace. Truyền DatabricksClaude(host='https://<workspace-url>').")
        host = host.strip().rstrip("/")
        return host if host.startswith("http") else "https://" + host

    def _resolve_token(self) -> Dict[str, str]:
        token = self.token or os.environ.get("DATABRICKS_TOKEN")
        if not token:
            _, dbu = self._nb_globals()
            try:
                token = dbu.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            except Exception:
                token = None
        if token:
            return {"Authorization": f"Bearer {token}"}
        try:
            from databricks.sdk import WorkspaceClient
            return dict(WorkspaceClient().config.authenticate())
        except Exception as ex:
            raise RuntimeError(f"Không lấy được token Databricks ({ex}). Truyền DatabricksClaude(token=...).")

    def _auth(self) -> Tuple[str, Dict[str, str]]:
        host = self._resolve_host()
        self.resolved_url = host + self.ROUTES[self.api]
        return host, self._resolve_token()

    def __call__(self, system: str, messages: List[Dict[str, str]]) -> str:
        import requests
        host, headers = self._auth()
        headers = {**headers, "Content-Type": "application/json"}
        url = host + self.ROUTES[self.api]
        if self.api == "anthropic":
            headers["anthropic-version"] = "2023-06-01"
            payload = {"model": self.model_service, "max_tokens": self.max_tokens, "system": system, "messages": messages}
        else:
            payload = {"model": self.model_service, "max_tokens": self.max_tokens,
                       "messages": [{"role": "system", "content": system}] + messages}
        last = None
        for attempt in range(self.retries + 1):
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                if r.status_code in (429, 500, 502, 503, 504) and attempt < self.retries:
                    time.sleep(2 * (attempt + 1) ** 2); continue
                if r.status_code >= 400:
                    hint = ""
                    if r.status_code in (401, 403):
                        hint = " → Kiểm tra quyền query model service này trong Unity Catalog / AI Gateway."
                    elif r.status_code == 404:
                        hint = (" → Kiểm tra: (1) host phải là URL workspace (spark.databricks.workspaceUrl), không phải host vùng;"
                                " (2) tên model service catalog.schema.service; (3) workspace đã bật Unity AI Gateway.")
                    raise RuntimeError(f"HTTP {r.status_code} từ {url} (model={self.model_service}): {r.text[:600]}{hint}")
                return self._parse(r.json())
            except requests.RequestException as ex:
                last = ex
                if attempt < self.retries:
                    time.sleep(2 * (attempt + 1) ** 2); continue
                raise RuntimeError(f"Lỗi gọi AI Gateway: {ex}") from None
        raise RuntimeError(f"Lỗi gọi AI Gateway: {last}")

    def ping(self) -> str:
        """Kiểm tra kết nối/quyền nhanh trước khi chạy agent."""
        return self("Reply with exactly: OK", [{"role": "user", "content": "ping"}]).strip()

    @staticmethod
    def _parse(data: dict) -> str:
        def blocks_to_text(c):
            if isinstance(c, str):
                return c
            if isinstance(c, list):
                return "".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type", "text") == "text")
            return ""
        if "choices" in data:
            return blocks_to_text(data["choices"][0].get("message", {}).get("content", ""))
        if "content" in data:
            return blocks_to_text(data["content"])
        raise RuntimeError(f"Không đọc được phản hồi: {str(data)[:400]}")


# -----------------------------------------------------------------------------
# 7. PROMPT & AGENT LOOP
# -----------------------------------------------------------------------------
def build_system_prompt() -> str:
    shape_lines = "\n".join(f'  - "{k}": {v["vi"]} (draw.io: {v["drawio"]}). {v["use"]}' for k, v in SHAPES.items())
    return f"""You are a senior business-process analyst at a private-banking / wealth-management firm.
You convert a user's free-text description of a process into a clean, presentation-ready FLOWCHART SPEC in JSON.

ALLOWED NODE TYPES (draw.io flowchart entities):
{shape_lines}

OPTIONAL NODE "tone" (visual emphasis): "default" | "gold" (key step / highlight) | "red" (rejection, error, risk) | "green" (success, approved) | "muted" (secondary).

OUTPUT FORMAT – return ONLY one JSON object, no prose, no markdown fences:
{{
  "title": "short title in the user's language",
  "subtitle": "one-line scope / owner / SLA (optional, may be empty)",
  "direction": "TB" or "LR",
  "lanes": ["Actor 1", "Actor 2"],          // optional swimlanes; [] if not useful
  "nodes": [ {{"id": "snake_case_id", "type": "<type>", "label": "...", "lane": "Actor 1", "tone": "default"}} ],
  "edges": [ {{"from": "id_a", "to": "id_b", "label": "", "style": "solid"}} ]   // style: solid | dashed | dotted
}}

RULES
1. Labels in the SAME LANGUAGE as the user's text (Vietnamese if they write Vietnamese). Short, verb-first, max ~7 words. No trailing periods.
2. Exactly one "start". At least one "end". Every node must be reachable from start. Do not leave dead ends except "end"/"note".
3. Every "decision" is phrased as a question and has >= 2 outgoing edges, EACH with a label ("Có"/"Không", "Đạt"/"Không đạt", or the case names).
4. Pick the most specific entity: stored data → database; contracts/reports → document; forms/API payloads → io; staff typing data → manual_input;
   waiting/SLA → delay; app/screen output → display; SMS/email/webhook → event; calling a known sub-flow → subprocess.
5. Use "lanes" when 2+ actors/departments/systems are involved (e.g. Khách hàng, RM, Hệ thống, Phòng Tuân thủ); every node then has a "lane".
6. Loops (retry, request more documents) are edges pointing back to an earlier node.
   The chart goes on a slide: aim for 8–16 nodes and a main path of at most ~10 steps. Merge trivial or purely administrative steps.
7. Use tone "red" for rejection ends / risk steps, "green" for the successful end, "gold" for 1–3 key milestones. Most nodes stay "default".
8. "note" nodes only when it adds real context; connect them with style "dotted".
9. Prefer "LR" for short linear flows (<= 7 steps per path) and "TB" for long or highly branched flows.
10. Never invent facts the user did not imply; if details are missing, keep steps generic but logical."""


def build_user_prompt(context: str, previous: Optional[dict] = None, revision: Optional[str] = None) -> str:
    if previous and revision:
        return ("Here is the CURRENT flowchart spec:\n" + json.dumps(previous, ensure_ascii=False, indent=1) +
                "\n\nApply this CHANGE REQUEST from the user and return the FULL updated JSON spec (same format, keep unchanged ids):\n" +
                revision.strip() + ("\n\nOriginal process context for reference:\n" + context.strip() if context else ""))
    return "Create the flowchart spec for this process description:\n\n" + context.strip()


@dataclass
class AgentStep:
    attempt: int
    ok: bool
    errors: List[str]
    warnings: List[str]
    seconds: float


def generate_spec(context: str, llm: Callable[[str, list], str], previous: Optional[dict] = None,
                  revision: Optional[str] = None, max_repairs: int = 2, log: Callable = print):
    """Agent loop: sinh spec → kiểm tra → gửi lỗi lại cho model để tự sửa (tối đa max_repairs lần)."""
    system = build_system_prompt()
    messages = [{"role": "user", "content": build_user_prompt(context, previous, revision)}]
    steps: List[AgentStep] = []
    best: Optional[SpecCheck] = None
    for attempt in range(max_repairs + 1):
        t0 = time.time()
        log(f"[agent] Lần {attempt + 1}: gọi model…")
        text = llm(system, messages)
        try:
            chk = normalize_spec(extract_json(text))
        except ValueError as ex:
            chk = SpecCheck({}, [str(ex)], [], True)
        steps.append(AgentStep(attempt + 1, not chk.errors and not chk.fatal, chk.errors, chk.warnings, round(time.time() - t0, 1)))
        if not chk.fatal and (best is None or len(chk.errors) < len(best.errors)):
            best = chk
        if not chk.errors and not chk.fatal:
            log(f"[agent] ✓ Spec hợp lệ: {len(chk.spec['nodes'])} node, {len(chk.spec['edges'])} cạnh ({steps[-1].seconds}s).")
            return chk.spec, chk.warnings, steps
        log(f"[agent] ✗ {len(chk.errors)} lỗi → yêu cầu model tự sửa: " + " | ".join(chk.errors[:4]))
        messages += [{"role": "assistant", "content": text},
                     {"role": "user", "content": "Your JSON has these problems:\n- " + "\n- ".join(chk.errors) +
                      "\nReturn the FULL corrected JSON object only."}]
    if best is None:
        raise RuntimeError("Model không trả về JSON dùng được sau nhiều lần thử: " + "; ".join(steps[-1].errors))
    log(f"[agent] ⚠ Dùng bản tốt nhất còn {len(best.errors)} cảnh báo chất lượng.")
    return best.spec, best.warnings + best.errors, steps


# -----------------------------------------------------------------------------
# 8. LAYOUT (layered – Sugiyama rút gọn) + định tuyến cạnh vuông góc
# -----------------------------------------------------------------------------
@dataclass
class LNode:
    id: str
    type: str
    label: str
    tone: str
    lane: int
    lines: List[str]
    w: float
    h: float
    tdy: float = 0.0
    dummy: bool = False
    rank: int = 0
    r: float = 0.0       # toạ độ theo trục rank
    o: float = 0.0       # toạ độ theo trục order
    sr: float = 0.0
    so: float = 0.0
    x: float = 0.0
    y: float = 0.0


@dataclass
class Layout:
    direction: str
    width: float
    height: float
    nodes: List[dict]
    edges: List[dict]
    lanes: List[dict]
    build_end: float
    title: str = ""
    subtitle: str = ""


def _ray(poly, dx, dy) -> float:
    best = None
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        den = dx * ey - dy * ex
        if abs(den) < 1e-9:
            continue
        t = (x1 * ey - y1 * ex) / den
        s = (x1 * dy - y1 * dx) / den
        if t > 1e-6 and -1e-6 <= s <= 1 + 1e-6:
            best = t if best is None else min(best, t)
    return best or 0.0


def _simplify(pts):
    out = []
    for p in pts:
        if out and abs(out[-1][0] - p[0]) < 0.5 and abs(out[-1][1] - p[1]) < 0.5:
            continue
        out.append(p)
    i = 1
    while i < len(out) - 1:
        a, b, c = out[i - 1], out[i], out[i + 1]
        if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) < 0.5:
            out.pop(i)
        else:
            i += 1
    return out


def _round_poly(pts, rad=8.0, n=5):
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, p, b = pts[i - 1], pts[i], pts[i + 1]
        la, lb = math.dist(a, p), math.dist(p, b)
        r = min(rad, la / 2, lb / 2)
        if r < 1:
            out.append(p); continue
        p1 = (p[0] + (a[0] - p[0]) * r / la, p[1] + (a[1] - p[1]) * r / la)
        p2 = (p[0] + (b[0] - p[0]) * r / lb, p[1] + (b[1] - p[1]) * r / lb)
        for k in range(n + 1):
            u = k / n
            out.append(((1 - u) ** 2 * p1[0] + 2 * (1 - u) * u * p[0] + u * u * p2[0],
                        (1 - u) ** 2 * p1[1] + 2 * (1 - u) * u * p[1] + u * u * p2[1]))
    out.append(pts[-1])
    return out


def _plen(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def compute_layout(spec: dict, direction: str = "TB") -> Layout:
    TB = direction == "TB"
    lanes = list(spec.get("lanes") or [])
    lane_idx = {nm: i for i, nm in enumerate(lanes)}
    N: Dict[str, LNode] = {}
    order0: List[str] = []
    for n in spec["nodes"]:
        lines = wrap_text(n["label"], WRAP.get(n["type"], 150) * (1.0 if TB else 0.8), FS, "sans_bold" if n["type"] in ("start", "end") else "sans")
        tw = max(text_w(s, FS, "sans_bold" if n["type"] in ("start", "end") else "sans") for s in lines)
        th = len(lines) * LH
        w, h, tdy = node_box(n["type"], tw, th)
        ln = LNode(n["id"], n["type"], n["label"], n.get("tone", "default"), lane_idx.get(n.get("lane", ""), 0), lines, w, h, tdy)
        ln.sr, ln.so = (h, w) if TB else (w, h)
        N[n["id"]] = ln
        order0.append(n["id"])
    E = [dict(i=k, u=e["from"], v=e["to"], label=e.get("label", ""), style=e.get("style", "solid"))
         for k, e in enumerate(spec["edges"]) if e["from"] in N and e["to"] in N and e["from"] != e["to"]]
    out_e: Dict[str, list] = {i: [] for i in N}
    in_e: Dict[str, list] = {i: [] for i in N}
    for e in E:
        out_e[e["u"]].append(e); in_e[e["v"]].append(e)

    # --- back edges (DFS) ---
    roots = [i for i in order0 if N[i].type == "start"] + [i for i in order0 if not in_e[i] and N[i].type != "start"] + order0
    state: Dict[str, int] = {}
    back = set()
    for root in roots:
        if state.get(root):
            continue
        state[root] = 1
        stack = [(root, iter(out_e[root]))]
        while stack:
            u, it = stack[-1]
            e = next(it, None)
            if e is None:
                state[u] = 2; stack.pop(); continue
            s = state.get(e["v"], 0)
            if s == 1:
                back.add(e["i"])
            elif s == 0:
                state[e["v"]] = 1; stack.append((e["v"], iter(out_e[e["v"]])))
    fwd = [e for e in E if e["i"] not in back]
    dsucc: Dict[str, list] = {i: [] for i in N}
    dpred: Dict[str, list] = {i: [] for i in N}
    for e in fwd:
        dsucc[e["u"]].append(e["v"]); dpred[e["v"]].append(e["u"])

    # --- ranking: longest path ---
    indeg = {i: len(dpred[i]) for i in N}
    queue = [i for i in order0 if indeg[i] == 0]
    topo = []
    while queue:
        u = queue.pop(0); topo.append(u)
        for v in dsucc[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    rank = {i: 0 for i in N}
    for u in topo:
        for v in dsucc[u]:
            rank[v] = max(rank[v], rank[u] + 1)
    for u in reversed(topo):  # kéo các nguồn phụ (note, database...) xuống gần nơi dùng
        if not dpred[u] and N[u].type != "start" and dsucc[u]:
            rank[u] = max(rank[u], min(rank[v] for v in dsucc[u]) - 1)
    for i in N:
        N[i].rank = rank[i]

    # --- dummy nodes cho cạnh dài ---
    chains: Dict[int, List[str]] = {}
    seg_succ: Dict[str, list] = {i: [] for i in N}
    seg_pred: Dict[str, list] = {i: [] for i in N}
    for e in fwd:
        u, v = e["u"], e["v"]
        chain = [u]
        for k in range(rank[u] + 1, rank[v]):
            did = f"__d{e['i']}_{k}"
            dn = LNode(did, "dummy", "", "default", N[v].lane, [], 10, 0, dummy=True)
            dn.sr, dn.so, dn.rank = 0.0, 10.0, k
            N[did] = dn; seg_succ[did] = []; seg_pred[did] = []
            chain.append(did)
        chain.append(v)
        chains[e["i"]] = chain
        for a, b in zip(chain, chain[1:]):
            seg_succ[a].append(b); seg_pred[b].append(a)

    R = max(n.rank for n in N.values()) + 1
    layers: List[List[str]] = [[] for _ in range(R)]
    # thứ tự ban đầu: BFS
    bfs_idx: Dict[str, int] = {}
    q = [i for i in roots if i in N and not seg_pred[i]]
    for i in q:
        bfs_idx.setdefault(i, len(bfs_idx))
    qi = 0
    q = list(dict.fromkeys(q))
    while qi < len(q):
        u = q[qi]; qi += 1
        for v in seg_succ[u]:
            if v not in bfs_idx:
                bfs_idx[v] = len(bfs_idx); q.append(v)
    for i in N:
        bfs_idx.setdefault(i, len(bfs_idx))
    for i in sorted(N, key=lambda k: bfs_idx[k]):
        layers[N[i].rank].append(i)
    for L in layers:
        L.sort(key=lambda k: N[k].lane)

    def crossings(lay):
        c = 0
        for r in range(len(lay) - 1):
            pos = {k: j for j, k in enumerate(lay[r + 1])}
            segs = [(j, pos[v]) for j, u in enumerate(lay[r]) for v in seg_succ[u] if v in pos]
            for a in range(len(segs)):
                for b in range(a + 1, len(segs)):
                    if (segs[a][0] - segs[b][0]) * (segs[a][1] - segs[b][1]) < 0:
                        c += 1
        return c

    best_layers = [list(L) for L in layers]
    best_c = crossings(layers)
    for it in range(16):
        down = it % 2 == 0
        rng = range(1, R) if down else range(R - 2, -1, -1)
        for r in rng:
            ref = layers[r - 1] if down else layers[r + 1]
            pos = {k: j for j, k in enumerate(ref)}
            cur = {k: j for j, k in enumerate(layers[r])}

            def bc(k):
                nb = [pos[x] for x in (seg_pred[k] if down else seg_succ[k]) if x in pos]
                return sum(nb) / len(nb) if nb else cur[k]
            layers[r].sort(key=lambda k: (N[k].lane, bc(k), cur[k]))
        c = crossings(layers)
        if c < best_c:
            best_c, best_layers = c, [list(L) for L in layers]
    layers = best_layers

    # --- toạ độ trục order ---
    GAP, DGAP, MIX = 36.0, 14.0, 22.0
    nl = max(1, len(lanes))
    LANE_PAD = 26.0 if lanes else 0.0
    MIN_LANE = 190.0 if lanes else 0.0

    def sep(a: LNode, b: LNode):
        g = GAP if not (a.dummy or b.dummy) else (DGAP if a.dummy and b.dummy else MIX)
        return (a.so + b.so) / 2 + g

    def group(L, l):
        return [k for k in L if N[k].lane == l]

    need = [0.0] * nl
    for L in layers:
        for l in range(nl):
            g = group(L, l)
            if g:
                tot = N[g[0]].so / 2 + N[g[-1]].so / 2 + sum(sep(N[a], N[b]) for a, b in zip(g, g[1:]))
                need[l] = max(need[l], tot)
    band_w = [max(need[l] + 2 * LANE_PAD, MIN_LANE) for l in range(nl)]
    band_lo = [sum(band_w[:l]) for l in range(nl)]

    for L in layers:
        for l in range(nl):
            g = group(L, l)
            if not g:
                continue
            tot = N[g[0]].so / 2 + N[g[-1]].so / 2 + sum(sep(N[a], N[b]) for a, b in zip(g, g[1:]))
            c = band_lo[l] + (band_w[l] - tot) / 2 + N[g[0]].so / 2
            N[g[0]].o = c
            for a, b in zip(g, g[1:]):
                c += sep(N[a], N[b]); N[b].o = c

    def place(g, desired, lo, hi):
        blocks = []  # [nodes, offsets]
        for k in g:
            blk = {"n": [k], "off": [0.0]}
            blk["pos"] = desired[k]
            blocks.append(blk)
            while len(blocks) > 1:
                A, B = blocks[-2], blocks[-1]
                need_gap = sep(N[A["n"][-1]], N[B["n"][0]])
                if A["pos"] + A["off"][-1] + need_gap <= B["pos"] + 1e-6:
                    break
                base = A["off"][-1] + need_gap
                A["n"] += B["n"]; A["off"] += [base + x for x in B["off"]]
                A["pos"] = sum(desired[n] - o for n, o in zip(A["n"], A["off"])) / len(A["n"])
                blocks.pop()
        cs = []
        for b in blocks:
            for n, o in zip(b["n"], b["off"]):
                cs.append([n, b["pos"] + o])
        for i, it in enumerate(cs):
            mn = lo + N[it[0]].so / 2 if i == 0 else cs[i - 1][1] + sep(N[cs[i - 1][0]], N[it[0]])
            it[1] = max(it[1], mn)
        for i in range(len(cs) - 1, -1, -1):
            mx = hi - N[cs[i][0]].so / 2 if i == len(cs) - 1 else cs[i + 1][1] - sep(N[cs[i][0]], N[cs[i + 1][0]])
            cs[i][1] = min(cs[i][1], mx)
        for n, c in cs:
            N[n].o = c

    for it in range(12):
        mode = ("down", "up", "both")[it % 3]
        rng = list(range(1, R)) if mode == "down" else (list(range(R - 2, -1, -1)) if mode == "up" else list(range(R)))
        for r in rng:
            desired = {}
            for k in layers[r]:
                nb = (seg_pred[k] if mode == "down" else seg_succ[k] if mode == "up" else seg_pred[k] + seg_succ[k])
                desired[k] = sum(N[x].o for x in nb) / len(nb) if nb else N[k].o
            for l in range(nl):
                g = group(layers[r], l)
                if g:
                    place(g, desired, band_lo[l] + LANE_PAD, band_lo[l] + band_w[l] - LANE_PAD)

    # nắn thẳng: node chỉ có 1 cha / 1 con lệch nhẹ thì kéo về thẳng hàng nếu không chồng lấn
    for _ in range(3):
        for r in list(range(1, R)) + list(range(R - 2, -1, -1)):
            for l in range(nl):
                g = group(layers[r], l)
                lo_b, hi_b = band_lo[l] + LANE_PAD, band_lo[l] + band_w[l] - LANE_PAD
                for j, k in enumerate(g):
                    cands = []
                    if len(seg_pred[k]) == 1:
                        cands.append(N[seg_pred[k][0]].o)
                    if len(seg_succ[k]) == 1:
                        cands.append(N[seg_succ[k][0]].o)
                    for t in cands:
                        dlt = abs(t - N[k].o)
                        if dlt < 0.5 or dlt > 40:
                            continue
                        ok_lo = (t - N[k].so / 2 >= lo_b - 1e-6) if j == 0 else (t - N[g[j - 1]].o >= sep(N[g[j - 1]], N[k]) - 1e-6)
                        ok_hi = (t + N[k].so / 2 <= hi_b + 1e-6) if j == len(g) - 1 else (N[g[j + 1]].o - t >= sep(N[k], N[g[j + 1]]) - 1e-6)
                        if ok_lo and ok_hi:
                            N[k].o = t
                            break

    # --- toạ độ trục rank + định tuyến (2 lượt: lượt 1 đếm số track/nhãn mỗi khe, lượt 2 dựng thật) ---
    HDR = (42.0 if TB else 140.0) if lanes else 0.0
    BASE_GAP = 46.0 if TB else 52.0
    thick = [max([N[k].sr for k in L if not N[k].dummy] or [0.0]) for L in layers]
    dvec = {"+r": (0, 1) if TB else (1, 0), "-r": (0, -1) if TB else (-1, 0),
            "+o": (1, 0) if TB else (0, 1), "-o": (-1, 0) if TB else (0, -1)}
    polys = {k: shape_geometry(n.type, n.w, n.h)[0] for k, n in N.items() if not n.dummy}
    face_d = {(k, s): _ray(polys[k], *dvec[s]) for k in polys for s in dvec}

    # cạnh ra của decision: cạnh xa nhất hai bên ra từ đỉnh trái/phải (giống draw.io)
    used_side0: Dict[str, set] = {k: set() for k in N}
    exit_side: Dict[int, str] = {}
    for u in order0:
        outs = [e for e in fwd if e["u"] == u]
        for e in outs:
            exit_side[e["i"]] = "+r"
        if N[u].type == "decision" and len(outs) >= 2:
            nxt = sorted(outs, key=lambda e: N[chains[e["i"]][1]].o)
            thr = N[u].so / 2 + 10
            lo_e, hi_e = nxt[0], nxt[-1]
            if N[chains[lo_e["i"]][1]].o < N[u].o - thr:
                exit_side[lo_e["i"]] = "-o"; used_side0[u].add("-o")
            if N[chains[hi_e["i"]][1]].o > N[u].o + thr:
                exit_side[hi_e["i"]] = "+o"; used_side0[u].add("+o")
    bottom_out = {k: sum(1 for e in fwd if e["u"] == k and exit_side[e["i"]] == "+r") for k in N}
    fan_in = {k: sum(1 for e in fwd if e["v"] == k) for k in N}

    # kích thước nhãn cạnh (cần để chừa chỗ trong khe)
    lab_dim: Dict[int, Tuple[List[str], float, float]] = {}
    for e in E:
        if e["label"]:
            ls = wrap_text(e["label"], 120, EFS, "sans_bold")
            lab_dim[e["i"]] = (ls, max(text_w(s, EFS, "sans_bold") for s in ls) + 12, len(ls) * ELH + 6)
    lab_ext = [0.0] * R
    for e in fwd:
        if e["label"] and N[e["u"]].type == "decision" and exit_side[e["i"]] == "+r":
            _, lw_, lh_ = lab_dim[e["i"]]
            g = N[e["u"]].rank
            lab_ext[g] = max(lab_ext[g], (lh_ + 10) if TB else (lw_ + 14))

    def assign_r(ntr):
        r_start = [0.0] * R
        gaps = [0.0] * R
        cur = (HDR + 26.0) if lanes else 0.0
        for r in range(R):
            r_start[r] = cur
            need = 22 + 10 * max(0, ntr[r] - 1) + lab_ext[r] + (12 if lab_ext[r] else 0)
            gaps[r] = max(BASE_GAP, need)
            cur += thick[r] + gaps[r]
        return r_start, gaps, cur - gaps[-1]

    def route(r_start, gaps):
        for L in layers:
            for k in L:
                N[k].r = r_start[N[k].rank] + thick[N[k].rank] / 2

        def face(k, side):
            n, d = N[k], face_d[(k, side)]
            if side in ("+r", "-r"):
                return (n.r + (d if side == "+r" else -d), n.o)
            return (n.r, n.o + (d if side == "+o" else -d))

        used_side = {k: set(v) for k, v in used_side0.items()}
        plans: Dict[int, list] = {}
        gap_keys: Dict[int, Dict[tuple, list]] = {}
        for e in fwd:
            ch = chains[e["i"]]
            u, v = ch[0], ch[-1]
            side = exit_side[e["i"]]
            F = face(u, side)
            plan = [("P", F)]
            cur_o = F[1]
            if side != "+r":
                plan.append(("P", (F[0], N[ch[1]].o))); cur_o = N[ch[1]].o
            for idx, k in enumerate(ch[1:]):
                is_t = k == v
                W = face(v, "-r") if is_t else (N[k].r, N[k].o)
                if abs(W[1] - cur_o) > 0.5:
                    g = N[k].rank - 1
                    if idx == 0 and side == "+r" and bottom_out[u] > 1:
                        key = ("s", u)
                    elif is_t and fan_in[v] > 1:
                        key = ("t", v)
                    else:
                        key = ("e", e["i"], idx)
                    plan.append(("J", g, key, cur_o, W[1]))
                    gap_keys.setdefault(g, {}).setdefault(key, []).extend([cur_o, W[1]])
                plan.append(("P", W))
                cur_o = W[1]
            plans[e["i"]] = plan
        ntr = [len(gap_keys.get(g, {})) for g in range(R)]
        track: Dict[Tuple[int, tuple], float] = {}
        for g, keys in gap_keys.items():
            ks = sorted(keys, key=lambda k: sum(keys[k]) / len(keys[k]))
            a = r_start[g] + thick[g]
            b = r_start[g + 1] if g + 1 < R else a + gaps[g]
            if lab_ext[g]:
                # bus của decision: track sớm, nhãn đặt SAU điểm tách; track khác: đặt SAU vùng nhãn
                early = [k for k in ks if k[0] == "s" and N[k[1]].type == "decision"]
                late = [k for k in ks if k not in early]
                for j, k in enumerate(early):
                    track[(g, k)] = a + 12 + 10 * j
                for j, k in enumerate(late):
                    track[(g, k)] = a + lab_ext[g] + 12 + 10 * j
            else:
                for j, k in enumerate(ks):
                    track[(g, k)] = a + (b - a) * (j + 1) / (len(ks) + 1)
        routes: Dict[int, list] = {}
        anchors: Dict[int, tuple] = {}
        for e in fwd:
            pts, first_j = [], None
            for st in plans[e["i"]]:
                if st[0] == "P":
                    pts.append(st[1])
                else:
                    _, g, key, o1, o2 = st
                    rt = track[(g, key)]
                    pts += [(rt, o1), (rt, o2)]
                    if first_j is None:
                        first_j = (rt, o2)
            routes[e["i"]] = pts
            u = e["u"]
            if N[u].type == "decision" and exit_side[e["i"]] == "+r":
                bus = track.get((N[u].rank, ("s", u)))
                if bus is not None and first_j is not None and len(pts) > 1 and abs(pts[1][0] - bus) < 0.5:
                    anchors[e["i"]] = first_j                     # nhánh rẽ khỏi bus: nhãn sau điểm tách
                elif bus is not None:
                    anchors[e["i"]] = (bus, pts[0][1])            # nhánh thẳng nhưng chung bus
                else:
                    anchors[e["i"]] = pts[0]
        # back edges: chạy vòng qua kênh bên cạnh
        side_count = {"+o": 0, "-o": 0}
        below_count: Dict[int, int] = {}
        for e in E:
            if e["i"] not in back:
                continue
            u, v = e["u"], e["v"]
            ru, rv = N[u].rank, N[v].rank
            if ru == rv:
                k = below_count.get(ru, 0); below_count[ru] = k + 1
                yb = r_start[ru] + thick[ru] + 14 + 9 * k
                Fu, Fv = face(u, "+r"), face(v, "+r")
                routes[e["i"]] = [Fu, (yb, Fu[1]), (yb, Fv[1]), Fv]
                continue
            rng_nodes = [n for n in N.values() if min(ru, rv) <= n.rank <= max(ru, rv)]
            ext_p = max(n.o + n.so / 2 for n in rng_nodes)
            ext_m = min(n.o - n.so / 2 for n in rng_nodes)
            cost_p = (ext_p - N[u].o) + (ext_p - N[v].o) + (1e4 if "+o" in used_side[u] else 0) + side_count["+o"] * 30
            cost_m = (N[u].o - ext_m) + (N[v].o - ext_m) + (1e4 if "-o" in used_side[u] else 0) + side_count["-o"] * 30
            s = "+o" if cost_p <= cost_m else "-o"
            k = side_count[s]; side_count[s] += 1
            och = ext_p + 28 + 16 * k if s == "+o" else ext_m - 28 - 16 * k
            Fu, Fv = face(u, s), face(v, s)
            used_side[u].add(s); used_side[v].add(s)
            routes[e["i"]] = [Fu, (Fu[0], och), (Fv[0], och), Fv]
        return routes, anchors, ntr

    r_start, gaps, r_end_all = assign_r([0] * R)
    _, _, ntr = route(r_start, gaps)
    r_start, gaps, r_end_all = assign_r(ntr)
    routes, anchors, _ = route(r_start, gaps)

    # --- chuyển sang x,y ---
    def xy(p):
        return (p[1], p[0]) if TB else (p[0], p[1])

    for n in N.values():
        n.x, n.y = xy((n.r, n.o))
    lane_rects = []
    if lanes:
        all_o = [n.o - n.so / 2 for n in N.values()] + [n.o + n.so / 2 for n in N.values()]
        for pts in routes.values():
            all_o += [p[1] for p in pts]
        lo0 = min(band_lo[0], min(all_o) - 18)
        hiN = max(band_lo[-1] + band_w[-1], max(all_o) + 18)
        r0, r1 = 0.0, r_end_all + 26
        for pts in routes.values():
            r1 = max(r1, max(p[0] for p in pts) + 18)
        for l, nm in enumerate(lanes):
            o_a = lo0 if l == 0 else band_lo[l]
            o_b = hiN if l == nl - 1 else band_lo[l] + band_w[l]
            if TB:
                rect = (o_a, r0, o_b - o_a, r1 - r0); head = (o_a, r0, o_b - o_a, HDR)
                hl = wrap_text(nm, (o_b - o_a) - 20, 13, "sans_bold")
            else:
                rect = (r0, o_a, r1 - r0, o_b - o_a); head = (r0, o_a, HDR, o_b - o_a)
                hl = wrap_text(nm, HDR - 24, 13, "sans_bold")
            lane_rects.append({"name": nm, "rect": rect, "head": head, "lines": hl, "alt": l % 2 == 1})

    edges_out = []
    for e in E:
        if e["i"] not in routes:
            continue
        raw = _simplify([xy(p) for p in routes[e["i"]]])
        if len(raw) < 2:
            continue
        a, b = raw[-2], raw[-1]
        L = math.dist(a, b) or 1
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        AL, AW = 9.0, 7.0
        base = (b[0] - ux * AL, b[1] - uy * AL)
        arrow = [b, (base[0] - uy * AW / 2, base[1] + ux * AW / 2), (base[0] + uy * AW / 2, base[1] - ux * AW / 2)]
        raw_draw = raw[:-1] + [(base[0] + ux * 0.5, base[1] + uy * 0.5)]
        pts = _round_poly(raw_draw, 9)
        lab = None
        if e["label"]:
            lines = wrap_text(e["label"], 120, EFS, "sans_bold")
            lw = max(text_w(s, EFS, "sans_bold") for s in lines) + 12
            lh = len(lines) * ELH + 6
            if e["i"] in anchors:
                ax, ay = xy(anchors[e["i"]])
                if TB:
                    cx, cy = ax + lw / 2 + 6, ay + lh / 2 + 6
                else:
                    cx, cy = ax + lw / 2 + 8, ay - lh / 2 - 3
            elif N[e["u"]].type == "decision":
                p0, p1 = raw[0], raw[1]
                horiz = abs(p1[1] - p0[1]) < 0.5
                sgn = 1 if (p1[0] - p0[0] if horiz else p1[1] - p0[1]) >= 0 else -1
                if horiz:
                    cx, cy = p0[0] + sgn * (lw / 2 + 8), p0[1] - lh / 2 - 3
                else:
                    cx, cy = p0[0] + lw / 2 + 6, p0[1] + sgn * (lh / 2 + 6)
            else:
                segs = [(raw[i], raw[i + 1]) for i in range(len(raw) - 1)]
                sa, sb = max(segs, key=lambda s: math.dist(*s))
                cx, cy = (sa[0] + sb[0]) / 2, (sa[1] + sb[1]) / 2
            lab = {"lines": lines, "x": cx, "y": cy, "w": lw, "h": lh, "tone": edge_label_tone(e["label"])}
        edges_out.append({"i": e["i"], "u": e["u"], "v": e["v"], "back": e["i"] in back, "style": e["style"],
                          "raw": raw, "pts": pts, "len": _plen(pts), "arrow": arrow, "label": lab})

    # --- khung bao & dịch toạ độ ---
    xs, ys = [], []
    for n in N.values():
        if not n.dummy:
            xs += [n.x - n.w / 2, n.x + n.w / 2]; ys += [n.y - n.h / 2, n.y + n.h / 2]
    for e in edges_out:
        xs += [p[0] for p in e["raw"]]; ys += [p[1] for p in e["raw"]]
        if e["label"]:
            lb = e["label"]
            xs += [lb["x"] - lb["w"] / 2, lb["x"] + lb["w"] / 2]; ys += [lb["y"] - lb["h"] / 2, lb["y"] + lb["h"] / 2]
    for lr in lane_rects:
        x, y, w, h = lr["rect"]; xs += [x, x + w]; ys += [y, y + h]
    M = 28.0
    dx, dy = M - min(xs), M - min(ys)
    W, H = max(xs) + dx + M, max(ys) + dy + M

    def mv(p):
        return (p[0] + dx, p[1] + dy)

    STEP = 0.32
    nodes_out = []
    for k in order0:
        n = N[k]
        poly, extra = shape_geometry(n.type, n.w, n.h)
        cx, cy = n.x + dx, n.y + dy
        nodes_out.append({"id": n.id, "type": n.type, "tone": n.tone, "label": n.label, "lines": n.lines,
                          "x": cx, "y": cy, "w": n.w, "h": n.h, "tdy": n.tdy, "rank": n.rank,
                          "poly": [(cx + px, cy + py) for px, py in poly],
                          "extra": [[(cx + px, cy + py) for px, py in pl] for pl in extra],
                          "delay": round(0.15 + n.rank * STEP, 3)})
    nd = {n["id"]: n for n in nodes_out}
    t_main = max(n["delay"] for n in nodes_out) + 0.45
    kb = 0
    for e in edges_out:
        e["raw"] = [mv(p) for p in e["raw"]]; e["pts"] = [mv(p) for p in e["pts"]]
        e["arrow"] = [mv(p) for p in e["arrow"]]
        if e["label"]:
            e["label"]["x"] += dx; e["label"]["y"] += dy
        if e["back"]:
            e["start"] = round(t_main + 0.1 + 0.15 * kb, 3); e["dur"] = 0.6; kb += 1
        else:
            e["start"] = round(nd[e["u"]]["delay"] + 0.2, 3)
            e["dur"] = round(max(0.25, nd[e["v"]]["delay"] - e["start"] + 0.05), 3)
    for lr in lane_rects:
        x, y, w, h = lr["rect"]; lr["rect"] = (x + dx, y + dy, w, h)
        x, y, w, h = lr["head"]; lr["head"] = (x + dx, y + dy, w, h)
    build_end = max([t_main] + [e["start"] + e["dur"] for e in edges_out]) + 0.3
    return Layout(direction, W, H, nodes_out, edges_out, lane_rects, round(build_end, 3),
                  spec.get("title", ""), spec.get("subtitle", ""))


def auto_layout(spec: dict, direction: str = "auto", target_ratio: float = 16 / 9) -> Layout:
    d = (direction or "auto").upper()
    if d in ("TB", "LR"):
        return compute_layout(spec, d)
    cands = [compute_layout(spec, "TB"), compute_layout(spec, "LR")]
    return min(cands, key=lambda L: abs(math.log((L.width / L.height) / target_ratio)) + (0.05 if L.direction == "LR" else 0))


# -----------------------------------------------------------------------------
# 9. RENDER SVG / HTML
# -----------------------------------------------------------------------------
def _esc(s) -> str:
    return _html.escape(str(s), quote=True)


def _f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _pts_d(pts, close=False) -> str:
    d = "M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in pts)
    return d + (" Z" if close else "")


def _label_colors(theme, tone):
    if tone == "red":
        return theme["red"], theme["red_soft"]
    if tone == "green":
        return theme["green"], theme["green_soft"]
    return theme["gold_deep"], theme["card"]


def render_svg(lay: Layout, theme: Dict[str, str], animated: bool = True, flow_speed: float = 0.9) -> str:
    th = theme
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_f(lay.width)} {_f(lay.height)}" '
         f'width="{_f(lay.width)}" height="{_f(lay.height)}" style="max-width:{_f(lay.width)}px" font-family="{_esc(FONT_STACK)}" '
         f'class="fc{" anim" if animated else ""}" role="img" aria-label="{_esc(lay.title)}">']
    o.append('<defs><filter id="fcsh" x="-20%" y="-20%" width="140%" height="160%">'
             f'<feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="{th["shadow"]}" flood-opacity="0.13"/></filter></defs>')
    o.append(f'<rect width="100%" height="100%" fill="{th["card"]}"/>')
    # lanes
    for lr in lay.lanes:
        x, y, w, h = lr["rect"]
        o.append(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" fill="{th["lane_alt"] if lr["alt"] else th["card"]}" '
                 f'stroke="{th["lane_line"]}" stroke-width="1"/>')
        hx, hy, hw, hh = lr["head"]
        o.append(f'<rect x="{_f(hx)}" y="{_f(hy)}" width="{_f(hw)}" height="{_f(hh)}" fill="{th["lane_head"]}" stroke="{th["lane_line"]}" stroke-width="1"/>')
        n = len(lr["lines"])
        for i, s in enumerate(lr["lines"]):
            ty = hy + hh / 2 + (i - (n - 1) / 2) * 16
            o.append(f'<text x="{_f(hx + hw / 2)}" y="{_f(ty)}" text-anchor="middle" dominant-baseline="central" font-size="13" '
                     f'font-weight="700" letter-spacing="0.4" fill="{th["gold_deep"]}">{_esc(s)}</text>')
    # edges
    for e in lay.edges:
        d = _pts_d(e["pts"])
        dash = ' stroke-dasharray="6 5"' if (e["back"] or e["style"] == "dashed") else (' stroke-dasharray="2 4"' if e["style"] == "dotted" else "")
        L = e["len"]
        if animated:
            o.append(f'<g class="edge" style="--d:{e["start"]}s;--dur:{e["dur"]}s;--len:{_f(L + 2)};--ad:{_f(e["start"] + e["dur"] - 0.05)}s">')
            cls = "e-fade" if dash else "e-base"
            o.append(f'<path class="{cls}" d="{d}" fill="none" stroke="{th["edge"]}" stroke-width="1.6" stroke-linejoin="round"{dash}/>')
            o.append(f'<path class="e-flow" d="{d}" fill="none" stroke="{th["gold"]}" stroke-width="2.2" stroke-linecap="round" '
                     f'stroke-dasharray="5 13" style="--fb:{lay.build_end}s;animation-duration:{flow_speed}s,0.4s"/>')
        else:
            o.append('<g>')
            o.append(f'<path d="{d}" fill="none" stroke="{th["edge"]}" stroke-width="1.6" stroke-linejoin="round"{dash}/>')
        o.append(f'<path class="arrow" d="{_pts_d(e["arrow"], True)}" fill="{th["edge_strong"]}"/>')
        o.append('</g>')
    # tokens
    if animated:
        o.append('<g class="tokens">')
        for e in lay.edges:
            dur = max(0.8, e["len"] / 120.0)
            o.append(f'<circle class="tok" r="3.6" fill="{th["token"]}" stroke="{th["token_ring"]}" stroke-width="1.3" '
                     f'style="--fb:{lay.build_end}s"><animateMotion dur="{dur:.2f}s" begin="{lay.build_end}s" repeatCount="indefinite" '
                     f'path="{_pts_d(e["pts"])}"/></circle>')
        o.append('</g>')
    # nodes
    for n in lay.nodes:
        c = node_colors(th, n["type"], n["tone"])
        dash = f' stroke-dasharray="{c["dash"][0]} {c["dash"][1]}"' if c["dash"] else ""
        cls = f' class="node" style="--d:{n["delay"]}s"' if animated else ""
        o.append(f'<g{cls} data-id="{_esc(n["id"])}">')
        o.append(f'<path d="{_pts_d(n["poly"], True)}" fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="{c["sw"]}"{dash} filter="url(#fcsh)"/>')
        for pl in n["extra"]:
            o.append(f'<path d="{_pts_d(pl)}" fill="none" stroke="{c["stroke"]}" stroke-width="{c["sw"]}"/>')
        k = len(n["lines"])
        for i, s in enumerate(n["lines"]):
            ty = n["y"] + n["tdy"] + (i - (k - 1) / 2) * LH
            o.append(f'<text x="{_f(n["x"])}" y="{_f(ty)}" text-anchor="middle" dominant-baseline="central" font-size="{FS}" '
                     f'font-weight="{700 if c["bold"] else 500}" fill="{c["text"]}">{_esc(s)}</text>')
        o.append('</g>')
    # edge labels (trên cùng)
    for e in lay.edges:
        lb = e["label"]
        if not lb:
            continue
        fg, bg = _label_colors(th, lb["tone"])
        cls = f' class="elabel" style="--ad:{_f(e["start"] + e["dur"] * 0.5)}s"' if animated else ""
        o.append(f'<g{cls}><rect x="{_f(lb["x"] - lb["w"] / 2)}" y="{_f(lb["y"] - lb["h"] / 2)}" width="{_f(lb["w"])}" height="{_f(lb["h"])}" '
                 f'rx="{_f(min(9, lb["h"] / 2))}" fill="{bg}" stroke="{fg}" stroke-opacity="0.45" stroke-width="1"/>')
        k = len(lb["lines"])
        for i, s in enumerate(lb["lines"]):
            ty = lb["y"] + (i - (k - 1) / 2) * ELH
            o.append(f'<text x="{_f(lb["x"])}" y="{_f(ty)}" text-anchor="middle" dominant-baseline="central" font-size="{EFS}" '
                     f'font-weight="700" fill="{fg}">{_esc(s)}</text>')
        o.append('</g>')
    o.append('</svg>')
    return "\n".join(o)


def _mini_icon(t: str, theme, w=34, h=22) -> str:
    sw, sh = (22, 22) if t == "connector" else (w - 4, h - 4)
    poly, extra = shape_geometry(t, sw, sh)
    c = node_colors(theme, t, "default")
    pts = [(px + w / 2, py + h / 2) for px, py in poly]
    s = f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"><path d="{_pts_d(pts, True)}" fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="1.3"/>'
    for pl in extra:
        s += f'<path d="{_pts_d([(px + w / 2, py + h / 2) for px, py in pl])}" fill="none" stroke="{c["stroke"]}" stroke-width="1.3"/>'
    return s + "</svg>"


_PAGE_CSS = """
:root{--bg:%(page_bg)s;--card:%(card)s;--ink:%(ink)s;--muted:%(muted)s;--rule:%(rule)s;--gold:%(gold)s;--gold-deep:%(gold_deep)s;--gold-soft:%(gold_soft)s}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font-family:%(font)s}
.wrap{max-width:1500px;margin:0 auto;padding:28px 24px 36px}
header{display:flex;flex-wrap:wrap;gap:16px 24px;align-items:flex-end;justify-content:space-between;padding-bottom:18px;border-bottom:1px solid var(--rule);margin-bottom:22px}
.kicker{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);font-weight:700}
h1{font-family:%(serif)s;font-weight:600;font-size:clamp(24px,3.2vw,38px);line-height:1.15;margin:6px 0 4px;letter-spacing:.01em}
.sub{color:var(--muted);font-size:14px;margin:0}
.tools{display:flex;flex-wrap:wrap;gap:8px}
.tools button,.tools a{font:inherit;font-size:13px;font-weight:600;color:var(--gold-deep);background:transparent;border:1px solid var(--gold);border-radius:999px;padding:7px 14px;cursor:pointer;text-decoration:none;transition:background .2s,color .2s}
.tools button:hover,.tools a:hover{background:var(--gold);color:var(--card)}
.card{background:var(--card);border:1px solid var(--rule);border-radius:16px;padding:14px;overflow:auto;box-shadow:0 18px 40px -28px rgba(60,40,10,.35)}
.card svg{display:block;width:100%%;height:auto;margin:0 auto}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:16px;color:var(--muted);font-size:12.5px;align-items:center}
.legend span{display:inline-flex;align-items:center;gap:6px}
footer{margin-top:18px;color:var(--muted);font-size:12px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
.anim .node{opacity:0;transform-box:fill-box;transform-origin:center;animation:fcPop .5s cubic-bezier(.2,.8,.2,1) forwards;animation-delay:var(--d)}
.anim .e-base{stroke-dasharray:var(--len);stroke-dashoffset:var(--len);animation:fcDraw var(--dur) ease-in-out forwards;animation-delay:var(--d)}
.anim .e-fade{opacity:0;animation:fcFade .5s forwards;animation-delay:var(--d)}
.anim .arrow,.anim .elabel{opacity:0;animation:fcFade .3s forwards;animation-delay:var(--ad)}
.anim .e-flow{opacity:0;animation-name:fcFlow,fcFade;animation-timing-function:linear,ease;animation-iteration-count:infinite,1;animation-fill-mode:none,forwards;animation-delay:var(--fb),var(--fb)}
.anim .tok{opacity:0;animation:fcFade .4s forwards;animation-delay:var(--fb)}
.anim.paused *{animation-play-state:paused!important}
@keyframes fcPop{from{opacity:0;transform:translateY(6px) scale(.92)}to{opacity:1;transform:none}}
@keyframes fcDraw{to{stroke-dashoffset:0}}
@keyframes fcFade{to{opacity:1}}
@keyframes fcFlow{to{stroke-dashoffset:-18}}
@media (prefers-reduced-motion:reduce){.anim *{animation:none!important;opacity:1!important;stroke-dashoffset:0!important}.anim .tok,.anim .e-flow{display:none}}
@media print{.tools{display:none}.card{box-shadow:none}}
"""

_PAGE_JS = """
(function(){
  var stage=document.getElementById('stage'),fresh=stage.innerHTML;
  function svg(){return stage.querySelector('svg')}
  document.getElementById('replay').onclick=function(){stage.innerHTML=fresh;pb.textContent='⏸ Dừng';};
  var pb=document.getElementById('pause');
  pb.onclick=function(){var s=svg();if(!s)return;var p=s.classList.toggle('paused');
    try{p?s.pauseAnimations():s.unpauseAnimations()}catch(e){}
    pb.textContent=p?'▶ Chạy':'⏸ Dừng';};
  document.getElementById('dlpng').onclick=function(){
    var a=document.getElementById('dlsvg'),img=new Image();
    img.onload=function(){var k=2,c=document.createElement('canvas');c.width=img.width*k;c.height=img.height*k;
      var x=c.getContext('2d');x.scale(k,k);x.drawImage(img,0,0);
      c.toBlob(function(b){var u=URL.createObjectURL(b),l=document.createElement('a');l.href=u;l.download=a.getAttribute('download').replace(/\\.svg$/,'.png');
        document.body.appendChild(l);l.click();setTimeout(function(){URL.revokeObjectURL(u);l.remove()},500)});};
    img.src=a.href;};
})();
"""


def render_html(lay: Layout, theme: Dict[str, str], file_stub: str = "flowchart") -> Tuple[str, str]:
    """Trả về (html, svg_tĩnh)."""
    svg_anim = render_svg(lay, theme, animated=True)
    svg_static = render_svg(lay, theme, animated=False)
    used = []
    for n in lay.nodes:
        if n["type"] not in used:
            used.append(n["type"])
    legend = "".join(f'<span>{_mini_icon(t, theme)}{_esc(SHAPES[t]["vi"])}</span>' for t in SHAPE_ORDER if t in used)
    css = _PAGE_CSS % {**theme, "font": FONT_STACK, "serif": SERIF_STACK}
    svg_b64 = base64.b64encode(svg_static.encode("utf-8")).decode()
    now = _dt.datetime.now().strftime("%d/%m/%Y %H:%M")
    page = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(lay.title or 'Flowchart')}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
<header>
  <div>
    <div class="kicker">Quy trình · Flowchart</div>
    <h1>{_esc(lay.title)}</h1>
    {f'<p class="sub">{_esc(lay.subtitle)}</p>' if lay.subtitle else ''}
  </div>
  <div class="tools">
    <button id="replay" type="button">↻ Phát lại</button>
    <button id="pause" type="button">⏸ Dừng</button>
    <a id="dlsvg" download="{_esc(file_stub)}.svg" href="data:image/svg+xml;base64,{svg_b64}">Tải SVG</a>
    <button id="dlpng" type="button">Tải PNG</button>
  </div>
</header>
<div class="card" id="stage">
{svg_anim}
</div>
<div class="legend"><strong style="color:var(--gold-deep)">Chú giải</strong>{legend}</div>
<footer><span>{len(lay.nodes)} bước · {len(lay.edges)} luồng · hướng {lay.direction}</span><span>Tạo bởi Flowchart Agent · {now}</span></footer>
</div>
<script>{_PAGE_JS}</script>
</body>
</html>"""
    return page, svg_static


# -----------------------------------------------------------------------------
# 10. RENDER GIF (Pillow) – cùng hình học với SVG, khử răng cưa bằng supersampling
# -----------------------------------------------------------------------------
def _hex(c: str, a: int = 255):
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


def _cut(pts, d):
    if d <= 0:
        return [pts[0]]
    out = [pts[0]]
    acc = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L = math.dist(a, b)
        if acc + L >= d:
            u = (d - acc) / L if L else 0
            out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            return out
        out.append(b); acc += L
    return out


def _point_at(pts, d):
    acc = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L = math.dist(a, b)
        if acc + L >= d:
            u = (d - acc) / L if L else 0
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        acc += L
    return pts[-1]


def _sub(pts, a, b):
    """Đoạn polyline từ độ dài a đến b."""
    out = [_point_at(pts, a)]
    acc = 0.0
    for i in range(len(pts) - 1):
        acc += math.dist(pts[i], pts[i + 1])
        if a < acc < b:
            out.append(pts[i + 1])
    out.append(_point_at(pts, b))
    return out


def _dashes(pts, on, off, offset):
    """Các đoạn nét đứt dọc polyline; offset âm dần → nét chạy theo chiều cạnh."""
    total = _plen(pts)
    period = on + off
    out = []
    s = -(offset % period)
    while s < total:
        a, b = max(0.0, s), min(total, s + on)
        if b > a + 0.3:
            out.append(_sub(pts, a, b))
        s += period
    return out


def render_gif(lay: Layout, theme: Dict[str, str], path: str, mode: str = "build_flow", width: Optional[int] = None,
               aspect: Optional[str] = "auto", show_title: bool = True, fps: int = 15, flow_seconds: float = 2.7,
               hold_seconds: float = 2.5, ss: int = 2, log: Callable = print) -> str:
    """mode  : 'build_flow' (dựng dần rồi chảy), 'flow' (vòng lặp chảy liền mạch), 'build' (dựng dần rồi đứng yên).
    aspect: 'auto' (khung ôm sát sơ đồ, tỉ lệ 1:1 → 2.6:1, chữ giữ ~cỡ thật) | '16:9' | '4:3' | None (đúng tỉ lệ sơ đồ).
    width : None = tự chọn (1280–2400px); hoặc số px cố định."""
    from PIL import Image, ImageDraw, ImageFilter
    RES = getattr(Image, "Resampling", Image).LANCZOS
    th = theme
    t0 = time.time()
    title_h = (78 if lay.subtitle else 58) if show_title and lay.title else 0
    m = 28
    cw, ch = lay.width, lay.height + title_h
    if aspect and aspect != "auto":
        a, b = [float(x) for x in aspect.split(":")]
        FW = int(width or 1920)
        FH = int(round(FW * b / a))
    else:
        FW0, FH0 = cw + 2 * m, ch + 2 * m
        if aspect == "auto":
            ratio = FW0 / FH0
            if ratio < 1.0:
                FW0 = FH0 * 1.0
            elif ratio > 2.6:
                FH0 = FW0 / 2.6
        if width:
            k = width / FW0
        else:
            k = min(1.0, 2400 / max(FW0, FH0))
            if FW0 * k < 1280:
                k = min(1.6, 1280 / FW0)
        FW, FH = int(round(FW0 * k)), int(round(FH0 * k))
    S = min(FW / (cw + 2 * m), FH / (ch + 2 * m))
    ox = (FW - cw * S) / 2
    oy_t = (FH - ch * S) / 2
    oy = oy_t + title_h * S
    if S < 0.6:
        log(f"[gif] ⚠ Sơ đồ lớn, chữ trong GIF sẽ nhỏ (scale {S:.2f}). Tăng gif_width hoặc bỏ aspect.")

    def T(p, k=1.0):
        return ((ox + p[0] * S) * k, (oy + p[1] * S) * k)

    bg = _hex(th["card"])
    # ---------- base: nền + lanes + tiêu đề ----------
    big = Image.new("RGBA", (FW * ss, FH * ss), bg)
    dr = ImageDraw.Draw(big)
    for lr in lay.lanes:
        x, y, w, h = lr["rect"]
        p0, p1 = T((x, y), ss), T((x + w, y + h), ss)
        dr.rectangle([p0, p1], fill=_hex(th["lane_alt"] if lr["alt"] else th["card"]), outline=_hex(th["lane_line"]), width=max(1, int(S * ss)))
        hx, hy, hw, hh = lr["head"]
        q0, q1 = T((hx, hy), ss), T((hx + hw, hy + hh), ss)
        dr.rectangle([q0, q1], fill=_hex(th["lane_head"]), outline=_hex(th["lane_line"]), width=max(1, int(S * ss)))
    base = big.resize((FW, FH), RES)
    d1 = ImageDraw.Draw(base)
    for lr in lay.lanes:
        hx, hy, hw, hh = lr["head"]
        f = get_font(13 * S, "sans_bold")
        n = len(lr["lines"])
        for i, s in enumerate(lr["lines"]):
            d1.text(T((hx + hw / 2, hy + hh / 2 + (i - (n - 1) / 2) * 16)), s, font=f, fill=_hex(th["gold_deep"]), anchor="mm")
    if title_h:
        tx, ty = ox, oy_t
        d1.text((tx, ty + 2 * S), lay.title, font=get_font(26 * S, "serif_bold"), fill=_hex(th["ink"]), anchor="la")
        if lay.subtitle:
            d1.text((tx, ty + 38 * S), lay.subtitle, font=get_font(13.5 * S, "sans"), fill=_hex(th["muted"]), anchor="la")
        ry = ty + (title_h - 10) * S
        d1.line([(tx, ry), (tx + 64 * S, ry)], fill=_hex(th["gold"]), width=max(2, int(2 * S)))

    # ---------- sprites: node & nhãn cạnh ----------
    def node_sprite(n):
        c = node_colors(th, n["type"], n["tone"])
        pad = 12
        x0, y0 = n["x"] - n["w"] / 2 - pad, n["y"] - n["h"] / 2 - pad
        Wp, Hp = int(math.ceil((n["w"] + 2 * pad) * S)), int(math.ceil((n["h"] + 2 * pad) * S))
        px0, py0 = T((x0, y0))
        ix, iy = int(math.floor(px0)), int(math.floor(py0))
        fx, fy = px0 - ix, py0 - iy

        def loc(p):
            return (((p[0] - x0) * S + fx) * ss, ((p[1] - y0) * S + fy) * ss)
        Wp += 2; Hp += 2
        im = Image.new("RGBA", (Wp * ss, Hp * ss), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        poly = [loc(p) for p in n["poly"]]
        # bóng mềm
        sh = Image.new("L", im.size, 0)
        ImageDraw.Draw(sh).polygon([(x, y + 2 * S * ss) for x, y in poly], fill=int(255 * 0.16))
        sh = sh.filter(ImageFilter.GaussianBlur(3 * S * ss))
        shadow = Image.new("RGBA", im.size, _hex(th["shadow"]))
        shadow.putalpha(sh)
        im = Image.alpha_composite(im, shadow)
        dd = ImageDraw.Draw(im)
        dd.polygon(poly, fill=_hex(c["fill"]))
        lw = max(1, int(round(c["sw"] * S * ss)))
        if c["dash"]:
            for seg in _dashes(poly + [poly[0]], c["dash"][0] * S * ss, c["dash"][1] * S * ss, 0):
                if len(seg) >= 2:
                    dd.line(seg, fill=_hex(c["stroke"]), width=lw, joint="curve")
        else:
            dd.line(poly + [poly[0], poly[1]], fill=_hex(c["stroke"]), width=lw, joint="curve")
        for pl in n["extra"]:
            dd.line([loc(p) for p in pl], fill=_hex(c["stroke"]), width=lw, joint="curve")
        im = im.resize((Wp, Hp), RES)
        dt = ImageDraw.Draw(im)
        f = get_font(FS * S, "sans_bold" if c["bold"] else "sans")
        k = len(n["lines"])
        for i, s in enumerate(n["lines"]):
            p = (n["x"], n["y"] + n["tdy"] + (i - (k - 1) / 2) * LH)
            q = ((p[0] - x0) * S + fx, (p[1] - y0) * S + fy)
            dt.text(q, s, font=f, fill=_hex(c["text"]), anchor="mm")
        return im, (ix, iy)

    def label_sprite(lb):
        fg, bgc = _label_colors(th, lb["tone"])
        x0, y0 = lb["x"] - lb["w"] / 2 - 2, lb["y"] - lb["h"] / 2 - 2
        px0, py0 = T((x0, y0))
        ix, iy = int(math.floor(px0)), int(math.floor(py0))
        fx, fy = px0 - ix, py0 - iy
        Wp, Hp = int(math.ceil((lb["w"] + 4) * S)) + 2, int(math.ceil((lb["h"] + 4) * S)) + 2
        im = Image.new("RGBA", (Wp * ss, Hp * ss), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        r0 = ((2 * S + fx) * ss, (2 * S + fy) * ss)
        r1 = (r0[0] + lb["w"] * S * ss, r0[1] + lb["h"] * S * ss)
        fga = _hex(fg, 115)
        dd.rounded_rectangle([r0, r1], radius=min(9, lb["h"] / 2) * S * ss, fill=_hex(bgc), outline=fga, width=max(1, int(S * ss)))
        im = im.resize((Wp, Hp), RES)
        dt = ImageDraw.Draw(im)
        f = get_font(EFS * S, "sans_bold")
        k = len(lb["lines"])
        for i, s in enumerate(lb["lines"]):
            q = ((lb["x"] - x0) * S + fx, (lb["y"] + (i - (k - 1) / 2) * ELH - y0) * S + fy)
            dt.text(q, s, font=f, fill=_hex(fg), anchor="mm")
        return im, (ix, iy)

    nsp = [node_sprite(n) for n in lay.nodes]
    lsp = {e["i"]: label_sprite(e["label"]) for e in lay.edges if e["label"]}

    # vùng bao cạnh (để vẽ lớp động nhỏ gọn)
    exs = [T(p) for e in lay.edges for p in e["pts"] + e["arrow"]]
    if exs:
        bx0 = max(0, int(min(p[0] for p in exs)) - 8); by0 = max(0, int(min(p[1] for p in exs)) - 8)
        bx1 = min(FW, int(max(p[0] for p in exs)) + 9); by1 = min(FH, int(max(p[1] for p in exs)) + 9)
    else:
        bx0, by0, bx1, by1 = 0, 0, FW, FH
    BW, BH = max(1, bx1 - bx0), max(1, by1 - by0)

    def E2(p):
        q = T(p)
        return ((q[0] - bx0) * ss, (q[1] - by0) * ss)

    lw_base = max(1, int(round(1.6 * S * ss)))
    lw_flow = max(1, int(round(2.3 * S * ss)))
    edge_col, arrow_col, gold = _hex(th["edge"]), _hex(th["edge_strong"]), _hex(th["gold"])

    def edge_layer(progress: Dict[int, float], flow_phase: Optional[float], tok_phase: Optional[Dict[int, float]], draw_base=True):
        im = Image.new("RGBA", (BW * ss, BH * ss), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        for e in lay.edges:
            p = progress.get(e["i"], 1.0)
            if p <= 0:
                continue
            pts = [E2(q) for q in e["pts"]]
            if draw_base:
                part = _cut(pts, _plen(pts) * p) if p < 1 else pts
                if len(part) >= 2:
                    if e["back"] or e["style"] in ("dashed", "dotted"):
                        on, off = (6, 5) if e["style"] != "dotted" else (2, 4)
                        for seg in _dashes(part, on * S * ss, off * S * ss, 0):
                            if len(seg) >= 2:
                                dd.line(seg, fill=edge_col, width=lw_base, joint="curve")
                    else:
                        dd.line(part, fill=edge_col, width=lw_base, joint="curve")
                if p >= 1:
                    dd.polygon([E2(q) for q in e["arrow"]], fill=arrow_col)
            if flow_phase is not None:
                for seg in _dashes(pts, 5 * S * ss, 13 * S * ss, -flow_phase * 18 * S * ss):
                    if len(seg) >= 2:
                        dd.line(seg, fill=gold, width=lw_flow, joint="curve")
                        r = lw_flow / 2
                        for q in (seg[0], seg[-1]):
                            dd.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=gold)
            if tok_phase is not None:
                L = _plen(pts)
                q = _point_at(pts, L * (tok_phase[e["i"]] % 1.0))
                r1, r2 = 4.9 * S * ss, 3.6 * S * ss
                dd.ellipse([q[0] - r1, q[1] - r1, q[0] + r1, q[1] + r1], fill=_hex(th["token_ring"]))
                dd.ellipse([q[0] - r2, q[1] - r2, q[0] + r2, q[1] + r2], fill=_hex(th["token"]))
        return im.resize((BW, BH), RES)

    def with_alpha(im, a):
        if a >= 0.999:
            return im
        im2 = im.copy()
        im2.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        return im2

    def ease(x):
        x = max(0.0, min(1.0, x))
        return 1 - (1 - x) ** 3

    frames, durs = [], []
    dt_ms = int(round(1000 / fps))

    def compose(edge_img, node_alpha=None, node_dy=None, label_alpha=None, base_img=None):
        fr = (base_img if base_img is not None else base).copy()
        if edge_img is not None:
            fr.alpha_composite(edge_img, (bx0, by0))
        for j, (im, (x, y)) in enumerate(nsp):
            a = 1.0 if node_alpha is None else node_alpha[j]
            if a <= 0:
                continue
            dy = 0 if node_dy is None else int(round(node_dy[j]))
            fr.alpha_composite(with_alpha(im, a), (x, y + dy))
        for e in lay.edges:
            if e["i"] in lsp:
                a = 1.0 if label_alpha is None else label_alpha.get(e["i"], 1.0)
                if a > 0:
                    im, (x, y) = lsp[e["i"]]
                    fr.alpha_composite(with_alpha(im, a), (x, y))
        return fr

    # ---------- pha dựng ----------
    if mode in ("build_flow", "build"):
        T_build = lay.build_end + 0.2
        nfr = int(math.ceil(T_build * fps))
        for fi in range(nfr + 1):
            t = fi / fps
            prog = {e["i"]: max(0.0, min(1.0, (t - e["start"]) / e["dur"])) for e in lay.edges}
            na = [ease((t - n["delay"]) / 0.45) for n in lay.nodes]
            ndy = [(1 - a) * 6 * S for a in na]
            la = {e["i"]: ease((prog[e["i"]] - 0.5) / 0.4) for e in lay.edges}
            frames.append(compose(edge_layer(prog, None, None), na, ndy, la)); durs.append(dt_ms)
    # ---------- pha chảy ----------
    if mode in ("build_flow", "flow"):
        static_edges = edge_layer({}, None, None)
        base_e = base.copy(); base_e.alpha_composite(static_edges, (bx0, by0))
        nfr = int(round(flow_seconds * fps))
        cyc = {}
        for e in lay.edges:
            n_c = max(1, round(flow_seconds * 120.0 / max(e["len"], 1)))
            cyc[e["i"]] = n_c
        flow_period = 0.9
        n_flow = max(1, round(flow_seconds / flow_period))
        for fi in range(nfr):
            u = fi / nfr
            tok = {k: u * c for k, c in cyc.items()}
            dyn = edge_layer({}, u * n_flow, tok, draw_base=False)
            frames.append(compose(dyn, base_img=base_e)); durs.append(dt_ms)
    if mode == "build":
        durs[-1] = int(hold_seconds * 1000)

    # ---------- lượng tử hoá với bảng màu chung & ghi file ----------
    ref = frames[-1].convert("RGB")
    try:
        pal = ref.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    except AttributeError:
        pal = ref.quantize(colors=255, method=0)
    NO_DITHER = getattr(getattr(Image, "Dither", Image), "NONE", 0)
    q = [f.convert("RGB").quantize(palette=pal, dither=NO_DITHER) for f in frames]
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    q[0].save(path, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=False, disposal=1)
    log(f"[gif] {len(q)} khung hình, {FW}×{FH}px, {os.path.getsize(path) / 1e6:.2f} MB ({time.time() - t0:.1f}s)")
    return path


# -----------------------------------------------------------------------------
# 11. CATALOG ENTITY (HTML mẫu các entity – tương đương thư viện draw.io)
# -----------------------------------------------------------------------------
def build_entity_catalog_html(theme_name: str = "wealth_light") -> str:
    th = THEMES[theme_name]
    cards = []
    for t in SHAPE_ORDER:
        meta = SHAPES[t]
        label = "A" if t == "connector" else meta["vi"]
        lines = wrap_text(label, WRAP.get(t, 150), FS, "sans_bold" if t in ("start", "end") else "sans")
        tw = max(text_w(s, FS) for s in lines); w, h, tdy = node_box(t, tw, len(lines) * LH)
        W, H = 250, 130
        poly, extra = shape_geometry(t, w, h)
        c = node_colors(th, t, "default")
        cx, cy = W / 2, H / 2
        dash = f' stroke-dasharray="{c["dash"][0]} {c["dash"][1]}"' if c["dash"] else ""
        s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
             f'<path d="{_pts_d([(cx + x, cy + y) for x, y in poly], True)}" fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="1.6"{dash} filter="url(#sh)"/>']
        for pl in extra:
            s.append(f'<path d="{_pts_d([(cx + x, cy + y) for x, y in pl])}" fill="none" stroke="{c["stroke"]}" stroke-width="1.6"/>')
        k = len(lines)
        for i, ln in enumerate(lines):
            s.append(f'<text x="{cx}" y="{_f(cy + tdy + (i - (k - 1) / 2) * LH)}" text-anchor="middle" dominant-baseline="central" '
                     f'font-size="{FS}" font-weight="{700 if c["bold"] else 500}" fill="{c["text"]}">{_esc(ln)}</text>')
        s.append("</svg>")
        cards.append(f'<article class="ent"><div class="pic">{"".join(s)}</div><div class="meta"><code>{t}</code>'
                     f'<h3>{_esc(meta["vi"])}</h3><div class="dio">draw.io: {_esc(meta["drawio"])}</div><p>{_esc(meta["use"])}</p></div></article>')
    tone_cells = []
    for tone in TONES:
        c = node_colors(th, "process", tone)
        poly, _ = shape_geometry("process", 130, 48)
        dash = f' stroke-dasharray="{c["dash"][0]} {c["dash"][1]}"' if c["dash"] else ""
        tone_cells.append(f'<div class="tone"><svg viewBox="0 0 150 64" width="150" height="64"><path d="{_pts_d([(75 + x, 32 + y) for x, y in poly], True)}" '
                          f'fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="1.6"{dash}/><text x="75" y="32" text-anchor="middle" dominant-baseline="central" '
                          f'font-size="13" font-weight="600" fill="{c["text"]}">tone: {tone}</text></svg></div>')
    sw = "".join(f'<div class="sw"><i style="background:{v}"></i><b>{k}</b><span>{v}</span></div>'
                 for k, v in th.items() if k in ("card", "ink", "muted", "gold", "gold_soft", "gold_deep", "red", "green", "edge", "node_stroke", "lane_head"))
    demo = {"title": "Ví dụ cạnh & nhãn", "lanes": [], "nodes": [
        {"id": "a", "type": "start", "label": "Bắt đầu", "tone": "default", "lane": ""},
        {"id": "b", "type": "decision", "label": "Hợp lệ?", "tone": "default", "lane": ""},
        {"id": "c", "type": "process", "label": "Xử lý tiếp", "tone": "default", "lane": ""},
        {"id": "d", "type": "manual_input", "label": "Bổ sung thông tin", "tone": "default", "lane": ""},
        {"id": "e", "type": "end", "label": "Hoàn tất", "tone": "green", "lane": ""}],
        "edges": [{"from": "a", "to": "b", "label": "", "style": "solid"}, {"from": "b", "to": "c", "label": "Có", "style": "solid"},
                  {"from": "b", "to": "d", "label": "Không", "style": "solid"}, {"from": "d", "to": "b", "label": "", "style": "solid"},
                  {"from": "c", "to": "e", "label": "", "style": "solid"}]}
    demo_svg = render_svg(compute_layout(demo, "LR"), th, animated=True)
    css = _PAGE_CSS % {**th, "font": FONT_STACK, "serif": SERIF_STACK}
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Flowchart Entities</title><style>{css}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:14px}}
.ent{{background:var(--card);border:1px solid var(--rule);border-radius:14px;overflow:hidden;display:flex;flex-direction:column}}
.pic{{display:flex;justify-content:center;padding:6px 0;border-bottom:1px solid var(--rule)}} .pic svg{{max-width:100%;height:auto}}
.meta{{padding:12px 14px 14px}} .meta code{{font-size:12px;color:var(--gold-deep);background:var(--gold-soft);padding:2px 7px;border-radius:6px}}
.meta h3{{margin:8px 0 2px;font-size:15px}} .dio{{font-size:12px;color:var(--gold)}} .meta p{{margin:6px 0 0;font-size:13px;color:var(--muted);line-height:1.45}}
h2{{font-family:{SERIF_STACK};font-weight:600;font-size:22px;margin:30px 0 12px}}
.tones,.sws{{display:flex;flex-wrap:wrap;gap:10px}} .sw{{display:flex;align-items:center;gap:8px;font-size:12px;background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:6px 10px}}
.sw i{{width:22px;height:22px;border-radius:6px;border:1px solid var(--rule)}} .sw span{{color:var(--muted);font-family:ui-monospace,Menlo,monospace}}
</style></head><body><div class="wrap"><header><div><div class="kicker">Thư viện entity · Flowchart Agent</div><h1>Entity mẫu (draw.io flowchart)</h1>
<p class="sub">{len(SHAPES)} loại entity agent được phép dùng. Trường <code>type</code> trong JSON spec phải là một trong các mã dưới đây.</p></div></header>
<div class="grid">{''.join(cards)}</div>
<h2>Tone nhấn mạnh</h2><div class="tones">{''.join(tone_cells)}</div>
<h2>Cạnh, nhãn & vòng lặp</h2><div class="card">{demo_svg}</div>
<h2>Bảng màu ({theme_name})</h2><div class="sws">{sw}</div>
<footer><span>Sinh từ SHAPES / THEMES trong flowchart_agent_lib.py – sửa ở đó để đổi đồng bộ prompt, HTML và GIF.</span></footer>
</div></body></html>"""


# -----------------------------------------------------------------------------
# 12. ORCHESTRATOR
# -----------------------------------------------------------------------------
def slugify(s: str, maxlen: int = 48) -> str:
    s = str(s).replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()
    return (s[:maxlen].strip("_")) or "flowchart"


@dataclass
class AgentResult:
    spec: dict
    layout: Layout
    html_path: str
    gif_path: Optional[str]
    svg_path: str
    json_path: str
    html: str
    warnings: List[str]
    steps: List[AgentStep]


def run_flowchart_agent(context: str = "", llm: Optional[Callable] = None, out_dir: str = "./flowcharts",
                        name: Optional[str] = None, direction: str = "auto", theme: str = "wealth_light",
                        gif_mode: str = "build_flow", gif_width: Optional[int] = None, gif_aspect: Optional[str] = "auto",
                        gif_title: bool = True, previous_spec: Optional[dict] = None, revision: Optional[str] = None,
                        spec: Optional[dict] = None, make_gif: bool = True, log: Callable = print) -> AgentResult:
    if theme not in THEMES:
        raise ValueError(f"theme phải là một trong {list(THEMES)}")
    steps: List[AgentStep] = []
    warnings: List[str] = []
    if spec is None:
        if llm is None:
            raise ValueError("Cần truyền llm (vd DatabricksClaude()) hoặc spec có sẵn.")
        if not (context or "").strip() and not (previous_spec and revision):
            raise ValueError("Context đang trống.")
        spec, warnings, steps = generate_spec(context, llm, previous_spec, revision, log=log)
    else:
        chk = normalize_spec(spec)
        if chk.fatal:
            raise ValueError("Spec không hợp lệ: " + "; ".join(chk.errors))
        spec, warnings = chk.spec, chk.warnings + chk.errors
    lay = auto_layout(spec, direction)
    log(f"[layout] hướng {lay.direction}, {lay.width:.0f}×{lay.height:.0f}px, {len(lay.lanes)} lane")
    os.makedirs(out_dir, exist_ok=True)
    stub = f"{slugify(name or spec.get('title') or 'flowchart')}_{_dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    page, svg_static = render_html(lay, THEMES[theme], stub)
    p_html, p_svg, p_json = (os.path.join(out_dir, stub + ext) for ext in (".html", ".svg", ".json"))
    with open(p_html, "w", encoding="utf-8") as f:
        f.write(page)
    with open(p_svg, "w", encoding="utf-8") as f:
        f.write(svg_static)
    with open(p_json, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)
    p_gif = None
    if make_gif:
        p_gif = render_gif(lay, THEMES[theme], os.path.join(out_dir, stub + ".gif"), mode=gif_mode, width=gif_width,
                           aspect=gif_aspect, show_title=gif_title, log=log)
    log(f"[done] HTML: {p_html}")
    if p_gif:
        log(f"[done] GIF : {p_gif}")
    return AgentResult(spec, lay, p_html, p_gif, p_svg, p_json, page, warnings, steps)
