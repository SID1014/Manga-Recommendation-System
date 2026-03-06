
# **Manga Recommendation System**

> A Netflix-style recommendation system for manga, powered by **Content-Based Filtering (CBF)** and **Collaborative Filtering (CF)** with a **Hybrid Model**.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![Machine Learning](https://img.shields.io/badge/ML-Recommendation-orange)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## **🌟 About the Project**

The Manga Recommendation System suggests manga titles tailored to the user's taste, similar to Netflix or MyAnimeList.
**[ Live Demo](https://manga-recommendation-system-g635.onrender.com)** *(may take 30-60 seconds to load on first visit — free tier)*

* **Guest Users:**
  Get instant recommendations using **Content-Based Filtering (CBF)** based on manga descriptions and genres.

* **Logged-in Users:**
  Ratings are collected and used to power **Collaborative Filtering (CF)** for personalized suggestions.

* **Hybrid Model:**
  Combines both approaches to deliver highly accurate results by blending user behavior and content similarity.

* **Dynamic Dataset Updates:**
  Fetches the latest manga data automatically through APIs, ensuring the recommendations stay relevant.

---

## **🚀 Features**

* 🔹 Content-Based Filtering using **TF-IDF** and **Cosine Similarity**.
* 🔹 Collaborative Filtering with **Singular Value Decomposition (SVD)**.
* 🔹 Hybrid approach combining both for Netflix-like accuracy.
* 🔹 **Guest Onboarding Flow** for instant recommendations without signup.
* 🔹 Secure authentication using **Flask-Login**.
* 🔹 Dynamic backend designed for scalability and dataset updates.

---

## **🛠 Tech Stack**

| Layer                | Technology                                    |
| -------------------- | --------------------------------------------- |
| **Backend**          | Flask, Flask-Login, SQLAlchemy                |
| **Machine Learning** | Scikit-learn, Pandas, NumPy                   |
| **Database**         | SQLite (development), PostgreSQL (production) |
| **Deployment**       | Render + Gunicorn                             |

---

## **⚙️ Installation**

Follow these steps to run the project locally:

### **1. Clone the repository**

```bash
git clone https://github.com/SID1014/manga-recommendation-system.git
cd manga-recommendation-system
```

### **2. Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

### **4. Run the app locally**

```bash
flask run
```

The app will run at:

```
http://127.0.0.1:5000
```

---

## **📂 Folder Structure**

```
Manga-Recommendation-System/
│
├── app/
│   ├── __init__.py        # App factory with create_app()
│   ├── routes.py          # Main routes
│   ├── auth_routes.py     # Authentication routes
│   ├── collaborative.py   # Collaborative Filtering model
│   ├── hybrid.py          # Hybrid recommender logic
│   ├── recommender.py     # Content-Based Filtering logic
│   └── models.py          # Database models
│
├── Data/                  # Dataset storage
├── models/                # Saved ML models
├── Notebook/              # Jupyter notebooks for exploration
│
├── static/                # Static files (CSS, JS)
├── templates/             # HTML templates
│
├── requirements.txt
├── wsgi.py                # For deployment
├── run.py                 # Local run script
└── README.md
```

---

## **💡 How It Works**

The recommendation system works in three layers:

### **1. Content-Based Filtering (CBF)**

* Uses **TF-IDF** on manga **genres** and **synopsis**.
* Similarity between mangas is calculated using **Cosine Similarity**.
* Perfect for **new users with no rating history**.

---

### **2. Collaborative Filtering (CF)**

* Uses **user ratings** to find hidden relationships.
* Implemented using **Singular Value Decomposition (SVD)**.
* Generates recommendations by comparing a user's rating patterns with others.

---

### **3. Hybrid Model**

* **CBF** recommendations are filtered through **CF scores** for better accuracy.
* If a user has no ratings, **CBF alone** is used.

---

## **🧪 Example Use Case**

* **Guest User Flow:**

  * User visits the site → Instantly receives recommendations using CBF.
* **Registered User Flow:**

  * Logs in → Rates a few manga → Hybrid model kicks in for highly personalized recommendations.

---

## **🚀 Deployment**

The app is deployed on **Render** using **Gunicorn**.

### Start Command:

```
gunicorn wsgi:app
```

Make sure `gunicorn` is included in `requirements.txt`:

```
gunicorn>=20.1.0
```

---

---

## **🤝 Contributing**

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

