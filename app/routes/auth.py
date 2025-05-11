import random
import string
from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from flask_mail import Message
from app.extensions import mysql, mail

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Only admins can sign up using this secret key
ADMIN_SIGNUP_ACCESS = "admin-secret"


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        role = request.form.get('role')
        

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]

            if role != user[4]:
                flash('Invalid secret key for {user[4]} signup.', 'danger')

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
        email = request.form.get('email')

        # Check if the email exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            # Generate a random password
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Update the password in the database
            cur.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
            mysql.connection.commit()
            cur.close()

            # Send the new password via email
            msg = Message(
                subject="Your New Password",
                sender="noreply@digidine.com",
                recipients=[email]
            )
            msg.body = f"Hello,\n\nYour new password is: {new_password}\n\nPlease log in and change your password immediately."
            mail.send(msg)

            flash("A new password has been sent to your email.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Email not found. Please try again.", "danger")
            return redirect(url_for('auth.forgot_password'))

    return render_template('forgot-password.html')
