# app.py
from flask import Flask, render_template
from .db import init_db
from .routes import routes_bp
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
# New line adding database URI directly
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = init_db(app)

app.register_blueprint(routes_bp)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)