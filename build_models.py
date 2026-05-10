# build_models.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import numpy as np
from pathlib import Path

DATA_PATH = Path("Data/Processed/processed_manga.csv")
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

# Required columns — must exist in processed CSV
REQUIRED_COLS = ['id', 'title', 'genres', 'synopsis', 'image_url']

# Optional enrichment columns — used if available, skipped if not
OPTIONAL_COLS = ['themes', 'demographics', 'authors']


def build_content_string(df):
    """
    Combines available text features into a single content string per manga.
    Weighted by repeating genres/themes to give them more influence over
    the long-tail words in synopsis.
    """
    content = pd.Series([''] * len(df), index=df.index)

    # Genres — repeat twice to upweight them in TF-IDF
    genres = df['genres'].fillna('').astype(str)
    content = content + genres + ' ' + genres + ' '

    # Optional fields — add if present and non-empty
    for col in OPTIONAL_COLS:
        if col in df.columns:
            content = content + df[col].fillna('').astype(str) + ' '

    # Synopsis — main body of text
    content = content + df['synopsis'].fillna('').astype(str)

    return content.str.lower().str.strip()


def build_and_save():
    # --- Load ---
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} manga from {DATA_PATH}")

    # --- Validate required columns ---
    for col in REQUIRED_COLS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}' in {DATA_PATH}")

    # --- Report optional columns found ---
    found_optional = [c for c in OPTIONAL_COLS if c in df.columns]
    missing_optional = [c for c in OPTIONAL_COLS if c not in df.columns]
    print(f"Optional enrichment columns found: {found_optional}")
    if missing_optional:
        print(f"Optional columns not found (skipped): {missing_optional}")

    # --- Build content string ---
    df['content'] = build_content_string(df)

    avg_len = df['content'].apply(len).mean()
    empty_count = (df['content'].str.strip() == '').sum()
    print(f"Content string built — avg length: {avg_len:.0f} chars, empty: {empty_count}")

    # --- TF-IDF Vectorisation ---
    # max_features=5000 is appropriate for a 500-2000 title dataset
    # ngram_range=(1,2) captures bigrams like 'martial arts', 'slice life'
    # min_df=2 removes terms that only appear in one manga (noise)
    tfidf = TfidfVectorizer(
        stop_words='english',
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        sublinear_tf=True   # dampens effect of very frequent terms
    )
    tfidf_matrix = tfidf.fit_transform(df['content'])
    print(f"TF-IDF matrix: {tfidf_matrix.shape} — vocab size: {len(tfidf.vocabulary_)}")

    # --- Cosine Similarity Matrix ---
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print(f"Cosine similarity matrix: {cosine_sim.shape}")

    # --- Evaluation Stats (for report) ---
    # Average similarity of top-10 recommendations across 50 random samples
    sample_indices = np.random.choice(len(df), size=min(50, len(df)), replace=False)
    avg_sim_scores = []
    for idx in sample_indices:
        sims = cosine_sim[idx]
        top10 = np.sort(sims)[::-1][1:11]  # exclude self (index 0)
        avg_sim_scores.append(top10.mean())

    avg_top10_sim = np.mean(avg_sim_scores)
    print(f"\n--- CBF Evaluation ---")
    print(f"Average Top-10 Cosine Similarity: {avg_top10_sim:.4f}")
    print(f"(Higher = recommendations are more content-similar to query manga)")

    
    joblib.dump(tfidf, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(cosine_sim, MODELS_DIR / "cosine_sim.joblib")
    df.to_csv(MODELS_DIR / "manga_indexed.csv", index=False)

    print(f"\nSaved to {MODELS_DIR}/:")
    print("  tfidf_vectorizer.joblib")
    print("  cosine_sim.joblib")
    print("  manga_indexed.csv")
    print(f"\nCBF Average Top-10 Similarity Score: {avg_top10_sim:.4f} ")


if __name__ == "__main__":
    build_and_save()