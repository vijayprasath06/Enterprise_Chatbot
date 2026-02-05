import os
from langchain_core.documents import Document

def process_emails(directory_path):
    email_docs = []
    
    # Check if directory exists
    if not os.path.exists(directory_path):
        print(f"Error: Email directory '{directory_path}' not found.")
        return []

    print(f"--- Scanning Emails in: {directory_path} ---")

    # Loop through all .txt files
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                    # We add "EMAIL SOURCE:" so the AI knows this is from an email
                    # This helps the AI distinguish between a formal PDF report and an informal email
                    final_content = f"SOURCE: EMAIL ({filename})\n{content}"
                    
                    doc = Document(
                        page_content=final_content,
                        metadata={
                            "source": "email_folder",
                            "filename": filename,
                            "type": "communication"
                        }
                    )
                    email_docs.append(doc)
                    
            except Exception as e:
                print(f"Skipped {filename}: {e}")
                
    print(f"Loaded {len(email_docs)} emails.")
    return email_docs

# Quick Test
if __name__ == "__main__":
    # Update this to your actual email folder path
    EMAIL_FOLDER = r"C:\Users\admin\Documents\NEW_INFOSYS_INTERNSHIP_PROJECT\fake_enterprise_dataset\data\emails"
    
    docs = process_emails(EMAIL_FOLDER)
    if docs:
        print("\n--- Email Preview ---")
        print(docs[0].page_content[:200]) # Print first 200 chars of first email