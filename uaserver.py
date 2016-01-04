#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clases (y programa principal) para un uaserver de eco en UDP simple
"""

import socketserver
import sys
import os
import os.path
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib


# Creamos una clase XMLHandler de la misma forma que creamos una en la P3 para
# Smil
class XMLHandler(ContentHandler):
    """
    Clase para manejar xml
    """

    def __init__(self):
        """
        Constructor. Inicializamos las variables
        """
        self.lista_etiquetas = []
        self.dic = {'account': ['username', 'passwd'],
                    'uaserver': ['ip', 'puerto'],
                    'rtpaudio': ['puerto'],
                    'regproxy': ['ip', 'puerto'],
                    'log': ['path'],
                    'audio': ['path']}

    def startElement(self, name, attrs):
        """
        Método que se llama para alamacenar las etiquetas,
        los atributos y su contenido
        """
        if name in self.dic:
            dicc = {}
            for item in self.dic[name]:
                dicc[item] = attrs.get(item, "")
            diccname = {name: dicc}
            self.lista_etiquetas.append(diccname)

    def get_tags(self):
        """
        Método que devuelve las etiquetas,
        los atributos y su contenido
        """
        return self.lista_etiquetas


def Datos_Log(fichero, evento, ip, port, line):
    fich = open(fichero, 'a')
    time_now = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))
    if evento == 'Error':
        datos1 = time_now + ' ' + evento + ': No server listening at '
        datos = datos1 + ip + port + '\r\n'
    elif evento != 'Starting...' and evento != 'Finishing.':
        puerto = str(port)
        datos1 = time_now + ' ' + evento + ip + ':' + puerto + ': ' + line
        datos = datos1 + '\r\n'
    else:
        datos = time_now + ' ' + evento + '\r\n'
    fich.write(datos)
    fich.close()


def Response_INVITE(username, ipserver, port, message_send)   
    message_send = b'SIP/2.0 100 Trying\r\n\r\n'
    message_send += b'SIP/2.0 180 Ring\r\n\r\n'
    message_send += b'SIP/2.0 200 OK\r\n\r\n'
    message_send += b'Content-Type: application/sdp\r\n\r\n'
    message_send += b'v=0\r\n'
    message_send += b'o=' + USER_NAME + ' ' + UASERVER_IP
    message_send += b' \r\n' + 's=misesion\r\n' + 't=0'
    message_send += b'm=audio' + PORT_AUDIO + 'RTP\r\n\r\n'


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            line_decod = line.decode('utf-8')
            METHOD = line_decod.split(' ')[0].upper()
            METHODS = ['INVITE', 'BYE', 'ACK']
            if len(line_decod) >= 2:
                print("El cliente nos manda " + line_decod)
                # Escribimos mensages de recepción en el fichero de log
                Evento = ' Received from '
                Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, line_decod)
                if METHOD == 'INVITE':
                    print("Nos ha llegado un INVITE")
                    Response_INVITE(USER_NAME, UASERVER_IP, PORT_AUDIO, message)
                    # Enviamos el mensaje de respuesta al INVITE
                    self.wfile.write(message)
                    print("Enviamos" + message)
                    # Escribimos los mensages de envio en el log
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, message)
                elif METHOD == 'ACK':
                    print("Nos ha llegado un ACK")
                    os.system('chmod 777 mp32rtp')
                    # Contenido del archivo de audio a ejecutar
                    Primero_a_Ejecutar = './mp32rtp -i ' + IP_PROXY + ' -p '
                    Segundo_a_Ejecutar = str(PORT_AUDIO) + '<' + PATH_AUDIO
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
                elif METHOD == 'BYE':
                    print("Nos ha llegado un BYE")
                    mssg_send = b"SIP/2.0 200 OK\r\n\r\n"
                    self.wfile.write(mssg_send)
                    # Escribimos el mensage de envio en el log
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, mssg_send)
                elif METHOD not in METHODS:
                    print("Nos ha llegado un método descoocido")
                    message_send = b'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    self.wfile.write(message_send)
                else:
                    # Respuesta mal formada
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            else:
                print("El cliente nos manda " + line_decod)

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break


if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    try:
		# Archivo xml pasado como parámetro
        CONFIG = sys.argv[1]

        # Comprobación de si existe el fichero pasado como parámetro
        if os.path.exists(CONFIG) is False:
        	sys.exit("This name of file doesn´t exist")

		# Saco el contenido del fichero xml
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

        # Comprobación de si existe el archivo de audio
        if not os.path.exists(PATH_AUDIO):
           sys.exit("This name of file os audio doesn´t exist")

    except IOError:
        sys.exit("Usage: python uaserver.py config")
    PORT = int(UASERVER_PORT)
    serv = socketserver.UDPServer((UASERVER_IP, PORT), EchoHandler)
    print("Listening...")
    serv.serve_forever()
