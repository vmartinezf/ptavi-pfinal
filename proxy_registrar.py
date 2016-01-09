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


def Data_Regist(line_decod, NONCE, Port_UA, Client):
    lista = line_decod.split('\r\n')
    Client = lista[0].split(':')[1]
    lista0 = lista[0].split(':')[2]
    Port_UA = lista0.split(' ')[0]
    NONCE = random.getrandbits(898989898798989898989)


def Open_Socket(Path, Ip, Port, Line):
    # Abrimos un socket para reeenviar el mensaje a la
    # direccion que va dirigido
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET,  socket.SO_REUSEADDR, 1)
    my_socket.connect((Ip, Port))
    my_socket.send(Line)
    # Escribimos el mensaje de envio en el archivo de log
    Puerto = str(Port)
    Event = ' Send to '
    Datos_Log(PATH_LOG, Event, Ip, Puerto, Line)


def Conexion_Segura(Path, Port, Ip, data_decod):
    Puerto = str(Port)
    try:
        data = my_socket.recv(1024)
        data_decod = data.decode('utf-8')
        # Escribimos mensages de recepción en el fichero de log
        Evento = ' Received from '
        Datos_Log(PATH_LOG, Evento, Ip, Puerto, data_decod)
    except:
        # Escribimos en el log el mensaje de error
        Event = 'Error'
        Datos_Log(Path, Event, Ip, Puerto, '')
        Error = ip + "Port" + Puerto + '\r\n'
        sys.exit("Error: No server listening at " + Error)


def User_Not_Found(Path, Puerto, Ip, messg):
    messg = "SIP/2.0 404 User Not Found\r\n\r\n"
    print("Enviamos " + messg)
    # Ecribimos los datos que se envian en el log
    Event = ' Send to '
    Datos_Log(Path, Event, Ip, Puerto, messg)


    def register2txt(Path, dicc_client):
        """
        Función de registro de usuarios en el archivo database.txt
        """
        fich = open(Path, "w")
        Linea = "Usuario\tIP\tPuerto\t" + "Fecha de Registro\t" 
        Linea += "Tiempo de expiracion\r\n"
        fich.write(Linea)
        for Client in dicc_client:
            Ip = dicc_client[Client][0]
            Port = dicc_client[Client][1]
            Fecha_Registro = dic_clientes[Client][2]
            Expiration = dic_clientes[Client][3]
            Line = Client + "\t" + Ip + "\t" + str(Port) + "\t"
            Line += str(Fecha_Registro) + "\t\t" + str(Expiration) + "\r\n"
            fich.write(Line)
        fich.close()


    def register2registered(dicc_client, Client):
    """
    Función para ver si un usuario está registrado, nos devuelve 0 si el
    usuario no está registrado con ninguna de las claves, en caso cotrario se
    devuelven los datos del cliente
    """
    if Client not in dicc_client.keys():
        datos = '0'
    else
        datos dicc_client[Client]
    return datos


    def Time_Caduced(dicc_client):
    """
    Función para actualizar el diccionario, elimina cientes que tengan el
    Expires caducado
    """
    for Client in dicc_client:
        Expiration = int(dicc_client[Client][3]) 
        Time_now = int(time.time()) 
        if Time_now >= Expiration:
            print("Borramos el cliente: ", Client)
            del dicc_client[Client]


class SIPProxyRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo proxy class
    """

    dicc_client = {}

    def handle(self):
        # Comprobación de que esté creado el archivo txt
        self.txt2registered()

        # Actualizamos el diccionario de clientes por si ha caducado el Espires
        # de algún cliente
        Time_Caduced(dicc_client)

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            line_decod = line.decode('utf-8')
            print("El cliente nos manda " + line_decod)
            METHOD = line_decod.split(' ')[0].upper()
            # Métodos permitidos
            METHODS = ['REGISTER', 'INVITE', 'BYE', 'ACK']
            # La IP y el Puerto de quien recibimos el mensaje
            Ip = self.client_addres[0]
            Puerto = self.client_addres[1]
            # Escribimos mensages de recepción en el fichero de log
            Evento = ' Received from '
            Datos_Log(PATH_LOG, Evento, Ip, Puerto, line_decod)
            if len(line_decod) >= 2:
                if METHOD  == 'REGISTER':
                    Data_Regist(line_decod, NONCE, Port_UA, Client)
                    if len(lista) == 2:
                        # Comprobación de si el usuario está registrado o no
                        User_Regist = register2registered(dicc_client, Client)
                        # En función de si está registrado o no actuamos de
                        # diferente forma
                        if User_Regist == 0:
                            User_Not_Found(PATH_LOG, Puerto, Ip, mssg)
                        else:
                            mssg = 'SIP/2.0 401 Unauthorized\r\n\r\n'
                            mssg += 'WWW Authenticate: nonce=' + NONCE
                        # Enviamos el mensaje de respuesta al REGISTER sin
                        # Autenticación
                        self.wfile.write(bytes(mssg, 'utf-8'))
                        print("Enviamos" + messg)
                        # Escribimos los mensages de envio en el log
                        Event = ' Send to '
                        Datos_Log(PATH_LOG, Event, Ip, Port_UA, mssg)
                    elif len(lista) == 3: #MIRAR
                        Passwd_Nonce = lista[2].split('response=')[1]
                        Passwd = Passwd_Nonce - NONCE
                        self.CheckPsswd(DATA_PASSWDPATH, Passwd, Client, Found,
                                        Ip, Puerto)
                        if Found:
                            try:
                                Expires = lista[2].split(' ')[1]
                                if Expires == '0':
                                    Event = ' Borrando ' + Client
                                    Datos_Log(PATH_LOG, Event, '', '', '')
                                else:
                                    
                            except:
                                Error_Entero = "No es un entero"
                                self.wfile.write(Error_Entero)
                                print(Error_Entero)
                                break
                            messg = b"SIP/2.0 200 OK\r\n\r\n"
                            # Escribimos los mensages de envio en el log
                            Event = ' Send to '#mirar ip y port y cambiar
                            Datos_Log(PATH_LOG, Event, IP_UA, Port_UA, messg)

                elif METHOD == 'INVITE':
                    Sip_direccion = line_decod.split(' ')[1]
                    dir_UA = Sip_direccion.split(':')[1]
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Registro = register2registered(dicc_client, dir_UA)
                    # En función de si está registrado o no actuamos de
                    # diferente forma
                    if Usuario_Registro == 0:
                        User_Not_Found(PATH_LOG, Puerto, Ip, messg)
                        self.wfile.write(bytes(messg, 'utf-8'))
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Registro[0]
                        Port_Regist = int(Usuario_Registro[1])

                        # Abrimos un socket y enviamos
                        Open_Socket(PATH_LOG, Ip_Regist, Port_Regist, line)
                        # Miramos que la conexión sea segura y se envían datos
                        # o se hace sys.exit en función de la conexión
                        Conexion_Segura(PATH_LOG, Port_Regist, Ip_Regist, data)
                        # Si hay un server escuchando seguimos y enviamos
                        self.wfile.write(bytes(data, 'utf-8'))
                        # Escribimos en el log el mensage enviado
                        Event = ' Send to '
                        Datos_Log(PATH_LOG, Event, Ip, Puerto, data)

                elif METHOD == 'ACK':
                    Sip_direccion = line_decod.split(' ')[1]
                    dir_UA = Sip_direccion.split(':')[1] 
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Registro = register2registered(dicc_client, dir_UA)
                    if Usuario_Registro == 0:
                        User_Not_Found(PATH_LOG, Puerto, Ip, messg)
                        self.wfile.write(bytes(messg, 'utf-8'))
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Registro[0]
                        Port_Regist = int(Usuario_Registro[1])

                        # Abrimos un socket y enviamos
                        Open_Socket(PATH_LOG, Ip_Regist, Port_Regist, line)

                elif METHOD == 'BYE':
                    Sip_direccion = line_decod.split(' ')[1]
                    dir_UA = Sip_direccion.split(':')[1]
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Registro = register2registered(dicc_client, dir_UA)
                    if Usuario_Registro == 0:
                        User_Not_Found(PATH_LOG, Puerto, Ip, messg)
                        self.wfile.write(bytes(messg, 'utf-8')) 
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Registro[0]
                        Port_Regist = int(Usuario_Registro[1])
                        
                        # Abrimos un socket y enviamos
                        Open_Socket(PATH_LOG, Ip_Regist, Port_Regist, line)
                        # Miramos que la conexión sea segura y se envían datos
                        # o se hace sys.exit en función de la conexión
                        Conexion_Segura(PATH_LOG, Port_Regist, Ip_Regist, data)
                        # Si hay un server escuchando seguimos y enviamos
                        self.wfile.write(bytes(data, 'utf-8'))
                        # Escribimos en el log el mensage enviado
                        Event = ' Send to '
                        Datos_Log(PATH_LOG, Event, Ip, Puerto, data)
                    
                elif METHOD not in METHODS:
                    mssg_send = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    self.wfile.write(bytes(mssg_send, 'utf-8'))
                    # Escribimos en el log el mensaje de envío 405
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, Ip, Puerto, mssg_send)
                else:
                    # Respuesta mal formada
                    mssg_send = 'SIP/2.0 400 Bad Request\r\n\r\n'
                    self.wfile.write(bytes(mssg_send, 'utf-8'))
                    # Escribimos en el log el mensaje de envío 405
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, Ip, Puerto, mssg_send)

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

            
    def CheckPsswd(self, Path, Passwd, User_agent, Found, Ip, Puerto):
        Found = 'False'
        fich = open(Path, 'r')
        lines = fich.readlines()
        for line in range(len(lines)):
            User = lines[line].split(' ')[1]
            Password = lines[line].split(' ')[4]
            if User == User_agent:
                if Password == Passwd:
                    Found = 'True'
                else:
                    message = b'Acceso denegado: password is incorrect\r\n\r\n'
                    self.wfile.write(message)
                    # Escribimos en el log el mensaje acceso denegado
                    Event = ' Send to 
                    Datos_Log(PATH_LOG, Event, Ip, Puerto, message)
        fich.close()


    def txt2registered(self):
        """
        Comprobar la existencia del fichero json y se actua en función
        de si existe o no
        """
        fichero_txt = DATABASE_PATH 
        try:
            self.dicc_client = txt.loads(open(DATABASE_PATH).read())
        except:
            self.dicc_client = {}


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
