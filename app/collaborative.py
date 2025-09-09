import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds

from .models import Rating
from .database import db

# CF model container
# The model will now store the SVD components and mappings
cf_model = None

def build_cf_model():
    """
    Builds the SVD-based collaborative filtering model using SciPy.
    """
    global cf_model
    
    # Load ratings from the database
    ratings_df = pd.read_sql(db.session.query(Rating).statement, db.session.bind)

    if ratings_df.empty or len(ratings_df) < 20: # SVD needs a reasonable amount of data
        print("Not enough ratings available to build the CF model.")
        return None

    # --- Data Preparation ---
    # Create unique integer mappings for users and mangas
    user_ids = ratings_df['user_id'].unique()
    manga_ids = ratings_df['manga_id'].unique()
    
    user_map = {id: i for i, id in enumerate(user_ids)}
    manga_map = {id: i for i, id in enumerate(manga_ids)}

    # Create inverse mappings to retrieve original IDs later
    user_inv_map = {i: id for id, i in user_map.items()}
    manga_inv_map = {i: id for id, i in manga_map.items()}

    # Map original IDs to matrix indices
    user_indices = ratings_df['user_id'].map(user_map)
    manga_indices = ratings_df['manga_id'].map(manga_map)

    # --- Create the User-Item Sparse Matrix ---
    # csr_matrix is efficient for sparse data (most users haven't rated most mangas)
    user_item_matrix = csr_matrix((ratings_df['rating'], (user_indices, manga_indices)),
                                  shape=(len(user_map), len(manga_map)))

    # --- SVD Model Training ---
    # Decompose the matrix. 'k' is the number of latent factors (a hyperparameter).
    # svds is used for sparse matrices.
    k = 50 
    U, sigma, Vt = svds(user_item_matrix, k=k)

    # Sigma is returned as a 1D array, convert it to a diagonal matrix
    sigma = np.diag(sigma)

    # Store all necessary components for prediction
    cf_model = {
        'U': U,
        'sigma': sigma,
        'Vt': Vt,
        'user_map': user_map,
        'manga_map': manga_map
    }
    
    print("CF Model trained successfully using SciPy.")
    return cf_model


def get_cf_recommendations(user_id, manga_ids, top_n=10):
    """
    Generate CF-based predictions for a given user and list of manga IDs using the SciPy model.
    """
    if cf_model is None:
        print("CF model is not available.")
        return []

    # Unpack the model components
    U = cf_model['U']
    sigma = cf_model['sigma']
    Vt = cf_model['Vt']
    user_map = cf_model['user_map']
    manga_map = cf_model['manga_map']

    # Check if the user exists in the model's training data
    if user_id not in user_map:
        print(f"User {user_id} not in the training data. Cannot provide recommendations.")
        return []

    # Get the internal index for the user
    user_index = user_map[user_id]
    
    # --- Prediction ---
    # Get the user's latent factor vector
    user_vector = U[user_index, :]
    
    # Predict ratings for all mangas for this user by reconstructing their row in the matrix
    # R_hat = U @ sigma @ Vt
    user_predictions = user_vector @ sigma @ Vt

    predictions = []
    for mid in manga_ids:
        # Check if the manga was in the training data
        if mid in manga_map:
            manga_index = manga_map[mid]
            # Get the estimated rating from the full prediction vector
            estimated_rating = user_predictions[manga_index]
            predictions.append((mid, estimated_rating))

    # Sort by the estimated rating in descending order
    sorted_preds = sorted(predictions, key=lambda x: x[1], reverse=True)
    
    return sorted_preds[:top_n]