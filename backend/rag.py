import os

def load_brochure():
    """Loads the official brochure text safely."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Synchronized with the backend/data/admission_brochure.txt path
    file_path = os.path.join(base_dir, "data", "admission_brochure.txt")
    
    if not os.path.exists(file_path):
        return ""

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def retrieve_context(query):
    """
    Optimized RAG Retrieval:
    Instead of returning the first matching line, it finds the paragraph 
    with the highest keyword density.
    """
    text = load_brochure()
    if not text:
        return ""

    # Split into paragraphs/chunks instead of single lines for better context
    # This allows the AI to see the full explanation for a milestone
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    
    query_words = set(query.lower().split())
    best_chunk = ""
    max_matches = 0

    for chunk in chunks:
        chunk_lower = chunk.lower()
        # Count unique keyword matches in this chunk
        matches = sum(1 for word in query_words if word in chunk_lower)
        
        if matches > max_matches:
            max_matches = matches
            best_chunk = chunk

    # Only return if we actually found a decent match
    return best_chunk if max_matches > 0 else ""