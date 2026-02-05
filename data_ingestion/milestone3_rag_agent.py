import os
import json
import faiss
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
FAISS_INDEX = "vector_store.faiss"
METADATA_FILE = "faiss_metadata.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# 🔑 PASTE YOUR GROQ KEY HERE
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- TEST QUESTIONS (The Exam Paper) ---

TEST_QUERIES = [
    "Who is the manager of the Finance department?",    # Factual
    "Summarize the company's remote work policy.",      # Summarization
    "What are the safety guidelines for construction?", # Specific Context
    "Who won the 2030 World Cup?",                      # Negative Test (Should say "I don't know")
]

class RAGPipeline:
    def __init__(self):
        print("--- INITIALIZING RAG PIPELINE (Groq Llama 3) ---")
        
        if not os.path.exists(FAISS_INDEX):
            raise FileNotFoundError("Run embedding_pipeline.py first!")
        self.index = faiss.read_index(FAISS_INDEX)
        
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
            
        print("Loading Embedding Model...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        
        print("Connecting to Groq...")
        # Using the NEW supported model
        self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
        
        # Self-Correction / Grading LLM (Same model, different prompt)
        self.grader_llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
        
        print("System Ready!")

    def retrieve(self, query, k=3):
        query_vector = self.embedder.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: continue
            text = self.metadata[idx]['text']
            source = self.metadata[idx]['source']
            results.append(f"[Source: {source}]\n{text}")
        return results

    def generate_answer(self, query):
        retrieved_docs = self.retrieve(query)
        context_text = "\n\n".join(retrieved_docs)
        
        if not retrieved_docs:
            return "I couldn't find any relevant information."

        template = """
        You are a corporate assistant. Answer the question based ONLY on the context.
        If the answer is not in the context, say "I don't know."
        
        Context: {context}
        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        # We need the full string for evaluation, not a stream
        return chain.invoke({"context": context_text, "question": query})

    def evaluate_answer(self, question, answer):
        """
        Uses the LLM to grade the answer (Scale 1-10) based on relevance.
        """
        grader_template = """
        You are a strict teacher grading an AI's answer.
        
        Question: {question}
        AI Answer: {answer}
        
        Task:
        1. Does the answer directly address the question?
        2. Is the answer professional?
        3. If the answer is "I don't know" for an invalid question, that is a Good answer.
        
        Output ONLY a single number from 1 to 10. Do not write any words.
        """
        
        prompt = ChatPromptTemplate.from_template(grader_template)
        chain = prompt | self.grader_llm | StrOutputParser()
        
        try:
            score = chain.invoke({"question": question, "answer": answer})
            return int(score.strip())
        except:
            return 5 # Default if grading fails

def run_evaluation_suite(rag):
    print("\n" + "="*40)
    print("      STARTING AUTOMATED EVALUATION")
    print("="*40)
    
    total_score = 0
    total_time = 0
    
    for i, query in enumerate(TEST_QUERIES):
        print(f"\nTest {i+1}: {query}")
        
        # 1. Measure Latency (Speed)
        start_time = time.time()
        answer = rag.generate_answer(query)
        end_time = time.time()
        latency = end_time - start_time
        total_time += latency
        
        print(f"  > AI Answer: {answer[:100]}...") # Show summary
        
        # 2. Measure Quality (LLM Grading)
        score = rag.evaluate_answer(query, answer)
        total_score += score
        
        print(f"  > ⏱️ Time: {latency:.2f}s | 📝 Accuracy: {score}/10")

    avg_score = total_score / len(TEST_QUERIES)
    avg_time = total_time / len(TEST_QUERIES)
    
    print("\n" + "="*40)
    print("         FINAL REPORT CARD")
    print("="*40)
    print(f"✅ Average Accuracy Score: {avg_score}/10")
    print(f"⚡ Average Response Time:   {avg_time:.2f} seconds")
    print("="*40 + "\n")

if __name__ == "__main__":
    rag = RAGPipeline()
    
    # ASK USER MODE
    mode = input("Choose Mode: [1] Chat  [2] Run Evaluation Suite: ")
    
    if mode == "2":
        run_evaluation_suite(rag)
    else:
        print("\n--- CHAT MODE (Type 'exit' to quit) ---")
        while True:
            q = input("\nYou: ")
            if q.lower() == "exit": break
            print(f"AI: {rag.generate_answer(q)}")