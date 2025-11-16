# TODO List for Shifts Module Implementation

## 1. Update empleados_data.json Structure ✅ COMPLETED
- Change "turnos" from list to dict with "shifts", "monthly_assignments", "current_month"
- Initialize shifts grid for weekdays and Saturday
- Set current_month to current or specified

## 2. Update Templates/registro.html ✅ COMPLETED
- Add cargo field as select with options: GESTOR OPERATIVO, TECNICO MINTIC, LIDER DE PROCESO, SUPERVISOR DE CAMPO, COORDINADOR
- Ensure cedula field is properly closed

## 3. Implement Automatic Shift Assignment Logic in app.py ✅ COMPLETED
- Add function to assign shifts based on ID
- Shifts per ID:
  - 1070963486: 6:30 am and 8:30 am
  - 1067949514: 8:00 am and 6:30 am
  - 1140870406: 8:30 am and 9:00 am
  - 1068416077: 9:00 am and 8:00 am
- Start with 6:30 am this week
- Avoid repeating grid within same month
- Mark used shifts from last week

## 4. Add Shift Links to Dashboard ✅ COMPLETED
- Update Templates/dashboard.html menu and dropdown to include shifts links
- Add "Seleccionar Turno" and "Ver Turnos Asignados" links

## 5. Add Shift Traceability Section to Dashboard ✅ COMPLETED
- Add interactive section showing shift assignments
- Include tables for current month assignments
- Show traceability since Nov 3, 2025
- Add charts for shift usage

## 6. Update Shift Selection Logic ✅ COMPLETED
- Modify validar_turno_usuario to prevent repeats in month
- Implement ID-based automatic assignment on registration

## 7. Test Registration with Automatic Assignment
- Verify ID identification and automatic shift marking
- Test position selection

## 8. Verify Dashboard Traceability
- Ensure full interactive traceability of shifts
- Confirm visibility of shifts module
