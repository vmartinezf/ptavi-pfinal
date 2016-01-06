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


def Data_REGIST_NO_AUT(Linea, Port, username, option, LINE):
    Line_Register = username + ":" + Port + " SIP/2.0\r\n"
    Line_Expires = "Expires: " + option + "\r\n"
    LINE = Linea + Line_Register + Line_Expires


def Data_INVITE(Linea, option, username, Port ,ip, LINE):
    Line_Invite_sip = Linea + option + " SIP/2.0\r\n"
    Line_Content_Type = "Content-Type: application/sdp\r\n\r\n"
    Line_Version_Option = "v=0\r\n" + "o=" + username + " " + ip + " \r\n"
    Line_Session_T = "s=misesion\r\n" + "t=0\r\n"
    Line_Audio = "m=audio " + Port + " RTP\r\n"
    LINE = Line_Invite_sip + Line_Content_Type + Line_Version_Option
    LINE += Line_Session_T + Line_Audio


# Cliente UDP simple Sip.
if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("Usage: python uaclient.py config method option")
    try:
        CONFIG = sys.argv[1]
        METHOD1 = sys.argv[2]
        METHOD = METHOD1.upper()
        OPTION = sys.argv[3]
    except:
        sys.exit("Usage: python uaclient.py config method option")

    try:
        if os.path.exists(CONFIG) is False:
            sys.exit ("This name of file doesn´t exist")
        
        # Sacamos los datos del xml
        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(CONFIG))
        lista = cHandler.get_tags()

        # Meto los valores del xml en variables
        USER_NAME = lista[0]['account']['username']
        PASSWD = lista[0]['account']['passwd']
        UASERVER_IP = lista[1]['uaserver']['ip']
        UASERVER_PORT = lista[1]['uaserver']['puerto']
        PORT_AUDIO  = lista[2]['rtpaudio']['puerto']
        IP_PROXY = lista[3]['regproxy']['ip']
        PORT_PROXY = lista[3]['regproxy']['puerto']
        PATH_LOG = lista[4]['log']['path']
        PATH_AUDIO = lista[5]['audio']['path']

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
            Data_REGIST_NO_AUT(Line_Sip, UASERVER_PORT, USER_NAME, OPTION, LINE)
        elif METHOD == 'INVITE':
            IP = UASERVER_IP
            Data_INVITE(Line_Sip, OPTION, USER_NAME, PORT_AUDIO, IP, LINE)
        elif METHOD == 'BYE':
	        LINE = Line_Sip + Receptor + " SIP/2.0\r\n"
        else:
            sys.exit("This method is incorrect")


        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, PORT_PROXY))

        # Estamos enviando datos
        print("Enviando: " + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        # Escribimos en el log los datos que enviamos
        Evento = ' Send to '
        Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, LINE)

        # Recibimos datos
        data = my_socket.recv(1024)
        data_decod = data.decode('utf-8')

        print('Recibido -- ', data_decod)
        print("Terminando socket...")

        lista = data_decod.split('\r\n\r\n')[0:-1]
        Trying = 'SIP/2.0 100 Trying'
        Ring = 'SIP/2.0 180 Ring'
        OK = 'SIP/2.0 200 OK'
        if lista[0:3] == [Trying, Ring, OK]:
            print("Hemos recibido Trying, Ring y OK")
            LINEACK = "ACK" + " sip:" + Receptor + " SIP/2.0\r\n"
            print("Enviando: " + LINEACK)
            my_socket.send(bytes(LINEACK, 'utf-8') + b'\r\n')
            data = my_socket.recv(1024)
            # Escribimos en el log los datos que enviamos
            Evento = ' Send to ' 
            Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, LINEACK)

            # RTP
            IP_RECEPT = lista[4].split(' ')[2]
            PORT_RECEPT = lista[5].split(' ')[1]
            os.system('chmod 777 mp32rtp')
            # Contenido del archivo de audio a ejecutar
            Primero_a_Ejecutar = './mp32rtp -i ' + IP_RECEPT + ' -p '
            Segundo_a_Ejecutar = str(PORT_RECEPT) + '<' + PATH_AUDIO
            aEjecutar = Primero_a_Ejecutar + Segundo_a_Ejecutar
            print('Se está ejecutando el RTP')
            # Escribimos el mensage de comienzo RTP en el log
            Event = ' Terminando el envío RTP '
            Datos_Log(PATH_LOG, Event, '', '', '')
            # Se está ejecutando
            os.system(aEjecutar)
            # Escribimos el mensage de fin RTP en el log
            Event = ' Terminando el envío RTP '
            Datos_Log(PATH_LOG, Event, '', '', '')
        elif lista == OK:
            print ("Recibido el OK")
        elif lista[0] == 'SIP/2.0 401 Unauthorized':
            print("Hemos recibido 401 Unauthorized")
            m = hashlib.md5()
            Nonce = lista[1].split('=')[1]
            m.update(bytes(PASSWD + Nonce, 'utf-8'))
            RESPONSE = m.hexdigest()
            Data_REGIST_NO_AUT(Line_Sip, UASERVER_PORT, USER_NAME, OPTION, Line)
            Line_Authorization = "Authorization: response="+ RESPONSE + "\r\n"
            LINE_REGIST = Line + Line_Authorization
            my_socket.send(bytes(LINE_REGIST, 'utf-8') + b'\r\n')
            print("Enviando: " + LINE_REGIST)
            # Escribimos en el log los datos que enviamos
            Evento = ' Send to ' 
            Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, LINEREGIST)
        else:
            print("Hemos recibido un método incorrecto")
            # Escribimos en el log el mensaje de error
            Evento = 'Error: Method incorrect'
            Datos_Log(PATH_LOG, Evento, '', '', '')

        # Cerramos todo
        print("Terminando el socket")
        my_socket.close()
        Event = ' Finishing.'
        Datos_Log(PATH_LOG, Event, '', '', '')
        print("Fin.")

    except:
        Evento = 'Error'
        Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, '')
        sys.exit("Error: No server listening")
