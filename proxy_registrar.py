#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Programa Proxy registrar y clase del proxy
"""

import socketserver
import sys
import time
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaserver import Datos_Log
import hashlib
import random


class XMLHandler_Proxy(ContentHandler):
    """
    Clase para manejar xml
    """

    def __init__(self):
        """
        Constructor. Inicializamos las variables
        """
        self.lista_etiquetas = []
        self.dic = {'server': ['name', 'ip', 'puerto'],
                    'database': ['path', 'passwdpath'],
                    'log': ['path']}

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
        

def Check_Password(Path, Passwd, User_agent, Found):
    Found = 'False'
    fich = open(Path, 'r')
    lines = fich.readlines()
    for line in range(len(lines)):
        User = lines[line].split(' ')[1]
        Password = lines[line].split(' ')[3]
        if User == User_agent:
            if Password == Passwd:
                print("Contraseña correcta, acceso permitido")
                Found = 'True'
            else:
                print("Acceso denegado: password is incorrect")
                message = b'Acceso denegado: password is incorrect\r\n\r\n'
                self.wfile.write(message)
    fich.close()


def regist(line_decod, dicc_usuarios, dicc, client_infor):#MIRARRARRRA
    """
    Función de registro de usuarios
    """
    sip = line_decod.split()[1]
    direction = sip.split('sip:')[1]
    expiration = int(line_decod.split()[4])
    expires = int(time.time()) + expiration
    dicc_usuarios["address"] = client_infor[0]
    time_now = time.strftime('%Y­%m­%d %H:%M:%S',
                             time.gmtime(time.time()))
    time_now1 = time_now.split('\u00ad')[0] + '-'
    time_now2 = time_now1 + time_now.split('\u00ad')[1] + '-'
    time_now3 = time_now2 + time_now.split('\u00ad')[2]
    dicc_usuarios["expires"] = time_now3 + ' + ' + str(expiration)
    if expiration == 0:
        if direction in dicc:
            del dicc[direction]
    elif '@' in direction:
        dicc[direction] = dicc_usuarios
    for usuario in dicc:
        if int(time.time()) > expires:
            del dicc[direction]


class SIPProxyRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo proxy class
    """

    dicc = {}

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        self.json2registered()
        dicc_usuarios = {}
        client_infor = self.client_address
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            line_decod = line.decode('utf-8')
            print("El cliente nos manda " + line_decod)
            METHOD = line_decod.split(' ')[0].upper()
            METHODS = ['REGISTER', 'INVITE', 'BYE', 'ACK']
            if len(line_decod) >= 2:
                if METHOD  == 'REGISTER':
                    lista = line_decod.split('\r\n')
                    Client = lista[0].split(':')[1]
                    lista0 = lista[0].split(':')[2]
                    Port_Client = lista0.split(' ')[0]
                    NONCE = random.getrandbits(898989898798989898989)
                    # MIRAR EL LOG
                    if len(lista) == 2:
                        mssg = b'SIP/2.0 401 Unauthorized\r\n\r\n'
                        mssg += b'WWW Authenticate: nonce=' + NONCE
                        # Enviamos el mensaje de respuesta al REGISTER sin
                        # Autenticación
                        self.wfile.write(messg)
                        print("Enviamos" + messg)
                        # Escribimos los mensages de envio en el log
                        Event = ' Send to '#mirar la ip y el port de envio
                        Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, mssg)
                    else len(lista) == 3: #MIRAR
                        Passwd_Nonce = lista[2].split('response=')[1]
                        Passwd = Passwd_Nonce - NONCE
                        Check_Password(DATA_PASSWDPATH, Passwd, Client, Found)
                        if Found:
                            messg = b"SIP/2.0 200 OK\r\n\r\n"
                            # Escribimos los mensages de envio en el log
                            Event = ' Send to '#mirar ip y port y cambiar
                            Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, messg)
                    # FALTA MIRAROS BIEN
                    regist(line_decod, dicc_usuarios, self.dicc, client_infor)
                    self.wfile.write(mssg_send)
                    # Escribimos en el log el mensage enviado
                    Event = ' Send to '
                    # CAMBIAR LOS DATOS DEL LOG IP Y PORT
                    Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, mssg_send)
                    #MIRRRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAR
                    self.register2json()
                elif METHOD == 'INVITE':
                elif METHOD == 'ACK':
                elif METHOD == 'BYE':
                elif METHOD not in METHODS:
                    print("Nos ha llegado un método desconocido")
                    mssg_send = b'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    self.wfile.write(message_send)
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, IP_PROXY, PORT_PROXY, mssg_send)
                else:
                    # Respuesta mal formada
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            print("El cliente nos manda " + line_decod)

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

    def register2json(self):
        """
        Registro de usuarios en un fichero json
        """
        fichero_json = json.dumps(self.dicc)
        with open('registered.json', 'w') as fichero_json:
            json.dump(self.dicc, fichero_json, sort_keys=True, indent=4)#MIRRAAAAAR

    def json2registered(self):#MIRARRR Y CAMBIAR TXT
        """
        Comprobar la existencia del fichero json y se actua en función
        de si existe o no
        """
        fichero_json = 'registered.json'
        try:
            self.dicc = json.loads(open(fichero_json).read())
        except:
            self.dicc = {}


if __name__ == "__main__":
    try:
    	CONFIG = int(sys.argv[1])

        # Comprobación de si existe el fichero pasado como parámetro
        if os.path.exists(CONFIG) is False:
        	sys.eit("This name of file doesn´t exist")

		# Saco el contenido del fichero xml
		parser = make_parser()
    	cHandler = XMLHandler_Proxy()
    	parser.setContentHandler(cHandler)
    	parser.parse(open(CONFIG))
		lista = cHandler.get_tags()

        # Meto los valores del xml en variables
        SERVER_NAME = lista[0]['server']['name']
        SERVER_IP = lista[0]['server']['ip']
        SERVER_PORT = lista[0]['server']['puerto']
        DATABASE_PATH = lista[1]['database']['path']
        DATA_PASSWDPATH = lista[1]['database']['passwdpath']]
        PATH_LOG = lista[2]['log']['path']]

	except:
		sys.exit("Usage: python proxy_registrar.py config")
    try:
	    message = 'Server ' + SERVER_NAME + ' listening at port ' 
        message += SERVER_PORT + '...'
	    print(message)
        PORT = int(SERVER_PORT)

        # Meto en el log el mensaje de starting...
        Event = ' Starting...'
        Datos_Log(PATH_LOG, Event, '', '', '')
        serv = socketserver.UDPServer(("", PORT), EchoHandler)
        print("Listening...")
        serv.serve_forever()
    except:
        sys.exit("Usage: Error")
