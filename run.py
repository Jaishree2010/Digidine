from app import create_app
from flask import Flask, render_template


app = create_app()


@app.route('/')
def home():
    return render_template('home.html')


# config.py
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin123',
    'database': 'digidine'
}

if __name__ == '__main__':
    app.run(debug=True)
