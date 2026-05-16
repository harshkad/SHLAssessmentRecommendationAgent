import json
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEX_FILE = os.path.join(BASE_DIR, "data", "faiss.index")
METADATA_FILE = os.path.join(BASE_DIR, "data", "metadata.json")


print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading FAISS index...")
index = faiss.read_index(INDEX_FILE)

print("Loading metadata...")
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)


def search_assessments(query, top_k=5):

    # Convert query to embedding
    query_embedding = model.encode([query])

    query_embedding = np.array(query_embedding).astype("float32")

    # Search FAISS
    distances, indices = index.search(query_embedding, top_k)

    results = []

    for idx in indices[0]:

        if idx >= len(metadata):
            continue

        item = metadata[idx]

        results.append({
            "name": item["name"],
            "url": item["url"],
            "description": item["description"],
            "test_type": item["test_type"]
        })

    return results


if __name__ == "__main__":

    query = input("Enter hiring query: ")

    results = search_assessments(query)

    print("\nTop Matches:\n")

    for r in results:

        print("=" * 50)

        print("Name:", r["name"])

        print("Type:", r["test_type"])

        print("URL:", r["url"])

        print()
        