from flask_login import current_user, login_required
from .models import Rating
from .database import db
from flask import Blueprint, render_template, request, redirect,url_for
from .recommender import get_cbf_recommendations,manga_df

main = Blueprint('main', __name__)


@main.route("/", methods=["GET"])
def index():
    sample_titles = list(manga_df['title'].head(200).astype(str))
    return render_template("index.html", sample_titles=sample_titles)


@main.route("/recommend", methods=["GET","POST"])
def recommend():
    print("Is user authenticated?", current_user.is_authenticated)
    if request.method == "POST":
        # When user submits search form
        title = request.form.get("title")
    else:
        # When redirected after rating
        print("adsda")
        title = request.args.get("title")

    if not title:
        return redirect(url_for("main.index"))  # fallback if no title given

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

