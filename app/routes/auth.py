from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from app.extensions import mysql

auth_bp = Blueprint('auth_bp', __name__, template_folder='../../templates')

# Only admins can sign up using this secret key
ADMIN_SIGNUP_ACCESS = "admin-secret"


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
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

            if user[4] == 'admin':
                return redirect('/admin/dashboard')
            elif user[4] == 'kitchen':
                return redirect('/kitchen/dashboard')
            else:
                return redirect('/customer/dashboard')
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (email, password, role, username) VALUES (%s, %s, %s, %s)",
                        (email, password, role, email.split('@')[0]))
            mysql.connection.commit()
            flash("Account created successfully!", "success")
            return redirect('/auth/login')
        except Exception as e:
            flash("Signup failed: " + str(e), "danger")
        finally:
            cur.close()

    return render_template('signup.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@auth_bp.route('/guest')
def guest_access():
    session['username'] = 'Guest'
    session['role'] = 'customer'
    session['user_id'] = 'guest'
    return redirect('/customer/menu')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            # Logic to send a password reset email (placeholder)
            flash('Password reset instructions have been sent to your email.', 'success')
        else:
            flash('No account found with that email address.', 'danger')

        return redirect(url_for('auth_bp.forgot_password'))

    return render_template('forgot-password.html')
