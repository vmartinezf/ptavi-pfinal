#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un uaserver de eco en UDP simple
"""

import socketserver
import sys
import os
import os.path


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
