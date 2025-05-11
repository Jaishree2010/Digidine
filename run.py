from app import create_app
from flask import Flask, render_template
from config import CONFIG  # Import DB_CONFIG from config.py

app = create_app()

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
