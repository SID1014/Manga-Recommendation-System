import requests
import time
import pandas as pd

save_path = "Data/raw/manga.csv"

def fetch_manga(page):
    url=f"https://api.jikan.moe/v4/manga?page={page}&limit=25"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()["data"]
    
    records = []
    for item in data:
        records.append({
            "id":item["mal_id"],
            "title": item["title"],
            "synopsis": item.get("synopsis", ""),
            "genres": " ".join([g["name"] for g in item.get("genres", [])]),
            "score": item.get("score", 0),
            "image_url": item["images"]["jpg"]["image_url"]
        })
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    for i in range(1,40):
        print(f"getting page {i}")
        page_df= fetch_manga(i)
        if i == 1:
            # For the first page, write with the header
            page_df.to_csv(save_path, index=False, mode='w', header=True)
        else:
            # For all other pages, append without the header
            page_df.to_csv(save_path, index=False, mode='a', header=False)
        
        # --- RESPECT THE API RATE LIMIT ---
        print("Waiting 1 second before next request...")
        time.sleep(1) 