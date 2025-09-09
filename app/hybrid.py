from .collaborative import get_cf_recommendations
from .recommender import get_cbf_scores, manga_df

def get_hybrid_recommendations(user_id, title, alpha=0.5, top_n=10):
    """
    Combine CBF + CF scores for final hybrid recommendations.
    """
    # Step 1: Content-based recommendations
    cbf_scores = get_cbf_scores(title, top_n=50)  # Get a bigger pool
    cbf_dict = {mid: score for mid, score in cbf_scores}

    # Step 2: Collaborative recommendations (for the same pool of manga IDs)
    manga_ids = [mid for mid, _ in cbf_scores]
    cf_scores = get_cf_recommendations(user_id, manga_ids, top_n=len(manga_ids))
    cf_dict = {mid: score for mid, score in cf_scores}

    # Step 3: Merge scores
    hybrid_scores = []
    for mid in manga_ids:
        cbf = cbf_dict.get(mid, 0)
        cf = cf_dict.get(mid, 0)
        final_score = alpha * cbf + (1 - alpha) * cf
        hybrid_scores.append((mid, final_score))

    # Step 4: Sort and return
    sorted_scores = sorted(hybrid_scores, key=lambda x: x[1], reverse=True)
    recommendations = []
    # Iterate through the top N results to build the dictionary list
    for mid, score in sorted_scores[:top_n]:
        # Find the manga's details in the main DataFrame
        manga_details = manga_df[manga_df['id'] == mid]
        
        # Make sure we found the manga before proceeding
        if not manga_details.empty:
            # Get the first matching row (should be only one)
            manga_row = manga_details.iloc[0]
            
            # Create a dictionary with all the desired fields
            rec_dict = {
                'id': int(mid),
                'title': manga_row['title'],
                'recommendation_score': round(score, 4), # The calculated hybrid score
                # --- Add any other fields you want from manga_df here ---
                'genres': manga_row.get('genres', 'N/A'), # Using .get is safer if a column might not exist
                'synopsis': manga_row.get('synopsis', ''),
                'image_url': manga_row.get('image_url', '')
            }
            recommendations.append(rec_dict)
            
    return recommendations
   
