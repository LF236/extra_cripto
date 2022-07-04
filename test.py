# Creamos el contexto del servidor
import socket
import ssl

contexto = ssl.SSLContext( ssl.PROTOCOL_TLS_SERVER )
contexto.minimum_version = ssl.TLSVersion.TLSv1_3 # Permitir a partir de TLS 1.3
# Cagar certificados
contexto.load_cert_chain( 'lf236.crt', 'lf236.key' )

with socket.socket( socket.AF_INET, socket.SOCK_STREAM, 0 ) as sock:
    sock.bind( ( 'localhost', 8982 ) )
    sock.listen( 5 )
    with contexto.wrap_socket( sock, server_side=True ) as ssock:
        conn, addr = ssock.accept()
        mensaje = conn.recv( 4096 )
        print( mensaje )
        conn.send( b'OK' )