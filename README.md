# 📘 Enterprise Hybrid RAG System (Graph + Vector)

### Infosys Springboard Internship Project 
**Author:** Vijay Prasath | **Batch:** 2026

### Agile document 
https://drive.google.com/drive/u/0/folders/199R2wOkqlm3tX1OkGCWPkGptZNY0qeBR

## 🚀 Overview
This project is an **Enterprise Knowledge Assistant** designed to answer queries about Infosys using a **Hybrid Retrieval-Augmented Generation (RAG)** approach. It combines the precision of a **Neo4j Knowledge Graph** with the semantic understanding of a **FAISS Vector Database** to deliver accurate, hallucination-free answers.

## 🏗️ Architecture
* **Frontend:** React.js, Tailwind CSS (Soft SaaS UI).
* **Backend:** Python, FastAPI (High-performance API).
* **AI Engine:** * **LLM:** Llama-3-70b (via Groq).
    * **Graph DB:** Neo4j (Structured Relationships).
    * **Vector DB:** FAISS (Unstructured Text).
    * **Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`).

## ✨ Key Features
1.  **Hybrid Search:** Queries Graph and Vector stores in parallel.
2.  **Reasoning Engine:** A UI "Accordion" that reveals the exact data sources (Nodes vs. Text) used for the answer.
3.  **Automatic Failover:** If the Graph has no data, the system seamlessly defaults to Vector search.
4.  **Enterprise Security:** Rejects out-of-domain queries to prevent hallucinations.

## 🛠️ Installation & Setup

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Create a .env file with your API Keys
uvicorn main:app --reload
```


### 2. Frontend Setup
```bash
cd frontend
npm install
npm start
```
📸 Usage
Start Neo4j Desktop.

Run the Backend (uvicorn).

Run the Frontend (npm start).

Ask questions like "Who is the CEO?" or "Summarize the ESG report."
