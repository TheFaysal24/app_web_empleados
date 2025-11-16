# TODO List for App Updates

## 1. Update Flash Message Timeout ✅
- Changed timeout in Templates/base.html from 1000ms to 500ms.

## 2. Ensure Menu Functionality ✅
- Verified in Templates/dashboard.html that "Gestión de Usuarios" and "Backups" are in the dropdown menu for admins.

## 3. Reset Admin Password ✅
- Confirmed admin password in empleados_data.json is set to "1234".

## 4. Update Password Recovery ✅
- Modified app.py recuperar_contrasena function to generate a new random password, update user data, and send notification via mailto (email) or whatsapp link.

## 5. Test Changes ✅
- Ran the app successfully, running on http://127.0.0.1:5000
