import requests

API_KEY = "ff63bce5bcb9772f8a90f10f5e7ab5c4"

authors = [
    ("Dr Manoj Diwakar", "55253528500"),
    ("Dr Neeraj Kumar Pandey", "57193866895"),
    ("Dr Aditya Joshi", "58144718500"),
    ("Dr Sanjay Roka", "57202367574")
]

def get_papers(name, author_id):
    url = "https://api.elsevier.com/content/search/scopus"

    params = {
        "query": f"AU-ID({author_id})",
        "httpAccept": "application/json",
        "count": 25   # number of results per request
    }

    headers = {
        "X-ELS-APIKey": API_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    print(f"\n================ {name} ================\n")

    papers = data["search-results"]["entry"]

    for paper in papers:
        print("Title:", paper.get("dc:title"))
        print("Author:", paper.get("dc:creator"))
        print("Journal:", paper.get("prism:publicationName"))
        print("Date:", paper.get("prism:coverDate"))
        print("DOI:", paper.get("prism:doi"))
        print("Citations:", paper.get("citedby-count"))
        print("Document Type:", paper.get("subtypeDescription"))
        print("ISSN:", paper.get("prism:issn"))
        print("EID:", paper.get("eid"))
        print("-----------------------------------")

# 🔹 loop through all faculty
for name, aid in authors:
    get_papers(name, aid)
