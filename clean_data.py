import json
import re

INPUT_FILE = "data/assessments.json"
OUTPUT_FILE = "data/clean_assessments.json"


def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_test_type(text):

    text = text.lower()

    if "personality" in text:
        return "Personality"

    if "cognitive" in text:
        return "Cognitive"

    if "technical" in text:
        return "Technical"

    if "behavior" in text:
        return "Behavioral"

    return "General"


def main():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []
    seen_urls = set()

    for item in data:

        url = item.get("url", "").strip()

        if not url:
            continue

        # remove duplicates
        if url in seen_urls:
            continue

        seen_urls.add(url)

        name = clean_text(item.get("name", ""))
        description = clean_text(item.get("description", ""))
        full_text = clean_text(item.get("full_text", ""))

        combined_text = f"{name}. {description}. {full_text}"

        assessment = {
            "name": name,
            "url": url,
            "description": description,
            "test_type": extract_test_type(combined_text),
            "search_text": combined_text[:5000]
        }

        cleaned.append(assessment)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(cleaned)} clean assessments")


if __name__ == "__main__":
    main()
    