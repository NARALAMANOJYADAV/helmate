import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.app import app
except ImportError as e:
    print(f"Error importing app from backend.app: {e}")
    # Fallback to direct import if pathing is weird on Render
    try:
        sys.path.append(os.path.join(os.getcwd(), 'backend'))
        from app import app
    except ImportError as e2:
        print(f"Critical Error: Could not find app module. {e2}")
        raise

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
