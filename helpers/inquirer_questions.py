import inquirer
from helpers.validacionesCrearCuenta import *

question_menu = [
    inquirer.List(
        'accion',
        message='¿Qué deseas hacer?',
        choices=[ ( '1.Iniciar Sesión', '1' ), ( '2.Registrar Cuenta', '2' ), ( '3.Salir', '3' ) ]
    )
]

question_registro_usuario = [
    inquirer.Text( 'nombre_usuario', message='Ingresa un nombre de usuario', validate = validarNombreUsuario ),
    inquirer.Text( 'password_usuario', message='Ingresa una contraseña', validate = validarPassword ),
    inquirer.Text( 'repite_password_usuario', message='Repite la contraseña', validate = validarRepeatPassword )
]

question_login = [
    inquirer.Text( 'usuario', message='Ingresa tu nombre de usuario' ),
    inquirer.Text( 'password', message='Ingresa tu contraseña' )
]

question_agregar_servicio = [
    inquirer.Text( 'nombre_servicio', message='Ingresa el nombre del servicio', validate = validarNombreServicio ),
    inquirer.Text( 'password_servicio', message='Ingresa la contraseña del servicio', validate= validarPasswordServicio )
]

question_sesion_activa = [
    inquirer.List(
        'opcion_activa',
        message='Menú de sesión activa',
        choices=[
            ( '1.Listas mis llaves', '1' ),
            ( '2.Agregar llave nueva', '2' ),
            ( '3.Cerrar Sesión', '3' )
        ]
    )
]