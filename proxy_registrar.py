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
            IP_UA = '127.0.0.1'
            if len(line_decod) >= 2:
                if METHOD  == 'REGISTER':
                    lista = line_decod.split('\r\n')
                    Client = lista[0].split(':')[1]
                    lista0 = lista[0].split(':')[2]
                    Port_UA = lista0.split(' ')[0]
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
                        Event = ' Send to '
                        Datos_Log(PATH_LOG, Event, IP_UA, Port_UA, mssg)
                    else len(lista) == 3: #MIRAR
                        Passwd_Nonce = lista[2].split('response=')[1]
                        Passwd = Passwd_Nonce - NONCE
                        self.CheckPsswd(DATA_PASSWDPATH, Passwd, Client, Found)
                        if Found:
                            try:
                                Expires = lista[2].split(' ')[1]
                                if Expires == '0':
                                    Event = ' Borrando ' + Client
                                    Datos_Log(PATH_LOG, Event, '', '', '')
                            except:
                                Error_Entero = "No es un entero"
                                self.wfile.write(Error_Entero)
                                print(Error_Entero)
                                break
                            messg = b"SIP/2.0 200 OK\r\n\r\n"
                            # Escribimos los mensages de envio en el log
                            Event = ' Send to '#mirar ip y port y cambiar
                            Datos_Log(PATH_LOG, Event, IP_UA, Port_UA, messg)
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
                    # Escribimos en el log el mensaje de envío 405
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, IP_UA, PORT_PROXY, mssg_send)
                else:
                    # Respuesta mal formada
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            print("El cliente nos manda " + line_decod)

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

            
    def CheckPsswd(self, Path, Passwd, User_agent, Found):
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


    def register2txt(self):
        """
        Función de registro de usuarios en el archivo database.txt
        """
        fich = open(DATABASE_PATH, "w")
        Linea = "Usuario\tIP\tPuerto\t" + "Fecha de Registro\t" 
        Linea += "Tiempo de expiracion\r\n"
        fich.write(Linea)
        for Client in self.dicc_client:
            Ip = self.dicc_client[Client][0]
            Port = self.dicc_client[Client][1]
            Fecha_Registro = self.dic_clientes[Client][2]
            Expiration = self.dic_clientes[Client][3]
            Line = Client + "\t" + Ip + "\t" + str(Port) + "\t"
            Line += str(Fecha_Registro) + "\t\t" + str(Expiration) + "\r\n"
            fich.write(Line)
        fich.close()


    def register2registered(self, client):
    """
    Función para ver si un usuario está registrado, nos devuelve 0 si el
    usuario no está registrado con ninguna de las claves, en caso cotrario se
    devuelven los datos del cliente
    """
    if Client not in self.dicc_client.keys():
        datos = '0'
    else
        datos self.dicc_client[Client]
    return datos


    def txt2registered(self):
        """
        Comprobar la existencia del fichero json y se actua en función
        de si existe o no
        """
        fichero_txt = DATABASE_PATH 
        try:
            self.dicc = txt.loads(open(DATABASE_PATH).read())
        except:
            self.dicc = {}


    def Time_Caduced(self):
    """
    Función para actualizar el diccionario, elimina cientes que tengan el
    Expires caducado
    """
    for Client in self.dicc_client:
        # Imprimimos el diccionario de clientes
        print(self.dicc_client)
        Expiration = int(self.dicc_client[Client][3]) 
        Time_now = int(time.time()) 
        if Time_now >= Expiration:
            print("Borramos el cliente: ", Client)
            del self.dicc_client[Client]


if __name__ == "__main__":
    try:
    	CONFIG = int(sys.argv[1])
        if len(sys.argv) != 2:
            sys.exit("Usage: python proxy_registrar.py config")
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
        IP = '127.0.0.1'
        serv = socketserver.UDPServer((IP, PORT), SIPProxyRegisterHandler)
        print("Listening...")
        serv.serve_forever()
    except:
        sys.exit("Usage: Error")
