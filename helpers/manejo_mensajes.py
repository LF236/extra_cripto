DELIMITADOR = b'###$###'

def quitar_delimitador( mensaje ):
    if not mensaje.endswith( DELIMITADOR ):
        return mensaje
    return mensaje[ :-len( DELIMITADOR ) ]

def leer_mensaje( socket ):
    # Permite leer un mensaje con una longitud 
    chunk = socket.recv( 1024 )
    mensaje = b''
    while not chunk.endswith( DELIMITADOR ):
        mensaje += chunk
        if DELIMITADOR in mensaje:
            break
        chunk = socket.recv( 1024 )
    mensaje += chunk
    return quitar_delimitador( mensaje )

def mandar_mensaje( socket, mensaje ):
    # -> Armar cuestiones de seguridad :c
    socket.send( mensaje + DELIMITADOR )