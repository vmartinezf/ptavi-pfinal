#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Programa uaclient que abre un socket a un uaserver
"""

import socket
import sys
import os
import time

# Cliente UDP simple.

# Dirección IP del servidor.
if len(sys.argv) != 4:
    sys.exit("Usage: python uaclient.py config method option")
try:
    CONFIG = sys.argv[1]
    MeTHOD1 = sys.argv[2]
    METHOD = METHOD1.upper()
    OPTION = sys.argv[3]
# MIRAR EXCEPCION DEL LOG
except:
    sys.exit("Usage: python uaclient.py config method option")
if PORT < 1024:
    sys.exit("ERROR: PORT IS INCORRECT")


fich = open(CONFIG, 'r')


# Excepción por si es un método diferente a los permitidos       
lista_metodos = ['REGISTER', 'INVITE', 'BYE']
if METHOD not in lista_metodos:
	sys.exit("Usage: python uaclient.py config method option")

Line_Sip = METHOD + " sip:" 
if METHOD == 'REGISTER':
	Line_Register = USER + ":" + PORT + " SIP/2.0\r\n"
    Line_Expires = "Expires: " + EXPIRATION + "\r\n"
    LINE = Line_Sip + Line_Register + Line_Expires
	# FALTA AUTHORIZATION
elif METHOD == 'INVITE':
	Line_Invite_sip = Line_Sip + Receptor + " SIP/2.0\r\n"
	Line_Content_Type = "Content-Type: application/sdp\r\n\r\n"
	Line_Version_Option = "v=0\r\n" + "o=" + USER + " " + IP + " \r\n"
	Line_Session_T = "s=misesion\r\n" + "t=0" 
	Line_Audio = "m=audio" + PORT_AUDIO + "RTP\r\n"
	LINE = Line_Invite_sip + Line_Content_Type + Line_Version_Option
	LINE += Line_Session_T + Line_Audio
elif METHOD == 'BYE':
	LINE = Line_Sip + Receptor + " SIP/2.0\r\n"


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
    LINEACK = "ACK" + " sip:" + Receptor + " SIP/2.0\r\n"
    print("Enviando: " + LINEACK)
    my_socket.send(bytes(LINEACK, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
elif lista[0] == 'SIP/2.0 401 Unauthorized':
	Line_Regist = "REGISTER" + " sip:" + USER + ":" + PORT + " SIP/2.0\r\n"
    Line_Expires = "Expires: " + EXPIRATION + "\r\n"
	Line_Authorization = "Authorization: response="+ Password + "\r\n"
    LINE = Line_Regist + Line_Expires + Line_Authorization 

# Cerramos todo
my_socket.close()
print("Fin.")
