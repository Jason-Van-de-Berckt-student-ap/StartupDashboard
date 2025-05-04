from flask import Flask, render_template, redirect, url_for, flash, request
from kinde_sdk import Configuration
from kinde_sdk.kinde_api_client import GrantType, KindeApiClient
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

KINDE_HOST = os.getenv('KINDE_HOST')
KINDE_CLIENT_ID = os.getenv('KINDE_CLIENT_ID')
KINDE_CLIENT_SECRET = os.getenv('KINDE_CLIENT_SECRET')
KINDE_REDIRECT_URL = os.getenv('KINDE_REDIRECT_URL')
KINDE_POST_LOGOUT_REDIRECT_URL = os.getenv('KINDE_POST_LOGOUT_REDIRECT_URL')
GRANT_TYPE = GrantType.AUTHORIZATION_CODE

configuration = Configuration(host=KINDE_HOST)
kinde_api_client_params = {
    "configuration": configuration,
    "domain": KINDE_HOST,
    "client_id": KINDE_CLIENT_ID,
    "client_secret": KINDE_CLIENT_SECRET,
    "grant_type": GRANT_TYPE,
    "callback_url": KINDE_REDIRECT_URL
}
kinde_client = KindeApiClient(**kinde_api_client_params)

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

@app.context_processor
def inject_user():
    user = kinde_client.get_user_details() if kinde_client.is_authenticated() else None
    return dict(user=user)

@app.route('/')
def index():
    if kinde_client.is_authenticated():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return redirect(kinde_client.get_login_url())

@app.route('/register')
def register():
    return redirect(kinde_client.get_register_url())

@app.route('/callback')
def callback():
    kinde_client.fetch_token(authorization_response=request.url)
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if not kinde_client.is_authenticated():
        return redirect(url_for('login'))
    energy_data = generate_energy_data()
    user = kinde_client.get_user_details()
    return render_template('dashboard.html', energy_data=energy_data, active_page='dashboard', user=user)

@app.route('/companies')
def companies():
    if not kinde_client.is_authenticated():
        return redirect(url_for('login'))
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
def fluvius():
    if not kinde_client.is_authenticated():
        return redirect(url_for('login'))
    return render_template('fluvius.html', active_page='fluvius')

@app.route('/logout')
def logout():
    return redirect(kinde_client.logout(redirect_to=KINDE_POST_LOGOUT_REDIRECT_URL))

if __name__ == '__main__':
    app.run(debug=True)