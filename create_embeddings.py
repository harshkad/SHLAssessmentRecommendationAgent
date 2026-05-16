import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

INPUT_FILE = "data/clean_assessments.json"

INDEX_FILE = "data/faiss.index"

METADATA_FILE = "data/metadata.json"


def main():

    print("Loading cleaned assessments...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        assessments = json.load(f)

    texts = [a["search_text"] for a in assessments]

    print("Loading embedding model...")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Creating embeddings...")

    embeddings = model.encode(texts, show_progress_bar=True)

    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    print("Creating FAISS index...")

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    faiss.write_index(index, INDEX_FILE)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2)

    print("Saved FAISS index and metadata")


if __name__ == "__main__":
    main()
    