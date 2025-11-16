import faiss
import numpy as np
import os

EMBEDDING_DIM = 384  # Must match SentenceTransformer output

def create_index(embeddings):
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(np.array(embeddings))
    return index

def save_index(index, file_path="embeddings/index.faiss"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    faiss.write_index(index, file_path)

def load_index(file_path="embeddings/index.faiss"):
    if os.path.exists(file_path):
        return faiss.read_index(file_path)
    return None

def search_index(index, query_embedding, top_k=3):
    distances, indices = index.search(np.array([query_embedding]), top_k)
    return indices[0]
