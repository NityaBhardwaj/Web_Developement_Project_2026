import requests
import firebase_admin
from firebase_admin import credentials, db
import time

# 🔐 CONFIG
API_KEY = "ff63bce5bcb9772f8a90f10f5e7ab5c4"

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://research-paper-webscrapp-e6d2b-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

root = db.reference()

# 👨‍🏫 FACULTY LIST
authors = [
    ("Dr Manoj Diwakar", "55253528500"),
    ("Dr Neeraj Kumar Pandey", "57193866895"),
    ("Dr Aditya Joshi", "58144718500"),
    ("Dr Sanjay Roka", "57202367574")
]

# 🚀 FETCH PAPERS
def fetch_papers(author_id):
    url = "https://api.elsevier.com/content/search/scopus"

    params = {
        "query": f"AU-ID({author_id})",
        "httpAccept": "application/json",
        "count": 25,
        "sort": "-coverDate"
    }

    headers = {
        "X-ELS-APIKey": API_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    return data.get("search-results", {}).get("entry", [])


# 💾 STORE DATA
def store_data(faculty_name, author_id):

    # ✅ FIX: use author_id as unique key (NO push)
    faculty_id = author_id

    # Store faculty (only once or overwrite safely)
    root.child("faculties").child(faculty_id).set({
        "name": faculty_name,
        "author_id": author_id,
        "department": "CSE",
        "field": "Unknown"
    })

    print(f"\n📌 Processing {faculty_name}...\n")

    papers = fetch_papers(author_id)

    for paper in papers:

        eid = paper.get("eid")

        # 🔥 Skip if no EID
        if not eid:
            continue

        # 🔍 Check duplicate
        existing = root.child("papers").child(faculty_id)\
    .order_by_child("eid").equal_to(eid).get()

        if existing:
            continue

        # 📄 Extract data
        paper_data = {
            "title": paper.get("dc:title"),
            "year": int(paper.get("prism:coverDate", "0000")[:4]) if paper.get("prism:coverDate") else 0,

            "scopus_url": f"https://www.scopus.com/record/display.uri?eid={eid}",

            "doi": paper.get("prism:doi"),
            "doi_url": f"https://doi.org/{paper.get('prism:doi')}" if paper.get("prism:doi") else None,

            "faculty_id": faculty_id,
            "citations": int(paper.get("citedby-count", 0)),
            "eid": eid
        }

        # 💾 Store paper
        root.child("papers").child(faculty_id).push(paper_data)

        print("✔ Stored:", paper_data["title"])

    # 🔄 Update sync time
    root.child("sync_logs").child(faculty_id).set({
        "last_sync_time": int(time.time())
    })

    # ⏳ avoid API rate limit
    time.sleep(1)


# 🔁 MAIN LOOP
for name, aid in authors:
    store_data(name, aid)