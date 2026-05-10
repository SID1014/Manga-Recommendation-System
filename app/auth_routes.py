from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from .database import db, bcrypt
from .models import User, Rating

auth = Blueprint('auth', __name__)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "error")
            return redirect(url_for('auth.signup'))

        user = User(username=username, email=email, password_hash=password)
        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template("signup.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            
            guest_ratings = session.pop('guest_ratings', None)
            if guest_ratings:
                for manga_id, rating_value in guest_ratings.items():
                    existing = Rating.query.filter_by(user_id=user.id, manga_id=int(manga_id)).first()
                    if existing:
                        existing.rating = rating_value
                    else:
                        new_rating = Rating(user_id=user.id, manga_id=int(manga_id), rating=rating_value)
                        db.session.add(new_rating)
                db.session.commit()
                
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Invalid email or password", "error")
            
    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out.", "info")
    return redirect(url_for('main.index'))
