
Fake Enterprise Dataset - NovaTech Solutions
==========================================

This synthetic dataset is designed for building and testing an AI Knowledge Graph / RAG pipeline.
Location: /mnt/data/fake_enterprise_dataset/data/

Contents:
- data/spreadsheets/employees.csv     (250 employees)
- data/spreadsheets/products.csv      (20 products)
- data/spreadsheets/tickets.csv       (800 tickets)
- data/emails/                        (300 plain-text emails email_1.txt ... email_300.txt)
- data/pdfs/                          (150 text 'reports' report_1.txt ...)
- data/meeting_notes/                 (200 meeting note files)
- data/contracts/                     (50 contract files)
- data/sql/enterprise.db              (SQLite DB with employees, products, tickets, projects tables)

Usage ideas:
- Use the emails and reports for NER and relation extraction.
- Use the CSVs and SQLite DB as structured sources to link entities.
- Use meeting notes and contracts for relationship and event extraction.
- Build embeddings over the text files for semantic search (FAISS/Chroma).
- The dataset is intentionally diverse to mimic real enterprise data.

Generated on: 2025-12-07 13:59:15
