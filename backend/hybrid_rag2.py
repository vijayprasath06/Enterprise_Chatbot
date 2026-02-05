import os
import json
import time
import faiss
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

FAISS_INDEX = "vector_store.faiss"
METADATA_FILE = "faiss_metadata.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"

# --- CYPHER PROMPT ---
CYPHER_GENERATION_TEMPLATE = """
Task: Generate Cypher statement to query a graph database.
Instructions:
1. Use only the provided schema.
2. Do NOT use directional arrows. Use undirected relationships: (e1)-[:RELATION]-(e2).
3. Do NOT assume the 'type' is 'ASSOCIATED_WITH'. Allow ANY relationship type.
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
        print("--- INITIALIZING BACKEND ENGINE ---")
        
        # 1. Setup Vector Store
        if not os.path.exists(FAISS_INDEX):
            raise FileNotFoundError("Vector store missing!")
        self.index = faiss.read_index(FAISS_INDEX)
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        
        # 2. Setup Graph
        try:
            self.graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)
            self.graph.refresh_schema()
            print("✅ Neo4j Graph Connected")
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
                cypher_prompt=CYPHER_PROMPT,
                validate_cypher=True
            )

    def get_vector_context(self, query, k=3):
        query_vector = self.embedder.encode([query])
        # Search FAISS
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        context_list = []
        sources = []
        
        # Calculate Confidence Score (0-100%) based on L2 distance
        # Lower distance = better match.
        raw_score = distances[0][0]
        confidence = max(0, min(100, (1.5 - raw_score) * 100)) # Approximation

        for idx in indices[0]:
            if idx == -1: continue
            text = self.metadata[idx]['text']
            full_path = self.metadata[idx]['source']
            filename = os.path.basename(full_path) # Extract "report.pdf" from "C:/users/..."
            
            context_list.append(f"[Source: {filename}] {text[:300]}...") 
            sources.append(filename)
        
        return "\n".join(context_list), list(set(sources)), round(confidence, 1)

    def get_graph_context(self, query):
        if not self.graph:
            return "Graph database not available."
        try:
            response = self.graph_chain.invoke({"query": query})
            result = response['result']
            if isinstance(result, list) and result:
                clean_values = []
                for item in result:
                    clean_values.extend(item.values())
                return f"Direct Relationships: {', '.join([str(v) for v in clean_values])}"
            elif not result:
                return "No direct connections found in Knowledge Graph."
            else:
                return str(result)
        except Exception as e:
            return f"Graph Query Error: {str(e)}"

    def ask(self, query):
        start_time = time.time()
        
        # 1. Get Contexts
        vector_text, vector_sources, confidence = self.get_vector_context(query)
        graph_data = self.get_graph_context(query)
        
        # 2. Prepare Prompt (Natural Tone)
        full_context = f"""
        --- SOURCE 1: VECTOR DATABASE ---
        {vector_text}
        
        --- SOURCE 2: KNOWLEDGE GRAPH ---
        {graph_data}
        """
        
        template = """
        You are an Enterprise Chatbot for Infosys.
        Answer the user's question based ONLY on the context provided below.
        
        Guidelines:
        1. Be direct and professional.
        2. Do NOT say "According to the Knowledge Graph" or "According to the vector database". Just state the facts.
        3. If the answer is not in the context, say "I don't have that information in my internal database."
        
        Context:
        {context}
        
        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        # 3. Generate Answer
        answer_text = chain.invoke({"context": full_context, "question": query})
        
        # 4. Metrics
        latency = round(time.time() - start_time, 2)
        token_count = len(answer_text.split()) * 1.3 # Rough estimate
        
        return {
            "answer": answer_text,
            "thoughts": {
                "graph": graph_data,
                "vector": vector_text
            },
            "sources": vector_sources, # List of filenames ["report.pdf"]
            "metrics": {
                "latency": f"{latency}s",
                "confidence": f"{confidence}%",
                "tokens": int(token_count)
            }
        }