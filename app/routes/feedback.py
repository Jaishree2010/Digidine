from flask import Blueprint, render_template, request, session, redirect, flash
from app.extensions import mysql

feedback_bp = Blueprint('feedback_bp', __name__, url_prefix='/feedback')


@feedback_bp.route('/submit', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        message = request.form['message']
        rating = request.form['rating']
        user_id = session.get('user_id')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO feedback (user_id, message, rating, created_at) VALUES (%s, %s, %s)",
                    (user_id, message, rating, 'NOW()'))
        mysql.connection.commit()
        cur.close()
        flash("Thank you for your feedback!", "success")
        return redirect('/')
    return render_template('feedback.html')
    

@feedback_bp.route('/admin/feedback')
def view_feedback():
    if session.get('role') != 'admin':
        flash("Access denied", "danger")
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.id, u.username, f.message, f.rating, f.created_at 
        FROM feedback f
        LEFT JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    """)
    feedback = cur.fetchall()
    cur.close()

    return render_template('admin_feedback.html', feedback=feedback)
