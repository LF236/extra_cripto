from distutils.command.clean import clean
import os
from pydoc import cli
import sys
import socket
import json
import inquirer
from helpers.inquirer_questions import *
from helpers.manejo_mensajes import *

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

def login( cliente ):
    # Función que lee los datos desde consola los manda al socket para verificar credenciales
    res = inquirer.prompt( question_login )
    if type( res ) == NoneType:
        return
    res = json.dumps( res )
    msj = '1.'
    msj += res
    mandar_mensaje( cliente, bytes( msj, encoding='raw_unicode_escape' ) )
    print( leer_mensaje( cliente ).decode( 'utf-8' ) )
    print( '\n' )

    # Si el mensaje es OK lanzamos el submenu, ciclando 


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
            break

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