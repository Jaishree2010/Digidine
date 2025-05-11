from app.extensions import mysql

from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from flask import Blueprint, render_template

main_blueprint = Blueprint('main_blueprint', __name__,
                           template_folder='../../templates')


@main_blueprint.route('/')
def home():
    return render_template('home.html')


@main_blueprint.route('/about')
def about():
    return render_template('about.html')


# app/routes/auth.py

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
            return redirect('/')
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                    (username, email, password, role))
        mysql.connection.commit()
        cur.close()
        flash('Signup successful. Please log in.', 'success')
        return redirect(url_for('auth_bp.login'))
    return render_template('signup.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
