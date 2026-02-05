import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the saved files
INDEX_FILE = "vector_store.faiss"
METADATA_FILE = "faiss_metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"

def search(query):
    print(f"\n--- Searching for: '{query}' ---")
    
    # 1. Load Resources
    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Embed the Query
    query_vector = model.encode([query])
    
    # 3. Search FAISS
    # k=3 means "return top 3 results"
    distances, indices = index.search(np.array(query_vector).astype('float32'), k=3)
    
    # 4. Display Results
    for i, idx in enumerate(indices[0]):
        if idx == -1: continue # No result found
        
        result_meta = metadata[idx]
        score = distances[0][i]
        
        print(f"\nResult {i+1} (Score: {score:.4f}):")
        print(f"Text: {result_meta['text'][:150]}...") # Show first 150 chars
        print(f"Source: {result_meta['source']}")

if __name__ == "__main__":
    # Change this query to test different things!
    search("What is the company policy on remote work?")