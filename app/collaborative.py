# app/collaborative.py
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from pathlib import Path

from .models import Rating
from .database import db

# CF model container
cf_model = None

# Minimum real ratings needed before we attempt to build the model
MIN_RATINGS_THRESHOLD = 20


def _load_ratings_from_db():
    """Pull all ratings from the database into a DataFrame."""
    ratings_df = pd.read_sql(
        db.session.query(Rating).statement,
        db.session.bind
    )
    return ratings_df


def generate_synthetic_ratings(manga_ids, n_users=200, seed=42):
    
    np.random.seed(seed)

    rating_weights = [0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.20, 0.12, 0.06]
    rating_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    records = []
    for user_num in range(1, n_users + 1):
        # Each user rates a random subset — not everyone rates everything
        n_ratings = np.random.randint(10, 50)
        rated_ids = np.random.choice(manga_ids, size=min(n_ratings, len(manga_ids)), replace=False)

        for manga_id in rated_ids:
            rating = np.random.choice(rating_values, p=rating_weights)
            records.append({
                'user_id': f'synthetic_{user_num}',
                'manga_id': int(manga_id),
                'rating': int(rating)
            })

    return pd.DataFrame(records)


def _safe_k(n_users, n_manga):
    
    max_possible = min(n_users, n_manga) - 1
    # Use small k for small datasets, cap at 20 for larger ones
    if max_possible <= 5:
        return max_possible
    elif max_possible <= 20:
        return max(2, max_possible // 2)
    else:
        return min(20, max_possible)


def build_cf_model(use_synthetic_if_needed=False):
    global cf_model

    ratings_df = _load_ratings_from_db()
    real_count = len(ratings_df)
    print(f"Real ratings in DB: {real_count}")

    using_synthetic = False
    if real_count < MIN_RATINGS_THRESHOLD:
        if not use_synthetic_if_needed:
            print("Not enough real ratings and synthetic data disabled.")
            return None

        print(f"Insufficient real ratings ({real_count} < {MIN_RATINGS_THRESHOLD}).")
        print("Generating synthetic ratings for model evaluation...")

        # Load manga IDs from the indexed CSV
        manga_csv = Path("models/manga_indexed.csv")
        if not manga_csv.exists():
            print("manga_indexed.csv not found — run build_models.py first.")
            return None

        manga_df = pd.read_csv(manga_csv)
        manga_ids = manga_df['id'].tolist()

        synthetic_df = generate_synthetic_ratings(manga_ids, n_users=200)
        print(f"Generated {len(synthetic_df)} synthetic ratings from 200 users.")

        # Combine real + synthetic
        ratings_df = pd.concat([ratings_df, synthetic_df], ignore_index=True)
        using_synthetic = True
        print(f"Total ratings for training: {len(ratings_df)}")

    # --- Step 3: Build user-item matrix ---
    user_ids = ratings_df['user_id'].unique()
    manga_ids = ratings_df['manga_id'].unique()

    user_map = {uid: i for i, uid in enumerate(user_ids)}
    manga_map = {mid: i for i, mid in enumerate(manga_ids)}

    user_indices = ratings_df['user_id'].map(user_map)
    manga_indices = ratings_df['manga_id'].map(manga_map)

    user_item_matrix = csr_matrix(
        (ratings_df['rating'], (user_indices, manga_indices)),
        shape=(len(user_map), len(manga_map))
    )

    print(f"User-item matrix: {user_item_matrix.shape} "
          f"(sparsity: {1 - user_item_matrix.nnz / (user_item_matrix.shape[0] * user_item_matrix.shape[1]):.3f})")

    # --- Step 4: SVD ---
    k = _safe_k(len(user_map), len(manga_map))
    print(f"Training SVD with k={k} latent factors...")

    U, sigma, Vt = svds(user_item_matrix.astype(float), k=k)
    sigma_diag = np.diag(sigma)

    # --- Step 5: Store model ---
    cf_model = {
        'U': U,
        'sigma': sigma_diag,
        'Vt': Vt,
        'user_map': user_map,
        'manga_map': manga_map,
        'using_synthetic': using_synthetic,
        'real_ratings_count': real_count,
        'k': k,
    }

    print(f"CF model built successfully. "
          f"({'synthetic-augmented' if using_synthetic else 'real data only'})")
    return cf_model

def get_cf_recommendations(user_id, manga_ids, top_n=10):
    
    if cf_model is None:
        print("CF model not built yet — call build_cf_model() first.")
        return []

    user_map = cf_model['user_map']
    manga_map = cf_model['manga_map']

    if user_id not in user_map:
        print(f"User '{user_id}' not in training data — falling back to CBF.")
        return []

    u_idx = user_map[user_id]
    user_vector = cf_model['U'][u_idx, :]
    user_predictions = user_vector @ cf_model['sigma'] @ cf_model['Vt']

    predictions = []
    for mid in manga_ids:
        if mid in manga_map:
            m_idx = manga_map[mid]
            predictions.append((mid, float(user_predictions[m_idx])))

    return sorted(predictions, key=lambda x: x[1], reverse=True)[:top_n]