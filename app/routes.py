from flask_login import current_user, login_required
from .models import Rating
from .database import db
from flask import Blueprint, render_template, request, redirect,url_for,session,flash
from .recommender import get_cbf_recommendations,manga_df,get_random_manga_samples,get_cbf_scores
from .hybrid import get_hybrid_recommendations

main = Blueprint('main', __name__)


@main.route("/")
def index():
    recommendations = []

    if current_user.is_authenticated:
        # Logged-in user
        has_ratings = Rating.query.filter_by(user_id=current_user.id).count() > 0
        if not has_ratings:
            return redirect(url_for("main.onboarding"))
        user_ratings_count = Rating.query.filter_by(user_id=current_user.id).count()

        if user_ratings_count >= 3:
            # Hybrid recommendations
            # Use their most recently rated manga as a seed
            last_rating = Rating.query.filter_by(user_id=current_user.id).order_by(Rating.id.desc()).first()
            seed_title = manga_df[manga_df['manga_id'] == last_rating.manga_id]['title'].values[0]
            recommendations = get_hybrid_recommendations(current_user.id, seed_title, alpha=0.5, top_n=10)
        else:
            # Not enough ratings → random diverse recommendations
            recommendations = manga_df.sample(10)[['title', 'genres']].to_dict(orient='records')

    else:
        # Guest user
        if 'guest_ratings' not in session or len(session['guest_ratings']) == 0:
            return redirect(url_for("main.onboarding"))
        guest_history = session.get('guest_manga_history', [])

        if guest_history:
            # Use guest's last viewed manga for CBF
            last_manga_id = guest_history[-1]
            seed_title = manga_df[manga_df['manga_id'] == last_manga_id]['title'].values[0]
            cbf_recs = get_cbf_scores(seed_title, top_n=10)
            recommendations = [{'title': t, 'genre': manga_df[manga_df['title'] == t]['genre'].values[0]} for t, _ in cbf_recs]
        else:
            # No history → random diverse recommendations
            recommendations = manga_df.sample(10)[['title', 'genres']].to_dict(orient='records')

    return render_template("index.html", recommendations=recommendations)



@main.route("/recommend", methods=["GET","POST"])
def recommend():
    print("Is user authenticated?", current_user.is_authenticated)

    if request.method == 'POST':
        title = request.form.get('title')
    
        if current_user.is_authenticated:
            user_ratings_count = Rating.query.filter_by(user_id=current_user.id).count()
            if user_ratings_count >= 3:
                print("hybrid")
                recs = get_hybrid_recommendations(current_user.id, title, alpha=0.5, top_n=8)
            else:
                print("Non-hybrid")
                recs = get_cbf_recommendations(title, top_n=8)
        else:
            print("Non Hybrid")
            recs = get_cbf_recommendations(title, top_n=8)
    
        return render_template("results.html", title=title, recommendations=recs)
    title = request.args.get('title')
    if current_user.is_authenticated:
            user_ratings_count = Rating.query.filter_by(user_id=current_user.id).count()
            if user_ratings_count >= 3:
                print("hybrid")
                recs = get_hybrid_recommendations(current_user.id, title, alpha=0.5, top_n=8)
            else:
                print("Non-hybrid")
                recs = get_cbf_recommendations(title, top_n=8)
    else:
            print("Non Hybrid")
            recs = get_cbf_recommendations(title, top_n=8)
    
    return render_template("results.html", title=title, recommendations=recs)



@main.route("/rate", methods=["GET","POST"])

@login_required
def rate_manga():
    print("DEBUG: /rate was hit!")
    if request.method == 'POST':
        manga_id = int(request.form.get("manga_id"))
        rating_value = int(request.form.get("rating"))
        next_url = request.form.get("next")
        title = request.form.get("title")
    # Update if exists, else add
        existing = Rating.query.filter_by(user_id=current_user.id, manga_id=manga_id).first()
        if existing:
            existing.rating = rating_value
        else:
            new_rating = Rating(user_id=current_user.id, manga_id=manga_id, rating=rating_value)
            db.session.add(new_rating)
        db.session.commit()
        print(title)
        return redirect(url_for('main.recommend',title=title))
    return redirect(url_for('main.index'))




@main.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    if request.method == "POST":
        ratings = request.form.to_dict(flat=False)  # { 'manga_id': ['rating'], ... }

        if current_user.is_authenticated:
            # Save directly to DB
            for manga_id, rating_list in ratings.items():
                rating_value = int(rating_list[0])
                existing = Rating.query.filter_by(user_id=current_user.id, manga_id=manga_id).first()
                if existing:
                    existing.rating = rating_value
                else:
                    new_rating = Rating(user_id=current_user.id, manga_id=manga_id, rating=rating_value)
                    db.session.add(new_rating)
            db.session.commit()
        else:
            # Save to session for guest user
            session['guest_ratings'] = {manga_id: int(rating_list[0]) for manga_id, rating_list in ratings.items()}

        return redirect(url_for("main.index"))

    # GET → show random sample
    sample_mangas = get_random_manga_samples(manga_df, n=10)
    return render_template("onboarding.html", sample_mangas=sample_mangas)


@main.route("/dashboard")
@login_required
def dashboard():
    # Get all ratings for the current user
    ratings = Rating.query.filter_by(user_id=current_user.id).all()

    # Match manga_id with manga_df for title & genre
    user_data = []
    for r in ratings:
        manga_info = manga_df[manga_df['id'] == r.manga_id].iloc[0]
        user_data.append({
            'id': r.id,
            'manga_id': r.manga_id,
            'title': manga_info['title'],
            'genre': manga_info['genres'],
            'rating': r.rating
        })

    return render_template("dashboard.html", ratings=user_data)

@main.route("/edit_rating/<int:rating_id>", methods=["POST"])
@login_required
def edit_rating(rating_id):
    new_rating = int(request.form.get("rating"))
    rating = Rating.query.get_or_404(rating_id)
    if rating.user_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for('main.dashboard'))

    rating.rating = new_rating
    db.session.commit()
    flash("Rating updated successfully!", "success")
    return redirect(url_for('main.dashboard'))

@main.route("/delete_rating/<int:rating_id>", methods=["POST"])
@login_required
def delete_rating(rating_id):
    rating = Rating.query.get_or_404(rating_id)
    if rating.user_id != current_user.id:
        flash("Unauthorized action!", "danger")
        return redirect(url_for('main.dashboard'))

    db.session.delete(rating)
    db.session.commit()
    flash("Rating deleted successfully!", "success")
    return redirect(url_for('main.dashboard'))
