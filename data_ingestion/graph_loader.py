def load_triples(connector, triples):
    # Cypher query to create nodes and relationships
    query = """
    MERGE (h:Entity {name: $head})
    MERGE (t:Entity {name: $tail})
    MERGE (h)-[:RELATION {type: $relation}]->(t)
    """
    
    with connector.driver.session() as session:
        for h, r, t in triples:
            try:
                session.run(query, head=h, tail=t, relation=r)
            except Exception as e:
                print(f"Error inserting {h}-{r}-{t}: {e}")