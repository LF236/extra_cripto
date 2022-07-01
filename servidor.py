import socket
import sys
import threading
import os
from time import sleep

from helpers.manejo_mensajes import *
from helpers.DB.db import *
from helpers.servidor.manejo_servidor import almacenar_credencial, almacenar_usuario, listar_servicios, proceso_login

from cryptography.hazmat.primitives.asymmetric import dh, ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

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

# ------> Funciones para la rutina de seguridad
def serializar_llave(llave):
    llave_serializada = llave.public_bytes( encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return llave_serializada

def crear_llaves_dh():
    dh_servidor_priv = ec.generate_private_key( ec.SECP384R1(), default_backend() )
    # Esta es la que se tiene que intercambiar
    dh_servidor_pub = dh_servidor_priv.public_key()
    return dh_servidor_priv, dh_servidor_pub

def crear_llaves_ec():
    ec_servidor_priv = ec.generate_private_key( ec.SECP384R1(), default_backend() )
    ec_servidor_pub = ec_servidor_priv.public_key()
    return ec_servidor_priv, ec_servidor_pub

# ------> Hilos principales de ejecución
def crear_servidor( puerto ):
    # Función que crear un servidor Socket TCP para antender clientes
    servidor = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    servidor.bind( ( 'localhost', int( puerto ) ) )
    return servidor

def escuchar( servidor, dh_servidor_priv, dh_servidor_pub ):
    servidor.listen( 5 )
    while True:
        cliente, _ = servidor.accept()
        dh_servidor_pub_S = serializar_llave( dh_servidor_pub )
        ec_servidor_pub_S = serializar_llave( ec_servidor_pub )
        signature = ec_servidor_priv.sign( dh_servidor_pub_S, ec.ECDSA( hashes.SHA256() ) )
        firmas = b'FIRMAS' + dh_servidor_pub_S + ec_servidor_pub_S + signature
        mandar_mensaje( cliente, firmas )

        hilo_atencion = threading.Thread( target = atencion_clientes, args = ( cliente, ) )
        hilo_atencion.start()

def atencion_clientes( cliente ):
    while True:
        # -> Rutina de seguirad xd
        # mandar_mensaje( cliente, b'puro lf236' )
        leer_opcion_cliente( cliente )


if __name__ == '__main__':
    try:
        start_db()
        puerto = sys.argv[ 1 ]
        # -> Armar proceso de validación de entradas
        servidor = crear_servidor( puerto )
        # Creación de las llaves EC
        ec_servidor_priv, ec_servidor_pub = crear_llaves_ec()
        # Serializar la llave pública del servidor
        dh_servidor_priv, dh_servidor_pub = crear_llaves_dh()
        print( 'Servidor en escucha' )
        escuchar( servidor,  dh_servidor_priv, dh_servidor_pub )

    except IndexError:
        print( 'Error al ingresar datos - Estructura: python servidor.py puerto' )