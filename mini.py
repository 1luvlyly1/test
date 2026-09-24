# Databricks notebook source
# MAGIC %md
# MAGIC # Banking RAG

# COMMAND ----------

# MAGIC %pip install -U databricks-vectorsearch databricks-agents mlflow openai pypdf python-docx
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Config
CATALOG, SCHEMA = "main", "banking_rag"
RAW_DOCS_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/raw_docs"

TABLE = f"{CATALOG}.{SCHEMA}.banking_documents"
VS_ENDPOINT = "banking_vs_endpoint"
VS_INDEX = f"{CATALOG}.{SCHEMA}.banking_documents_index"
EMBEDDING_ENDPOINT = "databricks-gte-large-en"
LLM_ENDPOINT = "databricks-claude-sonnet-4-5"
REGISTERED_MODEL = f"{CATALOG}.{SCHEMA}.banking_assistant"
SERVING_ENDPOINT = "banking-assistant"

TOP_K = 5
USE_RERANKER = True
CHUNK_WORDS, OVERLAP_WORDS = 300, 50
FALLBACK_ANSWER = "I cannot find relevant information in the policy documents."

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

# COMMAND ----------

# DBTITLE 1,Kiem tra endpoint co that
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
names = [e.name for e in w.serving_endpoints.list()]
print("LLM      :", "OK" if LLM_ENDPOINT in names else f"KHONG CO -> chon: {[n for n in names if 'claude' in n.lower()]}")
print("Embedding:", "OK" if EMBEDDING_ENDPOINT in names else f"KHONG CO -> chon: {[n for n in names if 'gte' in n.lower() or 'bge' in n.lower()]}")

# COMMAND ----------

# DBTITLE 1,Ingest -> Delta table
import os

import pandas as pd

def read_doc(path):
    if path.lower().endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    import docx
    return "\n".join(p.text for p in docx.Document(path).paragraphs)

rows = []
files = [f for f in sorted(os.listdir(RAW_DOCS_PATH)) if f.lower().endswith((".pdf", ".docx"))]
for name in files:
    words = " ".join(read_doc(os.path.join(RAW_DOCS_PATH, name)).split()).split()
    step = CHUNK_WORDS - OVERLAP_WORDS
    parts = [" ".join(words[i:i + CHUNK_WORDS]) for i in range(0, max(len(words), 1), step)]
    for i, part in enumerate(parts):
        if len(part.split()) >= 20:
            rows.append({"chunk_id": f"{len(rows):05d}", "document_name": name, "chunk_content": part})
    print(f"{name:40s} {len(parts)} chunks")

df = pd.DataFrame(rows)
assert not df.empty, "Khong doc duoc noi dung nao"

(spark.createDataFrame(df).write.format("delta").mode("overwrite")
 .option("overwriteSchema", "true").option("delta.enableChangeDataFeed", "true")
 .saveAsTable(TABLE))
spark.sql(f"ALTER TABLE {TABLE} SET TBLPROPERTIES (delta.enableChangeDataFeed = true)")

N_ROWS = spark.table(TABLE).count()
print(f"\n{N_ROWS} chunks -> {TABLE}")

# COMMAND ----------

# DBTITLE 1,Vector Search endpoint + index
import time

from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient(disable_notice=True)

if VS_ENDPOINT not in [e["name"] for e in vsc.list_endpoints().get("endpoints", [])]:
    vsc.create_endpoint(name=VS_ENDPOINT, endpoint_type="STANDARD")
while vsc.get_endpoint(VS_ENDPOINT)["endpoint_status"]["state"] != "ONLINE":
    print("  endpoint dang tao...")
    time.sleep(20)

if VS_INDEX not in [i["name"] for i in vsc.list_indexes(VS_ENDPOINT).get("vector_indexes", [])]:
    vsc.create_delta_sync_index(
        endpoint_name=VS_ENDPOINT, index_name=VS_INDEX, source_table_name=TABLE,
        pipeline_type="TRIGGERED", primary_key="chunk_id",
        embedding_source_column="chunk_content",
        embedding_model_endpoint_name=EMBEDDING_ENDPOINT)
index = vsc.get_index(VS_ENDPOINT, VS_INDEX)

# COMMAND ----------

# DBTITLE 1,Cho index sync du so dong (chay lai cell nay neu chua xong)
st = index.describe().get("status", {})
state, rows_done = str(st.get("detailed_state")), int(st.get("indexed_row_count") or 0)
print(f"{state}  {rows_done}/{N_ROWS}")
assert "FAILED" not in state, st.get("message")
assert rows_done >= N_ROWS, "Chua sync xong, doi vai phut roi chay lai cell nay"
print("Index san sang")

# COMMAND ----------

# DBTITLE 1,Agent
import uuid
from typing import Optional

import mlflow
from databricks.vector_search.reranker import DatabricksReranker
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatAgentResponse, ChatContext

SYSTEM_PROMPT = (
    "You are a banking policy assistant. Answer ONLY from the context below. "
    "Cite the document name for each fact. If the context does not contain the answer, "
    f"reply exactly: {FALLBACK_ANSWER}"
)

class BankingAssistant(ChatAgent):
    def __init__(self):
        self._index = None
        self._llm = None

    def __getstate__(self):
        return {"_index": None, "_llm": None}

    @property
    def idx(self):
        if self._index is None:
            self._index = VectorSearchClient(disable_notice=True).get_index(VS_ENDPOINT, VS_INDEX)
        return self._index

    @property
    def llm(self):
        if self._llm is None:
            self._llm = WorkspaceClient().serving_endpoints.get_open_ai_client()
        return self._llm

    @mlflow.trace(span_type="RETRIEVER")
    def retrieve(self, query):
        kw = dict(query_text=query, columns=["chunk_id", "document_name", "chunk_content"],
                  num_results=TOP_K, query_type="HYBRID")
        if USE_RERANKER:
            kw["reranker"] = DatabricksReranker(columns_to_rerank=["chunk_content"])
        res = self.idx.similarity_search(**kw)
        cols = [c["name"] for c in res["manifest"]["columns"]]
        return [dict(zip(cols, r)) for r in res["result"].get("data_array", [])]

    def predict(self, messages: list, context: Optional[ChatContext] = None,
                custom_inputs: Optional[dict] = None) -> ChatAgentResponse:
        question = next((m.content for m in reversed(messages) if m.role == "user"), "")
        hits = self.retrieve(question)

        if not hits:
            answer = FALLBACK_ANSWER
        else:
            ctx = "\n\n".join(f"[{h['document_name']}]\n{h['chunk_content']}" for h in hits)
            out = self.llm.chat.completions.create(
                model=LLM_ENDPOINT, temperature=0, max_tokens=800,
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
                          {"role": "user", "content": f"<context>\n{ctx}\n</context>\n\nQuestion: {question}"}])
            answer = (out.choices[0].message.content or "").strip()

        return ChatAgentResponse(
            messages=[ChatAgentMessage(role="assistant", content=answer, id=str(uuid.uuid4()))],
            custom_outputs={"chunks": [h["chunk_id"] for h in hits]})

AGENT = BankingAssistant()

# COMMAND ----------

# DBTITLE 1,Test truoc khi deploy
for q in ["What documents are required for KYC verification?",
          "How can a customer open a current account?",
          "What is the weather in Hanoi today?"]:
    r = AGENT.predict([ChatAgentMessage(role="user", content=q)])
    print(f"Q: {q}\nA: {r.messages[0].content}\n")

# COMMAND ----------

# DBTITLE 1,MLflow eval
import time

EVAL_QUESTIONS = [
    "How can a customer open a current account?",
    "What documents are required for KYC verification?",
    "What is the approval process for personal loans?",
    "How are suspicious transactions reported?",
    "How long must KYC records be retained?",
    "What is the weather in Hanoi today?",
]

mlflow.set_experiment(f"/Users/{spark.sql('SELECT current_user()').collect()[0][0]}/banking_rag_eval")

rows = []
for q in EVAL_QUESTIONS:
    t0 = time.perf_counter()
    r = AGENT.predict([ChatAgentMessage(role="user", content=q)])
    rows.append({
        "question": q,
        "answer": r.messages[0].content,
        "latency_s": round(time.perf_counter() - t0, 2),
        "retrieved_chunks": ", ".join(r.custom_outputs["chunks"]),
    })
    print(f"{rows[-1]['latency_s']:5.2f}s  {q[:55]}")

eval_df = pd.DataFrame(rows)
fallback = eval_df.answer.str.startswith("I cannot find")

with mlflow.start_run(run_name="banking_assistant_eval") as run:
    mlflow.log_table(eval_df, artifact_file="eval_results.json")
    mlflow.log_metric("avg_latency_s", float(eval_df.latency_s.mean()))
    mlflow.log_metric("fallback_rate", float(fallback.mean()))
    mlflow.log_params({"llm_endpoint": LLM_ENDPOINT, "top_k": TOP_K,
                       "reranker": USE_RERANKER, "n_chunks": N_ROWS})
    print(f"\nrun_id: {run.info.run_id}")

print(f"latency trung binh: {eval_df.latency_s.mean():.2f}s")
print(f"fallback: {fallback.sum()}/{len(eval_df)}  (ky vong 1 - chi cau ngoai pham vi)")
display(eval_df)

# COMMAND ----------

# DBTITLE 1,Log model
from mlflow.models.resources import DatabricksServingEndpoint, DatabricksVectorSearchIndex

mlflow.set_registry_uri("databricks-uc")

with mlflow.start_run(run_name="banking_assistant"):
    logged = mlflow.pyfunc.log_model(
        python_model=AGENT, name="agent",
        resources=[DatabricksVectorSearchIndex(index_name=VS_INDEX),
                   DatabricksServingEndpoint(endpoint_name=LLM_ENDPOINT),
                   DatabricksServingEndpoint(endpoint_name=EMBEDDING_ENDPOINT)],
        pip_requirements=["mlflow", "databricks-vectorsearch", "databricks-sdk", "openai"],
        registered_model_name=REGISTERED_MODEL)

MODEL_VERSION = logged.registered_model_version
print(REGISTERED_MODEL, "version", MODEL_VERSION)

# COMMAND ----------

# DBTITLE 1,Deploy (10-20 phut)
from databricks import agents

agents.deploy(REGISTERED_MODEL, MODEL_VERSION, endpoint_name=SERVING_ENDPOINT, scale_to_zero=True)

# COMMAND ----------

# DBTITLE 1,Test endpoint
import json

import requests

ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
HOST, TOKEN = ctx.apiUrl().get(), ctx.apiToken().get()

r = requests.post(
    f"{HOST}/serving-endpoints/{SERVING_ENDPOINT}/invocations",
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    json={"messages": [{"role": "user", "content": "What documents are required for KYC verification?"}]},
    timeout=180)
print(r.status_code)
print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:2000])
