import streamlit as st
from chunking.chunk import process_pdf_to_chunks
from ingestion.ingest import ingest
from retriever.retrievechunks import retrieve_chunks
from vectorstore.cleanup import deletecollections
from ChatModel.bot import answergenerator
from main import convert_obj_to_json
import json

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "retrieved_docs" not in st.session_state:
    st.session_state.retrieved_docs = []

# --- LAYOUT ---
main_col, right_col = st.columns([3, 1.5])

# --- CHAT AREA (CENTER) ---
with main_col:
    st.title("🤖 RAG Chat")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ChatGPT-style input (BOTTOM)
    user_query = st.chat_input("Ask something about your document...")

    if user_query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.chat_message("user"):
            st.markdown(user_query)

        # Retrieve + Generate
        chunks = retrieve_chunks(user_query)
        context = convert_obj_to_json(chunks)
        # response = answergenerator(user_query, json.dumps(context))
        response = answergenerator(user_query,context)
        

        # Store retrieval for debug panel
        st.session_state.retrieved_docs = context

        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.chat_message("assistant"):
            st.markdown(response)

# --- RIGHT PANEL (DEBUG) ---
with right_col:
    st.title("📊 Retrieval Panel")

    docs = st.session_state.get("retrieved_docs", [])
    if docs:
        print(docs[0])
        for i, doc in enumerate(docs):
            with st.expander(f"Result {i+1} | Score: {doc['metadata']['score']:.4f}"):
                st.write("**Content:**")
                st.write(doc["properties"]["content"])

                st.write("**Metadata:**")
                st.json(doc["metadata"])
    else:
        st.info("No retrieval yet.")