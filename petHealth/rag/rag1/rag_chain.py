from dotenv import load_dotenv
import os

from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA

# Thử import Gemini, nếu lỗi thì dùng local LLM
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Fallback LLM local (nhanh và miễn phí)
try:
    from langchain.llms import HuggingFacePipeline
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    LOCAL_AVAILABLE = True
except ImportError:
    LOCAL_AVAILABLE = False

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

    # ===== Chọn LLM =====
    if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")

        )

    elif LOCAL_AVAILABLE:
        # Sử dụng model local từ HuggingFace (mặc định dùng small GPT2-like)
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)
        llm = HuggingFacePipeline(pipeline=pipe)
        print("⚠️ Gemini không dùng được, đang fallback sang local HuggingFace LLM.")
    else:
        raise RuntimeError("Không tìm thấy LLM hợp lệ: Gemini key hoặc HuggingFace local.")

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt}
    )
