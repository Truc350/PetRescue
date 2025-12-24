import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

df = pd.read_csv("data/data.csv")

docs = []
for _, row in df.iterrows():
    text = " ".join(str(v) for v in row.values if pd.notna(v))
    docs.append(Document(page_content=text))

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(docs, embeddings)

vectorstore.save_local("data/faiss_db")

print("✅ FAISS database đã tạo xong!", len(docs))
