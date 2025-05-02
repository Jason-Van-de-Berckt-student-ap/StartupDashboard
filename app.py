from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User data from environment variables
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = {
    '1': User('1', os.getenv('USER_EMAIL', 'demo@example.com'), os.getenv('USER_PASSWORD', 'password123'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Generate dummy energy consumption data
def generate_energy_data():
    data = []
    current_date = datetime.now()
    for i in range(30):
        date = current_date - timedelta(days=i)
        consumption = random.uniform(2.5, 5.0)
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'consumption': round(consumption, 2)
        })
    return data

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = next((u for u in users.values() if u.username == email), None)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    energy_data = generate_energy_data()
    return render_template('dashboard.html', energy_data=energy_data, active_page='dashboard')

@app.route('/companies')
@login_required
def companies():
    companies = [
        {
            'name': 'Bedrijf A',
            'image': 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80',
            'location': 'Tailfer',
            'description': 'Bedrijfs informatie',
            'ordered_percent': 56,
            'almost_sold_out': False
        },
        {
            'name': 'KBedrijf B',
            'image': 'https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=600&q=80',
            'location': 'Sint-Niklaas',
            'description': 'Bedrijfs informatie',
            'ordered_percent': 80,
            'almost_sold_out': True
        },
        {
            'name': 'Bedrijf C',
            'image': 'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=600&q=80',
            'location': 'Mettet',
            'description': 'Bedrijfs informatie',
            'ordered_percent': 70,
            'almost_sold_out': False
        },
        {
            'name': 'Bedrijf D',
            'image': 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80',
            'location': 'Tessenderlo',
            'description': 'Bedrijfs informatie',
            'ordered_percent': 30,
            'almost_sold_out': False
        },
    ]
    return render_template('companies.html', companies=companies, active_page='companies')

@app.route('/fluvius')
@login_required
def fluvius():
    return render_template('fluvius.html', active_page='fluvius')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) 