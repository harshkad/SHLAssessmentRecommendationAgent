import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/products/product-catalog/"


headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_catalog_links():
    """
    Scrape all assessment links from all catalog pages
    """

    assessment_links = set()

    page = 1

    while True:

        print(f"Scraping catalog page {page}...")

        # Pagination
        url = f"{CATALOG_URL}?start={12 * (page - 1)}"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Failed page")
            break

        soup = BeautifulSoup(response.text, "lxml")

        page_links = 0

        # Find all links
        for a in soup.find_all("a", href=True):

            href = a["href"]

            # Keep only assessment pages
            if "/products/product-catalog/view/" in href:

                full_url = BASE_URL + href

                full_url = full_url.replace("//products", "/products")

                if full_url not in assessment_links:
                    assessment_links.add(full_url)
                    page_links += 1

        print(f"Found {page_links} assessments on page {page}")

        # Stop when no new links found
        if page_links == 0:
            break

        page += 1

        time.sleep(1)

    return list(assessment_links)

def scrape_assessment(url):

    print(f"Scraping assessment: {url}")

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "lxml")

    try:

        title = soup.find("h1").text.strip()

    except:
        title = "Unknown"

    try:
        description = soup.find("meta", attrs={"name": "description"})["content"]

    except:
        description = ""

    page_text = soup.get_text(" ", strip=True)

    assessment_data = {
        "name": title,
        "url": url,
        "description": description,
        "full_text": page_text
    }

    return assessment_data


def main():

    links = get_catalog_links()

    print(f"Found {len(links)} assessments")

    all_assessments = []

    for link in links:

        data = scrape_assessment(link)

        if data:
            all_assessments.append(data)

        time.sleep(1)

    with open("../data/assessments.json", "w", encoding="utf-8") as f:

        json.dump(all_assessments, f, indent=2, ensure_ascii=False)

    print("Saved assessments.json")


if __name__ == "__main__":
    main()
