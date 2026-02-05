def build_triples(relations):
    triples = []
    
    # We loop through the relations list we created in the previous step
    for r in relations:
        # The 'relations' list now has dictionaries like:
        # {"head": "John", "head_type": "PERSON", "relation": "WORKS_ON", ...}
        
        # We convert this into a standard Tuple: (Subject, Predicate, Object)
        # This is the format required by the graph_loader.py script
        new_triple = (
            r["head"],
            r["relation"],
            r["tail"]
        )
        
        # Prevent duplicates (e.g., if "John works at Infosys" appears twice)
        if new_triple not in triples:
            triples.append(new_triple)
            
    return triples