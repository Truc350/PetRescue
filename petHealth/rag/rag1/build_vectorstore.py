import os

import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

csv_path = os.path.join("..", "data", "data.csv")
df = pd.read_csv(csv_path)


docs = []
for _, row in df.iterrows():
    text = " ".join(str(v) for v in row.values if pd.notna(v))
    docs.append(Document(page_content=text))

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(docs, embeddings)

vectorstore.save_local(r"E:\Work_Space\Ki1_nam3\PetRescue\petHealth\rag\data\faiss_db")

print("✅ FAISS database đã tạo xong!", len(docs))
