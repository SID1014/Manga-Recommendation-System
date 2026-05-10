import requests
import time
import pandas as pd
from pathlib import Path

RAW_PATH = Path("/Data/Raw/manga.csv")
RAW_PATH.parent.mkdir(parents=True, exist_ok=True)

MIN_SCORE = 7.5
MIN_SCORED_BY = 1000

def extract_names(items):

    if not items:
        return ""
    return " ".join([item["name"] for item in items if "name" in item])

def fetch_manga(page):
    url = f"https://api.jikan.moe/v4/manga?page={page}&limit=25&order_by=score&sort=desc"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()["data"]

    records = []
    for item in data:
        score = item.get("score") or 0
        scored_by = item.get("scored_by") or 0

   
        if score < MIN_SCORE or scored_by < MIN_SCORED_BY:
            continue

        authors = item.get("authors", [])
        author_names = " ".join([a.get("name", "") for a in authors])

        records.append({

            "id": item["mal_id"],
            "title": item.get("title", ""),
            "title_english": item.get("title_english", ""),   
            "type": item.get("type", ""),                     
            "synopsis": item.get("synopsis", ""),
            "genres": extract_names(item.get("genres", [])),
            "themes": extract_names(item.get("themes", [])),  
            "demographics": extract_names(item.get("demographics", [])),  
            "authors": author_names,
            "score": score,
            "scored_by": scored_by,
            "rank": item.get("rank"),
            "popularity": item.get("popularity"),
            "members": item.get("members", 0),
            "favorites": item.get("favorites", 0),
            "status": item.get("status", ""),                 
            "chapters": item.get("chapters"),                
            "year": item.get("year"),
            "image_url": item["images"]["jpg"]["image_url"],
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    all_dfs = []
    empty_pages = 0

    for i in range(1, 80):
        print(f"Fetching page {i}...")
        try:
            page_df = fetch_manga(i)

            if page_df.empty:
                empty_pages += 1
                print(f"  No qualifying manga on page {i} (empty streak: {empty_pages})")
                if empty_pages >= 3:
                    print("Stopping — 3 consecutive empty pages.")
                    break
            else:
                empty_pages = 0
                print(f"  {len(page_df)} manga added from page {i}")
                all_dfs.append(page_df)

        except requests.exceptions.HTTPError as e:
            print(f"  HTTP error on page {i}: {e}")
            time.sleep(3)
            continue

        time.sleep(1)  

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.drop_duplicates(subset=["id"], inplace=True)
        final_df.sort_values("score", ascending=False, inplace=True)
        final_df.to_csv(RAW_PATH, index=False)

        print(f"\nDone! Saved {len(final_df)} manga to {RAW_PATH}")
        print(f"Score range: {final_df['score'].min():.2f} - {final_df['score'].max():.2f}")
        print(f"\nColumn summary:")
        print(final_df.dtypes)
        print(f"\nSample titles:\n{final_df['title'].head(10).to_string()}")
    else:
        print("No manga met the criteria.")