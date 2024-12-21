import sqlite3

def create_database():
    # Conectar o crear la base de datos
    conn = sqlite3.connect('expedientes.db')
    cursor = conn.cursor()

    # Crear la tabla expedientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expedientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expediente TEXT NOT NULL,
        dependencia TEXT NOT NULL,
        caratula TEXT NOT NULL,
        situacion TEXT NOT NULL,
        ultima_act TEXT NOT NULL,
        juzgado TEXT NOT NULL,
        demandados TEXT,
        actores TEXT,
        letrados_patrocinantes TEXT,
        letrados_apoderados TEXT,
        incidentistas TEXT,
        otros TEXT
    )
    ''')
    print("Tabla 'expedientes' creada correctamente.")

    # Cerrar conexión
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
