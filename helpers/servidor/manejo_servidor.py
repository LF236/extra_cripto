import ast
from helpers.DB.db import *
from helpers.manejo_mensajes import mandar_mensaje
from helpers.gcm import *
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
        password_encrypt = cifrar( 'lf236', mensaje_to_json[ 'password_usuario' ] )
        nuevo_usuario = Usuario( user = mensaje_to_json[ 'nombre_usuario' ], password = password_encrypt )
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
            print( usuario.password )
            password_desc_db = descifrar( 'lf236', usuario.password )
            password_desc_db = password_desc_db.decode( 'utf-8' )
            if usuario.user == mensaje_to_json[ 'usuario' ] and password_desc_db == mensaje_to_json[ 'password' ]:
                band = True
        if band:
            mandar_mensaje( cliente, b'OK' )
        else:
            mandar_mensaje( cliente, b'Contrasena incorrecta' )


    except Usuario.DoesNotExist:
        mandar_mensaje( cliente, b'Usuario no existe en la base de datos' )

def almacenar_credencial( mensaje, cliente ):
    try:
        mensaje = mensaje.decode( 'utf-8' )
        # Eliminar el tipo de comando
        mensaje = mensaje[ 2: ]
        # Separar el mensaje con la información del cliente logueado
        data_mensaje, info_login = mensaje.split( '-' )
        # Parseamos la data a JSON
        data_mensaje = ast.literal_eval( data_mensaje )
        info_login = ast.literal_eval( info_login )
        # Buscamos la información del usuario logueado en la DB
        query = ( Usuario.select( ).where( Usuario.user == info_login[ 'usuario' ] ).get() )
        id_usuario = query.id_usuario
        # Verificar que el servicio no exista en la base de datos
        queryServicio = ( Servicio.select( ).where( Servicio.id_usuario == id_usuario, Servicio.nombre == data_mensaje[ 'nombre_servicio' ] ).get() )
        mandar_mensaje( cliente, b'El usuario ya tiene un servicio registrado con el mismo nombre' )

    except Servicio.DoesNotExist:
        password_encrypt = cifrar( 'lf236', data_mensaje[ 'password_servicio' ] )
        nuevo_servicio = Servicio( nombre = data_mensaje[ 'nombre_servicio' ], password = password_encrypt, id_usuario = id_usuario )
        nuevo_servicio.save()
        mandar_mensaje( cliente, b'El servicio se registro de manera exitosa' )

def listar_servicios( mensaje, cliente ):
    try:
        print( mensaje )
        mensaje = mensaje.decode( 'utf-8' )
        # Eliminar el tipo de comando
        mensaje = mensaje[ 2: ]
        # Parseamos la data
        mensaje_to_json = ast.literal_eval( mensaje )
        query = ( Usuario.select( ).where( Usuario.user == mensaje_to_json[ 'usuario' ] ).get() )
        id_usuario = query.id_usuario
        queryServicio = ( Servicio.select( ).where( Servicio.id_usuario == id_usuario ).get() )
        queryServicioAux = ( Servicio.select( ).where( Servicio.id_usuario == id_usuario ) )
        res = ''
        for elemento in queryServicioAux:
            password_desc_db = descifrar( 'lf236', elemento.password )
            password_desc_db = password_desc_db.decode( 'utf-8' )
            res += 'Servicio: {nombre} - Password: {password} \n'.format( nombre = elemento.nombre, password = password_desc_db )
        mandar_mensaje( cliente, bytes( res, encoding='raw_unicode_escape' ) )    

    except Servicio.DoesNotExist:
        mandar_mensaje( cliente, b'El usuario no tiene ningun servicio registrado' )


