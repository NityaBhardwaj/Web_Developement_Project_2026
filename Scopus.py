import os
import time
import json
import requests
from typing import Dict, Any, List, Optional

# ----------------------------
# 1) CONFIG (edit these)
# ----------------------------
API_KEY = os.getenv("ELS_API_KEY", "PASTE_YOUR_API_KEY_HERE")
INST_TOKEN = os.getenv("ELS_INSTTOKEN", "")  # optional (leave "" if you don't have it)

AFFILIATION_ID = "PASTE_AFID_HERE"  # e.g. "60017098"
COUNT_PER_PAGE = 25                # Scopus typically supports 25; keep <= 25 for safety
MAX_RESULTS_TO_FETCH = 200         # change as you need (e.g., 1000)

OUT_FILE = "scopus_affiliation_papers.json"

# ----------------------------
# 2) HELPERS
# ----------------------------
BASE_URL = "https://api.elsevier.com/content/search/scopus"


def build_headers() -> Dict[str, str]:
    if not API_KEY or API_KEY == "PASTE_YOUR_API_KEY_HERE":
        raise ValueError("Please set your API key in API_KEY or environment variable ELS_API_KEY.")

    headers = {
        "X-ELS-APIKey": API_KEY,
        "Accept": "application/json",
    }
    if INST_TOKEN:
        headers["X-ELS-Insttoken"] = INST_TOKEN
    return headers


def scopus_search(query: str, start: int, count: int) -> Dict[str, Any]:
    params = {
        "query": query,
        "start": start,
        "count": count,
    }
    r = requests.get(BASE_URL, headers=build_headers(), params=params, timeout=30)
    # Helpful debugging if something fails:
    if r.status_code != 200:
        raise RuntimeError(
            f"HTTP {r.status_code}\nURL: {r.url}\nResponse: {r.text[:1200]}"
        )
    return r.json()


def extract_entries(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return payload.get("search-results", {}).get("entry", []) or []


def main() -> None:
    query = f"AF-ID({AFFILIATION_ID})"
    all_entries: List[Dict[str, Any]] = []

    start = 0
    while start < MAX_RESULTS_TO_FETCH:
        remaining = MAX_RESULTS_TO_FETCH - start
        count = min(COUNT_PER_PAGE, remaining)

        data = scopus_search(query=query, start=start, count=count)
        entries = extract_entries(data)

        if not entries:
            break

        all_entries.extend(entries)
        start += len(entries)

        # Respect rate limits (small delay helps avoid 429)
        time.sleep(0.4)

        # If returned less than requested, likely end of results
        if len(entries) < count:
            break

    # Save raw entries (best for projects)
    out = {
        "query": query,
        "fetched": len(all_entries),
        "entries": all_entries,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"✅ Done. Fetched {len(all_entries)} records.")
    print(f"📄 Saved to: {OUT_FILE}")

    # Print a small preview
    for i, e in enumerate(all_entries[:5], start=1):
        title = e.get("dc:title")
        year = (e.get("prism:coverDate") or "")[:4]
        creator = e.get("dc:creator")
        citedby = e.get("citedby-count")
        print(f"{i}. {title} | {year} | {creator} | cited-by: {citedby}")


if __name__ == "__main__":
    main()
