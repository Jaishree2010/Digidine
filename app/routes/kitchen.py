from flask import Blueprint, render_template, session, redirect, flash, request
from app.extensions import mysql

kitchen_bp = Blueprint('kitchen_bp', __name__,
                       template_folder='../../templates')


@kitchen_bp.route('/dashboard')
def dashboard_kitchen():
    if session.get('role') != 'kitchen':
        flash("Access denied. Kitchen staff only.", "danger")
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            o.id, o.status, o.created_at, 
            IFNULL(u.username, 'Guest') AS username,
            GROUP_CONCAT(m.name SEPARATOR ', ') AS items,
            GROUP_CONCAT(oi.quantity SEPARATOR ', ') AS quantities
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN menu_items m ON oi.menu_item_id = m.id
        LEFT JOIN users u ON o.user_id = u.id
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """)
    orders = cur.fetchall()
    cur.close()

    return render_template('kitchen/dashboard.html', orders=orders)


@kitchen_bp.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    if session.get('role') != 'kitchen':
        flash("Access denied. Kitchen staff only.", "danger")
        return redirect('/')

    new_status = request.form.get('status')
    cur = mysql.connection.cursor()
    try:
        if new_status == 'Served':
            cur.execute(
                "SELECT user_id FROM orders WHERE id = %s", (order_id,))
            user_id = cur.fetchone()[0]
            if user_id:
                cur.execute("INSERT INTO notifications (user_id, message, is_read) VALUES (%s, %s, 0)",
                            (user_id, f"Your order #{order_id} has been served."))
        else:
            cur.execute("UPDATE orders SET status = %s WHERE id = %s",
                        (new_status, order_id))

        mysql.connection.commit()
        flash("Order status updated.", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("Failed to update: " + str(e), "danger")
    finally:
        cur.close()

    return redirect('/kitchen/dashboard')
