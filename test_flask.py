from flask import Flask, render_template
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Recreate the app initialization logic from app.py
app = Flask(__name__, 
            template_folder='../frontend',
            static_folder='../frontend',
            static_url_path='')

print(f"Current Working Directory: {os.getcwd()}")
print(f"App Root Path: {app.root_path}")
print(f"Template Folder: {app.template_folder}")
print(f"Absolute Template Folder: {os.path.abspath(os.path.join(app.root_path, app.template_folder))}")

# Try to find login.html
target = os.path.abspath(os.path.join(app.root_path, app.template_folder, 'login.html'))
print(f"Searching for login.html at: {target}")
if os.path.exists(target):
    print("SUCCESS: login.html found!")
else:
    print("FAILURE: login.html NOT found!")

# Try to render it in a test context
with app.test_request_context():
    try:
        rendered = render_template('login.html', error=None)
        print("SUCCESS: Rendered login.html successfully!")
    except Exception as e:
        print(f"FAILURE: Could not render login.html: {e}")
