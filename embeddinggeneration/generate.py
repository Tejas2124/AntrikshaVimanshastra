import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Load model
model = SentenceTransformer("BAAI/bge-large-en-v1.5")


def build_embedding_text(chunk):
    return f"""
{chunk['title']}
{chunk['path']}

{chunk['content']}
"""


def load_chunks(jsonl_path):
    chunks = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def embed_chunks(chunks, batch_size=32):
    texts = [build_embedding_text(c) for c in chunks]
    embeddings = []

    for i in tqdm(range(0, len(texts), batch_size)):
        batch = texts[i:i+batch_size]
        emb = model.encode(
            batch,
            normalize_embeddings=True
        )
        embeddings.extend(emb)

    return embeddings
