import chromadb
import requests
from fuzzysearch import find_near_matches


LM_STUDIO_URL = "http://localhost:1234/v1/embeddings"  # Use the correct embedding endpoint


def create_drug_collection(drug_name):
    drug_name = drug_name.strip()
    client = chromadb.PersistentClient(path="./chroma_db")
    existing_collections = [col.name for col in client.list_collections()]

    if drug_name in existing_collections:
        print(f"Collection '{drug_name}' already exists. Skipping creation.")
        collection = client.get_collection(name=drug_name)
    else:
        print(f"Creating collection '{drug_name}'...")
        collection = client.create_collection(name=drug_name)
    return collection




# Function to send request to LM Studio and get embeddings
def get_embedding(text):
    """Sends text to LM Studio and retrieves the embedding."""
    payload = {
        "model": "text-embedding-nomic-embed-text-v1.5",  # Use the correct model identifier
        "input": text  # For embedding, use 'input' instead of 'messages'
    }

    try:
        response = requests.post(LM_STUDIO_URL, json=payload)
        response_data = response.json()

        if "data" in response_data and response_data["data"]:
            return response_data["data"][0]["embedding"]
        else:
            print(f"Error: No embedding found for '{text}'")
            return None
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

