from .collaborative import get_cf_recommendations
from .recommender import get_cbf_scores, manga_df

def get_hybrid_recommendations(user_id, title, alpha=0.5, top_n=10):
    
    # Step 1: Content-based recommendations
    cbf_scores = get_cbf_scores(title, top_n=50)  # Get a bigger pool
    cbf_dict = {mid: score for mid, score in cbf_scores}

    # Step 2: Collaborative recommendations (for the same pool of manga IDs)
    manga_ids = [mid for mid, _ in cbf_scores]
    cf_scores = get_cf_recommendations(user_id, manga_ids, top_n=len(manga_ids))
    cf_dict = {mid: score for mid, score in cf_scores}

    # Step 3: Merge scores
    hybrid_scores = []
    
    # If CF returned nothing (new user), fall back to pure CBF
    if not cf_dict:
        for mid in manga_ids:
            hybrid_scores.append((mid, cbf_dict.get(mid, 0)))
    else:
        for mid in manga_ids:
            cbf = cbf_dict.get(mid, 0)
            cf = cf_dict.get(mid, 0)
            # Normalise CF score (1-10) to 0-1 range to match CBF
            cf_norm = cf / 10.0
            final_score = alpha * cbf + (1 - alpha) * cf_norm
            hybrid_scores.append((mid, final_score))

    # Step 4: Sort and return
    sorted_scores = sorted(hybrid_scores, key=lambda x: x[1], reverse=True)
    recommendations = []
    # Iterate through the top N results to build the dictionary list
    for mid, score in sorted_scores[:top_n]:
        manga_details = manga_df[manga_df['id'] == mid]
        
        
        if not manga_details.empty:
            manga_row = manga_details.iloc[0]
            
            
            rec_dict = {
                'id': int(mid),
                'title': manga_row.get('title', ''),
                'recommendation_score': round(score, 4),
                'genres': manga_row.get('genres', 'N/A'),
                'synopsis': manga_row.get('synopsis', ''),
                'image_url': manga_row.get('image_url', ''),
                'score': manga_row.get('score', 'N/A'),
                'authors': manga_row.get('authors', 'N/A'),
                'status': manga_row.get('status', 'N/A'),
                'chapters': manga_row.get('chapters', 'N/A'),
                'themes': manga_row.get('themes', ''),
                'demographics': manga_row.get('demographics', ''),
                'rank': manga_row.get('rank', 'N/A'),
                'popularity': manga_row.get('popularity', 'N/A')
            }
            recommendations.append(rec_dict)
            
    return recommendations
   
