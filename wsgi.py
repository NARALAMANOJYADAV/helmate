import sys
import os

# Add the repository root and its subdirectories to the path
# This helps if the project is being run from a parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to find the backend folder if we are one level up
backend_path = os.path.join(current_dir, 'backend')
if not os.path.exists(backend_path):
    # Try searching for it
    for root, dirs, files in os.walk(current_dir):
        if 'backend' in dirs and 'app.py' in os.listdir(os.path.join(root, 'backend')):
            sys.path.insert(0, root)
            break

try:
    from backend.app import app
except ImportError:
    # Fallback to direct import if backend is already in path
    try:
        from app import app
    except ImportError as e:
        print(f"CRITICAL: Could not find the 'app' variable. Paths: {sys.path}")
        raise e

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
