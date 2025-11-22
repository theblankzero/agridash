HOME_CONTENT = """
{% if not session.user_id %}
<div class="hero-section text-center">
    <div class="container">
        <h1 class="display-4 mb-4">
            <i class="fas fa-tractor me-3"></i>
            Welcome to AgriDash Pro
        </h1>
        <p class="lead mb-4">Modern farm management system for the digital age</p>
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <i class="fas fa-cloud-sun fa-3x mb-2"></i>
                        <h5>Weather Intelligence</h5>
                        <p>Real-time weather data and forecasts</p>
                    </div>
                    <div class="col-md-4 mb-3">
                        <i class="fas fa-seedling fa-3x mb-2"></i>
                        <h5>Crop Management</h5>
                        <p>Track and manage your crops efficiently</p>
                    </div>
                    <div class="col-md-4 mb-3">
                        <i class="fas fa-chart-line fa-3x mb-2"></i>
                        <h5>Farm Analytics</h5>
                        <p>Make data-driven decisions for your farm</p>
                    </div>
                </div>
            </div>
        </div>
        <a href="{{ url_for('register') }}" class="btn btn-light btn-lg me-3">
            <i class="fas fa-user-plus me-2"></i>Get Started
        </a>
        <a href="{{ url_for('login') }}" class="btn btn-outline-light btn-lg">
            <i class="fas fa-sign-in-alt me-2"></i>Login
        </a>
    </div>
</div>

<div class="row">
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-rocket me-2"></i>Why Choose AgriDash Pro?</h5>
            </div>
            <div class="card-body">
                <ul class="list-unstyled">
                    <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Personalized farm dashboard</li>
                    <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Weather-based farming advisory</li>
                    <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Crop management tools</li>
                    <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Fertilizer scheduling</li>
                    <li class="mb-2"><i class="fas fa-check text-success me-2"></i> Mobile-friendly interface</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-users me-2"></i>Join Our Farming Community</h5>
            </div>
            <div class="card-body">
                <p>Thousands of farmers are already using AgriDash Pro to improve their yields and manage their farms more efficiently.</p>
                <div class="text-center mt-4">
                    <a href="{{ url_for('register') }}" class="btn btn-success">
                        <i class="fas fa-user-plus me-2"></i>Create Your Account
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% else %}
<script>
    window.location.href = "{{ url_for('dashboard') }}";
</script>
{% endif %}
"""
LOGIN_CONTENT = """
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card auth-card">
            <div class="card-header bg-success text-white text-center">
                <h4 class="mb-0"><i class="fas fa-sign-in-alt me-2"></i> AgriDash Pro Login</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="identifier" class="form-label">Username, Email or Phone</label>
                        <input type="text" class="form-control" id="identifier" name="identifier" required 
                               placeholder="Enter username, email or phone number">
                        <div class="form-text">You can login with your username, email address, or phone number</div>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required 
                               placeholder="Enter your password">
                    </div>
                    <button type="submit" class="btn btn-success w-100">
                        <i class="fas fa-lock-open me-2"></i> Log In
                    </button>
                </form>
                <div class="text-center mt-3">
                    <p><a href="{{ url_for('forgot_password') }}">Forgot your password?</a></p>
                    <p>Don't have an account? <a href="{{ url_for('register') }}">Register here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from datetime import datetime
import numpy as np
import tensorflow as tf

# --- Flask App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

# --- ML Model Loading ---
MODEL_PATH = "model.h5"
model = None
ml_model_available = False

if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        ml_model_available = True
        print("ML Model loaded successfully!")
    except Exception as e:
        print(f"Error loading ML model: {e}")
        print("ML-based predictions will not be available.")
else:
    print(f"Warning: Model file not found at {MODEL_PATH}")
    print("ML-based predictions will not be available. Basic recommendations will still work.")

# --- ML Model Data ---
crops_ml = {
    "cereals": [
        "Rice", "Wheat", "Maize", "Barley", "Sorghum (Jowar)",
        "Pearl Millet (Bajra)", "Finger Millet (Ragi)", "Oats",
        "Buckwheat", "Foxtail Millet", "Little Millet", "Kodo Millet",
        "Proso Millet", "Barnyard Millet"
    ],
    "pulses": [
        "Chickpea (Chana)", "Pigeon Pea (Arhar/Toor)", "Mung Bean (Moong)",
        "Urd Bean (Urad)", "Lentil (Masur)", "Peas (Matar)",
        "Cowpea (Lobia)", "Horse Gram (Kulthi)", "Moth Bean (Matki)",
        "Kidney Bean (Rajma)", "Black Gram (Urad)", "Green Gram (Moong)",
        "Bengal Gram (Chana)", "Red Gram (Arhar)", "Grass Pea (Khesari)"
    ],
    "oilseeds": [
        "Groundnut", "Mustard", "Soybean", "Sunflower", "Sesame (Til)",
        "Safflower", "Niger Seed", "Castor", "Linseed", "Coconut",
        "Oil Palm", "Cottonseed", "Rapeseed", "Palm Kernel"
    ],
    "cash_crops": [
        "Sugarcane", "Cotton", "Jute", "Tobacco", "Rubber",
        "Tea", "Coffee", "Cocoa", "Indigo", "Opium Poppy"
    ],
    "vegetables": [
        "Potato", "Tomato", "Onion", "Brinjal (Eggplant)", "Okra (Bhindi)",
        "Cauliflower", "Cabbage", "Carrot", "Radish", "Cucumber",
        "Bottle Gourd", "Bitter Gourd", "Ridge Gourd", "Snake Gourd",
        "Pumpkin", "Spinach", "Fenugreek (Methi)", "Amaranth (Chaulai)",
        "Drumstick", "Peas", "Beans", "Capsicum", "Chilli",
        "Garlic", "Ginger", "Turmeric", "Sweet Potato", "Tapioca",
        "Yam", "Colocasia"
    ],
    "fruits": [
        "Mango", "Banana", "Citrus (Orange, Lemon, Lime)", "Apple",
        "Grapes", "Pomegranate", "Guava", "Pineapple", "Papaya",
        "Watermelon", "Muskmelon", "Pear", "Peach", "Plum",
        "Apricot", "Litchi", "Jackfruit", "Ber", "Aonla (Indian Gooseberry)",
        "Custard Apple", "Jamun", "Kiwi", "Strawberry", "Fig",
        "Cherry", "Avocado", "Persimmon", "Passion Fruit", "Dragon Fruit"
    ]
}

regions_ml = sorted([
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
])

months_ml = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

fertilizers_ml = [
    "Urea", "Ammonium Sulphate (AS)", "Calcium Ammonium Nitrate (CAN)",
    "Ammonium Chloride", "Anhydrous Ammonia", "Single Super Phosphate (SSP)",
    "Double Super Phosphate (DSP)", "Triple Super Phosphate (TSP)",
    "Diammonium Phosphate (DAP)", "Monoammonium Phosphate (MAP)", "Rock Phosphate",
    "Bone Meal", "Muriate of Potash (MOP)", "Sulphate of Potash (SOP)",
    "NPK 10:26:26", "NPK 12:32:16", "NPK 14:28:14", "NPK 14:35:14",
    "NPK 15:15:15", "NPK 16:20:0", "NPK 17:17:17", "NPK 19:19:19",
    "NPK 20:20:0", "NPK 20:20:13", "NPK 28:28:0", "NPK 30:10:10",
    "Zinc Sulphate", "Zinc Oxysulphate", "Zinc EDTA", "Ferrous Sulphate",
    "Manganese Sulphate", "Copper Sulphate", "Boron (Boric Acid/Borax)",
    "Molybdenum (Ammonium Molybdate)", "Compost", "Vermicompost",
    "Farmyard Manure (FYM)", "Green Manure", "Azolla", "Rhizobium Biofertilizer",
    "Azotobacter Biofertilizer", "Phosphobacteria", "Potash Mobilizing Biofertilizer",
    "Vesicular Arbuscular Mycorrhiza (VAM)", "Sulphur-Coated Urea",
    "Neem-Coated Urea", "Gypsum", "Pyrites", "Dolomite",
    "Ammonium Nitrate", "Calcium Nitrate", "Potassium Nitrate", "Magnesium Sulphate",
    "Chelated Iron", "Water Soluble NPK (19:19:19)", "Water Soluble NPK (13:40:13)",
    "Zinc Fortified Urea", "Boron Fortified NPK", "Polymer Coated Urea",
    "Sulfur Coated Urea"
]

crop_to_int = {crop: i for i, crop in enumerate([item for sublist in crops_ml.values() for item in sublist])}
region_to_int = {region: i for i, region in enumerate(regions_ml)}
month_to_int = {month: i for i, month in enumerate(months_ml)}

EXPECTED_MODEL_INPUT_FEATURES = 10

# --- Database Functions ---
def init_db():
    """Initialize SQLite database with users table if it doesn't exist."""
    conn = sqlite3.connect('agridash.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, 
            phone TEXT UNIQUE NOT NULL, 
            full_name TEXT NOT NULL,
            farm_name TEXT NOT NULL,
            location TEXT DEFAULT 'Delhi',
            total_land REAL DEFAULT 10.0,
            member_since TEXT DEFAULT CURRENT_DATE,
            reset_token TEXT,
            token_expiry DATETIME
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            acre REAL NOT NULL,
            crop_type TEXT NOT NULL,
            stage TEXT NOT NULL,
            planting_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soil_testing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            test_date TEXT NOT NULL,
            nitrogen_level TEXT,
            phosphorus_level TEXT,
            potassium_level TEXT,
            ph_level REAL,
            recommendations TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect('agridash.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_user_by_username(username):
    """Retrieve user by username from database."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    """Retrieve user by email from database."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ?', (email,)
    ).fetchone()
    conn.close()
    return user


def get_user_by_phone(phone):
    """Retrieve user by phone from database."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE phone = ?', (phone,)
    ).fetchone()
    conn.close()
    return user


def get_user_by_identifier(identifier):
    """Retrieve user by username, email, or phone."""
    if re.match(r'^[^@]+@[^@]+\.[^@]+$', identifier):
        return get_user_by_email(identifier)
    elif re.match(r'^[\+\d\s\-\(\)]{10,}$', identifier.replace(' ', '')):
        return get_user_by_phone(identifier)
    else:
        return get_user_by_username(identifier)


def get_user_by_id(user_id):
    """Retrieve user by ID from database."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return user


def get_user_by_reset_token(token):
    """Retrieve user by reset token."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE reset_token = ? AND token_expiry > datetime("now")', (token,)
    ).fetchone()
    conn.close()
    return user


def create_user(username, password_hash, email, phone, full_name, farm_name, location, total_land):
    """Create a new user in the database."""
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash, email, phone, full_name, farm_name, location, total_land) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (username, password_hash, email, phone, full_name, farm_name, location, total_land)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        return False
    finally:
        conn.close()


def update_password(user_id, password_hash):
    """Update user password."""
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE users SET password_hash = ?, reset_token = NULL, token_expiry = NULL WHERE id = ?',
            (password_hash, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Password update error: {e}")
        return False
    finally:
        conn.close()


def update_user_profile(user_id, email, phone, full_name, farm_name, location, total_land):
    """Update user profile details."""
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE users SET email = ?, phone = ?, full_name = ?, farm_name = ?, location = ?, total_land = ? WHERE id = ?',
            (email, phone, full_name, farm_name, location, total_land, user_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Profile update integrity error: {e}")
        return False
    except Exception as e:
        print(f"Profile update error: {e}")
        return False
    finally:
        conn.close()


def set_reset_token(user_id, token):
    """Set password reset token for user."""
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE users SET reset_token = ?, token_expiry = datetime("now", "+1 hour") WHERE id = ?',
            (token, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Set reset token error: {e}")
        return False
    finally:
        conn.close()


def get_user_crops(user_id):
    """Retrieve crops for the logged-in user."""
    conn = get_db_connection()
    crops = conn.execute(
        'SELECT * FROM crops WHERE user_id = ? ORDER BY planting_date DESC', (user_id,)
    ).fetchall()
    conn.close()
    return crops


def get_soil_testing_data(user_id):
    """Retrieve soil testing data for the user."""
    conn = get_db_connection()
    soil_data = conn.execute(
        'SELECT * FROM soil_testing WHERE user_id = ? ORDER BY test_date DESC', (user_id,)
    ).fetchall()
    conn.close()
    return soil_data


def add_user_crop(user_id, acre, crop_type, stage, planting_date):
    """Add a new crop for the user."""
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO crops (user_id, acre, crop_type, stage, planting_date) VALUES (?, ?, ?, ?, ?)',
            (user_id, acre, crop_type, stage, planting_date)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Add crop error: {e}")
        return False
    finally:
        conn.close()


def delete_user_crop(crop_id, user_id):
    """Delete a crop belonging to the user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM crops WHERE id = ? AND user_id = ?', (crop_id, user_id)
    )
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def add_soil_test_result(user_id, test_date, n_level, p_level, k_level, ph_level, recommendations):
    """Add a new soil test result for the user."""
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO soil_testing (user_id, test_date, nitrogen_level, phosphorus_level, potassium_level, ph_level, recommendations) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, test_date, n_level, p_level, k_level, ph_level, recommendations)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Add soil test error: {e}")
        return False
    finally:
        conn.close()


# --- Static Data/Simulation Functions ---
STATIC_WEATHER = {
    'Delhi': {'temperature': 28, 'description': 'Sunny with haze', 'humidity': 65, 'icon': '☀️', 'wind': '5 km/h'},
    'Pune': {'temperature': 24, 'description': 'Partly Cloudy', 'humidity': 70, 'icon': '⛅', 'wind': '10 km/h'},
    'Shimla': {'temperature': 15, 'description': 'Cloudy, chance of rain', 'humidity': 60, 'icon': '☁️',
               'wind': '8 km/h'},
    'Bangalore': {'temperature': 26, 'description': 'Clear skies', 'humidity': 68, 'icon': '☀️', 'wind': '7 km/h'},
    'Mumbai': {'temperature': 30, 'description': 'Humid', 'humidity': 75, 'icon': '🌤️', 'wind': '12 km/h'}
}

FORECAST_DATA = [
    {'day': 'Today', 'high': 28, 'low': 18, 'icon': '☀️', 'condition': 'Sunny'},
    {'day': 'Tomorrow', 'high': 26, 'low': 19, 'icon': '⛅', 'condition': 'Partly Cloudy'},
    {'day': 'Day 3', 'high': 24, 'low': 17, 'icon': '🌧️', 'condition': 'Light Rain'},
    {'day': 'Day 4', 'high': 25, 'low': 16, 'icon': '☁️', 'condition': 'Cloudy'},
    {'day': 'Day 5', 'high': 27, 'low': 18, 'icon': '☀️', 'condition': 'Sunny'}
]


def get_weather_data(location_str):
    """Simulates fetching weather data based on a location string."""
    location_str = location_str.title()
    if location_str in STATIC_WEATHER:
        data = STATIC_WEATHER[location_str].copy()
        data['city'] = location_str
        return data

    default_data = STATIC_WEATHER['Delhi'].copy()
    default_data['city'] = location_str
    default_data['temperature'] = default_data['temperature'] - 2
    default_data['description'] = f"Forecast for {location_str}"
    default_data['icon'] = '❓'
    return default_data


def get_fertilizer_recommendation(soil_data, crop_type):
    """Simulates a basic fertilizer recommendation logic based on soil and crop."""
    if not soil_data:
        return {
            'status': 'Warning',
            'message': 'No recent soil test found. Cannot provide a tailored recommendation. Please perform a soil test.',
            'recommendation': 'General NPK (15-15-15) as a starting point, but not recommended without data.'
        }

    recent_test = soil_data[0]

    n_status = recent_test['nitrogen_level']
    p_status = recent_test['phosphorus_level']
    k_status = recent_test['potassium_level']
    ph = recent_test['ph_level']

    base_rec = "Maintain current regimen. "

    if n_status in ['Low', 'Very Low']:
        base_rec += "Increase Nitrogen (N) application (e.g., Urea). "
    if p_status in ['Low', 'Very Low']:
        base_rec += "Increase Phosphorus (P) application (e.g., DAP). "
    if k_status in ['Low', 'Very Low']:
        base_rec += "Increase Potassium (K) application (e.g., Muriate of Potash). "

    if ph < 6.0:
        base_rec += "Soil pH is low (acidic). Consider liming (Calcium Carbonate). "
    elif ph > 7.5:
        base_rec += "Soil pH is high (alkaline). Consider Sulphur application. "

    if base_rec == "Maintain current regimen. ":
        base_rec += "Soil levels are balanced."
        status = "Good"
    else:
        status = "Needs Adjustment"

    return {
        'status': status,
        'message': f"Recommendation for **{crop_type.title()}** based on soil test from **{recent_test['test_date']}**.",
        'recommendation': base_rec
    }


def get_soil_status_class(level):
    """Utility to map soil levels to CSS classes."""
    if level in ['High', 'Very High']:
        return 'soil-status-excellent'
    elif level == 'Medium':
        return 'soil-status-good'
    elif level == 'Low':
        return 'soil-status-fair'
    else:
        return 'soil-status-poor'


def categorize_fertilizer(fertilizer_name):
    """Categorize the fertilizer based on its composition"""
    if "NPK" in fertilizer_name or "DAP" in fertilizer_name or "MAP" in fertilizer_name:
        return "Complex Fertilizer"
    elif "Urea" in fertilizer_name or "Ammonium" in fertilizer_name:
        return "Nitrogen Fertilizer"
    elif "Super" in fertilizer_name or "Phosphate" in fertilizer_name:
        return "Phosphatic Fertilizer"
    elif "Potash" in fertilizer_name or "Potassium" in fertilizer_name:
        return "Potassic Fertilizer"
    elif any(x in fertilizer_name for x in ["Zinc", "Iron", "Boron", "Manganese"]):
        return "Micronutrient Fertilizer"
    elif any(x in fertilizer_name for x in ["Compost", "Manure", "Biofertilizer"]):
        return "Organic Fertilizer"
    else:
        return "Special Fertilizer"


# --- Email Utility Functions ---
def send_reset_email(email, token):
    """Send password reset email."""
    try:
        msg = MIMEMultipart()
        msg['Subject'] = 'AgriDash Pro - Password Reset Request'
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email

        reset_url = f"http://127.0.0.1:5000/reset-password/{token}"

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #2e7d32;">AgriDash Pro Password Reset</h2>
                <p>You requested a password reset for your AgriDash Pro account.</p>
                <p>Click the link below to reset your password:</p>
                <a href="{reset_url}" style="background-color: #4caf50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this reset, please ignore this email.</p>
                <hr>
                <p style="color: #666;">AgriDash Pro - Farm Management System</p>
            </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


# --- Utility Functions & Decorators ---
def login_required(f):
    """Decorator to protect routes that require authentication."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def calculate_total_acreage(crops):
    """Calculates the total acreage under cultivation."""
    return sum(float(crop['acre']) for crop in crops) if crops else 0


@app.before_request
def load_logged_in_user_and_weather():
    """Load user data and weather into Flask's global context 'g'."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
        g.weather = get_weather_data('Delhi')
    else:
        g.user = get_user_by_id(user_id)
        if g.user and g.user['location']:
            g.weather = get_weather_data(g.user['location'])
        else:
            g.weather = get_weather_data('Delhi')


# --- Flask Routes ---
@app.route('/', methods=['GET'])
def home():
    """Renders the landing page."""
    return render_template_string(BASE_TEMPLATE + HOME_CONTENT, title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')

        user = get_user_by_identifier(identifier)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash(f'Welcome back, {user["full_name"].split()[0]}!', 'success')
            next_url = request.args.get('next') or url_for('dashboard')
            return redirect(next_url)
        else:
            flash('Login failed. Check your credentials.', 'error')

    return render_template_string(BASE_TEMPLATE + LOGIN_CONTENT, title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        full_name = request.form.get('full_name')
        farm_name = request.form.get('farm_name')
        location = request.form.get('location')
        total_land = request.form.get('total_land')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('register'))

        if get_user_by_username(username):
            flash('Username already taken.', 'error')
            return redirect(url_for('register'))

        if get_user_by_email(email):
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        if get_user_by_phone(phone):
            flash('Phone number already registered.', 'error')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)

        try:
            total_land = float(total_land)
        except ValueError:
            flash('Total Land must be a valid number.', 'error')
            return redirect(url_for('register'))

        if create_user(username, password_hash, email, phone, full_name, farm_name, location, total_land):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Username, Email, or Phone may already be in use.', 'error')

    return render_template_string(BASE_TEMPLATE + REGISTER_CONTENT, title='Register')


@app.route('/logout')
@login_required
def logout():
    """Handles user logout."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handles the forgot password request."""
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = get_user_by_email(email)

        if user:
            token = secrets.token_urlsafe(32)

            if set_reset_token(user['id'], token):
                if send_reset_email(email, token):
                    flash('A password reset link has been sent to your email.', 'success')
                else:
                    flash('Failed to send reset email. Please check server settings.', 'error')
            else:
                flash('An error occurred while setting the reset token.', 'error')
        else:
            flash('If an account exists with that email, a password reset link has been sent.', 'success')

        return redirect(url_for('forgot_password'))

    return render_template_string(BASE_TEMPLATE + FORGOT_PASSWORD_CONTENT, title='Forgot Password')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handles the actual password reset using the token."""
    if g.user:
        return redirect(url_for('dashboard'))

    user = get_user_by_reset_token(token)

    if not user:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template_string(BASE_TEMPLATE + RESET_PASSWORD_CONTENT, title='Reset Password')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template_string(BASE_TEMPLATE + RESET_PASSWORD_CONTENT, title='Reset Password')

        password_hash = generate_password_hash(password)
        if update_password(user['id'], password_hash):
            flash('Your password has been updated. You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('An error occurred during password update.', 'error')

    return render_template_string(BASE_TEMPLATE + RESET_PASSWORD_CONTENT, title='Reset Password')


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Renders the user's main dashboard."""
    user_crops = get_user_crops(g.user['id'])
    total_acreage = calculate_total_acreage(user_crops)
    soil_data = get_soil_testing_data(g.user['id'])

    last_test_date = soil_data[0]['test_date'] if soil_data else 'N/A'

    dashboard_rec = get_fertilizer_recommendation(soil_data, 'Wheat')

    return render_template_string(
        BASE_TEMPLATE + DASHBOARD_CONTENT,
        title='Dashboard',
        user=g.user,
        weather=g.weather,
        crops=user_crops,
        total_acreage=total_acreage,
        soil_data=soil_data[0] if soil_data else None,
        last_test_date=last_test_date,
        dashboard_rec=dashboard_rec,
        get_soil_status_class=get_soil_status_class
    )


@app.route('/weather', methods=['GET'])
@login_required
def weather():
    """Renders the detailed weather page."""
    return render_template_string(
        BASE_TEMPLATE + WEATHER_CONTENT,
        title='Weather Intelligence',
        weather=g.weather,
        forecast=FORECAST_DATA
    )


@app.route('/set_location', methods=['POST'])
@login_required
def set_location():
    """Updates the user's location based on the weather widget input."""
    new_location = request.form.get('location_input')
    user_id = g.user['id']

    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE users SET location = ? WHERE id = ?',
            (new_location.title(), user_id)
        )
        conn.commit()
        flash(f"Location updated to {new_location.title()}.", 'success')
    except Exception as e:
        flash("Failed to update location.", 'error')
        print(f"Location update error: {e}")
    finally:
        conn.close()

    return redirect(request.referrer or url_for('dashboard'))


@app.route('/fertilizer', methods=['GET', 'POST'])
@login_required
def fertilizer():
    """Renders the fertilizer/soil management page."""
    user_crops = get_user_crops(g.user['id'])
    soil_data = get_soil_testing_data(g.user['id'])

    recommendation = None
    default_crop = user_crops[0]['crop_type'] if user_crops else 'Wheat'
    selected_crop = request.args.get('crop', default_crop)

    if selected_crop:
        recommendation = get_fertilizer_recommendation(soil_data, selected_crop)

    if request.method == 'POST':
        if 'soil_test_submit' in request.form:
            test_date = request.form.get('test_date')
            n_level = request.form.get('n_level')
            p_level = request.form.get('p_level')
            k_level = request.form.get('k_level')
            ph_level = request.form.get('ph_level')
            recommendations_text = request.form.get('recommendations')

            try:
                ph_level = float(ph_level)
            except ValueError:
                flash('pH Level must be a number.', 'error')
                return redirect(url_for('fertilizer'))

            if add_soil_test_result(g.user['id'], test_date, n_level, p_level, k_level, ph_level, recommendations_text):
                flash('New soil test results added successfully! Recalculating recommendations.', 'success')
            else:
                flash('Failed to add soil test results.', 'error')

            return redirect(url_for('fertilizer'))

    return render_template_string(
        BASE_TEMPLATE + FERTILIZER_CONTENT,
        title='Fertilizer & Soil Management',
        crops=user_crops,
        soil_data=soil_data,
        recommendation=recommendation,
        selected_crop=selected_crop,
        get_soil_status_class=get_soil_status_class,
        current_date=datetime.now().strftime('%Y-%m-%d'),
        ml_model_available=ml_model_available
    )


@app.route('/ml-fertilizer-predictor', methods=['GET'])
@login_required
def ml_fertilizer_predictor():
    """Renders the ML-based fertilizer prediction page."""
    return render_template_string(
        BASE_TEMPLATE + ML_PREDICTOR_CONTENT,
        title='AI Fertilizer Predictor',
        crops=crops_ml,
        regions=regions_ml,
        months=months_ml,
        ml_model_available=ml_model_available
    )


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """ML-based fertilizer prediction endpoint."""
    if not ml_model_available:
        return jsonify({"error": "ML model is not available. Please ensure model.h5 exists."}), 503

    try:
        data = request.get_json()

        n_val = float(data.get("N"))
        p_val = float(data.get("P"))
        k_val = float(data.get("K"))
        temp_val = float(data.get("temperature"))
        humidity_val = float(data.get("humidity"))
        ph_val = float(data.get("ph"))
        moisture_val = float(data.get("moisture"))

        parameter_ranges = {
            "N": (0, 300),
            "P": (0, 200),
            "K": (0, 250),
            "temperature": (10, 50),
            "humidity": (0, 100),
            "ph": (4.0, 9.0),
            "moisture": (0, 100)
        }

        for param, value in [
            ("N", n_val), ("P", p_val), ("K", k_val),
            ("temperature", temp_val), ("humidity", humidity_val),
            ("ph", ph_val), ("moisture", moisture_val)
        ]:
            min_val, max_val = parameter_ranges[param]
            if not (min_val <= value <= max_val):
                return jsonify({
                    "error": f"Invalid {param} value: {value}. Must be between {min_val} and {max_val}."
                }), 400

        selected_crop_str = data.get("crop")
        selected_region_str = data.get("region")
        selected_month_str = data.get("month")

        crop_encoded = crop_to_int.get(selected_crop_str)
        region_encoded = region_to_int.get(selected_region_str)
        month_encoded = month_to_int.get(selected_month_str)

        if crop_encoded is None:
            return jsonify({"error": f"Invalid crop: '{selected_crop_str}'"}), 400
        if region_encoded is None:
            return jsonify({"error": f"Invalid region: '{selected_region_str}'"}), 400
        if month_encoded is None:
            return jsonify({"error": f"Invalid month: '{selected_month_str}'"}), 400

        features = [
            n_val, p_val, k_val, temp_val, humidity_val,
            ph_val, moisture_val, float(crop_encoded),
            float(region_encoded), float(month_encoded)
        ]

        if len(features) != EXPECTED_MODEL_INPUT_FEATURES:
            return jsonify({
                "error": f"Feature count mismatch. Expected {EXPECTED_MODEL_INPUT_FEATURES} features, got {len(features)}"
            }), 500

        input_data = np.array([features], dtype=np.float32)
        prediction = model.predict(input_data)
        predicted_index = int(np.argmax(prediction))

        if 0 <= predicted_index < len(fertilizers_ml):
            predicted_fertilizer = fertilizers_ml[predicted_index]
        else:
            predicted_fertilizer = "Custom Fertilizer Blend"

        return jsonify({
            "fertilizer": predicted_fertilizer,
            "fertilizer_type": categorize_fertilizer(predicted_fertilizer)
        })

    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/crop-management', methods=['GET', 'POST'])
@login_required
def crop_management():
    """Renders the crop management page."""
    user_crops = get_user_crops(g.user['id'])

    if request.method == 'POST':
        if 'add_crop' in request.form:
            acre = request.form.get('acre')
            crop_type = request.form.get('crop_type')
            stage = request.form.get('stage')
            planting_date = request.form.get('planting_date')

            try:
                acre = float(acre)
                if acre <= 0:
                    flash('Acreage must be a positive number.', 'error')
                    return redirect(url_for('crop_management'))
            except ValueError:
                flash('Acreage must be a valid number.', 'error')
                return redirect(url_for('crop_management'))

            if add_user_crop(g.user['id'], acre, crop_type, stage, planting_date):
                flash(f'{crop_type} added successfully!', 'success')
            else:
                flash('Failed to add crop.', 'error')

        elif 'delete_crop_id' in request.form:
            crop_id = request.form.get('delete_crop_id')

            try:
                crop_id = int(crop_id)
            except ValueError:
                flash('Invalid crop ID.', 'error')
                return redirect(url_for('crop_management'))

            if delete_user_crop(crop_id, g.user['id']):
                flash('Crop deleted successfully.', 'success')
            else:
                flash('Failed to delete crop or crop does not belong to you.', 'error')

        return redirect(url_for('crop_management'))

    return render_template_string(
        BASE_TEMPLATE + CROP_MANAGEMENT_CONTENT,
        title='Crop Management',
        user=g.user,
        crops=user_crops,
        total_acreage=calculate_total_acreage(user_crops)
    )


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Renders the user profile page."""
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        full_name = request.form.get('full_name')
        farm_name = request.form.get('farm_name')
        location = request.form.get('location')
        total_land = request.form.get('total_land')

        try:
            total_land = float(total_land)
        except ValueError:
            flash('Total Land must be a valid number.', 'error')
            return redirect(url_for('profile'))

        if update_user_profile(g.user['id'], email, phone, full_name, farm_name, location, total_land):
            flash('Profile updated successfully!', 'success')
            g.user = get_user_by_id(g.user['id'])
        else:
            flash('Profile update failed. Email or Phone may already be in use.', 'error')

        return redirect(url_for('profile'))

    return render_template_string(BASE_TEMPLATE + PROFILE_CONTENT, title='User Profile', user=g.user)


@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    """Renders the contact page with a simple feedback form."""
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')

        flash(f'Thank you for your feedback! Subject: "{subject}" - We will get back to you soon.', 'success')

        return redirect(url_for('contact'))

    return render_template_string(BASE_TEMPLATE + CONTACT_CONTENT, title='Contact & Support')


# --- HTML Templates ---
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriDash Pro - {% block title %}{{ title | default('Farm Management') }}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-green: #2e7d32;
            --light-green: #4caf50;
            --dark-green: #1b5e20;
            --earth-brown: #8d6e63;
            --sun-yellow: #ffd54f;
            --sky-blue: #29b6f6;
        }

        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding-top: 76px;
        }

        .navbar {
            background: linear-gradient(135deg, var(--dark-green), var(--primary-green)) !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
        }

        .weather-widget {
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 5px 15px !important;
            color: white; 
            display: flex;
            align-items: center;
        }

        .footer {
            background: linear-gradient(135deg, var(--dark-green), var(--primary-green));
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
        }

        .stat-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .weather-card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .forecast-day {
            transition: all 0.3s ease;
        }

        .forecast-day:hover {
            background-color: #f8f9fa;
            transform: scale(1.05);
        }

        .contact-info {
            border-left: 3px solid var(--primary-green);
            padding-left: 15px;
        }

        .btn-success {
            background: linear-gradient(135deg, var(--light-green), var(--primary-green));
            border: none;
        }

        .btn-primary {
            background: linear-gradient(135deg, #2196F3, var(--sky-blue));
            border: none;
        }

        .card {
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }

        .card-header {
            border-radius: 15px 15px 0 0 !important;
            border: none;
            font-weight: 600;
        }

        .table-hover tbody tr:hover {
            background-color: rgba(76, 175, 80, 0.1);
        }

        .badge {
            font-size: 0.8em;
            padding: 0.5em 0.8em;
        }

        .auth-card {
            max-width: 500px;
            margin: 2rem auto;
        }

        .hero-section {
            background: linear-gradient(135deg, var(--dark-green), var(--primary-green));
            color: white;
            padding: 4rem 0;
            border-radius: 15px;
            margin-bottom: 3rem;
        }

        .soil-status-excellent { color: #28a745; font-weight: bold; }
        .soil-status-good { color: #20c997; font-weight: bold; }
        .soil-status-fair { color: #ffc107; font-weight: bold; }
        .soil-status-poor { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home') }}">
                <i class="fas fa-tractor me-2"></i>
                AgriDash Pro
            </a>

            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    {% if session.user_id %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('dashboard') }}"><i class="fas fa-home me-1"></i>Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('weather') }}"><i class="fas fa-cloud-sun me-1"></i>Weather</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('fertilizer') }}"><i class="fas fa-flask me-1"></i>Fertilizer</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('profile') }}"><i class="fas fa-user me-1"></i>Profile</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('contact') }}"><i class="fas fa-envelope me-1"></i>Contact</a></li>
                    {% endif %}
                </ul>

                <div class="navbar-nav ms-auto">
                    {% if session.user_id %}
                    <div class="weather-widget nav-link p-1">
                        <form method="POST" action="{{ url_for('set_location') }}" class="d-flex align-items-center me-3" style="margin:0;">
                            <i class="fas fa-map-marker-alt me-1 text-white"></i>
                            <input type="text" name="location_input" value="{{ g.weather.city }}" 
                                   class="form-control form-control-sm bg-transparent border-0 text-white p-0" 
                                   placeholder="City" style="max-width: 100px;">
                            <button type="submit" class="btn btn-sm text-white p-0 ps-1">
                                <i class="fas fa-search" style="font-size: 0.8em;"></i>
                            </button>
                        </form>
                        <span class="ms-2">
                            <strong>{{ g.weather.temperature }}°C</strong> {{ g.weather.icon }}
                        </span>
                    </div>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt me-1"></i>Logout</a></li>
                    {% else %}
                    <a class="btn btn-sm btn-outline-light me-2" href="{{ url_for('login') }}">
                        <i class="fas fa-sign-in-alt me-1"></i> Login
                    </a>
                    <a class="btn btn-sm btn-light" href="{{ url_for('register') }}">
                        <i class="fas fa-user-plus me-1"></i> Register
                    </a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    <main class="container mt-5 pt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <footer class="footer mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2025 AgriDash Pro </p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p>📞 Support: +91 1800-AGRIHELP | ✉️ help@agridash.com</p>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
FORGOT_PASSWORD_CONTENT = """
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card auth-card">
            <div class="card-header bg-warning text-dark text-center">
                <h4 class="mb-0"><i class="fas fa-key me-2"></i> Reset Password</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="email" class="form-label">Email Address</label>
                        <input type="email" class="form-control" id="email" name="email" required 
                               placeholder="Enter your registered email address">
                        <div class="form-text">We'll send you a password reset link</div>
                    </div>
                    <button type="submit" class="btn btn-warning w-100">
                        <i class="fas fa-paper-plane me-2"></i> Send Reset Link
                    </button>
                </form>
                <div class="text-center mt-3">
                    <p>Remember your password? <a href="{{ url_for('login') }}">Login here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
"""

RESET_PASSWORD_CONTENT = """
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card auth-card">
            <div class="card-header bg-primary text-white text-center">
                <h4 class="mb-0"><i class="fas fa-lock me-2"></i> Set New Password</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="password" class="form-label">New Password</label>
                        <input type="password" class="form-control" id="password" name="password" required 
                               placeholder="Enter new password" minlength="6">
                        <div class="form-text">Password must be at least 6 characters</div>
                    </div>
                    <div class="mb-3">
                        <label for="confirm_password" class="form-label">Confirm Password</label>
                        <input type="password" class="form-control" id="confirm_password" name="confirm_password" required 
                               placeholder="Confirm new password">
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-check me-2"></i> Reset Password
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
"""

REGISTER_CONTENT = """
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card auth-card">
            <div class="card-header bg-success text-white text-center">
                <h4 class="mb-0"><i class="fas fa-user-plus me-2"></i> Create Your AgriDash Pro Account</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required 
                                   placeholder="Choose a unique username">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="email" class="form-label">Email Address</label>
                            <input type="email" class="form-control" id="email" name="email" required 
                                   placeholder="your@email.com">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="phone" class="form-label">Phone Number</label>
                            <input type="tel" class="form-control" id="phone" name="phone" required 
                                   placeholder="+91 1234567890">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="full_name" class="form-label">Full Name</label>
                            <input type="text" class="form-control" id="full_name" name="full_name" required 
                                   placeholder="Your full name">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="farm_name" class="form-label">Farm Name</label>
                            <input type="text" class="form-control" id="farm_name" name="farm_name" required 
                                   placeholder="Name of your farm">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="location" class="form-label">Location</label>
                            <input type="text" class="form-control" id="location" name="location" required 
                                   placeholder="City/District" value="Delhi">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="total_land" class="form-label">Total Land (acres)</label>
                        <input type="number" step="0.01" class="form-control" id="total_land" name="total_land" required 
                               placeholder="Total farmland in acres" value="10">
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required 
                                   placeholder="Create a strong password" minlength="6">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="confirm_password" class="form-label">Confirm Password</label>
                            <input type="password" class="form-control" id="confirm_password" name="confirm_password" required 
                                   placeholder="Re-enter password">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-success w-100">
                        <i class="fas fa-check-circle me-2"></i> Register
                    </button>
                </form>
                <div class="text-center mt-3">
                    <p>Already have an account? <a href="{{ url_for('login') }}">Login here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
"""

DASHBOARD_CONTENT = """
<div class="row mb-4">
    <div class="col-12">
        <h2 class="mb-4">
            <i class="fas fa-chart-line me-2"></i>
            Welcome back, {{ user.full_name.split()[0] }}!
        </h2>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-3 mb-3">
        <div class="stat-card card bg-success text-white">
            <div class="card-body text-center">
                <i class="fas fa-leaf fa-3x mb-2"></i>
                <h3>{{ crops|length }}</h3>
                <p class="mb-0">Active Crops</p>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card card bg-primary text-white">
            <div class="card-body text-center">
                <i class="fas fa-map fa-3x mb-2"></i>
                <h3>{{ "%.1f"|format(total_acreage) }}</h3>
                <p class="mb-0">Acres Under Cultivation</p>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card card bg-info text-white">
            <div class="card-body text-center">
                <i class="fas fa-cloud-sun fa-3x mb-2"></i>
                <h3>{{ weather.temperature }}°C</h3>
                <p class="mb-0">{{ weather.description }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="stat-card card bg-warning text-dark">
            <div class="card-body text-center">
                <i class="fas fa-flask fa-3x mb-2"></i>
                <h3>{{ last_test_date }}</h3>
                <p class="mb-0">Last Soil Test</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-8 mb-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-seedling me-2"></i>Your Crops</h5>
            </div>
            <div class="card-body">
                {% if crops %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Crop</th>
                                <th>Acres</th>
                                <th>Stage</th>
                                <th>Planted</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for crop in crops[:5] %}
                            <tr>
                                <td><strong>{{ crop.crop_type }}</strong></td>
                                <td>{{ crop.acre }}</td>
                                <td><span class="badge bg-info">{{ crop.stage }}</span></td>
                                <td>{{ crop.planting_date }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <a href="{{ url_for('crop_management') }}" class="btn btn-success">
                    <i class="fas fa-plus me-2"></i>Manage Crops
                </a>
                {% else %}
                <p class="text-muted">No crops added yet.</p>
                <a href="{{ url_for('crop_management') }}" class="btn btn-success">
                    <i class="fas fa-plus me-2"></i>Add Your First Crop
                </a>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="col-md-4 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-flask me-2"></i>Soil Health</h5>
            </div>
            <div class="card-body">
                {% if soil_data %}
                <div class="mb-3">
                    <strong>Nitrogen (N):</strong>
                    <span class="{{ get_soil_status_class(soil_data.nitrogen_level) }}">
                        {{ soil_data.nitrogen_level }}
                    </span>
                </div>
                <div class="mb-3">
                    <strong>Phosphorus (P):</strong>
                    <span class="{{ get_soil_status_class(soil_data.phosphorus_level) }}">
                        {{ soil_data.phosphorus_level }}
                    </span>
                </div>
                <div class="mb-3">
                    <strong>Potassium (K):</strong>
                    <span class="{{ get_soil_status_class(soil_data.potassium_level) }}">
                        {{ soil_data.potassium_level }}
                    </span>
                </div>
                <div class="mb-3">
                    <strong>pH Level:</strong> {{ "%.1f"|format(soil_data.ph_level) }}
                </div>
                {% else %}
                <p class="text-muted">No soil test data available.</p>
                {% endif %}
                <a href="{{ url_for('fertilizer') }}" class="btn btn-primary">
                    <i class="fas fa-vial me-2"></i>View Details
                </a>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-warning text-dark">
                <h5 class="mb-0"><i class="fas fa-lightbulb me-2"></i>Today's Recommendation</h5>
            </div>
            <div class="card-body">
                {% if dashboard_rec %}
                <div class="alert alert-{{ 'success' if dashboard_rec.status == 'Good' else 'warning' }}">
                    <strong>{{ dashboard_rec.status }}:</strong> {{ dashboard_rec.message }}
                </div>
                <p>{{ dashboard_rec.recommendation }}</p>
                {% else %}
                <p>No recommendations available at this time.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
"""

WEATHER_CONTENT = """
<div class="row mb-4">
    <div class="col-12">
        <h2 class="mb-4">
            <i class="fas fa-cloud-sun me-2"></i>
            Weather Intelligence for {{ weather.city }}
        </h2>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-6 mb-4">
        <div class="weather-card card">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0"><i class="fas fa-thermometer-half me-2"></i>Current Weather</h5>
            </div>
            <div class="card-body text-center">
                <div class="display-1 mb-3">{{ weather.icon }}</div>
                <h2 class="mb-3">{{ weather.temperature }}°C</h2>
                <p class="lead">{{ weather.description }}</p>
                <div class="row mt-4">
                    <div class="col-6">
                        <i class="fas fa-tint fa-2x text-info"></i>
                        <p class="mb-0"><strong>Humidity</strong></p>
                        <p>{{ weather.humidity }}%</p>
                    </div>
                    <div class="col-6">
                        <i class="fas fa-wind fa-2x text-primary"></i>
                        <p class="mb-0"><strong>Wind</strong></p>
                        <p>{{ weather.wind }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="col-md-6 mb-4">
        <div class="weather-card card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-calendar-week me-2"></i>5-Day Forecast</h5>
            </div>
            <div class="card-body">
                {% for day in forecast %}
                <div class="forecast-day d-flex justify-content-between align-items-center p-3 mb-2 rounded">
                    <div>
                        <strong>{{ day.day }}</strong>
                        <br>
                        <small class="text-muted">{{ day.condition }}</small>
                    </div>
                    <div class="text-center">
                        <span class="fs-2">{{ day.icon }}</span>
                    </div>
                    <div class="text-end">
                        <span class="text-danger"><strong>{{ day.high }}°</strong></span>
                        <span class="text-muted"> / {{ day.low }}°</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-book me-2"></i>Farming Advisory</h5>
            </div>
            <div class="card-body">
                <h6><i class="fas fa-check-circle text-success me-2"></i>Based on current conditions:</h6>
                <ul>
                    <li>Temperature is optimal for most crops. Continue regular irrigation.</li>
                    <li>Humidity levels are good. Monitor for fungal diseases.</li>
                    <li>No extreme weather predicted. Safe to proceed with field operations.</li>
                    <li>Consider applying fertilizers in the next 2-3 days when soil moisture is adequate.</li>
                </ul>
            </div>
        </div>
    </div>
</div>
"""

FERTILIZER_CONTENT = """
<div class="row mb-4">
    <div class="col-12">
        <h2 class="mb-4">
            <i class="fas fa-flask me-2"></i>
            Fertilizer & Soil Management
        </h2>
    </div>
</div>

{% if ml_model_available %}
<div class="alert alert-info">
    <i class="fas fa-robot me-2"></i>
    <strong>New!</strong> Try our <a href="{{ url_for('ml_fertilizer_predictor') }}" class="alert-link">AI-Powered Fertilizer Predictor</a> 
    for advanced recommendations based on machine learning.
</div>
{% endif %}

<div class="row mb-4">
    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-vial me-2"></i>Latest Soil Test Results</h5>
            </div>
            <div class="card-body">
                {% if soil_data %}
                {% set latest = soil_data[0] %}
                <p><strong>Test Date:</strong> {{ latest.test_date }}</p>
                <hr>
                <div class="row text-center mb-3">
                    <div class="col-4">
                        <h3 class="{{ get_soil_status_class(latest.nitrogen_level) }}">{{ latest.nitrogen_level }}</h3>
                        <p class="mb-0">Nitrogen (N)</p>
                    </div>
                    <div class="col-4">
                        <h3 class="{{ get_soil_status_class(latest.phosphorus_level) }}">{{ latest.phosphorus_level }}</h3>
                        <p class="mb-0">Phosphorus (P)</p>
                    </div>
                    <div class="col-4">
                        <h3 class="{{ get_soil_status_class(latest.potassium_level) }}">{{ latest.potassium_level }}</h3>
                        <p class="mb-0">Potassium (K)</p>
                    </div>
                </div>
                <p><strong>pH Level:</strong> {{ "%.1f"|format(latest.ph_level) }}</p>
                {% if latest.recommendations %}
                <p><strong>Notes:</strong> {{ latest.recommendations }}</p>
                {% endif %}
                {% else %}
                <p class="text-muted">No soil test data available. Add your first test below.</p>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="col-md-6 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-clipboard-check me-2"></i>Fertilizer Recommendation</h5>
            </div>
            <div class="card-body">
                {% if crops %}
                <form method="GET" class="mb-3">
                    <label for="crop" class="form-label">Select Crop:</label>
                    <select name="crop" id="crop" class="form-select" onchange="this.form.submit()">
                        {% for crop in crops %}
                        <option value="{{ crop.crop_type }}" {% if crop.crop_type == selected_crop %}selected{% endif %}>
                            {{ crop.crop_type }}
                        </option>
                        {% endfor %}
                    </select>
                </form>
                {% endif %}

                {% if recommendation %}
                <div class="alert alert-{{ 'success' if recommendation.status == 'Good' else 'warning' }}">
                    <strong>{{ recommendation.status }}:</strong> {{ recommendation.message }}
                </div>
                <p>{{ recommendation.recommendation }}</p>
                {% else %}
                <p class="text-muted">Add crops and soil test data to get recommendations.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-warning text-dark">
                <h5 class="mb-0"><i class="fas fa-plus-circle me-2"></i>Add New Soil Test Result</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-3 mb-3">
                            <label for="test_date" class="form-label">Test Date</label>
                            <input type="date" class="form-control" id="test_date" name="test_date" 
                                   value="{{ current_date }}" required>
                        </div>
                        <div class="col-md-3 mb-3">
                            <label for="n_level" class="form-label">Nitrogen Level</label>
                            <select class="form-select" id="n_level" name="n_level" required>
                                <option value="Very Low">Very Low</option>
                                <option value="Low">Low</option>
                                <option value="Medium" selected>Medium</option>
                                <option value="High">High</option>
                                <option value="Very High">Very High</option>
                            </select>
                        </div>
                        <div class="col-md-3 mb-3">
                            <label for="p_level" class="form-label">Phosphorus Level</label>
                            <select class="form-select" id="p_level" name="p_level" required>
                                <option value="Very Low">Very Low</option>
                                <option value="Low">Low</option>
                                <option value="Medium" selected>Medium</option>
                                <option value="High">High</option>
                                <option value="Very High">Very High</option>
                            </select>
                        </div>
                        <div class="col-md-3 mb-3">
                            <label for="k_level" class="form-label">Potassium Level</label>
                            <select class="form-select" id="k_level" name="k_level" required>
                                <option value="Very Low">Very Low</option>
                                <option value="Low">Low</option>
                                <option value="Medium" selected>Medium</option>
                                <option value="High">High</option>
                                <option value="Very High">Very High</option>
                            </select>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="ph_level" class="form-label">pH Level</label>
                            <input type="number" step="0.1" min="4" max="9" class="form-control" 
                                   id="ph_level" name="ph_level" value="6.5" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="recommendations" class="form-label">Additional Notes (Optional)</label>
                            <input type="text" class="form-control" id="recommendations" name="recommendations" 
                                   placeholder="Any observations or lab recommendations">
                        </div>
                    </div>
                    <button type="submit" name="soil_test_submit" class="btn btn-warning">
                        <i class="fas fa-save me-2"></i>Save Test Result
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

{% if soil_data and soil_data|length > 1 %}
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0"><i class="fas fa-history me-2"></i>Soil Test History</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>N</th>
                                <th>P</th>
                                <th>K</th>
                                <th>pH</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for test in soil_data[1:] %}
                            <tr>
                                <td>{{ test.test_date }}</td>
                                <td class="{{ get_soil_status_class(test.nitrogen_level) }}">{{ test.nitrogen_level }}</td>
                                <td class="{{ get_soil_status_class(test.phosphorus_level) }}">{{ test.phosphorus_level }}</td>
                                <td class="{{ get_soil_status_class(test.potassium_level) }}">{{ test.potassium_level }}</td>
                                <td>{{ "%.1f"|format(test.ph_level) }}</td>
                                <td>{{ test.recommendations or '-' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}
"""

ML_PREDICTOR_CONTENT = """
<div class="row mb-4">
    <div class="col-12">
        <h2 class="mb-4">
            <i class="fas fa-robot me-2"></i>
            AI-Powered Fertilizer Predictor
        </h2>
        <p class="lead">Get personalized fertilizer recommendations using machine learning</p>
    </div>
</div>

{% if not ml_model_available %}
<div class="alert alert-danger">
    <i class="fas fa-exclamation-triangle me-2"></i>
    <strong>ML Model Not Available:</strong> The machine learning model could not be loaded. 
    Please ensure model.h5 is in the application directory.
</div>
{% endif %}

<div class="row">
    <div class="col-lg-8 mx-auto">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-brain me-2"></i>Enter Your Farm Parameters</h5>
            </div>
            <div class="card-body">
                <form id="mlPredictionForm">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="crop" class="form-label">Crop Type</label>
                            <select class="form-select" id="crop" name="crop" required>
                                <optgroup label="Cereals">
                                    {% for crop in crops.cereals %}
                                    <option value="{{ crop }}">{{ crop }}</option>
                                    {% endfor %}
                                </optgroup>
                                <optgroup label="Pulses">
                                    {% for crop in crops.pulses %}
                                    <option value="{{ crop }}">{{ crop }}</option>
                                    {% endfor %}
                                </optgroup>
                                <optgroup label="Oilseeds">
                                    {% for crop in crops.oilseeds %}
                                    <option value="{{ crop }}">{{ crop }}</option>
                                    {% endfor %}
                                </optgroup>
                                <optgroup label="Cash Crops">
                                    {% for crop in crops.cash_crops %}
                                    <option value="{{ crop }}">{{ crop }}</option>
                                    {% endfor %}
                                </optgroup>
                                <optgroup label="Vegetables">
                                    {% for crop in crops.vegetables %}
                                    <option value="{{ crop }}">{{ crop }}</option>
                                    {% endfor %}
                                </optgroup>
                                <optgroup label="Fruits">
                                    {% for crop in crops.fruits %}
                                    <option value="{{ crop }}">{{ crop }}</option>
                                    {% endfor %}
                                </optgroup>
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="region" class="form-label">Region</label>
                            <select class="form-select" id="region" name="region" required>
                                {% for region in regions %}
                                <option value="{{ region }}">{{ region }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="month" class="form-label">Month</label>
                            <select class="form-select" id="month" name="month" required>
                                {% for month in months %}
                                <option value="{{ month }}">{{ month }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="temperature" class="form-label">Temperature (°C)</label>
                            <input type="number" class="form-control" id="temperature" name="temperature" 
                                   min="10" max="50" step="0.1" value="25" required>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="N" class="form-label">Nitrogen (N)</label>
                            <input type="number" class="form-control" id="N" name="N" 
                                   min="0" max="300" value="50" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="P" class="form-label">Phosphorus (P)</label>
                            <input type="number" class="form-control" id="P" name="P" 
                                   min="0" max="200" value="30" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="K" class="form-label">Potassium (K)</label>
                            <input type="number" class="form-control" id="K" name="K" 
                                   min="0" max="250" value="40" required>
                        </div>
                    </div>RetryClaude does not have the ability to run the code it generates yet.AContinueEditpython                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="humidity" class="form-label">Humidity (%)</label>
                            <input type="number" class="form-control" id="humidity" name="humidity" 
                                   min="0" max="100" value="65" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="ph" class="form-label">pH Level</label>
                            <input type="number" class="form-control" id="ph" name="ph" 
                                   min="4" max="9" step="0.1" value="6.5" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label for="moisture" class="form-label">Soil Moisture (%)</label>
                            <input type="number" class="form-control" id="moisture" name="moisture" 
                                   min="0" max="100" value="50" required>
                        </div>
                    </div>

                    <div class="d-grid">
                        <button type="submit" class="btn btn-success btn-lg" {% if not ml_model_available %}disabled{% endif %}>
                            <i class="fas fa-magic me-2"></i>Get AI Recommendation
                        </button>
                    </div>
                </form>

                <div id="predictionResult" class="mt-4" style="display:none;">
                    <div class="alert alert-success">
                        <h5><i class="fas fa-check-circle me-2"></i>Recommended Fertilizer</h5>
                        <h3 id="fertilizerName" class="mb-2"></h3>
                        <p class="mb-0"><strong>Type:</strong> <span id="fertilizerType"></span></p>
                    </div>
                </div>

                <div id="predictionError" class="mt-4 alert alert-danger" style="display:none;">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <span id="errorMessage"></span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('mlPredictionForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = {
        crop: document.getElementById('crop').value,
        region: document.getElementById('region').value,
        month: document.getElementById('month').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        N: parseFloat(document.getElementById('N').value),
        P: parseFloat(document.getElementById('P').value),
        K: parseFloat(document.getElementById('K').value),
        humidity: parseFloat(document.getElementById('humidity').value),
        ph: parseFloat(document.getElementById('ph').value),
        moisture: parseFloat(document.getElementById('moisture').value)
    };

    document.getElementById('predictionResult').style.display = 'none';
    document.getElementById('predictionError').style.display = 'none';

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('fertilizerName').textContent = data.fertilizer;
            document.getElementById('fertilizerType').textContent = data.fertilizer_type;
            document.getElementById('predictionResult').style.display = 'block';
        } else {
            document.getElementById('errorMessage').textContent = data.error || 'Prediction failed';
            document.getElementById('predictionError').style.display = 'block';
        }
    } catch (error) {
        document.getElementById('errorMessage').textContent = 'Network error: ' + error.message;
        document.getElementById('predictionError').style.display = 'block';
    }
});
</script>
"""

CROP_MANAGEMENT_CONTENT = """
<div class="row mb-4">
    <div class="col-12">
        <h2 class="mb-4">
            <i class="fas fa-seedling me-2"></i>
            Crop Management
        </h2>
    </div>
</div>

<div class="row mb-4">
    <div class="col-md-4">
        <div class="stat-card card bg-success text-white">
            <div class="card-body text-center">
                <i class="fas fa-leaf fa-3x mb-2"></i>
                <h3>{{ crops|length }}</h3>
                <p class="mb-0">Total Crops</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="stat-card card bg-primary text-white">
            <div class="card-body text-center">
                <i class="fas fa-map fa-3x mb-2"></i>
                <h3>{{ "%.1f"|format(total_acreage) }}</h3>
                <p class="mb-0">Acres in Use</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="stat-card card bg-info text-white">
            <div class="card-body text-center">
                <i class="fas fa-chart-pie fa-3x mb-2"></i>
                <h3>{{ "%.1f"|format(user.total_land - total_acreage) }}</h3>
                <p class="mb-0">Acres Available</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-8 mb-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-list me-2"></i>Your Crops</h5>
            </div>
            <div class="card-body">
                {% if crops %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Crop Type</th>
                                <th>Acres</th>
                                <th>Stage</th>
                                <th>Planting Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for crop in crops %}
                            <tr>
                                <td><strong>{{ crop.crop_type }}</strong></td>
                                <td>{{ crop.acre }}</td>
                                <td>
                                    <span class="badge bg-{% if crop.stage == 'Harvesting' %}success{% elif crop.stage == 'Growing' %}info{% else %}warning{% endif %}">
                                        {{ crop.stage }}
                                    </span>
                                </td>
                                <td>{{ crop.planting_date }}</td>
                                <td>
                                    <form method="POST" style="display:inline;">
                                        <input type="hidden" name="delete_crop_id" value="{{ crop.id }}">
                                        <button type="submit" class="btn btn-sm btn-danger" 
                                                onclick="return confirm('Are you sure you want to delete this crop?')">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </form>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted text-center py-4">No crops added yet. Add your first crop using the form.</p>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="col-lg-4 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-plus-circle me-2"></i>Add New Crop</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="crop_type" class="form-label">Crop Type</label>
                        <input type="text" class="form-control" id="crop_type" name="crop_type" 
                               placeholder="e.g., Wheat, Rice" required>
                    </div>
                    <div class="mb-3">
                        <label for="acre" class="form-label">Acreage</label>
                        <input type="number" step="0.01" class="form-control" id="acre" name="acre" 
                               placeholder="Enter acres" required>
                    </div>
                    <div class="mb-3">
                        <label for="stage" class="form-label">Growth Stage</label>
                        <select class="form-select" id="stage" name="stage" required>
                            <option value="Planting">Planting</option>
                            <option value="Growing" selected>Growing</option>
                            <option value="Flowering">Flowering</option>
                            <option value="Harvesting">Harvesting</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="planting_date" class="form-label">Planting Date</label>
                        <input type="date" class="form-control" id="planting_date" name="planting_date" required>
                    </div>
                    <button type="submit" name="add_crop" class="btn btn-primary w-100">
                        <i class="fas fa-plus me-2"></i>Add Crop
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
"""

PROFILE_CONTENT = """
<div class="row mb-4">
    <div class="col-12">
        <h2 class="mb-4">
            <i class="fas fa-user me-2"></i>
            User Profile
        </h2>
    </div>
</div>

<div class="row">
    <div class="col-lg-4 mb-4">
        <div class="card">
            <div class="card-body text-center">
                <div class="mb-3">
                    <i class="fas fa-user-circle fa-5x text-success"></i>
                </div>
                <h4>{{ user.full_name }}</h4>
                <p class="text-muted">@{{ user.username }}</p>
                <hr>
                <div class="text-start">
                    <p><i class="fas fa-envelope me-2 text-primary"></i>{{ user.email }}</p>
                    <p><i class="fas fa-phone me-2 text-success"></i>{{ user.phone }}</p>
                    <p><i class="fas fa-map-marker-alt me-2 text-danger"></i>{{ user.location }}</p>
                    <p><i class="fas fa-calendar me-2 text-info"></i>Member since {{ user.member_since }}</p>
                </div>
            </div>
        </div>
    </div>

    <div class="col-lg-8 mb-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-edit me-2"></i>Edit Profile</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="full_name" class="form-label">Full Name</label>
                            <input type="text" class="form-control" id="full_name" name="full_name" 
                                   value="{{ user.full_name }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" 
                                   value="{{ user.email }}" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="phone" class="form-label">Phone</label>
                            <input type="tel" class="form-control" id="phone" name="phone" 
                                   value="{{ user.phone }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="farm_name" class="form-label">Farm Name</label>
                            <input type="text" class="form-control" id="farm_name" name="farm_name" 
                                   value="{{ user.farm_name }}" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="location" class="form-label">Location</label>
                            <input type="text" class="form-control" id="location" name="location" 
                                   value="{{ user.location }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="total_land" class="form-label">Total Land (acres)</label>
                            <input type="number" step="0.01" class="form-control" id="total_land" name="total_land" 
                                   value="{{ user.total_land }}" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-success">
                        <i class="fas fa-save me-2"></i>Update Profile
                    </button>
                </form>
            </div>
        </div>

        <div class="card mt-4">
            <div class="card-header bg-warning text-dark">
                <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>Account Information</h5>
            </div>
            <div class="card-body">
                <p><strong>Username:</strong> {{ user.username }} <span class="badge bg-secondary">Cannot be changed</span></p>
                <p><strong>Account Created:</strong> {{ user.member_since }}</p>
                <p class="text-muted mb-0"><i class="fas fa-shield-alt me-2"></i>Your password is securely encrypted</p>
            </div>
        </div>
    </div>
</div>
"""

CONTACT_CONTENT = """
<div class="row mb-4">
    <div class="col-12">
        <h2 class="mb-4">
            <i class="fas fa-envelope me-2"></i>
            Contact & Support
        </h2>
    </div>
</div>

<div class="row">
    <div class="col-lg-8 mb-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0"><i class="fas fa-comment-dots me-2"></i>Send Us Feedback</h5>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="subject" class="form-label">Subject</label>
                        <input type="text" class="form-control" id="subject" name="subject" 
                               placeholder="What's this about?" required>
                    </div>
                    <div class="mb-3">
                        <label for="message" class="form-label">Message</label>
                        <textarea class="form-control" id="message" name="message" rows="6" 
                                  placeholder="Tell us your thoughts, suggestions, or issues..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-success">
                        <i class="fas fa-paper-plane me-2"></i>Send Message
                    </button>
                </form>
            </div>
        </div>
    </div>

    <div class="col-lg-4 mb-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>Get in Touch</h5>
            </div>
            <div class="card-body">
                <div class="contact-info mb-3">
                    <h6><i class="fas fa-phone text-success me-2"></i>Phone Support</h6>
                    <p>+91 1800-AGRIHELP<br>Mon-Sat: 9 AM - 6 PM</p>
                </div>
                <div class="contact-info mb-3">
                    <h6><i class="fas fa-envelope text-primary me-2"></i>Email</h6>
                    <p>support@agridash.com<br>We respond within 24 hours</p>
                </div>
                <div class="contact-info mb-3">
                    <h6><i class="fas fa-map-marker-alt text-danger me-2"></i>Address</h6>
                    <p>AgriDash Pro HQ<br>New Delhi, India</p>
                </div>
                <hr>
                <h6>Follow Us</h6>
                <div>
                    <a href="#" class="btn btn-sm btn-outline-primary me-2"><i class="fab fa-facebook"></i></a>
                    <a href="#" class="btn btn-sm btn-outline-info me-2"><i class="fab fa-twitter"></i></a>
                    <a href="#" class="btn btn-sm btn-outline-success"><i class="fab fa-whatsapp"></i></a>
                </div>
            </div>
        </div>
    </div>
</div>
"""

# --- Main Application Execution ---
if __name__ == '__main__':
    init_db()
    print("\n" + "=" * 60)
    print("🚜 AgriDash Pro - Integrated Farm Management System")
    print("=" * 60)
    print("\n📊 System Status:")
    print(f"   ✓ Database initialized")
    print(f"   {'✓' if ml_model_available else '✗'} ML Model loaded: {ml_model_available}")
    print("\n🌐 Server starting at: http://127.0.0.1:5000/")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)