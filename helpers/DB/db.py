from peewee import *

db = MySQLDatabase(database='bitWarden', user='sica_user', password='siscae1035', host='localhost', port=3306)
    

class Usuario( Model ):
    id_usuario = AutoField()
    user = CharField()
    password = BlobField()
    
    class Meta:
        database = db

class Servicio( Model ):
    id_servicio = AutoField()
    nombre = TextField()
    password = BlobField()
    id_usuario = ForeignKeyField( Usuario )
    class Meta:
        database = db

def start_db():
    db.connect()
    db.create_tables( [ Usuario, Servicio ] )


