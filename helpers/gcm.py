from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


def generarLlave( password: str, salt: bytes ):
    password_bin = password.encode('utf-8')
    kdf = Scrypt( salt = salt, length = 32, n = 2**14, r = 8, p = 1, backend = default_backend() )
    key = kdf.derive( password_bin )
    return key

def cifrar( password, data ):
    salt = os.urandom( 16 )
    key = generarLlave( password, salt )

    iv = os.urandom( 12 )
    encryptor = Cipher( algorithms.AES( key ), modes.GCM( iv ), backend = default_backend() ).encryptor()
    associated_data = iv + salt
    encryptor.authenticate_additional_data( associated_data )
    texto_cifrado = encryptor.update( bytes( data, encoding='raw_unicode_escape' ) )
    encryptor.finalize()
    tag = encryptor.tag
    res = texto_cifrado + b':::' + tag + b':::' + iv + b':::' + salt
    return res


def descifrar( password, data ):
    # Destructuramos lo necesario con base a la data
    res = data.split( b':::' )
    texto = res[ 0 ]
    tag = res[ 1 ]
    iv = res[ 2 ]
    salt = res[ 3 ]

    key = generarLlave( password, salt )
    decryptor = Cipher( algorithms.AES( key ), modes.GCM( iv, tag ), backend = default_backend ).decryptor()
    associated_data = iv + salt
    decryptor.authenticate_additional_data( associated_data )
    texto_decifrado = decryptor.update( texto )
    decryptor.finalize()
    return texto_decifrado
