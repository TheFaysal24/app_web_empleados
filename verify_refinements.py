from app import app

def verify_refinements():
    print("Verifying refinements...")
    with app.test_client() as client:
        try:
            # 1. Verify Button Styles
            with open('static/modern-design.css', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'padding: 10px 24px !important' in content:
                    print("OK: Buttons resized to be smaller and elegant.")
                else:
                    print("FAILED: Button styles not updated correctly.")
                    return False

            # 2. Verify User Dashboard History
            with open('Templates/dashboard.html', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'accordionUserHistory' in content:
                    print("OK: User dashboard contains history accordion.")
                else:
                    print("FAILED: User dashboard missing history accordion.")
                    return False

            # 3. Verify User Management UI
            with open('Templates/admin_usuarios.html', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'accordionUsers' in content:
                    print("OK: User management UI uses accordion.")
                else:
                    print("FAILED: User management UI missing accordion.")
                    return False
            
            # 4. Verify Audit Logging (Static Check)
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if "registrar_auditoria('Edición Horas'" in content:
                    print("OK: Audit logging call found in admin_editar_registro.")
                else:
                    print("FAILED: Audit logging missing in admin_editar_registro.")
                    return False

            print("Refinements verification successful.")
            return True
        except Exception as e:
            print(f"FAILED: Verification raised exception: {e}")
            return False

if __name__ == "__main__":
    if verify_refinements():
        print("VERIFICATION SUCCESSFUL")
    else:
        print("VERIFICATION FAILED")
