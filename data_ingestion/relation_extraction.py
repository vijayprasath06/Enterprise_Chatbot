def extract_relations(entities):
    relations = []
    
    # --- UPDATED RULES AS PER YOUR REQUEST ---
    RELATIONSHIP_RULES = {
        ("PERSON", "WORK_OF_ART"): "WORKS_ON",    # Mapping 'Project' (often detected as Work of Art)
        ("PERSON", "ORG"): "ASSOCIATED_WITH",
        ("ORG", "PRODUCT"): "OFFERS_PRODUCT",
        ("WORK_OF_ART", "PRODUCT"): "USES_PRODUCT", # Project -> Product
        ("WORK_OF_ART", "ORG"): "OWNED_BY",         # Project -> Org
        ("ORG", "ORG"): "PARTNER_WITH"
    }
    
    # Loop through all entities in this chunk to find connections
    for i in range(len(entities)):
        for j in range(len(entities)):
            if i == j: continue # Skip self-loop
            
            ent1 = entities[i]
            ent2 = entities[j]
            
            # Create a key to check against our rules
            # We check both directions: (Label1, Label2)
            pair_key = (ent1["label"], ent2["label"])
            
            if pair_key in RELATIONSHIP_RULES:
                relation_type = RELATIONSHIP_RULES[pair_key]
                
                new_relation = {
                    "head": ent1["text"],
                    "head_type": ent1["label"], # Useful for debugging
                    "relation": relation_type,
                    "tail": ent2["text"],
                    "tail_type": ent2["label"]
                }
                
                # Check for duplicates before adding
                if new_relation not in relations:
                    relations.append(new_relation)
            
    return relations