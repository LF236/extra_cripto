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

# GLOBAL VARS
USUARIOS = {'lf236': 'lf2366665', 'fernandoRH': 'xxx77s7as7a7s7sa7'}

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

def derivar_llave(secreto_receptor): 
    # Nota el handshake tiene que ser lo mismo de los dos lados
    derived_key = HKDF( algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data', backend=default_backend() ).derive( secreto_receptor )
    return derived_key

def deserealizar_llave(llave):
    llave_deserealizada = serialization.load_pem_public_key( llave, backend=default_backend() )
    return llave_deserealizada

def crear_secreto(dh_cliente_pub, dh_servidor_priv):
    secreto_emisor = dh_servidor_priv.exchange(ec.ECDH(), dh_cliente_pub)
    return secreto_emisor

def descifrar_recvs(mensaje_cifrado, llave_aes):
    """
    print('MENSAJE DECIFRADO')
    print(mensaje_cifrado)
    """
    iv = mensaje_cifrado[0:12]
    mensaje_cifrado = mensaje_cifrado[12:]
    aad = mensaje_cifrado[0:32]
    mensaje_cifrado = mensaje_cifrado[32:]
    mc = mensaje_cifrado
    chacha = ChaCha20Poly1305(llave_aes)
    mensaje = chacha.decrypt(iv, mc, aad)
    return mensaje

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
    # -> Rutina de seguridad xd        
    mensaje = leer_mensaje(cliente)
    if mensaje.startswith(b'DHCLIENTEPUB'):
        print( 'VAMOS A VALIDAR LAS LLAVES XD' )
        dh_cliente_pub_S = mensaje[12:]
        dh_cliente_pub = deserealizar_llave( dh_cliente_pub_S )
        secreto_receptor = crear_secreto( dh_cliente_pub, dh_servidor_priv )
        secreto_recibir = secreto_receptor[:24]
        secreto_enviar = secreto_receptor[24:]

        aes_recibir = derivar_llave( secreto_recibir )
        aes_enviar = derivar_llave( secreto_enviar )

        llaveHKDF = derivar_llave( secreto_receptor[:32] )
        credenciales = mensaje[-77:]
        credenciales_des = descifrar_recvs( credenciales, llaveHKDF )

        # credencialesU = credenciales_des.decode( 'utf-8' )
        # username = credencialesU.split(':')[0]
        # password = credencialesU.split(':')[1]
        # if username in USUARIOS.keys():
        #     print('ENTRO')

    print( mensaje )
    while True:
        
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