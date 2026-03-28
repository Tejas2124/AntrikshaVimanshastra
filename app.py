import streamlit as st
import tempfile
from typing import List, Dict

# --- MOCK FUNCTIONS (Replace with your actual pipeline) ---

def ingest_pdf(file):
    # TODO: Replace with your PDF parsing + chunking + embedding + vector DB upsert
    return {"status": "success", "chunks": 120}

def retrieve(query: str):
    """
    Simulates vector retrieval.
    Replace with your actual retriever (FAISS, Pinecone, Chroma, etc.)
    """
    return [
        {
            "content": "Sample chunk about AI and embeddings.",
            "score": 0.89,
            "metadata": {"page": 3, "section": "Introduction"}
        },
        {
            "content": "Another chunk related to transformers.",
            "score": 0.82,
            "metadata": {"page": 5, "section": "Architecture"}
        }
    ]

def generate_answer(query: str, contexts: List[Dict]):
    # TODO: Replace with LLM call
    return "This is a generated answer based on retrieved context."

# --- STREAMLIT CONFIG ---
st.set_page_config(layout="wide", page_title="RAG App")

# --- SIDEBAR (LEFT) ---
st.sidebar.title("📄 PDF Ingestion")

uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    if st.sidebar.button("Ingest PDF"):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            result = ingest_pdf(tmp.name)

        st.sidebar.success(f"Ingested! Chunks: {result['chunks']}")

# --- MAIN LAYOUT (3 COLUMNS) ---
left_spacer, center_col, right_col = st.columns([1, 4, 2])

# --- CENTER (QUERY + ANSWER) ---
with center_col:
    st.title("🔍 RAG Query Interface")

    query = st.chat_input(placeholder="Ask something about your document...")

    if st.button("Search"):
        if query:
            retrieved_docs = retrieve(query)
            answer = generate_answer(query, retrieved_docs)

            st.subheader("🧠 Answer")
            st.write(answer)

            # Store in session for right panel
            st.session_state["retrieved_docs"] = retrieved_docs
        else:
            st.warning("Please enter a query.")

# --- RIGHT PANEL (RETRIEVAL DEBUG) ---
with right_col:
    st.title("📊 Retrieval Debug Panel")

    docs = st.session_state.get("retrieved_docs", [])

    if docs:
        for i, doc in enumerate(docs):
            with st.expander(f"Result {i+1} | Score: {doc['score']:.4f}"):
                st.write("**Content:**")
                st.write(doc["content"])

                st.write("**Metadata:**")
                st.json(doc["metadata"])
    else:
        st.info("No retrieval results yet.")
