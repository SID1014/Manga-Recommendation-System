# build_models.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from pathlib import Path

DATA_PATH = Path("Data/Processed/processed_manga.csv")
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

def build_and_save():
    df = pd.read_csv(DATA_PATH)
    # Ensure required columns exist
    for col in ['id','title','genres','synopsis']:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col} in {DATA_PATH}")

    df['genres'] = df['genres'].fillna('').astype(str)
    df['synopsis'] = df['synopsis'].fillna('').astype(str)
    df['content'] = (df['genres'] + " " + df['synopsis']).astype(str)

    tfidf = TfidfVectorizer(stop_words='english', max_features=20000)
    tfidf_matrix = tfidf.fit_transform(df['content'])

    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    joblib.dump(tfidf, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(cosine_sim, MODELS_DIR / "cosine_sim.joblib")
    df.to_csv(MODELS_DIR / "manga_indexed.csv", index=False)

    print("Saved tfidf_vectorizer.joblib, cosine_sim.joblib, manga_indexed.csv")

if __name__ == "__main__":
    build_and_save()
