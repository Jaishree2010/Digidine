from flask import Blueprint, render_template, session, redirect, flash
from app.extensions import mysql

notifications_bp = Blueprint(
    'notifications_bp', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
def view_notifications():
    if not session.get('user_id'):
        flash("Login required", "warning")
        return redirect('/auth/login')

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, message, is_read, created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    notifications = cur.fetchall()

    # Mark as read
    cur.execute(
        "UPDATE notifications SET is_read = 1 WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return render_template('notifications.html', notifications=notifications)


@notifications_bp.route('/notifications')
def notifications():
    if not session.get('user_id'):
        flash("Please log in to view notifications.", "warning")
        return redirect('/auth/login')

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    all_notifications = cur.fetchall()

    # Mark all as read
    cur.execute(
        "UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (session['user_id'],))
    mysql.connection.commit()
    cur.close()

    session['has_unread_notifications'] = False
    return render_template('notifications.html', notifications=all_notifications)


@notifications_bp.context_processor
def inject_unread_notifications():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM orders WHERE user_id = %s AND notified = 0", (session['user_id'],))
        count = cur.fetchone()[0]
        cur.close()
        return {'unread_notifications': count}
    return {'unread_notifications': 0}


@notifications_bp.context_processor
def inject_notification_count():
    user_id = session.get('user_id')
    if not user_id:
        return dict(unread_notifications_count=0)

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id = %s AND notified = 0", (user_id,))
    count = cur.fetchone()[0]
    cur.close()
    return dict(unread_notifications_count=count)
