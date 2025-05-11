from flask import Flask, session
from flask_session import Session
from app.extensions import mysql # Import mail from extensions
from app.routes.customer import customer_bp
from app.routes.admin import admin_bp
from app.routes.kitchen import kitchen_bp
from app.routes.reservation import reservation_bp
from app.routes.feedback import feedback_bp
from app.routes.main import main_blueprint
from app.routes.auth import auth_bp
from app.routes.notifications import notifications_bp
from app.routes.payment import payment_bp
from app.routes.menu_admin import menu_bp
from config import CONFIG  # Import the configuration
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    # Load configuration
    app.secret_key = CONFIG['SECRET_KEY']
    app.config['MYSQL_HOST'] = CONFIG['MYSQL_HOST']
    app.config['MYSQL_USER'] = CONFIG['MYSQL_USER']
    app.config['MYSQL_PASSWORD'] = CONFIG['MYSQL_PASSWORD']
    app.config['MYSQL_DB'] = CONFIG['MYSQL_DB']
    app.config['SESSION_TYPE'] = CONFIG['SESSION_TYPE']

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = CONFIG['MAIL_SERVER']
    app.config['MAIL_PORT'] = CONFIG['MAIL_PORT']
    app.config['MAIL_USE_TLS'] = CONFIG['MAIL_USE_TLS']
    app.config['MAIL_USERNAME'] = CONFIG['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = CONFIG['MAIL_PASSWORD']
    app.config['MAIL_USE_SSL'] = CONFIG['MAIL_USE_SSL']
    app.config['MAIL_DEFAULT_SENDER'] = ('DIGIDINE', 'work.jeevanebi@gmail.com')
    mail.init_app(app)

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
