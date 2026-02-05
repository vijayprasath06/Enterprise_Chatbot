from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 1. SETUP: Use the same folder and model as before
VECTOR_DB_DIR = "chroma_db_store"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. CONNECT: Load the database from the disk
print("--- Loading Database... ---")
vector_db = Chroma(
    persist_directory=VECTOR_DB_DIR, 
    embedding_function=embedding_model
)

# 3. SEARCH: Ask a question based on your data
# (Change this query to match something in your specific PDFs/SQL)
query = "What projects are currently active?" 

print(f"\nQuerying: '{query}'\n")
results = vector_db.similarity_search(query, k=3) # Get top 3 matches

# 4. SHOW RESULTS
if not results:
    print("No results found. (Did you use the right query?)")
else:
    for i, doc in enumerate(results):
        print(f"--- Result {i+1} (Source: {doc.metadata.get('source', 'Unknown')}) ---")
        print(doc.page_content)
        print("\n")