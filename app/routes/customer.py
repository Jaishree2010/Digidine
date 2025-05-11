from flask import Blueprint, render_template, request, redirect, session, flash
from app.extensions import mysql
from datetime import datetime


customer_bp = Blueprint('customer_bp', __name__,
                        template_folder='../../templates')


@customer_bp.route('/customer/menu', methods=['GET'])
def menu():
    selected_category = request.args.get('category')
    cur = mysql.connection.cursor()

    if selected_category:
        cur.execute("SELECT * FROM menu_items WHERE category = %s",
                    (selected_category,))
    else:
        cur.execute("SELECT * FROM menu_items")
    items = cur.fetchall()

    # Get all unique categories
    cur.execute("SELECT DISTINCT category FROM menu_items")
    categories = [row[0] for row in cur.fetchall()]
    cur.close()

    return render_template('menu.html', items=items, categories=categories, selected_category=selected_category)


@customer_bp.route('/customer/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form.get('item_id')
    quantity = int(request.form.get('quantity', 1))

    if not item_id or quantity <= 0:
        flash("Invalid item or quantity.", "danger")
        return redirect('/customer/menu')

    # Initialize cart
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    if item_id in cart:
        cart[item_id] += quantity
    else:
        cart[item_id] = quantity

    session['cart'] = cart
    session.modified = True  # 🔁 Ensures Flask knows session has changed
    flash("Item added to cart!", "success")
    return redirect('/customer/menu')


@customer_bp.route('/customer/cart')
def view_cart():
    cart = session.get('cart', {})
    items = []
    total = 0

    if cart:
        item_ids = list(cart.keys())
        placeholders = ', '.join(['%s'] * len(item_ids))
        query = f"SELECT * FROM menu_items WHERE id IN ({placeholders})"

        cur = mysql.connection.cursor()
        cur.execute(query, item_ids)
        items = cur.fetchall()
        cur.close()

        # Calculate total in backend
        for item in items:
            item_id_str = str(item[0])
            quantity = int(cart.get(item_id_str, 0))
            subtotal = item[3] * quantity
            total += subtotal

    return render_template('cart.html', cart=cart, items=items, total=total)


@customer_bp.route('/customer/cart/remove/<item_id>')
def remove_from_cart(item_id):
    cart = session.get('cart', {})

    if item_id in cart:
        del cart[item_id]
        session['cart'] = cart
        session.modified = True
        flash("Item removed from cart.", "info")

    return redirect('/customer/cart')


# @customer_bp.route('/customer/checkout', methods=['POST'])
# def checkout():
#     cart = session.get('cart', {})
#     user_id = session.get('user_id')

#     if not cart:
#         flash("Your cart is empty!", "warning")
#         return redirect('/customer/menu')

#     cur = mysql.connection.cursor()

#     try:
#         cur.execute("INSERT INTO orders (user_id) VALUES (%s)", (user_id,))
#         order_id = cur.lastrowid

#         for item_id, qty in cart.items():
#             cur.execute(
#                 "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%s, %s, %s)",
#                 (order_id, item_id, qty)
#             )

#         mysql.connection.commit()
#         session.pop('cart', None)
#         flash("Order placed successfully! 👨‍🍳", "success")
#     except Exception as e:
#         mysql.connection.rollback()
#         flash("Error processing order: " + str(e), "danger")
#     finally:
#         cur.close()

#     return redirect('/customer/menu')


# @customer_bp.route('/customer/checkout', methods=['POST'])
# def checkout():
#     if 'cart' not in session or not session['cart']:
#         flash("Your cart is empty.", "warning")
#         return redirect('/customer/cart')

#     user_id = session.get('user_id')
#     cart = session['cart']

#     try:
#         cur = mysql.connection.cursor()
#         cur.execute(
#             "INSERT INTO orders (user_id, status) VALUES (%s, %s)", (user_id, "Pending"))
#         order_id = cur.lastrowid

#         for item_id, quantity in cart.items():
#             cur.execute("INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%s, %s, %s)",
#                         (order_id, item_id, quantity))

#         mysql.connection.commit()
#         session.pop('cart', None)

#         # 🔁 Redirect to QR mock page
#         return redirect(f'/customer/payment_method/{order_id}')

#     except Exception as e:
#         mysql.connection.rollback()
#         flash("Checkout failed: " + str(e), "danger")
#         return redirect('/customer/cart')
#     finally:
#         cur.close()

@customer_bp.route('/customer/checkout', methods=['POST'])
def checkout():
    if not session.get('cart'):
        flash("Your cart is empty.", "warning")
        return redirect('/customer/menu')
    return render_template('checkout_payment.html')


@customer_bp.route('/customer/payment_method/<int:order_id>')
def choose_payment(order_id):
    return render_template('payment_method.html', order_id=order_id)


@customer_bp.route('/customer/qr_payment/<int:order_id>')
def qr_payment(order_id):
    return render_template('qr_payment.html', order_id=order_id)


@customer_bp.route('/customer/payment', methods=['POST'])
def complete_payment():
    method = request.form.get('method')
    user_id = session.get('user_id')

    cur = mysql.connection.cursor()

    try:
        # Create order
        cur.execute(
            "INSERT INTO orders (user_id, status) VALUES (%s, %s)", (user_id, 'Pending'))
        order_id = cur.lastrowid

        # Insert order items
        for item_id, qty in session['cart'].items():
            cur.execute("INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%s, %s, %s)",
                        (order_id, item_id, qty))

        mysql.connection.commit()
        session.pop('cart', None)
        flash(
            f"Order placed successfully! Payment by {method.capitalize()}", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("Failed to place order: " + str(e), "danger")
    finally:
        cur.close()

    return redirect('/')


# Simulate QR Payment
@customer_bp.route('/customer/pay/qr')
def pay_qr():
    return render_template('qr_payment.html')

# Simulate Cash Payment


@customer_bp.route('/customer/pay/cash')
def pay_cash():
    return finalize_order("Cash")

# After QR Scanned → Finalize


@customer_bp.route('/customer/pay/success')
def payment_success():
    return finalize_order("QR")

# Common function to finalize and insert order


def finalize_order(method):
    cart = session.get('cart', {})
    if not cart:
        flash("Cart is empty.", "warning")
        return redirect('/customer/menu')

    user_id = session.get('user_id')  # optional check
    cur = mysql.connection.cursor()

    try:
        # Create order
        cur.execute("INSERT INTO orders (user_id, status, created_at) VALUES (%s, %s, %s)",
                    (user_id, "Pending", datetime.now()))
        order_id = cur.lastrowid

        # Add items
        for item_id_str, qty in cart.items():
            item_id = int(item_id_str)
            cur.execute("INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%s, %s, %s)",
                        (order_id, item_id, qty))

        mysql.connection.commit()
        session['cart'] = {}  # Clear cart
        flash("Order placed successfully using " + method + ".", "success")
    except Exception as e:
        mysql.connection.rollback()
        flash("Error placing order: " + str(e), "danger")
    finally:
        cur.close()

    return render_template('payment_success.html', method=method)


# ---------------- Notifications ----------------

@customer_bp.route('/customer/notifications')
def notifications():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view notifications.", "warning")
        return redirect('/auth/login')

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, message, is_read, created_at FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    notifs = cur.fetchall()

    # Mark all as read
    cur.execute(
        "UPDATE notifications SET is_read = 1 WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return render_template('notifications.html', notifications=notifs)


@customer_bp.route('/customer/dashboard')
def customer_dashboard():
    if 'user_id' not in session or session.get('role') != 'customer':
        flash("Access denied. Customers only.", "danger")
        return redirect('/')

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT o.id, o.status, o.created_at, 
               GROUP_CONCAT(m.name SEPARATOR ', ') AS items
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN menu_items m ON oi.menu_item_id = m.id
        WHERE o.user_id = %s
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """, (user_id,))
    orders = cur.fetchall()
    cur.close()

    return render_template('dashboard_customer.html', orders=orders)
