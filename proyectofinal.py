import os
import sqlite3


def alta_registro(bd_nombre_archivo, nombre_tabla, campos_def, campo_pk):
    campos_string = '('
    for campo in campos_def:
        if campo != campo_pk:
            campos_string += f'{campo}, '
    campos_string = campos_string.rstrip(', ') + ')'
    values_string = '('
    for _ in range(len(campos_def) -1):
        values_string += '?, '
    values_string = values_string.rstrip(', ') + ')'
    conexion = sqlite3.connect(bd_nombre_archivo)
    cursor = conexion.cursor()
    nombre = input('Ingrese nombre: ')
    descripcion = input('Ingrese descripción: ')
    cantidad = input_valida_entero_positivo('Ingrese cantidad: ')
    precio = input_valida_flotante_positivo('Ingrese precio: ')
    categoria = input('Ingrese categoría: ')
    cursor.execute(f"INSERT INTO {nombre_tabla} {campos_string}\
       VALUES {values_string}", (nombre, descripcion, cantidad, precio, categoria))
    conexion.commit()
    conexion.close()

def mostrar_registros(bd_nombre_archivo, tabla_nombre, campos_def):
    conexion = sqlite3.connect(bd_nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute(f"SELECT * FROM {tabla_nombre}")
    resultados = cursor.fetchall()
    imprime_cabecera(campos_def)
    for registro in resultados:
        imprime_registro(registro)
    conexion.close()

def mostrar_menu():
    print('''
Menú principal

    1) Registrar producto
    2) Mostrar el inventario
    3) Actualizar producto
    4) Eliminar producto
    5) Buscar producto
    6) Generar reporte de bajo stock

    0) Salir
''')
    
def crear_tabla(bd_nombre_archivo, nombre_tabla, tabla_def, campos_def):
    campos_string = ''
    for campo, const in campos_def.items():
        campos_string += f'"{campo}" {const},\n'
    query = 'CREATE TABLE IF NOT EXISTS ' + nombre_tabla + '(' + campos_string + tabla_def + ')'
    conexion = sqlite3.connect(bd_nombre_archivo)
    cursor = conexion.cursor()
    cursor.execute(query)
    conexion.commit()
    conexion.close()

def imprime_cabecera(campos_def):
    campos = list(campos_def.keys())
    for campo in campos: # Imprime cabecera (header) de la tabla
        print(f'{campo:<15}', end='|')
    print()
    
def imprime_registro(registro): # pide una tupla de las que devuelve el fetchall.
    if registro:
        for _ in range(len(registro)):
            print(f'{registro[_]:<15}', end='|')
        print()

def input_valida_entero_positivo(prompt):
    while True:
        dato = input(prompt)
        if dato.isdigit() or dato[0] == '-' and dato[1::].isdigit():
            dato = int(dato)
            if dato > 0:
                return dato
            else:
                print('El número debe ser entero positivo, inténtelo nuevamente...')
        else:
            print('El dato debe ser un número, inténtelo nuevamente')

def input_valida_flotante_positivo(prompt):
    while True:
        dato = input(prompt)
        if is_float(dato):
            dato = float(dato)
            if dato > 0:
                return dato
            else:
                print('El número debe ser un entero o decimal (.) positivo, inténtelo nuevamente...')
        else:
            print('El dato debe ser un número, inténtelo nuevamente')

def is_float(string):
    partes = string.split('.')
    if len(partes) <= 2:
        for parte in partes:
            if not parte.isdigit():
                return False
        return True
    return False

def reporte_bajo_stock(bd_nombre_archivo):
    conexion = sqlite3.connect(bd_nombre_archivo)
    cursor = conexion.cursor()
    limite = input_valida_entero_positivo("Ingrese el límite de stock:")
    cursor.execute("SELECT * FROM productos WHERE cantidad <= ?",
                   (limite,))
    resultados = cursor.fetchall()
    if resultados == []:
        print("No hay productos por debajo del límite.")
    else:
        for registro in resultados:
            print(f'{registro[0]}\t\t{registro[1]}\t\t{registro[2]}\t\t{registro[3]}\t\t{registro[4]}\t\t{registro[5]}')
    conexion.close()

    
def actualizar_registro(bd_nombre_archivo, tabla_nombre, campo_pk, campos_def):
    conexion = sqlite3.connect(bd_nombre_archivo)
    cursor = conexion.cursor()
    try:
        id_registro = input_valida_entero_positivo(f"Ingrese el {campo_pk} del registro que desea actualizar: ")
        cursor.execute(f"SELECT * FROM {tabla_nombre} WHERE {campo_pk} = ?", (id_registro,))
        registro = cursor.fetchone()
        if not registro:
            print(f"No se encontró un registro con {campo_pk} = {id_registro}.")
            return
        print("\nRegistro encontrado:")
        imprime_cabecera(campos_def)
        imprime_registro(registro)
        campos_actualizables = [campo for campo in campos_def if campo != campo_pk]
        campo_seleccionado = seleccionar_campo(campos_actualizables)
        nuevo_valor = obtener_valor_actualizado(campo_seleccionado, campos_def)
        cursor.execute(f"UPDATE {tabla_nombre} SET {campo_seleccionado} = ? WHERE {campo_pk} = ?",
                       (nuevo_valor, id_registro))
        conexion.commit()
        print(f"El campo '{campo_seleccionado}' ha sido actualizado exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al actualizar el registro: {e}")
    finally:
        conexion.close()

def seleccionar_campo(campos_actualizables):
    """Funcion para seleccionar el campo que quiere actualizar."""
    print("\nCampos disponibles para actualizar:")
    i = 1
    for campo in campos_actualizables:
        print(f"{i}) {campo}")
        i += 1
    while True:
        opcion = input_valida_entero_positivo("Seleccione el número del campo que desea actualizar: ")
        if 1 <= opcion <= len(campos_actualizables):
            return campos_actualizables[opcion - 1]
        print("Opción no válida. Intente nuevamente.")
       
def obtener_valor_actualizado(campo, campos_def):
    """Funcion para solicitar y validar el nuevo valor según el tipo definido en campos_def."""
    tipo_campo = campos_def[campo].upper()
    if "INTEGER" in tipo_campo:
        return input_valida_entero_positivo(f"Ingrese un valor numérico válido para '{campo}': ")
    elif "REAL" in tipo_campo:
        return input_valida_flotante_positivo(f"Ingrese un valor decimal válido para '{campo}': ")
    else:
        return input(f"Ingrese el nuevo valor para '{campo}': ")

def eliminar_producto(bd_nombre_archivo, tabla_nombre):
    conexion = sqlite3.connect(bd_nombre_archivo)
    cursor = conexion.cursor()
    
    id_producto = input_valida_entero_positivo("Ingrese el ID del producto a eliminar: ")
    # while True:
    #     id_producto = input("Ingrese el ID del producto a eliminar: ")
    #     if id_producto.isdigit():
    #         id_producto = int(id_producto)
    #         break
    #     print("El ID debe ser un número entero.")

    if existe_registro(id_producto, bd_nombre_archivo, tabla_nombre):
        cursor.execute(f"DELETE FROM {tabla_nombre} WHERE id = ?", (id_producto,))
        conexion.commit()
    else:
        print("No se encontró un producto con ese ID.")
    # if cursor.rowcount > 0:
    #     print("Producto eliminado correctamente.")
    # else:
    #     print("No se encontró un producto con ese ID.")
    conexion.close()
    
    
def buscar_registro(bd_nombre_archivo, tabla_nombre, campo_pk, campos_def):
    conexion = sqlite3.connect(bd_nombre_archivo)
    cursor = conexion.cursor()
    id_ = input(f"Ingrese el {campo_pk} del registro a buscar: ")
    cursor.execute(f"SELECT * FROM {tabla_nombre} WHERE {campo_pk} = ?", (id_,))
    resultado = cursor.fetchone()
    conexion.close()
    if resultado:
        imprime_cabecera(campos_def)
        imprime_registro(resultado)
    else:
        print(f"No se encontró un producto con ese {campo_pk}.")
    
        
def existe_registro(id_input, bd_nombre_archivo, tabla_nombre):
    conexion = sqlite3.connect(bd_nombre_archivo)
    cursor = conexion.cursor()
    while True:
        cursor.execute(f"SELECT id FROM {tabla_nombre} WHERE id = ?", (id_input,))
        resultado = cursor.fetchone()
        conexion.close()
        if resultado:  # Si se encuentra un registro
            return True
        else:
            return False
        
def main():
    rootdir = os.path.dirname(__file__) # Crea un string con la ruta completa donde está el archivo main.py
    bd_nombre_archivo = 'inventario.db'
    bd_directorio = 'data'
    bd_nombre_archivo_con_ruta = rootdir + '/' + bd_directorio + '/' +bd_nombre_archivo
     
    campos_def = {'id':'INTEGER',
                  'nombre':'TEXT NOT NULL',
                  'descripcion':'TEXT',
                  'cantidad':'INTEGER NOT NULL',
                  'precio':'REAL NOT NULL',
                  'categoria':'TEXT',
                  }
    
    campo_pk = 'id'
    tabla_def = f'PRIMARY KEY("{campo_pk}" AUTOINCREMENT)'
    tabla_nombre = 'productos'
    ##### Son las variables de inicialización básica de nuestro programa.

    crear_tabla(bd_nombre_archivo_con_ruta, tabla_nombre, tabla_def, campos_def)
    while True:
        #crear_tabla(bd_nombre_archivo_con_ruta, tabla_nombre, tabla_def, campos_def)
        mostrar_menu()
        opcion = input('Ingrese una opción y presione Enter: ')
        if opcion == '1': # Registrar
            alta_registro(bd_nombre_archivo_con_ruta, tabla_nombre, campos_def, campo_pk)
        elif opcion == '2': # Mostrar
            mostrar_registros(bd_nombre_archivo_con_ruta, tabla_nombre, campos_def)
        elif opcion == '3': # Actualizar
            actualizar_registro(bd_nombre_archivo_con_ruta, tabla_nombre, campo_pk, campos_def)
        elif opcion == '4': # Eliminar
            eliminar_producto(bd_nombre_archivo_con_ruta, tabla_nombre)
        elif opcion == '5': # Buscar
            buscar_registro(bd_nombre_archivo_con_ruta, tabla_nombre, campo_pk, campos_def)
        elif opcion == '6': # Generar reporte
            reporte_bajo_stock(bd_nombre_archivo_con_ruta, tabla_nombre, campo_pk, campos_def)
        elif opcion == '0': # Salir
            print('Gracias por utilizar el programa, saliendo...')
            break
        else:
            print('La opción ingresada es incorrecta, inténtelo nuevamente')
            
if __name__ == '__main__':
    main()