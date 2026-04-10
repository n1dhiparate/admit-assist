import os
import json
import faiss
import numpy as np
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("Loading local embedding model (all-MiniLM-L6-v2)...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")
brochure_path = os.path.join(data_dir, "admission_brochure.txt")
index_path = os.path.join(data_dir, "faiss_index.bin")
chunks_path = os.path.join(data_dir, "chunks.json")

def get_embedding(text):
    try:
        embedding = embed_model.encode(text)
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        print(f"Error fetching embedding: {e}")
        return np.zeros(384, dtype=np.float32)

def initialize_knowledge_base():
    """Reads brochure, creates embeddings for each paragraph, and builds a FAISS local index."""
    if os.path.exists(index_path) and os.path.exists(chunks_path):
        return # Already built, no need to waste API calls

    if not os.path.exists(brochure_path):
        print(f"File not found: {brochure_path}")
        return

    with open(brochure_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Smart Chunking strategy
    raw_chunks = text.split("\n\n")
    chunks = [c.strip() for c in raw_chunks if len(c.strip()) > 50]

    if not chunks:
        return

    print(f"Building FAISS vector index with {len(chunks)} chunks...")
    dimension = 384 # Standard all-MiniLM-L6-v2 output dimension
    index = faiss.IndexFlatL2(dimension)
    
    embeddings = []
    valid_chunks = []
    
    for chunk in chunks:
        vec = get_embedding(chunk)
        if vec.any():
            embeddings.append(vec)
            valid_chunks.append(chunk)

    if not embeddings:
        print("Failed to generate embeddings. Check API key.")
        return

    embeddings_matrix = np.vstack(embeddings)
    index.add(embeddings_matrix)

    faiss.write_index(index, index_path)
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(valid_chunks, f)

    print("Index built successfully!")

def retrieve_context(query, top_k=3):
    """Takes user query, converts to vector, and searches nearest neighbors in FAISS"""
    initialize_knowledge_base() 
    
    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        print("Knowledge base not initialized properly.")
        return ""

    index = faiss.read_index(index_path)
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    query_vec = get_embedding(query).reshape(1, -1)
    if not query_vec.any():
        return ""

    # Perform Vector Search
    distances, indices = index.search(query_vec, top_k)
    
    results = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks):
            results.append(chunks[idx])

    return "\n\n".join(results)