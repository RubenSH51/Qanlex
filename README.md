# Sistema de Gestión de Expedientes

Un programa desarrollado en Python para gestionar expedientes legales, incluyendo información sobre juzgados, demandados, actores, letrados y más. Utiliza SQLite como base de datos para almacenar los datos.

---

## Tabla de Contenidos
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Base de datos](#bd)
- [Uso](#uso)

---

## Características
- **Gestión de expedientes:** Registra información detallada como:
  - Número de expediente
  - Dependencia
  - Carátula
  - Situación
  - Última actualización
  - Juzgado
  - Intervinientes (demandados, actores, letrados, incidentistas, etc.)
- **Base de datos SQLite:** Guarda y consulta expedientes de manera eficiente.
- **Manejo robusto de datos:** Inserción y validación de datos segura para evitar errores.

---

## Requisitos
- Python 3.8 o superior
- Librerías necesarias (instalables con `pip`):
- sqlite3 y Selenium

---

## Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/RubenSH51/Qanlex.git
2. Instala [Python](https://www.python.org/downloads/) si aún no lo tienes desde la web oficial.
3. Ejecuta el script para crear la base de datos: python create_db.py
4. Corre el programa:  python main.py


## Base de datos

Insertar datos en la base de datos
El programa utiliza la función insertar_en_base_de_datos para añadir registros en la base de datos. Cada registro debe incluir:

Expediente
Dependencia
Carátula
Situación
Última actualización


## Uso

Luego de haber creado la base de datos con la tabla correspondiente a través del script create_db.py solo queda ejecutar el programa.
Aclaración: El programa hará una pausa en el momento de completar el captcha para que el usuario lo haga manuealmente, luego deberá dirigirse
a la terminal/consola desde la cual está corriendo el programa para hacer foco sobre la misma y presionar una tecla cualquiera para continuar.
El programa dará 3 segundos para volver al navegador chrome automatizado para cumplir finalmente su función.


