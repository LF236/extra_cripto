from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import dh, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os
from cryptography.hazmat.primitives import serialization
from time import sleep
import threading

import sys
import socket
import json
import inquirer
from helpers.inquirer_questions import *
from helpers.manejo_mensajes import *

# Variables globales
NoneType = type(None)
USUARIO = 'lf236'
PASSWORD = 'lf2366665'



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

# -----------------> Rutinas para cigrado
def deserealizar_llave( llave ):
    llave_deserealizada = serialization.load_pem_public_key( llave, backend=default_backend() )
    return llave_deserealizada

def serializar_llave(llave):
    llave_serializada = llave.public_bytes( encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo )
    return llave_serializada

def verificar_firma(ec_servidor_pub, signature, dh_servidor_pub_S):
    try:
        ec_servidor_pub.verify(
            signature, dh_servidor_pub_S, ec.ECDSA(hashes.SHA256()))
        print('**LA FIRMA ES VALIDA**')
    except:
        print('**LA FIRMA NO ES VALIDA**')
        exit()

def conectar_servidor( host, puerto ):
    # Socket para IP v4
    cliente = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    try:
        cliente.connect( ( host, int( puerto ) ) )
        return cliente
    except:
        print( 'Servidor no alcanzable' )
        exit()

def crear_secreto(dh_servidor_pub, dh_cliente_priv):
    secreto_emisor = dh_cliente_priv.exchange( ec.ECDH(), dh_servidor_pub )
    return secreto_emisor

def derivar_llave(secreto_emisor):
    # Nota - El handshake tiene que ser lo mismo de los dos lados
    derived_key = HKDF(algorithm=hashes.SHA256(), length=32,salt=None, info=b'handshake data', backend=default_backend()).derive(secreto_emisor)
    return derived_key

def cifrar_sends(mensaje_plano, llave_aes):
    iv = os.urandom(12)
    aad = os.urandom(32)
    mp = mensaje_plano

    chacha = ChaCha20Poly1305(llave_aes)
    mensaje_cifrado = chacha.encrypt(iv, mp, aad)
    print(mensaje_cifrado)
    return (iv+aad+mensaje_cifrado)

def work_loop( cliente, dh_cliente_pub ):
    # Rutina que solo ocurre una vez, cuando se inicia la conexión -> El servidor tiene que enviar las firmas
    # Si no hay firmas al inicio del mensaje entonces pasa
    mensaje = leer_mensaje( cliente )
    if mensaje.startswith( b'FIRMAS' ):
        firmas = mensaje[6:]
        dh_servidor_pub_S = firmas[:215]
        ec_servidor_pub_S = firmas[215:430]
        signature = firmas[430:]

        ec_servidor_pub = deserealizar_llave( ec_servidor_pub_S )
        verificar_firma( ec_servidor_pub, signature, dh_servidor_pub_S )
        dh_cliente_pub_S = serializar_llave( dh_cliente_pub )
        dh_cliente_pub_S = b'DHCLIENTEPUB' + dh_cliente_pub_S

        dh_servidor_pub = deserealizar_llave( dh_servidor_pub_S )
        secreto_emisor = crear_secreto( dh_servidor_pub, dh_cliente_priv )
        secreto_enviar = secreto_emisor[:24]
        secreto_recibir = secreto_emisor[24:]

        aes_recibir = derivar_llave( secreto_recibir )
        aes_enviar = derivar_llave( secreto_enviar )

        llaveHKSF = derivar_llave( secreto_emisor[:32] )

        # Armando mensaje con las credenciales
        mensaje = b'%s:%s' % ( USUARIO.encode( 'utf-8' ), PASSWORD.encode( 'utf-8' ) )
        credenciales = cifrar_sends(mensaje, llaveHKSF)
        mandar_mensaje( cliente, dh_cliente_pub_S + b'::::' + credenciales )
    
    # Si no se mandan las llaves
    else:   
        print( '\nFaltan las firmas\n' )
        exit( 1 )
    # Ciclo de atención para el cliente
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

def crear_llaves_dh():
    dh_cliente_priv = ec.generate_private_key(
        ec.SECP384R1(), default_backend())
    # Esta es la que se tiene que intercambiar
    dh_cliente_pub = dh_cliente_priv.public_key()
    return dh_cliente_priv, dh_cliente_pub

if __name__ == '__main__':
    # Ejecutar código
    try:
        host = sys.argv[ 1 ]
        puerto = sys.argv[ 2 ]
        cliente = conectar_servidor( host, puerto )
        dh_cliente_priv, dh_cliente_pub = crear_llaves_dh()
        work_loop( cliente, dh_cliente_pub )
        pass
    
    except IndexError:
        print( 'Error al ingresar datos - Estructura: python index.py host puerto ' )