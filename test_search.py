from app.retriever import search_assessments

results = search_assessments(
    "Java backend developer communication"
)

for r in results:

    print("\n")
    print("=" * 50)

    print("NAME:", r["name"])

    print("URL:", r["url"])
    