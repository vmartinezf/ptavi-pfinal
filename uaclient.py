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
from uaserver import Thread_CVLC


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
            sys.exit("This name of file doesn´t exist")

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
        PORT_AUDIO = lista[2]['rtpaudio']['puerto']
        IP_PROXY = lista[3]['regproxy']['ip']
        PORT_PROXY = lista[3]['regproxy']['puerto']
        PATH_LOG = lista[4]['log']['path']
        PATH_AUDIO = lista[5]['audio']['path']

    except IndexError:
        sys.exit("Usage: python uaclient.py config method option")

    try:
        lista_metodos = ['REGISTER', 'INVITE', 'BYE']
        if METHOD not in lista_metodos:
            print("Method have to be REGISTER, INVITE OR BYE")
            sys.exit("Usage: python uaclient.py config method option")

        Line_Sip = METHOD + " sip:"
        if METHOD == 'REGISTER':
            # Añadimos al  archivo log cuando comenzamos
            Event = ' Starting...'
            Datos_Log(PATH_LOG, Event, '', '', '')
            # Datos de envio del REGISTER sin Autentincación
            LINE = Line_Sip + USER_NAME + ":" + UASERVER_PORT
            LINE += " SIP/2.0\r\n" + "Expires: " + OPTION + "\r\n"
        elif METHOD == 'INVITE':
            LINE = Line_Sip + OPTION + " SIP/2.0\r\n"
            LINE += "Content-Type: application/sdp\r\n\r\n"
            LINE += "v=0\r\n" + "o=" + USER_NAME + " " + UASERVER_IP + " \r\n"
            LINE += "s=misesion\r\n" + "t=0\r\n"
            LINE += "m=audio " + PORT_AUDIO + " RTP\r\n"
        elif METHOD == 'BYE':
            LINE = Line_Sip + OPTION + " SIP/2.0\r\n"
        else:
            LINE = Line_Sip + OPTION + " SIP/2.0\r\n"
    except:
        sys.exit("Usage: python uaclient.py config method option")

    try:
        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, int(PORT_PROXY)))

        # Estamos enviando datos
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    except socket.error:
        Evento = 'Error'
        Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, '')
        sys.exit("Error: No server listening")
    try:
        # Escribimos en el log los datos que enviamos
        Evento = ' Send to '
        Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, LINE)

        # Recibimos datos
        data = my_socket.recv(1024)
        data_decod = data.decode('utf-8')
        print("Recibimos\r\n" + data_decod)

        # Escribimos el mensaje en el archivo de log el mensaje recibido
        Evento = ' Received from '
        Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, data_decod)
        print("Terminando socket...")

        Via = 'Via: SIP/2.0/UDP branch=z9hG4bKnashds7\r\n'
        Separacion = '\r\n' + Via + '\r\n'
        lista = data_decod.split(Separacion)[0:-1]
        Not_Aut = data_decod.split('\r\n')[0]
        Trying = 'SIP/2.0 100 Trying'
        Ring = 'SIP/2.0 180 Ring'
        OK = 'SIP/2.0 200 OK'
        Not_Found = 'SIP/2.0 404 User Not Found'
        Bad_R = 'SIP/2.0 400 Bad Request'
        if lista[0:3] == [Trying, Ring, OK]:
            LINEACK = "ACK" + " sip:" + OPTION + " SIP/2.0\r\n"
            try:
                my_socket.send(bytes(LINEACK, 'utf-8') + b'\r\n')
            except socket.error:
                Evento = 'Error'
                Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, '')
                sys.exit("Error: No server listening")
            # Escribimos en el log los datos que enviamos
            Evento = ' Send to '
            Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, LINEACK)

            # RTP
            Line_restante = data_decod.split('\r\n')[12]
            IP_RECEPT = Line_restante.split(' ')[1]
            Line_Port = data_decod.split('\r\n')[15]
            PORT_RECEPT = Line_Port.split(' ')[1]
            # Escribimos el mensage de comienzo RTP en el log
            Event = ' Terminando el envío RTP '
            Datos_Log(PATH_LOG, Event, '', '', '')
            # Ejecutamos el Thread
            hilo = Thread_CVLC(PORT_RECEPT, IP_RECEPT, PATH_AUDIO)
            hilo.start()
            hilo.join()
            os.system('pkill -9 4604')
            # Escribimos el mensage de fin RTP en el log
            Event = ' Terminando el envío RTP '
            Datos_Log(PATH_LOG, Event, '', '', '')
            data = my_socket.recv(1024)
        elif Not_Aut == 'SIP/2.0 401 Unauthorized':
            m = hashlib.md5()
            Nonce_Salto_Linea = data_decod.split('nonce="')[1]
            Nonce = Nonce_Salto_Linea.split('"')[0]
            m.update(bytes(PASSWD + Nonce, 'utf-8'))
            RESPONSE = m.hexdigest()
            LINE_REGIST = Line_Sip + USER_NAME + ":" + UASERVER_PORT
            LINE_REGIST += " SIP/2.0\r\n" + "Expires: " + OPTION + "\r\n"
            LINE_REGIST += 'Authorization: Digest response="' + RESPONSE
            LINE_REGIST += '"\r\n'
            try:
                my_socket.send(bytes(LINE_REGIST, 'utf-8') + b'\r\n')
            except error.socket:
                Evento = 'Error'
                Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, '')
                sys.exit("Error: No server listening")
            # Escribimos en el log los datos que enviamos
            Evento = ' Send to '
            Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, LINE_REGIST)
            data = my_socket.recv(1024)
            data_decod = data.decode('utf-8')
            print("Recibimos\r\n" + data_decod)
            # Escribimos el mensaje en el archivo de log el mensaje recibido
            Evento = ' Received from '
            Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, data_decod)
        elif lista == ['Acceso denegado: password is incorrect']:
            print("Usage: The Password is incorrect")
        elif lista == ['Expires no es un entero']:
            print("Usage: Expires no es un entero")
        elif lista != OK and lista != Bad_R and lista != Not_Found:
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
