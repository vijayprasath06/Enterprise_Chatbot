import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- CONFIGURATION ---
INPUT_FILE = "processed_data.json"
FAISS_INDEX_FILE = "vector_store.faiss"
METADATA_FILE = "faiss_metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"  # Small, fast, and free model

def main():
    print("--- STARTING EMBEDDING PIPELINE (FAISS) ---")

    # 1. LOAD DATA
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run main.py first!")
        return
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw_documents = json.load(f)
    print(f"Loaded {len(raw_documents)} source documents.")

    # 2. SETUP MODEL & SPLITTER
    print("Loading Embedding Model (this may take a moment)...")
    model = SentenceTransformer(MODEL_NAME)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # Per mentor's screenshot
        chunk_overlap=100     # Per mentor's screenshot
    )

    # 3. CHUNK & EMBED
    all_embeddings = []
    all_metadata = []
    
    print("Processing documents...")
    for doc in raw_documents:
        # Extract text and existing metadata
        full_text = doc.get("content", "")
        base_metadata = doc.get("metadata", {})
        
        # Split text into smaller chunks
        chunks = text_splitter.split_text(full_text)
        
        for chunk_text in chunks:
            # Generate Embedding (Vector)
            # encode() returns a numpy array
            vector = model.encode(chunk_text)
            
            # Add to our list
            all_embeddings.append(vector)
            
            # Store the text + metadata separately (FAISS can't store text!)
            all_metadata.append({
                "text": chunk_text,
                "source": base_metadata.get("source", "unknown"),
                "original_id": base_metadata.get("doc_id", "N/A")
            })

    print(f"Generated {len(all_embeddings)} vectors.")

    # 4. BUILD FAISS INDEX
    if len(all_embeddings) == 0:
        print("No embeddings generated. Exiting.")
        return

    # Convert list to numpy array (FAISS requires this)
    embedding_matrix = np.array(all_embeddings).astype('float32')
    
    # Get vector dimension (384 for all-MiniLM-L6-v2)
    dimension = embedding_matrix.shape[1]
    
    # Create the Index (L2 = Euclidean Distance)
    index = faiss.IndexFlatL2(dimension)
    
    # Add vectors to index
    index.add(embedding_matrix)
    print(f"FAISS Index built with {index.ntotal} vectors.")

    # 5. SAVE TO DISK
    print("Saving files...")
    
    # Save the Vector Index
    faiss.write_index(index, FAISS_INDEX_FILE)
    
    # Save the Metadata Map (Text)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, indent=4)
        
    print("\nSUCCESS! Pipeline Complete.")
    print(f"1. Vectors saved to: {FAISS_INDEX_FILE}")
    print(f"2. Text map saved to: {METADATA_FILE}")

if __name__ == "__main__":
    main()