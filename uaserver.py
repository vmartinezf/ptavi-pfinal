#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clases (y programa principal) para un uaserver de eco en UDP simple
"""

import socketserver
import socket
import sys
import os
import os.path
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time
import threading


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
        datos = datos1 + ip + " Port " + port + '\r\n'
    elif evento != 'Starting...' and evento != 'Finishing.':
        puerto = str(port)
        datos1 = time_now + ' ' + evento + ip + ':' + puerto + ': ' + line
        datos = datos1 + '\r\n'
    else:
        datos = time_now + ' ' + evento + '\r\n'
    fich.write(datos)
    fich.close()


class Thread_CVLC(threading.Thread):
    """
    Clase para crear hilos vcl
    """

    def __init__(self, Port, Ip, Path):
        threading.Thread.__init__(self)
        self.Port = Port
        self.Ip = Ip
        self.Path = Path

    def run(self):
        try:
            aEjecutarcvlc = 'cvlc rtp://@' + self.Ip + ':'
            aEjecutarcvlc += str(self.Port) + ' &'
            # Se está ejecutando
            os.system(aEjecutarcvlc)
            aEjecutar = './mp32rtp -i ' + self.Ip + ' -p '
            aEjecutar += str(self.Port) + '<' + self.Path
            # Se está ejecutando
            os.system(aEjecutar)
        except:
            sys.exit("Usage: Error en ejecución")


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        Envio_rtp = ''
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            line_decod = line.decode('utf-8')
            METHOD = line_decod.split(' ')[0].upper()
            METHODS = ['INVITE', 'BYE', 'ACK']
            if len(line_decod) >= 2:
                print("Recibimos\r\n" + line_decod)
                # Escribimos mensages de recepción en el fichero de log
                Evento = ' Received from '
                Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, line_decod)
                if METHOD == 'INVITE':
                    if Envio_rtp == 'Enviamos RTP':
                        messg = '480 Temporarily Unavailable\r\n\r\n'
                    else:
                        messg = 'SIP/2.0 100 Trying\r\n\r\n'
                        messg += 'SIP/2.0 180 Ring\r\n\r\n'
                        messg += 'SIP/2.0 200 OK\r\n\r\n'
                        messg += 'Content-Type: application/sdp\r\n\r\n'
                        messg += 'v=0\r\n'
                        messg += 'o=' + USER_NAME + ' ' + UASERVER_IP
                        messg += ' \r\n' + 's=misesion\r\n' + 't=0\r\n'
                        messg += 'm=audio ' + PORT_AUDIO + ' RTP\r\n\r\n'
                    # Enviamos el mensaje de respuesta al INVITE
                    self.wfile.write(bytes(messg, 'utf-8'))
                    # Escribimos los mensages de envio en el log
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, messg)
                elif METHOD == 'ACK':
                    # Escribimos el mensage de comienzo RTP en el log
                    Event = ' Comenzando el envío RTP '
                    Datos_Log(PATH_LOG, Event, '', '', '')
                    # Ejecutamos el Thread
                    hilo = Thread_CVLC(PORT_AUDIO, IP_PROXY, PATH_AUDIO)
                    hilo.start()
                    Envio_rtp = 'Enviamos RTP'
                    hilo.join()
                    os.system('killall vlc')
                    Envio_rtp = ''
                    # Escribimos el mensage de fin RTP en el log
                    Event = ' Terminando el envío RTP '
                    Datos_Log(PATH_LOG, Event, '', '', '')
                elif METHOD == 'BYE':
                    os.system('pkill -9 ' + Proceso)
                    Envio_rtp = ''
                    mssg_send = "SIP/2.0 200 OK\r\n\r\n"
                    self.wfile.write(bytes(mssg_send, 'utf-8'))
                    # Escribimos el mensage de envio en el log
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, mssg_send)
                elif METHOD not in METHODS:
                    messg = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    self.wfile.write(bytes(messg, 'utf-8'))
                    # Escribimos los mensages de envio en el log
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, messg)
                else:
                    # Respuesta mal formada
                    messg = "SIP/2.0 400 Bad Request\r\n\r\n"
                    self.wfile.write(bytes(messg, 'utf-8'))
                    # Escribimos los mensages de envio en el log
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, messg)
            else:
                # Escribimos mensages de recepción en el fichero de log
                Evento = ' Received from '
                Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, line_decod)

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

        # Comprobación de si existe el archivo de audio
        if not os.path.exists(PATH_AUDIO):
            sys.exit("This name of file os audio doesn´t exist")

    except IOError:
        sys.exit("Usage: python uaserver.py config")
    try:
        PORT = int(UASERVER_PORT)
        serv = socketserver.UDPServer((UASERVER_IP, PORT), EchoHandler)
        print("Listening...")
        serv.serve_forever()
    except:
        Evento = 'Error'
        Datos_Log(PATH_LOG, Evento, IP_PROXY, PORT_PROXY, '')
        sys.exit("Error: No server listening")
