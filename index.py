import sys
import socket
import json
import inquirer
from helpers.inquirer_questions import *
from helpers.manejo_mensajes import *

# Variables globales
NoneType = type(None)

def registrarUsuario( cliente ):
    res = inquirer.prompt( question_registro_usuario )
    if type( res ) == NoneType:
        return
    res = json.dumps( res )
    msj = '2.'
    msj += res
    # Si los datos se envian de manera correcta, enviamos la data al socket
    mandar_mensaje( cliente, bytes( msj, encoding="raw_unicode_escape" ) )
    print( leer_mensaje( cliente ).decode( 'utf-8' ) )
    print( '\n' )

def registrarNuevoServicio( cliente, sesion_activa ):
    res = inquirer.prompt( question_agregar_servicio )
    if type( res ) == NoneType:
        return
    res = json.dumps( res )
    msj = '4.'
    msj += res
    msj += '-'
    msj += sesion_activa
    # SI los datos se procesan de manera correcta, enviamos la data al Socket
    # Enviamos el mensaje
    mandar_mensaje( cliente, bytes( msj, encoding='raw_unicode_escape' ) )    
    print( leer_mensaje( cliente ).decode( 'utf-8' ) )
    print( '\n' )

def traer_mis_llaves( cliente, sesion_activa ):
    msj = '5.'
    msj += sesion_activa
    mandar_mensaje( cliente, bytes( msj, encoding='raw_unicode_escape' ) )    
    print( leer_mensaje( cliente ).decode( 'utf-8' ) )
    print( '\n' )

def work_logueado( cliente, sesion_activa ):
    while True:
        res = inquirer.prompt( question_sesion_activa )
        if res[ 'opcion_activa' ] == '1':
            print( 'LISTAMOS SERVICIOS' )
            traer_mis_llaves( cliente, sesion_activa )
        if res[ 'opcion_activa' ] == '2':
            print( '\nAgregar Nuevo Servicio' )
            registrarNuevoServicio( cliente, sesion_activa )
        if res[ 'opcion_activa' ] == '3':
            print( 'Cerrando Sesión\n' )
            sesion_activa = ''
            break    
        
def login( cliente ):
    # Limpiamos las credenciales de sesión
    # Función que lee los datos desde consola los manda al socket para verificar credenciales
    res = inquirer.prompt( question_login )
    if type( res ) == NoneType:
        return
    res = json.dumps( res )
    sesion_activa = res
    # Agregamos la info de las credenciales de sesión
    msj = '1.'
    msj += res
    mandar_mensaje( cliente, bytes( msj, encoding='raw_unicode_escape' ) )    
    response = leer_mensaje( cliente ).decode( 'utf-8' )
    print( response )
    if response == 'OK':
        print( 'Inicio de sesión exitoso' )
        # Armar el nuevo menu
        print( '\n' )
        work_logueado( cliente, sesion_activa )

def conectar_servidor( host, puerto ):
    # Socket para IP v4
    cliente = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    try:
        cliente.connect( ( host, int( puerto ) ) )
        return cliente
    except:
        print( 'Servidor no alcanzable' )
        exit()

def work_loop( cliente ):
    while True:
        res = inquirer.prompt( question_menu )
        
        if res[ 'accion' ] == '1':
            print( 'LOGIN' )
            login( cliente )
        
        if res[ 'accion' ] == '2':
            print( 'REGISTRAR' )
            registrarUsuario( cliente )
        if res[ 'accion' ] == '3':
            cliente.close()
            return

if __name__ == '__main__':
    # Ejecutar código
    try:
        host = sys.argv[ 1 ]
        puerto = sys.argv[ 2 ]
        cliente = conectar_servidor( host, puerto )
        work_loop( cliente )
        pass
    
    except IndexError:
        print( 'Error al ingresar datos - Estructura: python index.py host puerto ' )