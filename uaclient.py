#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Programa uaclient que abre un socket a un uaserver
"""

import socket
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib
from uaserver import XMLHandler
from uaserver import Datos_Log


# Cliente UDP simple Sip.
if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("Usage: python uaclient.py config method option")
    try:
        CONFIG = sys.argv[1]
        MeTHOD1 = sys.argv[2]
        METHOD = METHOD1.upper()
        OPTION = sys.argv[3]
    except:
        sys.exit("Usage: python uaclient.py config method option")
    if PORT < 1024:
        sys.exit("ERROR: PORT IS INCORRECT")

    try:
	    if os.path.exists(CONFIG) is False:
        	sys.exit ("This name of file doesn´t exist")
        # Sacamos los datos del xml
	    parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(CONFIG))
	    lista = cHandler.get_tags()

        diccionario = lista[0]
        # Meto los valores del xml en variables
        USER_NAME = diccionario['account']['username']
        PASSWD = diccionario['account']['passwd']
        UASERVER_IP = diccionario['uaserver']['ip']
        UASERVER_PORT = diccionario['uaserver']['puerto']
        PORT_AUDIO  = diccionario['rtpaudio']['puerto']
        IP_PROXY = diccionario['regproxy']['ip']
        PORT_PROXY = diccionario['regproxy']['puerto']
        PATH_LOG = diccionario['log']['path']
        PATH_AUDIO = diccionario['audio']['path']

    except IndexError:
	    sys.exit("Usage: python uaclient.py config method option")

    try:     
        lista_metodos = ['REGISTER', 'INVITE', 'BYE']
        if METHOD not in lista_metodos:
	        sys.exit("Usage: python uaclient.py config method option")

        Line_Sip = METHOD + " sip:" 
        if METHOD == 'REGISTER':
            # Añadimos al  archivo log cuando comenzamos
            Event = ' Starting...'
            Datos_Log(PATH_LOG, Event, '', '', '')
            # Datos de envio del REGISTER sin Autentincación
	        Line_Register = USER_NAME + ":" + UASERVER_PORT + " SIP/2.0\r\n"
            Line_Expires = "Expires: " + OPTION + "\r\n"
            LINE = Line_Sip + Line_Register + Line_Expires
        elif METHOD == 'INVITE':
	        Line_Invite_sip = Line_Sip + Receptor + " SIP/2.0\r\n"
	        Line_Content_Type = "Content-Type: application/sdp\r\n\r\n"
	        Line_Version_Option = "v=0\r\n" + "o=" + USER + " " + IP + " \r\n"
	        Line_Session_T = "s=misesion\r\n" + "t=0\r\n" 
	        Line_Audio = "m=audio" + PORT_AUDIO + "RTP\r\n"
	        LINE = Line_Invite_sip + Line_Content_Type + Line_Version_Option
	        LINE += Line_Session_T + Line_Audio
        elif METHOD == 'BYE':
	        LINE = Line_Sip + Receptor + " SIP/2.0\r\n"


        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, PORT_PROXY))

        # Estamos enviando ddatos
        print("Enviando: " + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        Evento = ' Send to '
        Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, LINE

        # Recibimos datos
        data = my_socket.recv(1024)
        data_decod = data.decode('utf-8')

        print('Recibido -- ', data_decod)
        print("Terminando socket...")

        lista = data_decod.split('\r\n\r\n')[0:-1]
        Trying = 'SIP/2.0 100 Trying'
        Ring = 'SIP/2.0 180 Ring'
        OK = 'SIP/2.0 200 OK'
        if lista == [Trying, Ring, OK]:
            LINEACK = "ACK" + " sip:" + Receptor + " SIP/2.0\r\n"
            print("Enviando: " + LINEACK)
            my_socket.send(bytes(LINEACK, 'utf-8') + b'\r\n')
            data = my_socket.recv(1024)
        elif lista[0] == 'SIP/2.0 401 Unauthorized':
            # MIRAR BIEN
            m = hashlib.md5()
            m.update(b(passwd) + b(nonce))
            response = m.hexdigest()
	        Line_Regist = "REGISTER" + " sip:" + USER + ":" + PORT 
            Line_Regist += " SIP/2.0\r\n"
            Line_Expires = "Expires: " + EXPIRATION + "\r\n"
	        Line_Authorization = "Authorization: response="+ RESPONSE + "\r\n"
            LINE = Line_Regist + Line_Expires + Line_Authorization 

        # Cerramos todo
        print("Terminando el socket")
        my_socket.close()
        print("Fin.")

    except:
        Evento = 'Error'
        Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, '')
        sys.exit("Error: No server listening")
