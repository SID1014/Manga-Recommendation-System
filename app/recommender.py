# app/recommender.py
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import random




MODELS_DIR = Path("models")

def load_models():
    # If models missing, user should run build_models.py
    tfidf = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    cosine_sim = joblib.load(MODELS_DIR / "cosine_sim.joblib")
    df = pd.read_csv(MODELS_DIR / "manga_indexed.csv")
    # Build map
    title_to_idx = {t.lower(): idx for idx, t in enumerate(df['title'].astype(str))}
    return tfidf, cosine_sim, df, title_to_idx

tfidf, cosine_sim, manga_df, title_to_idx = load_models()

def find_closest_title(query):
    q = query.strip().lower()
    if q in title_to_idx:
        return q, title_to_idx[q]
   
    for title, idx in title_to_idx.items():
        if q in title:
            return title, idx
    return None, None

def get_cbf_recommendations(manga_title, top_n=8):
    _, idx = find_closest_title(manga_title)
    if idx is None:
        # return top popular by score if can't find title
        top = manga_df.nlargest(top_n * 3, 'score').sample(top_n)
        return top.to_dict(orient='records')

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1: top_n+1]
    indices = [i for i, s in sim_scores]
    cols = ['id','title','genres','synopsis','image_url','score','authors','status','chapters','themes','demographics','rank','popularity']
    existing_cols = [c for c in cols if c in manga_df.columns]
    results = manga_df.iloc[indices][existing_cols]
    
    # short synopsis
    if 'synopsis' in results.columns:
        results['synopsis'] = results['synopsis'].fillna('')
    
    return results.to_dict(orient='records')



def get_random_manga_samples(df, n=10):
    
    sample_df = df.sample(n=n)
    return sample_df.to_dict(orient='records')

def get_cbf_scores(title, top_n=10):
    
    _, idx = find_closest_title(title)
    if idx is None:
        return []

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

    results = [(int(manga_df.iloc[i]['id']), score) for i, score in sim_scores]
    return results
