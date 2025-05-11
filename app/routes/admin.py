from flask import Blueprint, render_template, session, redirect, request, flash, url_for
from app.extensions import mysql

admin_bp = Blueprint('admin_bp', __name__, template_folder='../../templates')


@admin_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return redirect('/')

    cur = mysql.connection.cursor()

    # Orders
    cur.execute("SELECT o.id, u.username, o.status, o.created_at FROM orders o JOIN users u ON o.user_id = u.id ORDER BY o.created_at DESC")
    orders = cur.fetchall()

    # Dashboard stats
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM reservations")
    total_reservations = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM feedback")
    total_feedback = cur.fetchone()[0]

    cur.close()

    return render_template(
        'dashboard_admin.html',
        orders=orders,
        total_users=total_users,
        total_reservations=total_reservations,
        total_feedback=total_feedback
    )


@admin_bp.route('/update_status/<int:order_id>/<string:new_status>')
def update_status(order_id, new_status):
    if session.get('role') != 'admin':
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET status=%s WHERE id=%s",
                (new_status, order_id))
    mysql.connection.commit()
    cur.close()
    return redirect('/admin/dashboard')


@admin_bp.route('/menu', methods=['GET'])
def manage_menu():
    if session.get('role') != 'admin':
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM menu_items")
    items = cur.fetchall()

    cur.execute("SELECT DISTINCT category FROM menu_items")
    categories = [row[0] for row in cur.fetchall()]
    cur.close()

    return render_template('admin/admin_menu.html', items=items, categories=categories)


@admin_bp.route('/orders')
def view_orders():
    if session.get('role') != 'admin':
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders")
    orders = cur.fetchall()
    cur.close()
    return render_template('admin/view_orders.html', orders=orders)


@admin_bp.route('/reservations')
def view_reservations():
    if session.get('role') != 'admin':
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("SELECT r.id, u.username, r.date, r.time, r.guests, r.message FROM reservations r JOIN users u ON r.user_id = u.id ORDER BY r.date, r.time")
    reservations = cur.fetchall()
    cur.close()
    return render_template('admin/admin_reservation.html', reservations=reservations)


@admin_bp.route('/feedback')
def view_feedback():
    if session.get('role') != 'admin':
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.id, u.username, f.message, f.rating, f.created_at
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    """)
    feedback = cur.fetchall()
    cur.close()
    return render_template('admin/admin_feedback.html', feedback=feedback)


@admin_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if session.get('role') != 'admin':
        return redirect('/')

    success = False
    error = None

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        cur = mysql.connection.cursor()
        # Check current admin password
        cur.execute("SELECT password FROM users WHERE role='admin' LIMIT 1")
        stored_password = cur.fetchone()[0]

        if old_password != stored_password:
            error = "Current password is incorrect!"
        else:
            cur.execute(
                "UPDATE users SET password=%s WHERE role='admin'", (new_password,))
            mysql.connection.commit()
            success = True

        cur.close()

    return render_template('admin/change_password.html', success=success, error=error)


@admin_bp.route('/users')
def view_users():
    if session.get('role') != 'admin':
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, username, email FROM users WHERE role = 'customer' ORDER BY id DESC")
    users = cur.fetchall()
    cur.close()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if session.get('role') != 'admin':
        return redirect('/')
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = 'kitchen'  # Force kitchen role only

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                    (username, email, password, role))
        mysql.connection.commit()
        cur.close()

        flash("Kitchen staff added successfully!", "success")
        return redirect('/admin/kitchen-staff')

    return render_template('admin/add_user.html')


@admin_bp.route('/menu/delete/<int:item_id>', methods=['POST'])
def delete_menu_item(item_id):
    if session.get('role') != 'admin':
        return redirect('/')

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM menu_items WHERE id = %s", (item_id,))
        mysql.connection.commit()
        flash("Item deleted successfully.", "success")
    except Exception as e:
        flash("Error deleting item: " + str(e), "danger")
        mysql.connection.rollback()
    finally:
        cur.close()

    return redirect('/admin/menu')

@admin_bp.route('/kitchen-staff')
def manage_kitchen_staff():
    if session.get('role') != 'admin':
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE role = 'kitchen' ORDER BY id DESC")
    staff = cur.fetchall()
    cur.close()

    return render_template('admin/kitchen_staff.html', staff=staff)