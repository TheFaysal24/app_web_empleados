"""
Script para ejecutar backup automático usando APScheduler
Se ejecuta cada 10 días automáticamente
"""

from apscheduler.schedulers.background import BackgroundScheduler
from backup_automatico import backup_automatico
import time

def iniciar_backup_programado():
    """Inicia el scheduler de backups automáticos cada 10 días"""
    
    scheduler = BackgroundScheduler()
    
    # Programar backup cada 10 días a las 2:00 AM
    scheduler.add_job(
        backup_automatico,
        'interval',
        days=10,
        start_date='2025-01-01 02:00:00',
        id='backup_empleados'
    )
    
    # También hacer un backup inmediato al iniciar
    scheduler.add_job(
        backup_automatico,
        'date',
        run_date=None,  # Ejecutar inmediatamente
        id='backup_inicial'
    )
    
    scheduler.start()
    print("✅ Scheduler de backups iniciado - Backup cada 10 días")
    
    return scheduler

if __name__ == '__main__':
    scheduler = iniciar_backup_programado()
    
    try:
        # Mantener el script corriendo
        while True:
            time.sleep(3600)  # Dormir 1 hora
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler detenido")
