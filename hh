# Databricks notebook source
# MAGIC %pip install mlflow
# MAGIC %restart_python

# COMMAND ----------

import glob, os, json, operator, warnings
import pandas as pd
from mlflow.deployments import get_deploy_client

warnings.filterwarnings("ignore", category=UserWarning)

FOLDER = "/Volumes/main/default/my_volume/csv"   # doi theo folder cua ban
ENDPOINT = "databricks-claude-sonnet-4-5"        # doi theo endpoint cua ban
MAX_CHARS = 150_000                              # cat bot neu du lieu qua dai
MAX_STEPS = 4                                    # so lan goi tool toi da moi file

client = get_deploy_client("databricks")

SYSTEM = """Ban la chuyen gia phan tich du lieu. Doc du lieu CSV (ten cot va gia tri)
va viet nhan xet CHI TIET bang tieng Viet theo cau truc:
1. Tong quan: file chua du lieu gi, moi dong dai dien cho cai gi.
2. Y nghia tung cot: du doan dua tren ten cot va gia tri.
3. Chat luong du lieu: gia tri thieu, trung lap, bat thuong, outlier.
4. Insight chinh: xu huong, phan bo, moi lien he dang chu y.
5. De xuat: buoc lam sach hoac phan tich tiep theo.

Ban co 2 cong cu:
- filter_rows: loc du lieu khi nguoi dung yeu cau dieu kien (theo cot, ngay, khoang gia tri...).
- count_by: dem so dong theo mot cot (vd: ngay nao co nhieu dong nhat).
Cac cong cu chay tren du lieu hien tai (da ap dung cac lan loc truoc).
Neu yeu cau cua nguoi dung can loc hoac dem thi goi cong cu, roi viet nhan xet dua tren ket qua."""

TOOLS = [
    {"type": "function", "function": {
        "name": "filter_rows",
        "description": "Loc cac dong thoa TAT CA dieu kien. Tra ve du lieu sau khi loc.",
        "parameters": {"type": "object", "properties": {
            "conditions": {"type": "array", "items": {"type": "object", "properties": {
                "column": {"type": "string", "description": "Ten cot chinh xac"},
                "op": {"type": "string",
                       "enum": ["==", "!=", ">", ">=", "<", "<=", "in", "between", "contains"]},
                "value": {"type": "string",
                          "description": "Gia tri. 'in': 'a,b,c'. 'between': 'tu,den'. Ngay dang YYYY-MM-DD"},
            }, "required": ["column", "op", "value"]}}},
            "required": ["conditions"]}}},
    {"type": "function", "function": {
        "name": "count_by",
        "description": "Dem so dong theo tung gia tri cua mot cot, sap xep giam dan.",
        "parameters": {"type": "object", "properties": {
            "column": {"type": "string"},
            "top_n": {"type": "integer", "description": "So gia tri tra ve, mac dinh 10"},
            "by_date": {"type": "boolean", "description": "true neu cot la ngay gio va muon gom theo ngay"},
        }, "required": ["column"]}}},
]


# ---------- Ham goi LLM ----------
def ask(messages, tools=None, tool_choice="auto", max_tokens=4000):
    inputs = {"messages": messages, "max_tokens": max_tokens, "temperature": 0}
    if tools:
        inputs["tools"] = tools
        inputs["tool_choice"] = tool_choice
    return client.predict(endpoint=ENDPOINT, inputs=inputs)["choices"][0]["message"]


def to_text(df):
    t = df.to_csv(index=False)
    return t if len(t) <= MAX_CHARS else t[:MAX_CHARS] + "\n...(da cat bot)"


# ---------- Ham filter / count ----------
OPS = {"==": operator.eq, "!=": operator.ne, ">": operator.gt,
       ">=": operator.ge, "<": operator.lt, "<=": operator.le}

def _prep(s):
    """Doan kieu cot: so, ngay hay chu. Tra (series da chuyen kieu, ham ep gia tri)."""
    if pd.api.types.is_numeric_dtype(s):
        return s, float
    dt = pd.to_datetime(s, errors="coerce")
    if s.notna().any() and dt.notna().sum() >= 0.8 * s.notna().sum():
        return dt, pd.to_datetime
    return s.astype(str), str

def filter_rows(df, conditions):
    mask = pd.Series(True, index=df.index)
    for c in conditions:
        col, op, val = c["column"], c["op"], str(c["value"])
        if col not in df.columns:
            raise ValueError(f"Khong co cot '{col}'. Cac cot: {list(df.columns)}")
        s, cast = _prep(df[col])
        vals = [x.strip() for x in val.split(",")]
        if op == "contains":
            m = df[col].astype(str).str.contains(val, case=False, na=False)
        elif op == "in":
            m = s.isin([cast(x) for x in vals])
        elif cast is pd.to_datetime and op in ("==", "between"):
            d = s.dt.normalize()                       # so sanh theo ngay, bo gio
            m = (d == cast(val)) if op == "==" else d.between(cast(vals[0]), cast(vals[1]))
        elif op == "between":
            m = s.between(cast(vals[0]), cast(vals[1]))
        else:
            m = OPS[op](s, cast(val))
        mask &= m.fillna(False)
    return df[mask]

def count_by(df, column, top_n=10, by_date=False):
    if column not in df.columns:
        raise ValueError(f"Khong co cot '{column}'. Cac cot: {list(df.columns)}")
    s = pd.to_datetime(df[column], errors="coerce").dt.date if by_date else df[column]
    return s.value_counts().head(top_n)

def run_tool(name, args, state):
    if name == "filter_rows":
        before = len(state["df"])
        state["df"] = filter_rows(state["df"], args["conditions"])
        n = len(state["df"])
        if n == 0:
            return f"Sau khi loc con 0 dong (truoc: {before}). Khong co du lieu thoa dieu kien."
        return f"Da loc: con {n} dong (truoc: {before}).\nDU LIEU SAU LOC:\n{to_text(state['df'])}"
    if name == "count_by":
        vc = count_by(state["df"], args["column"], args.get("top_n", 10), args.get("by_date", False))
        return f"So dong theo '{args['column']}' (tren {len(state['df'])} dong):\n{vc.to_string()}"
    raise ValueError(f"Khong co tool '{name}'")


# ---------- Luong phan tich ----------
def analyze(name, df, prompt):
    info = f"Ten file: {name}\nSo dong: {len(df)}, so cot: {df.shape[1]}\n"
    full = info + f"\nDU LIEU:\n{to_text(df)}"

    # Khong co prompt -> nhan xet mac dinh tren toan bo du lieu
    if not prompt.strip():
        return ask([{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": full}])["content"]

    # Co prompt -> gui cau truc cot + vai dong mau, de Sonnet quyet dinh goi tool
    cols = ", ".join(f"{c} ({t})" for c, t in df.dtypes.astype(str).items())
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": info + f"Cac cot: {cols}\n5 dong dau:\n"
                 f"{df.head().to_csv(index=False)}\nYEU CAU CUA NGUOI DUNG:\n{prompt}"}]
    state = {"df": df}
    used_tool = False

    for _ in range(MAX_STEPS):
        msg = ask(messages, TOOLS)
        calls = msg.get("tool_calls")
        if not calls:
            break
        used_tool = True
        messages.append({"role": "assistant", "content": msg.get("content") or "",
                         "tool_calls": calls})
        for call in calls:
            fn = call["function"]
            args = json.loads(fn.get("arguments") or "{}")
            try:
                result = run_tool(fn["name"], args, state)
            except Exception as e:
                result = f"LOI: {e}"
            print(f"[tool] {fn['name']} {json.dumps(args, ensure_ascii=False)} -> {len(state['df'])} dong")
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    else:
        # Het so lan goi tool -> bat buoc tra loi
        msg = ask(messages, TOOLS, tool_choice="none")

    # Prompt khong can loc/dem -> nhan xet toan bo du lieu kem yeu cau nguoi dung
    if not used_tool:
        return ask([{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": full + f"\n\nYEU CAU CUA NGUOI DUNG:\n{prompt}"}])["content"]
    return msg["content"]


# Doc tat ca CSV mot lan
data = {os.path.basename(p): pd.read_csv(p)
        for p in sorted(glob.glob(os.path.join(FOLDER, "*.csv")))}
for name, df in data.items():
    print(f"{name}: {len(df)} dong, {df.shape[1]} cot")

# COMMAND ----------

# Nhap yeu cau / context / dieu kien loc. De trong = nhan xet mac dinh.
# Vi du:
#   "Ngay nao co nhieu dong nhat?"
#   "Chi xet region = HN trong thang 10/2026, ngay nao nhieu don nhat?"
USER_PROMPT = ""

for name, df in data.items():
    print("=" * 80 + f"\nFILE: {name}\n")
    print(analyze(name, df, USER_PROMPT))
