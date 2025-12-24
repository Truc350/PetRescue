from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA

load_dotenv()

def load_rag_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    faiss_dir = os.path.join(BASE_DIR, "data/faiss_db")
    vectorstore = FAISS.load_local(
        faiss_dir,
        embeddings,
        allow_dangerous_deserialization=True
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
Bạn là bác sĩ thú y AI.
Hãy trả lời rõ ràng, chính xác và bằng tiếng Việt,
chỉ dựa trên dữ liệu bệnh thú cưng dưới đây.
Nếu không có thông tin, hãy nói: "Không tìm thấy trong dữ liệu."

Câu hỏi: {question}
Dữ liệu liên quan: {context}
"""
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt}
    )
