# Databricks notebook source
# MAGIC %md
# MAGIC # Render architecture diagram
# MAGIC
# MAGIC Notebook doc lap, khong lien quan den notebook chinh. Chay cell duoi de ra chart,
# MAGIC chup man hinh hoac chuot phai vao hinh de luu anh.

# COMMAND ----------

# DBTITLE 1,Render bang displayHTML
MERMAID = """
flowchart TD
    subgraph "Ingestion"
        A1[Doc text<br/>pypdf / python-docx] --> A2[Chunk theo muc<br/>1. / 1.1 / 1.1.1]
        A2 --> A3[Child chunk + parent_content]
    end
    subgraph "Delta Table"
        B1[chunk_id, document_name<br/>chunk_content, parent_content] --> B2[Change Data Feed]
    end
    subgraph "Vector Search Index"
        C1[Embedding<br/>databricks-gte-large-en] --> C2[Hybrid<br/>vector + keyword]
        C2 --> C3[Rerank<br/>cross-encoder]
    end
    subgraph "Mosaic AI Agent"
        D1[Guard nguong score] --> D2[Gom muc cha<br/>dung context]
        D2 --> D3[Claude Sonnet<br/>system prompt guard]
        D3 --> D4[Kiem tra citation]
    end
    subgraph "Model Serving"
        E1[Unity Catalog model] --> E2[POST /invocations]
    end
    F[Fraud rule engine<br/>cham diem 0-100]
    G[MLflow<br/>trace + eval]
    A3 --> B1
    B2 --> C1
    C3 --> D1
    D4 --> E1
    F --> D3
    D4 -.-> G
"""

displayHTML(f"""
<div style="background:#fff;padding:16px">
  <pre class="mermaid">{MERMAID}</pre>
</div>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
</script>
""")

# COMMAND ----------

# MAGIC %md
# MAGIC Cach khac: dan truc tiep vao mot cell `%md` neu workspace render duoc mermaid.
# MAGIC
# MAGIC ```mermaid
# MAGIC flowchart TD
# MAGIC     A[Documents<br/>PDF / DOCX] --> B[Delta Table<br/>banking_documents]
# MAGIC     B --> C[Vector Search<br/>Index]
# MAGIC     C --> D[Mosaic AI Agent<br/>Claude Sonnet]
# MAGIC     D --> E[Model Serving<br/>POST /invocations]
# MAGIC ```
