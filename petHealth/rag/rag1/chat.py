from rag_chain import load_rag_chain
qa = load_rag_chain()

print("🐾 PetRescue AI – nhập 'exit' để thoát")

while True:
    q = input("\n👤 Bạn: ")
    if q.lower() == "exit":
        break

    result = qa.invoke({"query": q})
    print("🤖 AI:", result["result"])
