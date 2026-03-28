ANSWERING_PRMOMT = """
You are an expert assistant answering questions from a technical document.

Use ONLY the provided sources.
read from the provided JSON Sources given in the context.

Instructions:
- Answer the question clearly
- Cite sources using [Source X]
- If multiple sections are used, cite all
- Do NOT hallucinate

Question:
{query}

Sources:
{context}

Answer:
"""