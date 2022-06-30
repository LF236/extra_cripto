import socket
import sys
import threading
from helpers.manejo_mensajes import *
from helpers.DB.db import *
from helpers.servidor.manejo_servidor import almacenar_usuario, proceso_login
def leer_opcion_cliente( cliente ):
    mensaje = leer_mensaje( cliente )
    if mensaje.startswith( b'1' ):
        print( 'LOGIN' );
        proceso_login( mensaje, cliente )

    if mensaje.startswith( b'2' ):
        print( 'CREANDO NUEVO USUARIO' );
        almacenar_usuario( mensaje, cliente )
    pass

def atencion_clientes( cliente ):
    while True:
        # -> Rutina de seguirad xd
        leer_opcion_cliente( cliente )


def escuchar( servidor ):
    servidor.listen( 5 )
    while True:
        cliente, _ = servidor.accept()
        atencion_clientes( cliente )
        # print( cliente )
        # hilo_atencion = threading.Thread( target = atencion_clientes, args = ( cliente ) )
        # hilo_atencion.start()

def crear_servidor( puerto ):
    # Función que crear un servidor Socket TCP para antender clientes
    servidor = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    servidor.bind( ( 'localhost', int( puerto ) ) )
    return servidor

if __name__ == '__main__':
    try:
        start_db()
        puerto = sys.argv[ 1 ]
        # -> Armar proceso de validación de entradas
        servidor = crear_servidor( puerto )
        print( 'Servidor en escucha' )
        escuchar( servidor )

    except IndexError:
        print( 'Error al ingresar datos - Estructura: python servidor.py puerto' )