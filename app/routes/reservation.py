from flask import Blueprint, render_template, request, session, redirect
from app.extensions import mysql


reservation_bp = Blueprint('reservation_bp', __name__,
                           template_folder='../../templates')


@reservation_bp.route('/book', methods=['GET', 'POST'])
def book():
    if session.get('role') != 'customer':
        return redirect('/')
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        guests = request.form['guests']
        message = request.form['message']
        user_id = session.get('user_id')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO reservations (user_id, date, time, guests, message) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, date, time, guests, message))
        mysql.connection.commit()
        cur.close()
        return redirect('/customer/dashboard')
    return render_template('reservation.html')
