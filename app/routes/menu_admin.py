from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from app.extensions import mysql
import os
from werkzeug.utils import secure_filename
from uuid import uuid4

# Blueprint setup
menu_bp = Blueprint('menu_bp', __name__, template_folder='../../templates')

# Upload config
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@menu_bp.route('/menu', methods=['GET', 'POST'])
def manage_menu():
    # Only accessible by admin
    if session.get('role') != 'admin':
        return redirect('/')

    with mysql.connection.cursor() as cur:
        # Handle new item form submission
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            category = request.form['category']
            image_file = request.files.get('image')

            image_filename = None
            if image_file and allowed_file(image_file.filename):
                ext = image_file.filename.rsplit('.', 1)[1].lower()
                image_filename = f"{uuid4().hex}.{ext}"
                image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                image_file.save(image_path)

            # Insert new item into database
            cur.execute("""
                INSERT INTO menu_items (name, description, price, category, image)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, description, price, category, image_filename))
            mysql.connection.commit()
            flash("Menu item added successfully", "success")
            return redirect(url_for('menu_bp.manage_menu'))

        # Load menu items
        cur.execute("SELECT * FROM menu_items")
        items = cur.fetchall()

        # Load unique categories for the form
        cur.execute("SELECT DISTINCT category FROM menu_items")
        category_list = [row[0] for row in cur.fetchall()]

    return render_template('admin/admin_menu.html', items=items, categories=sorted(category_list))
