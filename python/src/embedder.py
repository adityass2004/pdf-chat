from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim embeddings

def embed_text(text_chunks):
    embeddings = model.encode(text_chunks)
    return embeddings
