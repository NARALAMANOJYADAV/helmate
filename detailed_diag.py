import os
import sys
from flask import Flask, render_template

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Recreate the app initialization logic from app.py
BASE_DIR = os.path.join(os.getcwd(), 'backend')
TEMPLATE_DIR = os.path.normpath(os.path.join(BASE_DIR, '../frontend'))
STATIC_DIR = os.path.normpath(os.path.join(BASE_DIR, '../frontend'))

app = Flask(__name__, 
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR,
            static_url_path='')

print(f"TEMPLATE_DIR: {TEMPLATE_DIR}")
print(f"Exists: {os.path.exists(TEMPLATE_DIR)}")

templates = ['index.html', 'login.html', 'dash-home.html', 'dashboard.html']
for t in templates:
    t_path = os.path.join(TEMPLATE_DIR, t)
    print(f"Checking {t}: {t_path} (Exists: {os.path.exists(t_path)})")

with app.test_request_context():
    for t in templates:
        try:
            render_template(t)
            print(f"SUCCESS: {t} rendered.")
        except Exception as e:
            print(f"FAILURE: {t} error: {e}")
