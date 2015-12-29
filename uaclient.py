#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Programa uaclient que abre un socket a un uaserver
"""

import socket
import sys

# Cliente UDP simple.

# Dirección IP del servidor.
if len(sys.argv) != 4:
    sys.exit("Usage: python uaclient.py config method option")
try:
    config = sys.argv[1]
    MeTHOD1 = sys.argv[2]
    METHOD = METHOD1.upper()
    OPTION = sys.argv[3]
    # MIRAR BIEN A PARTIR DE AQUÍ
    #if METHOD == 'INVITE' or METHOD == 'BYE':
        # MAL
       
# MIRAR EXCEPCION DEL LOG
except:
    sys.exit("Usage: python uaclient.py config method option")
if PORT < 1024:
    sys.exit("ERROR: PORT IS INCORRECT")

# Contenido que vamos a enviar
Line_sip = " sip:" + LOGIN + IPSERVER + " SIP/2.0\r\n"
LINE = METHOD + Line_sip

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IPSERVER, PORT))

print("Enviando: " + LINE)
my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
data = my_socket.recv(1024)
data_decod = data.decode('utf-8')

print('Recibido -- ', data_decod)
print("Terminando socket...")

lista = data_decod.split('\r\n\r\n')[0:-1]
if lista == ['SIP/2.0 100 Trying', 'SIP/2.0 180 Ring', 'SIP/2.0 200 OK']:
    LINEACK = "ACK" + Line_sip
    print("Enviando: " + LINEACK)
    my_socket.send(bytes(LINEACK, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)

# Cerramos todo
my_socket.close()
print("Fin.")
