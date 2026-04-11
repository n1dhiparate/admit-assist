import os
import glob
import json
import faiss
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

print("Loading local embedding model (all-MiniLM-L6-v2)...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
index_path = os.path.join(data_dir, "faiss_index.bin")
chunks_path = os.path.join(data_dir, "chunks.json")

def get_embedding(text):
    try:
        embedding = embed_model.encode(text)
        return np.array(embedding, dtype=np.float32)
    except Exception as e:
        print(f"Error fetching embedding: {e}")
        return np.zeros(384, dtype=np.float32)

def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())
        start += (chunk_size - overlap)
    return chunks

def extract_text_from_pdf(filepath):
    try:
        import PyPDF2
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Failed to read PDF {filepath}: {e}")
        return ""

def initialize_knowledge_base():
    # Only rebuild if forced or files missing
    if os.path.exists(index_path) and os.path.exists(chunks_path):
        return

    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        
    all_text = ""
    
    # Read text files
    for filepath in glob.glob(os.path.join(data_dir, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            all_text += f.read() + "\n\n"
            
    # Read PDF files
    for filepath in glob.glob(os.path.join(data_dir, "*.pdf")):
        all_text += extract_text_from_pdf(filepath) + "\n\n"

    if not all_text.strip():
        return

    print("Chunking documents...")
    chunks = chunk_text(all_text, chunk_size=500, overlap=100)

    if not chunks:
        return

    print(f"Building FAISS vector index with {len(chunks)} chunks...")
    dimension = 384
    index = faiss.IndexFlatL2(dimension)
    
    embeddings = []
    valid_chunks = []
    
    for chunk in chunks:
        vec = get_embedding(chunk)
        if vec.any():
            embeddings.append(vec)
            valid_chunks.append(chunk)

    if not embeddings:
        return

    embeddings_matrix = np.vstack(embeddings)
    index.add(embeddings_matrix)

    faiss.write_index(index, index_path)
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(valid_chunks, f)

    print("Index built successfully!")

def retrieve_context(query, top_k=5):
    initialize_knowledge_base() 
    
    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
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