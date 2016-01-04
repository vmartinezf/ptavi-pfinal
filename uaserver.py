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
    elif evento != 'Starting...' and evento 1= 'Finishing.':
        puerto = str(port)
        datos1 = time_now + ' ' + evento + ip  ':' + puerto + ': ' + line
        datos = datos1 + '\r\n'
    else:
        datos = time_now + ' ' + evento + '\r\n'
    fich.write(datos)
    fich.close()


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
                if METHOD == 'INVITE':
                    # Nos ha llegado un INVITE
                    # FALTA POR MIRAR
                    message_send = b'SIP/2.0 100 Trying\r\n\r\n'
                    message_send += b'SIP/2.0 180 Ring\r\n\r\n'
                    message_send += b'SIP/2.0 200 OK\r\n\r\n'
                    self.wfile.write(message_send)
                elif METHOD == 'ACK':
                    # Nos ha llegado un ACK
                    os.system('chmod 777 mp32rtp')
                    # Contenido del archivo de audio a ejecutar
                    Primero_a_Ejecutar = './mp32rtp -i ' + IP_PROXY + ' -p '
                    Segundo_a_Ejecutar = str(PORT_AUDIO) + '<' + PATH_AUDIO
                    aEjecutar = Primero_a_Ejecutar + Segundo_a_Ejecutar
                    print('Se está ejercutando el RTP')
                    os.system(aEjecutar)
                    # FALTA EL LOG
                elif METHOD == 'BYE':
                    # Nos ha llegado un BYE
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif METHOD not in METHODS:
                    # Nos ha llegado un método descoocido
                    message_send = b'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    self.wfile.write(message_send)
                    # FALTA EL LOG
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
        	print ("This name of file doesn´t exist")
            raise SystemExit

		# Saco el contenido del fichero xml
		parser = make_parser()
    	cHandler = SmallSMILHandler()
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
           print "This name of file os audio doesn´t exist"
           raise SystemExit    

    except IOError:
        sys.exit("Usage: python uaserver.py config")
    PORT = int(UASERVER_PORT)
    serv = socketserver.UDPServer((UASERVER_IP, PORT), EchoHandler)
    fich = open(PATH_LOG, 'a')
    print("Listening...")
    serv.serve_forever()
