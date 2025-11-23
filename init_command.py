from app import init_db, app

def initialize_database():
    """
    Función para ser llamada desde la línea de comandos de Heroku
    para inicializar la base de datos.
    """
    with app.app_context():
        init_db()
        print("✅ Base de datos inicializada correctamente.")

initialize_database()