import socket
import sys
import threading
import ssl
from helpers.manejo_mensajes import *
from helpers.DB.db import *
from helpers.servidor.manejo_servidor import almacenar_credencial, almacenar_usuario, listar_servicios, proceso_login

# GLOBAL VARS
# Creamos el contexto del servidor
contexto = ssl.SSLContext( ssl.PROTOCOL_TLS_SERVER )
contexto.minimum_version = ssl.TLSVersion.TLSv1_3 # Permitir a partir de TLS 1.3
# Cagar certificados
contexto.load_cert_chain( 'lf236.crt', 'lf236.key' )

def leer_opcion_cliente( cliente ):
    mensaje = leer_mensaje( cliente )
    if mensaje.startswith( b'1' ):
        print( 'LOGIN' );
        proceso_login( mensaje, cliente )

    if mensaje.startswith( b'2' ):
        print( 'CREANDO NUEVO USUARIO' );
        almacenar_usuario( mensaje, cliente )
    
    if mensaje.startswith( b'4' ):
        print( 'ALMACENANDO SERVICIO CON SU CREDENCIAL' )
        almacenar_credencial( mensaje, cliente )
    
    if mensaje.startswith( b'5' ):
        print( 'LISTAR SERVICIOS POR USUARIO' )
        listar_servicios( mensaje, cliente )

    pass

# ------> Hilos principales de ejecución
def crear_servidor( puerto ):
    # Función que crear un servidor Socket TCP para antender clientes
    servidor = socket.socket( socket.AF_INET, socket.SOCK_STREAM, 0 )
    # servidor = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    servidor.bind( ( 'localhost', int( puerto ) ) )
    return servidor

def escuchar( servidor ):
    with contexto.wrap_socket( servidor, server_side = True ) as servidor_sock:
        servidor_sock.listen( 5 )
        while True:
            cliente, _ = servidor_sock.accept()

            hilo_atencion = threading.Thread( target = atencion_clientes, args = ( cliente, ) )
            hilo_atencion.start()

def atencion_clientes( cliente ):
    while True:        
        leer_opcion_cliente( cliente )


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