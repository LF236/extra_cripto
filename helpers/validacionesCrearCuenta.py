import inquirer
def validarNombreUsuario( answers, current ):
    if len( current ) <= 1:
        raise inquirer.errors.ValidationError( "", reason='Ingresa un nombre de usuario más largo' )
    return True

def validarPassword( answers, current ):
    if len( current ) <= 1:
        raise inquirer.errors.ValidationError( "", reason='Ingresa tu contraseña' )
    return True

def validarRepeatPassword( answers, current ):
    if len( current ) <= 1:
        raise inquirer.errors.ValidationError( "", reason='Este campo no debe estar vacio' )
    if current != answers[ 'password_usuario' ]:
        raise inquirer.errors.ValidationError( "", reason='Las dos contraseñas deben ser iguales - Preciona Ctrl + c y reinicia el proceso' )
    return True

def validarNombreServicio ( answers, current ):
    if len( current ) <= 1:
        raise inquirer.errors.ValidationError( "", reason='Ingresa un nombre de usuario más grande' )
    return True

def validarPasswordServicio( answers, current ):
    if len( current ) <= 1:
        raise inquirer.errors.ValidationError( "", reason='Ingresa un password más grande' )
    return True