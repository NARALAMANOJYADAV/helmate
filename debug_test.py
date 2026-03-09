
import sys
import os

# Add the current directory to path so we can import backend properly
sys.path.append(os.getcwd())

try:
    from backend.app import app
    print("App imported successfully.")
except Exception as e:
    print(f"Failed to import app: {e}")
    sys.exit(1)

def test_violations():
    print("Starting Test...")
    with app.test_client() as client:
        # 1. Login
        print("Attempting Login...")
        login_resp = client.post('/login', data={'username': 'MANOJ', 'password': 'manoj@64'}, follow_redirects=True)
        print(f"Login Response Code: {login_resp.status_code}")
        
        if b"Dashboard" not in login_resp.data and b"System Overview" not in login_resp.data:
            print("Login failed or Dashboard not loaded in login response.")
            # print(login_resp.data[:500]) # First 500 chars

        # 2. Access Violations Page
        print("\nAttempting to fetch /violations...")
        vio_resp = client.get('/violations', follow_redirects=True)
        print(f"Violations Response Code: {vio_resp.status_code}")
        
        if vio_resp.status_code != 200:
            print("Violations page failed to load.")
            print(vio_resp.data.decode('utf-8'))
        else:
            print("Violations page loaded successfully (HTTP 200).")
            # Check if it rendered the template or my error message
            content = vio_resp.data.decode('utf-8')
            if "Error loading violations page" in content:
                 print("\nCRITICAL: Render Template Failed!")
                 print(content)
            elif "Violations Archive" in content:
                 print("Content verified: 'Violations Archive' found.")
            else:
                 print("Warning: Expected content 'Violations Archive' not found.")
                 print(content[:500])

        # 3. Access API
        print("\nAttempting to fetch /api/challans...")
        api_resp = client.get('/api/challans')
        print(f"API Response Code: {api_resp.status_code}")
        print(f"API Response Data: {api_resp.data.decode('utf-8')}")

if __name__ == "__main__":
    test_violations()
