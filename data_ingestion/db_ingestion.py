import sqlite3
from langchain_core.documents import Document

def process_database(db_path):
    docs = []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    cursor = conn.cursor()

    print(f"--- Connecting to Database: {db_path} ---")

    # ---------------------------------------------------------
    # 1. PROCESS EMPLOYEES
    # Schema: id, name, designation, department, email
    # ---------------------------------------------------------
    try:
        cursor.execute("SELECT name, designation, department, email FROM employees")
        rows = cursor.fetchall()
        
        for row in rows:
            # Construct a clear natural language sentence
            content = (
                f"Employee Profile: {row['name']} works as a {row['designation']} "
                f"in the {row['department']} department. "
                f"Email: {row['email']}."
            )
            
            docs.append(Document(
                page_content=content,
                metadata={
                    "source": "db", 
                    "table": "employees",
                    "row_type": "profile"
                }
            ))
        print(f"Loaded {len(rows)} employees.")
    except Exception as e:
        print(f"Error loading employees: {e}")

    # ---------------------------------------------------------
    # 2. PROCESS PRODUCTS
    # Schema: pid, name, description, revenue
    # ---------------------------------------------------------
    try:
        cursor.execute("SELECT name, description, revenue FROM products")
        rows = cursor.fetchall()
        
        for row in rows:
            content = (
                f"Product Info: The {row['name']} is a product described as: {row['description']}. "
                f"It generates a revenue of {row['revenue']}."
            )
            
            docs.append(Document(
                page_content=content,
                metadata={
                    "source": "db", 
                    "table": "products",
                    "row_type": "product_info"
                }
            ))
        print(f"Loaded {len(rows)} products.")
    except Exception as e:
        print(f"Error loading products: {e}")

    # ---------------------------------------------------------
    # 3. PROCESS TICKETS
    # Schema: ticket_id, customer, product, issue, assigned_to, status
    # ---------------------------------------------------------
    try:
        cursor.execute("SELECT customer, product, issue, assigned_to, status FROM tickets")
        rows = cursor.fetchall()
        
        for row in rows:
            content = (
                f"Support Ticket: Customer '{row['customer']}' reported an issue with '{row['product']}'. "
                f"Issue details: {row['issue']}. "
                f"This ticket is currently {row['status']} and is assigned to Agent {row['assigned_to']}."
            )
            
            docs.append(Document(
                page_content=content,
                metadata={
                    "source": "db", 
                    "table": "tickets",
                    "row_type": "support_ticket"
                }
            ))
        print(f"Loaded {len(rows)} tickets.")
    except Exception as e:
        print(f"Error loading tickets: {e}")

    # ---------------------------------------------------------
    # 4. PROCESS PROJECTS
    # Schema: proj_id, name, owner, budget
    # ---------------------------------------------------------
    try:
        cursor.execute("SELECT name, owner, budget FROM projects")
        rows = cursor.fetchall()
        
        for row in rows:
            content = (
                f"Project Record: The project '{row['name']}' is owned by {row['owner']}. "
                f"The allocated budget is {row['budget']}."
            )
            
            docs.append(Document(
                page_content=content,
                metadata={
                    "source": "db", 
                    "table": "projects",
                    "row_type": "project_record"
                }
            ))
        print(f"Loaded {len(rows)} projects.")
    except Exception as e:
        print(f"Error loading projects: {e}")

    conn.close()
    return docs

# Quick Test to verify it works
if __name__ == "__main__":
    # Update this path if necessary!
    DB_PATH = r"C:\Users\admin\Documents\NEW_INFOSYS_INTERNSHIP_PROJECT\fake_enterprise_dataset\data\sql\enterprise.db"
    
    docs = process_database(DB_PATH)
    if docs:
        print("\n--- PREVIEW (First 3 docs) ---")
        for d in docs[:3]:
            print(d.page_content)
            print("-" * 20)