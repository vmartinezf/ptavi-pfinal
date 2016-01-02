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
				if METHOD == 'REGISTER':
					# FALTA POR HACER
                if METHOD == 'INVITE':
                    message_send = b'SIP/2.0 100 Trying\r\n\r\n'
                    message_send += b'SIP/2.0 180 Ring\r\n\r\n'
                    message_send += b'SIP/2.0 200 OK\r\n\r\n'
                    self.wfile.write(message_send)
                elif METHOD == 'ACK':
                    aEjecutar = './mp32rtp -i ' + IP + ' -p 23032 <' + FICH
                    os.system(aEjecutar)
                elif METHOD == 'BYE':
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif METHOD not in METHODS:
                    message_send = b'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    self.wfile.write(message_send)
                else:
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            else:
                print("El cliente nos manda " + line_decod)

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    try:
        CONFIG = sys.argv[1]
    except IOError:
        sys.exit("Usage: python uaserver.py config")
    serv = socketserver.UDPServer(('', PORT), EchoHandler)
    print("Listening...")
    serv.serve_forever()
