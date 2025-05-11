from flask import Flask, session
from flask_mysqldb import MySQL
from flask_session import Session
from app.routes.customer import customer_bp
from app.routes.admin import admin_bp
from app.routes.kitchen import kitchen_bp
from app.routes.reservation import reservation_bp
from app.routes.feedback import feedback_bp
from app.extensions import mysql
from app.routes.main import main_blueprint
from app.routes.auth import auth_bp
from app.routes.notifications import notifications_bp
from app.routes.payment import payment_bp
from app.routes.menu_admin import menu_bp


def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    app.secret_key = 'your_secret_key'

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'admin123'
    app.config['MYSQL_DB'] = 'digidine'

    app.config['SESSION_TYPE'] = 'filesystem'
    mysql.init_app(app)
    Session(app)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(feedback_bp, url_prefix='/feedback')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(kitchen_bp, url_prefix='/kitchen')
    app.register_blueprint(reservation_bp, url_prefix='/reservation')
    app.register_blueprint(notifications_bp)
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(menu_bp, url_prefix='/admin')

    # 🔔 Notification badge loader
    @app.before_request
    def load_notification_count():
        if 'user_id' in session:
            cur = mysql.connection.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM notifications WHERE user_id = %s AND is_read = 0", (session['user_id'],))
            unread = cur.fetchone()[0]
            session['unread_notifications'] = unread > 0
            cur.close()
        else:
            session['unread_notifications'] = False

    return app
