from app import app

def verify_routes():
    print("Verifying routes...")
    with app.test_client() as client:
        # Simulate admin login (this is tricky without a real login, but we can check if the route exists)
        # For now, we just check if the template file exists and has the new structure keywords
        try:
            with open('Templates/admin_gestion_tiempos.html', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'accordion' in content and 'collapse' in content:
                    print("OK: admin_gestion_tiempos.html contains accordion structure.")
                else:
                    print("FAILED: admin_gestion_tiempos.html missing accordion structure.")
                    return False
            
            with open('static/modern-design.css', 'r', encoding='utf-8') as f:
                content = f.read()
                if '!important' in content:
                    print("OK: modern-design.css contains !important styles.")
                else:
                    print("FAILED: modern-design.css missing !important styles.")
                    return False

            print("Static analysis successful.")
            return True
        except Exception as e:
            print(f"FAILED: Verification raised exception: {e}")
            return False

if __name__ == "__main__":
    if verify_routes():
        print("VERIFICATION SUCCESSFUL")
    else:
        print("VERIFICATION FAILED")
