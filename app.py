from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)

df = pd.read_csv("Data/Processed/processed_manga.csv")
df["content"] = (df["synopsis"]+ " ")*3 + " " + (df["genres"]+ " ")*2
import joblib

cosine_sim = joblib.load("models/cbf_cosine_matrix.pkl")
tfidf = joblib.load("models/tfidf_vectorizer.pkl")
U = joblib.load("models/cf_U.pkl")
sigma = joblib.load("models/cf_sigma.pkl")
Vt = joblib.load("models/cf_Vt.pkl")


cosine_sim = joblib.load("models/cbf_cosine_matrix.pkl")
tfidf = joblib.load("models/tfidf_vectorizer.pkl")
U = joblib.load("models/cf_U.pkl")
sigma = joblib.load("models/cf_sigma.pkl")
Vt = joblib.load("models/cf_Vt.pkl")



def get_recommendations(title, top_n=5):
    if title not in df['title'].values:
        return []

    idx = df[df['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    manga_indices = [i[0] for i in sim_scores]
    
    return df.iloc[manga_indices][['title', 'genres','synopsis', 'image_url']].to_dict(orient='records')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title")
        recommendations = get_recommendations(title, top_n=5)
        return render_template("results.html", title=title, recommendations=recommendations)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
