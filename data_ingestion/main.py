import os
import time
import json # <--- New Import

# --- 1. Import your custom modules ---
try:
    from pdf_data import process_pdfs
    from db_ingestion import process_database
    from email_ingestion import process_emails
except ImportError as e:
    print(f"CRITICAL ERROR: {e}", flush=True)
    exit()

from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- CONFIGURATION ---
PDF_DIR = r"C:\Users\admin\Documents\NEW_INFOSYS_INTERNSHIP_PROJECT\fake_enterprise_dataset\data\pdf"
DB_PATH = r"C:\Users\admin\Documents\NEW_INFOSYS_INTERNSHIP_PROJECT\fake_enterprise_dataset\data\sql\enterprise.db"
EMAIL_DIR = r"C:\Users\admin\Documents\NEW_INFOSYS_INTERNSHIP_PROJECT\fake_enterprise_dataset\data\emails"

# OUTPUT FILE NAME
OUTPUT_JSON_FILE = "processed_data.json"

def main():
    start_time = time.time()
    print("\n=== STARTING DATA INGESTION (OUTPUT: JSON) ===", flush=True)

    # 1. LOAD DATA
    all_docs = []
    
    print("--- [1/3] Loading PDFs ---", flush=True)
    pdf_docs = process_pdfs(PDF_DIR)
    all_docs.extend(pdf_docs)

    print("\n--- [2/3] Loading Database ---", flush=True)
    db_docs = process_database(DB_PATH)
    all_docs.extend(db_docs)

    print("\n--- [3/3] Loading Emails ---", flush=True)
    email_docs = process_emails(EMAIL_DIR)
    all_docs.extend(email_docs)

    if not all_docs:
        print("ERROR: No documents found!", flush=True)
        return

    # 2. SPLIT DATA (Chunking)
    # Your mentor said "ready for embedding", so we MUST chunk it now.
    print(f"\n--- Splitting {len(all_docs)} documents into chunks ---", flush=True)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splitted_docs = text_splitter.split_documents(all_docs)
    
    print(f"--> Created {len(splitted_docs)} total chunks.", flush=True)

    # 3. CONVERT TO JSON FORMAT
    print(f"\n--- Saving to JSON file: {OUTPUT_JSON_FILE} ---", flush=True)
    
    # We need to convert the complex 'Document' objects into simple Dictionaries
    json_data = []
    for doc in splitted_docs:
        json_data.append({
            "content": doc.page_content, # The text
            "metadata": doc.metadata     # Source, page number, etc.
        })

    # Write to file
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

    end_time = time.time()
    print("\n==========================================", flush=True)
    print("       JSON EXPORT COMPLETE")
    print("==========================================", flush=True)
    print(f"File saved at: {os.path.abspath(OUTPUT_JSON_FILE)}")
    print(f"Total Records: {len(json_data)}")
    print(f"Time Taken: {end_time - start_time:.2f} seconds", flush=True)   
if __name__ == "__main__":
    main()