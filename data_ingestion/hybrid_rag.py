import os
import json
import faiss
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

FAISS_INDEX = "../backend/vector_store.faiss"
METADATA_FILE = "../backend/faiss_metadata.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

# --- CUSTOM CYPHER PROMPT (Fixes the "Entity" guessing issue) ---
CYPHER_GENERATION_TEMPLATE = """
Task: Generate Cypher statement to query a graph database.
Instructions:
1. Use only the provided schema.
2. Do NOT use directional arrows. Use undirected relationships: (e1)-[:RELATION]-(e2).
3. Do NOT assume the 'type' is 'ASSOCIATED_WITH'. Allow ANY relationship type if not sure.
4. Use case-insensitive matching: WHERE toLower(e.name) CONTAINS toLower('keyword').
5. Return distinct names.

Schema:
{schema}

The question is:
{question}
"""
CYPHER_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], 
    template=CYPHER_GENERATION_TEMPLATE
)

class HybridRAG:
    def __init__(self):
        print("--- INITIALIZING HYBRID RAG (Graph + Vector) ---")
        
        # 1. Setup Vector Store
        if not os.path.exists(FAISS_INDEX):
            raise FileNotFoundError("Vector store missing!")
        self.index = faiss.read_index(FAISS_INDEX)
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        print("✅ Vector Store Loaded")

        # 2. Setup Graph
        try:
            self.graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)
            self.graph.refresh_schema() # CRITICAL: Reads your actual labels (Person, Org)
            print(f"✅ Neo4j Connected. Schema: {self.graph.schema[:100]}...") # Print first 100 chars of schema
        except Exception as e:
            print(f"❌ Neo4j Failed: {e}")
            self.graph = None

        # 3. Setup LLM
        self.llm = ChatGroq(model_name=LLM_MODEL, temperature=0)
        
        # 4. Setup Graph Chain
        if self.graph:
            self.graph_chain = GraphCypherQAChain.from_llm(
                self.llm, 
                graph=self.graph, 
                verbose=True,
                allow_dangerous_requests=True,
                cypher_prompt=CYPHER_PROMPT, # Use our strict prompt
                validate_cypher=True
            )

    def get_vector_context(self, query, k=3):
        query_vector = self.embedder.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        context_list = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: continue
            text = self.metadata[idx]['text']
            source = self.metadata[idx]['source']
            context_list.append(f"[Source: {source}] {text}")
        
        return "\n".join(context_list)

    def get_graph_context(self, query):
        """Retrieve structured facts from Neo4j and clean them for the AI"""
        if not self.graph:
            return "Graph database not available."
        
        try:
            # The chain handles the Cypher generation internally
            response = self.graph_chain.invoke({"query": query})
            result = response['result']
            
            # --- NEW CLEANING LOGIC ---
            # If we get a list of dictionaries (which is what Neo4j returns)
            if isinstance(result, list) and result:
                # We extract just the values. 
                # From [{'e2.name': 'College A'}, {'e2.name': 'College B'}]
                # To "College A, College B"
                clean_values = []
                for item in result:
                    clean_values.extend(item.values()) # Grab the values inside the dict
                
                formatted_string = ", ".join([str(v) for v in clean_values])
                return f"[Graph Database Hit] Found these connections: {formatted_string}"
            
            elif not result:
                return "[Graph Database Result] Empty (No direct connections found)"
            else:
                return f"[Graph Database Result] {result}"
                
        except Exception as e:
            return f"[Graph Error] {str(e)}"

    def hybrid_answer(self, query):
        # A. Parallel Retrieval
        vector_data = self.get_vector_context(query)
        graph_data = self.get_graph_context(query)
        
        # B. Combine
        full_context = f"""
        --- SOURCE 1: VECTOR DATABASE (Text) ---
        {vector_data}
        
        --- SOURCE 2: KNOWLEDGE GRAPH (Relationships) ---
        {graph_data}
        """
        
        # C. Generate Answer (UPDATED PROMPT)
        template = """
        You are an advanced AI Assistant integrating two databases.
        
        INSTRUCTIONS:
        1. Analyze "SOURCE 2: KNOWLEDGE GRAPH" first. 
           - If it contains a list of items like [{{'e2.name': 'Value'}}], these are POSITIVE HITS.
           - Do NOT say "The graph result is empty" if this list exists.
           - Extract names from this list to answer the question.
        2. Then, use "SOURCE 1: VECTOR DATABASE" for additional details or if the Graph is truly empty (e.g., "[]").
        3. Combine both sources into a professional answer.
        
        Context:
        {context}
        
        Question: {question}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({"context": full_context, "question": query}), full_context

    def evaluate_response(self, query, answer, context):
        # Simple 1-10 Grading
        eval_template = """
        Rate the AI Answer (1-10) for Relevance to the Question.
        Output ONLY the number.
        
        Question: {query}
        Answer: {answer}
        """
        try:
            prompt = ChatPromptTemplate.from_template(eval_template)
            chain = prompt | self.llm | StrOutputParser()
            score = chain.invoke({"query": query, "answer": answer})
            return score.strip()
        except:
            return "N/A"

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    bot = HybridRAG()
    
    while True:
        print("\n" + "="*30)
        print("   HYBRID RAG SYSTEM")
        print("="*30)
        print("1. Chat Mode")
        print("2. Evaluation Mode (Test Suite)")
        print("3. Exit")
        
        choice = input("Select Mode (1-3): ")
        
        if choice == "1":
            print("\n--- CHAT MODE ---")
            while True:
                q = input("\nYou: ")
                if q.lower() in ["exit", "back"]: break
                
                print("Thinking...", end="", flush=True)
                answer, _ = bot.hybrid_answer(q)
                print(f"\rAI: {answer}")

        elif choice == "2":
            print("\n--- EVALUATION MODE ---")
            questions = [
                
                # 1. The Methodology Question (Target: "Forrester Wave Methodology")
                "What methodology is associated with Forrester?",
                # 2. i dont know question (Target: "Infosys Knowledge Institute")
                "Who will win the next cricket world cup?",

                # 3. The Stock Market Question (Target: "NASDAQ", "NYSE")
                "Which stock exchange is Infosys listed on?",

                # 4. The Certification Question (Target: "ISO9001/TickIT")
                "What certifications like ISO9001 are mentioned?",

                # 5. The Motto Question (Target: "Insight, Innovation, Acceleration")
                "What company uses the motto 'Insight, Innovation, Acceleration'?"
            ]
            
            for q in questions:
                print(f"\n❓ Question: {q}")
                start = time.time()
                answer, context = bot.hybrid_answer(q)
                latency = time.time() - start
                score = bot.evaluate_response(q, answer, context)
                
                print(f"💡 Answer: {answer}")
                print(f"⏱️ Time: {latency:.2f}s | ⭐ Relevance: {score}/10")
        
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")