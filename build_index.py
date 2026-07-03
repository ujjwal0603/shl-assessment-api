import json
import chromadb
from chromadb.utils import embedding_functions

def build_index():
    print("Loading catalog...")
    with open('shl_product_catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f, strict=False)

    print(f"Loaded {len(catalog)} items.")
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Use default embedding function (all-MiniLM-L6-v2)
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # Create or get collection
    collection = client.get_or_create_collection(name="shl_assessments", embedding_function=emb_fn)
    
    # Prepare data for insertion
    documents = []
    metadatas = []
    ids = []
    
    print("Preparing documents...")
    for idx, item in enumerate(catalog):
        if not isinstance(item, dict):
            continue
            
        # Create a rich text document for embedding
        name = item.get("name", "")
        desc = item.get("description", "")
        levels = item.get("job_levels_raw", "")
        keys = ", ".join(item.get("keys", []))
        
        doc = f"Name: {name}\nJob Levels: {levels}\nCategory/Keys: {keys}\nDescription: {desc}"
        
        documents.append(doc)
        
        # Store essential metadata for retrieval
        meta = {
            "name": name,
            "url": item.get("link", ""),
            "description": desc,
            # In the API response, we need 'test_type' but the catalog might not have it explicitly as "test_type"
            # It might be derived from "keys". Let's store keys.
            "keys": keys,
            "job_levels": levels
        }
        metadatas.append(meta)
        
        # ID as string
        ids.append(item.get("entity_id", str(idx)))

    print("Adding to ChromaDB (this may take a moment)...")
    
    # Add in batches to avoid overwhelming memory/limits
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
        print(f"Added batch {i//batch_size + 1}")
        
    print(f"Successfully indexed {collection.count()} items.")

if __name__ == "__main__":
    build_index()
