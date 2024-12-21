from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import time
import sqlite3

import os
os.environ["TF_XNNPACK_USE"] = "0"

"""
El programa consta de 6 funciones
- main: es la que controla el flujo de programa
- solve_captcha: es donde iría el mecanismo encargado de resolver el captcha, el cual usualmente es
una consulta a una api de pago que resuelve el captcha. La solución que en este programa se toma es
simplemente pausar el curso del programa para darle tiempo al usuario de completar el captcha manualmente. 
Luego de hacerlo se debe ir a la terminal o consola donde está corriendo el programa, hacer click para que
el foto esté en ese lugar y presionar una tecla para continuar con el programa. Se dispondrá de 3 segundos para
retomar la ventana del navegador (chrome)  que se encuentra automatizada.
- obtener_información_expedientes: esta función se encarga de obtener la información que aparece en la primer
pantalla.
- obtener_mas_info_expediente: esta función es la que lee datos sobre las tablas y busca información de los
intervinientes.
- lista_a_cadena: es una función simple que formatea una lista de elementes en un string apropiado para su
posterior almacenamiento.
- insertar_en_base_de_datos: es la función que garantiza la preservación de la información en una base de datos
llamada expedientes.db


Base de datos:
Agregué un archivo llamado "create_db.py" que tiene por propósito crear la base de datos con la tabla que 
posteriormente será utilizada con la ejecución del programa principal. Al momento de testear el programa 
recomiendo borrar el archivo expedientes.db y crear uno nuevo usando create_db.py, así se puede 
testear el funcionamiento del scraper desde cero.

"""


def insertar_en_base_de_datos(datos_fila):
    conn = sqlite3.connect('expedientes.db')
    cursor = conn.cursor()

    # Insertar el registro en la tabla
    cursor.execute('''
    INSERT INTO expedientes (
        expediente, dependencia, caratula, situacion, ultima_act, juzgado, 
        demandados, actores, letrados_patrocinantes, letrados_apoderados, 
        incidentistas, otros
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datos_fila['Expediente'], datos_fila['Dependencia'], datos_fila['Caratula'],
        datos_fila['Situacion'], datos_fila['Ultima_act'], datos_fila['Juzgado'],
        datos_fila.get('Demandados', None), datos_fila.get('Actores', None), 
        datos_fila.get('Letrados Patrocinantes', None), datos_fila.get('Letrados Apoderados', None),
        datos_fila.get('Incidentistas', None), datos_fila.get('Otros', None)
    ))

    conn.commit()
    conn.close()
    print(f"Registro insertado en la base de datos: {datos_fila['Expediente']}")


def lista_a_cadena(lista):
    # Función básica para formatear las listas de intervinientes como cadena de texto.
    # De esa forma se puede guardar en la base de datos sin problemas.

    if len(lista) == 0:
        return ""
    elif len(lista) == 1:
        return lista[0]
    else:
        # Todos los elementos excepto el último
        todos_excepto_ultimo = ", ".join(lista[:-1])
        # El último elemento con "y" antes
        return f"{todos_excepto_ultimo} y {lista[-1]}"


def obtener_mas_info_expediente(driver):

    actuaciones = []
    juzgado = driver.find_elements(By.CSS_SELECTOR, '.ui-fieldset-content div:nth-child(3)')[0].text
    menu = driver.find_elements(By.CSS_SELECTOR, 'table tbody')[1]
    
    intervinientes_td = menu.find_elements(By.CSS_SELECTOR, 'td')[5]
    intervinientes_span = intervinientes_td.find_element(By.CSS_SELECTOR, 'span')

    # Buscando tabla y filas
    try:
        tabla = driver.find_elements(By.CSS_SELECTOR, 'table tbody')[5]
        filas = tabla.find_elements(By.CSS_SELECTOR, 'tr')

        # Buscando fechas, tipos y detalles
        for fila in filas:
            fecha       = fila.find_elements(By.CSS_SELECTOR, 'td')[1].text
            tipo        = fila.find_elements(By.CSS_SELECTOR, 'td')[2].text
            detalle     = fila.find_elements(By.CSS_SELECTOR, 'td')[3].text

            actuaciones.append([fecha,tipo,detalle])
    except :
        print('Nada que ver')
    
    # Viendo intervinientes'
    intervinientes_span.click()
    time.sleep(1.5)

    tablas = driver.find_elements(By.CSS_SELECTOR, 'table.rf-dt')
    tabla_intervinientes = tablas[0]

    # Obtengo la cantidad de intervinientes (algunos valores pueden estar vacíos debido al HTML defectuoso)
    intervinientes = tabla_intervinientes.find_elements(By.CSS_SELECTOR,'tbody')

    # Limpio los valores vacíos de intervinientes
    intervinientes_limpios = [elem.text.strip() for elem in intervinientes if elem.text.strip() != '']

    # Formateo los textos
    intervinientes_textos_limpios = [
        item.replace('\n', ' ')   
        .replace('TIPO : ', '')   
        .replace('NOMBRE : ', '') 
        .replace('DEMANDADO','DEMANDADO:')
        .replace('ACTOR','ACTOR:')
        .replace('LETRADO PATROCINANTE','LETRADO PATROCINANTE:')
        .replace('LETRADO APODERADO','LETRADO APODERADO:')
        .replace('INCIDENTISTA','INCIDENTISTA:')
        .strip()    
        for item in intervinientes_limpios
    ]

    ################### Para propósitos de testeo ###################
    # print(f'\n\nLos intervinientes son:\n{len(intervinientes_textos_limpios)}')
    # for inter in intervinientes_textos_limpios:
    #     print(inter)
    # print('---------\n\n')


    # Organizando los intervinientes
    demandados = []
    actores = []
    letrados_patrocinantes = []
    letrados_apoderados = []
    incidentistas = []
    otros_tipos = []

    
    for inter in intervinientes_textos_limpios:
        if inter.startswith("DEMANDADO:"):
            demandados.append(inter.replace('DEMANDADO:',''))
        elif inter.startswith("ACTOR:"):
            actores.append(inter.replace('ACTOR:',''))
        elif inter.startswith("LETRADO PATROCINANTE:"):
            letrados_patrocinantes.append(inter.replace('LETRADO PATROCINANTE:',''))
        elif inter.startswith("LETRADO APODERADO:"):
            letrados_apoderados.append(inter.replace('LETRADO APODERADO:',''))
        elif inter.startswith("INCIDENTISTA:"):
            incidentistas.append(inter.replace('INCIDENTISTA:',''))
        else:
            otros_tipos.append(inter)
    
    lista_de_intervinientes = [demandados, actores, letrados_patrocinantes, letrados_apoderados, incidentistas, otros_tipos]

    ################### Para propósitos de testeo ###################
    # print(f'demandados: {demandados}')
    # print(f'actores: {actores}')
    # print(f'letrados_patrocinantes: {letrados_patrocinantes}')
    # print(f'letrados_apoderados: {letrados_apoderados}')
    # print(f'incidentistas: {incidentistas}')
    # print(f'otros_tipos: {otros_tipos}')

    return [juzgado.replace('Dependencia:',''), actuaciones, lista_de_intervinientes] 
    

def obtener_información_expedientes(driver):
    # Lista que almacenará todos los expedientes
    expedientes = []

    # Recorrer las filas de la tabla
    rows = driver.find_elements(By.CSS_SELECTOR, '#tablaConsulta table tbody tr')

    for i in range(len(rows)):
        row = driver.find_elements(By.CSS_SELECTOR, f'#tablaConsulta table tbody tr:nth-child({i+1})')[0]

        columnas = row.find_elements(By.TAG_NAME, 'td')
        datos_fila = {
            'Expediente': columnas[0].text,
            'Dependencia': columnas[1].text,
            'Caratula': columnas[2].text,
            'Situacion': columnas[3].text,
            'Ultima_act': columnas[4].text,
        }
        
        time.sleep(1)

        # Hacer click en el 6to td (el que contiene el enlace <a>) para buscar más información del expediente.
        link = columnas[5].find_element(By.TAG_NAME, 'a')
        link.click()

        time.sleep(2) # A veces se traba un poco la búsqueda

        info_expediente = obtener_mas_info_expediente(driver) 
        lista_de_intervinientes = info_expediente[2]

        # Actualizando registro con los datos del expediente
        datos_fila['Juzgado']                 = info_expediente[0]
        datos_fila['Demandados']              = lista_a_cadena(lista_de_intervinientes[0])
        datos_fila['Actores']                 = lista_a_cadena(lista_de_intervinientes[1])
        datos_fila['Letrados Patrocinantes']  = lista_a_cadena(lista_de_intervinientes[2])
        datos_fila['Letrados Apoderados']     = lista_a_cadena(lista_de_intervinientes[3])
        datos_fila['Incidentistas']           = lista_a_cadena(lista_de_intervinientes[4])
        datos_fila['Otros']                   = lista_a_cadena(lista_de_intervinientes[5])


        time.sleep(1)

        # Guardando en la lista e insertando el registro en la base de datos
        expedientes.append(datos_fila)
        insertar_en_base_de_datos(datos_fila)

        # Volver a la página anterior
        driver.back()

   # print(expedientes)


def solve_captcha(driver):

    time.sleep(1.5)

    # ENCUENTRA el checkbox del captcha y le hace click
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()

    # Espera para ver si aparece la ventana del captcha
    print(f'Resuelve el captcha manualmente')
    input(f'Presione una tecla para continuar...') # se debe hacer foco en la terminal
    time.sleep(3) # tiempo para volver al navegador
 

def main():
    # Configurar opciones de Chrome para iniciar maximizado
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # Configurar el navegador con las opciones
    driver = webdriver.Chrome( options=options)

    try:
        # 1. Abre la página
        url = 'http://scw.pjn.gov.ar/scw/home.seam'
        driver.get(url)
        
        time.sleep(3)

        # 2. Buscar pestaña correcta y cliquearla
        boton = driver.find_elements(By.CSS_SELECTOR, "span.rf-tab-lbl")[3]
        boton.click()
        
        # 3. Seleccionar una opción del select
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "formPublica:camaraPartes"))
        )
    
        select_element.send_keys("com")  

        # 4. Completar el input
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "formPublica:nomIntervParte"))
        )
        input_element.send_keys("RESIDUOS")
        
        # 5. Resolver el captcha (o darle tiempo para completar manualmente)
        solve_captcha(driver)

        # 6. Presionar el botón para iniciar la consulta
        boton_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "formPublica:buscarPorParteButton"))
        )
        boton_element.click()

        time.sleep(3)

        # 7. Buscar información de los expedientes
        obtener_información_expedientes(driver)

    finally:
        driver.quit()


if __name__ == '__main__':
    main()