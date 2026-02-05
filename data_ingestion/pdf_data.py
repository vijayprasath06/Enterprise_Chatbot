import os
from langchain_community.document_loaders import PyPDFLoader

def process_pdfs(directory_path):
    pdf_docs = []
    
    # Check if directory actually exists to prevent crashes
    if not os.path.exists(directory_path):
        print(f"Error: The directory '{directory_path}' does not exist.")
        return []

    # Use the variable 'directory_path' here, NOT the hardcoded string
    for filename in os.listdir(directory_path):     
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            
            try:
                # Load the PDF
                loader = PyPDFLoader(file_path)
                loaded_docs = loader.load()
                
                # Add custom metadata
                for doc in loaded_docs:
                    doc.metadata['source_type'] = 'pdf'
                    doc.metadata['file_name'] = filename
                
                pdf_docs.extend(loaded_docs)
                print(f"Loaded {len(loaded_docs)} pages from {filename}")
                
            except Exception as e:
                print(f"Failed to load {filename}: {e}")
            
    return pdf_docs

# --- THIS IS HOW YOU RUN IT ---
if __name__ == "__main__":
    # Define your specific path here with the 'r'
    my_pdf_folder = r"C:\Users\admin\Documents\NEW_INFOSYS_INTERNSHIP_PROJECT\fake_enterprise_dataset\data\pdf"
    
    # Call the function
    documents = process_pdfs(my_pdf_folder)
    print(f"\nTotal PDF pages collected: {len(documents)}")