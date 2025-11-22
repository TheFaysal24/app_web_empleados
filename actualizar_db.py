from app import init_db, get_db_connection
import logging

# Configurar logger básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    print("Iniciando actualización de base de datos...")
    
    # 1. Ejecutar init_db estándar
    init_db()
    print("init_db() ejecutado.")

    # 2. Verificar/Crear tablas manualmente por seguridad
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla Bitácora
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitacora_auditoria (
            id SERIAL PRIMARY KEY,
            fecha_hora TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            usuario_responsable VARCHAR(100),
            accion VARCHAR(100),
            detalle TEXT,
            ip_origen VARCHAR(50)
        )
    """)
    
    conn.commit()
    print("Tablas verificadas/creadas exitosamente.")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error durante la migración: {e}")
