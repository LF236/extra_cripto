import ast
from helpers.DB.db import *
from helpers.manejo_mensajes import mandar_mensaje
def almacenar_usuario( mensaje, cliente ):
    try:
        mensaje = mensaje.decode( 'utf-8' )
        # Eliminamos el tipo de comando
        mensaje = mensaje[ 2: ]
        # Parseamos a cadena a un JSON
        mensaje_to_json = ast.literal_eval( mensaje )
        # Crear objeto con base a clases 
        print( mensaje_to_json[ 'nombre_usuario' ] )
        # Verificamos que el nombre de usuario no se encuentre registrado en la db
        query = ( Usuario.select( ).where( Usuario.user == mensaje_to_json[ 'nombre_usuario' ] ).get() )
        print( 'Enviando mensaje de error al cliente' )
        mandar_mensaje( cliente, b'El usuario ya se encuentra registrar en el servidor, intenta de nuevo' )
        
    except Usuario.DoesNotExist:
        # Si el usuario no existe lo almacenamos en la DB
        nuevo_usuario = Usuario( user = mensaje_to_json[ 'nombre_usuario' ], password = mensaje_to_json[ 'password_usuario' ] )
        nuevo_usuario.save()
        mandar_mensaje( cliente, b'El usuario registrado de manera correcta' )


def proceso_login( mensaje, cliente ):
    try:
        mensaje = mensaje.decode( 'utf-8' )
        # Eliminamos el tipo de comando
        mensaje = mensaje[ 2: ]
        # Parseamos a cadena a un JSON
        mensaje_to_json = ast.literal_eval( mensaje )
        usuario_login = mensaje_to_json[ 'usuario' ]
        # Buscamos en la base si el usuario existe
        query = Usuario.select( Usuario ).where( Usuario.user == usuario_login ).get()

        queryAux = ( Usuario.select( Usuario ).where( Usuario.user == usuario_login ) )
        band = False
        for usuario in queryAux:
            print( usuario.user )
            if usuario.user == mensaje_to_json[ 'usuario' ] and usuario.password == mensaje_to_json[ 'password' ]:
                band = True
        if band:
            mandar_mensaje( cliente, b'OK' )
        else:
            mandar_mensaje( cliente, b'Contrasena incorrecta' )


    except Usuario.DoesNotExist:
        mandar_mensaje( cliente, b'Usuario no existe en la base de datos' )

