import json
import os

# Import your helper functions
from ner_extraction import extract_entities
from relation_extraction import extract_relations
from triple_builder import build_triples
from neo4j_connection import Neo4jConnector
from graph_loader import load_triples

# --- CONFIGURATION ---
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Umeswari@123"  # <--- CHECK THIS
JSON_FILE = "processed_data.json"

def main():
    print("--- STARTING GRAPH CONSTRUCTION (WITH JSON EXPORT) ---")
    
    # 1. Load Data
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            documents = json.load(f)
        print(f"Loaded {len(documents)} docs.")
    except FileNotFoundError:
        print("Error: processed_data.json missing.")
        return

    connector = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    # --- STORAGE FOR INTERMEDIATE OUTPUTS ---
    all_entities_export = []
    all_relations_export = []
    all_triples_export = []
    
    all_triples_for_db = [] # This list is for Neo4j

    # 2. Process Data
    print("Processing documents...")
    for i, doc in enumerate(documents):
        text = doc["content"]
        
        # A. NER
        entities = extract_entities(text)
        # Save to export list (we add the source text ID for context)
        all_entities_export.append({
            "doc_id": i, 
            "found_entities": entities
        })
        
        # B. RELATIONS
        relations = extract_relations(entities)
        all_relations_export.append({
            "doc_id": i, 
            "found_relations": relations
        })
        
        # C. TRIPLES
        triples = build_triples(relations)
        all_triples_export.append({
            "doc_id": i, 
            "triples": triples
        })
        
        all_triples_for_db.extend(triples)

    # 3. SAVE JSON FILES (For your Mentor)
    print("\n--- Saving Intermediate JSON Files ---")
    
    with open("output_1_entities.json", "w", encoding="utf-8") as f:
        json.dump(all_entities_export, f, indent=4)
    print("Saved 'output_1_entities.json'")

    with open("output_2_relations.json", "w", encoding="utf-8") as f:
        json.dump(all_relations_export, f, indent=4)
    print("Saved 'output_2_relations.json'")

    with open("output_3_triples.json", "w", encoding="utf-8") as f:
        json.dump(all_triples_export, f, indent=4)
    print("Saved 'output_3_triples.json'")

    # 4. Load into Neo4j
    print(f"\nLoading {len(all_triples_for_db)} triples into Neo4j...")
    load_triples(connector, all_triples_for_db)
    connector.close()
    print("SUCCESS: Graph Built.")

if __name__ == "__main__":
    main()