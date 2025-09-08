# app/routes.py
from flask import Blueprint, render_template, request
from .recommender import get_cbf_recommendations, manga_df

main = Blueprint('main', __name__)

@main.route("/", methods=["GET"])
def index():
    # For convenience, send a short list of titles for a dropdown/autocomplete if desired
    sample_titles = list(manga_df['title'].head(200).astype(str))
    return render_template("index.html", sample_titles=sample_titles)

@main.route("/recommend", methods=["POST"])
def recommend():
    title = request.form.get("title", "").strip()
    if not title:
        return render_template("results.html", title=title, recommendations=[], message="Enter a title")
    recs = get_cbf_recommendations(title, top_n=8)
    return render_template("results.html", title=title, recommendations=recs, message=None)
