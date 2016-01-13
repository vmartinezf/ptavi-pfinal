#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Programa Proxy registrar y clase del proxy
"""

import socketserver
import socket
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


def Open_Socket(Path, Ip, Port, Line):
    # Abrimos un socket para reeenviar el mensaje a la
    # direccion que va dirigido
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET,  socket.SO_REUSEADDR, 1)
    my_socket.connect((Ip, int(Port)))
    my_socket.send(Line)
    # Escribimos el mensaje de envio en el archivo de log
    Puerto = str(Port)
    Event = ' Send to '
    Line_decod = Line.decode('utf-8')
    Datos_Log(PATH_LOG, Event, Ip, Puerto, Line_decod)


def register2registered(dicc_client, Client):
    # Función para ver si un usuario está registrado, nos devuelve 0 si el
    # usuario no está registrado con ninguna de las claves, en caso cotrario se
    # devuelven los datos del cliente
    if Client not in dicc_client.keys():
        datos = '0'
    else:
        datos = dicc_client[Client]
    return datos


def Time_Caduced(dicc_client):
    # Función para actualizar el diccionario, elimina cientes que tengan el
    # Expires caducado
    Lista = []
    for Client in dicc_client:
        Expiration = int(dicc_client[Client][4])
        Time_now = int(time.time())
        if Time_now >= Expiration:
            Lista.append(Client)

    # Borramos del diccionario los clientes expirados
    for Usuario in Lista:
        del dicc_client[Usuario]


def Mssg_Error(Path, Ip, Port):
    # Escribimos en el log el mensaje de error
    Event = 'Error'
    Datos_Log(Path, Event, Ip, Port, '')
    sys.exit("Error: No server listening at " + Ip + " Port " + Port + "\r\n")


class SIPProxyRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo proxy class
    """

    dicc_client = {}
    # Variable aleatoria NONCE
    NONCE = random.getrandbits(100)

    def handle(self):

        # Actualizamos el diccionario de clientes por si ha caducado el Espires
        # de algún cliente
        Time_Caduced(self.dicc_client)

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            line_decod = line.decode('utf-8')
            print("Recibimos" + line_decod)
            METHOD = line_decod.split(' ')[0].upper()
            # Métodos permitidos
            METHODS = ['REGISTER', 'INVITE', 'BYE', 'ACK']
            # La IP y el Puerto de quien recibimos el mensaje
            Ip = self.client_address[0]
            Puerto = self.client_address[1]
            # Escribimos mensages de recepción en el fichero de log
            Evento = ' Received from '
            Datos_Log(PATH_LOG, Evento, Ip, Puerto, line_decod)
            if len(line_decod) >= 2:
                if METHOD == 'REGISTER':
                    lista = line_decod.split('\r\n')
                    Client = lista[0].split(':')[1]
                    lista0 = lista[0].split(':')[2]
                    Port_UA = lista0.split(' ')[0]
                    if len(lista) == 4:
                        mssg = 'SIP/2.0 401 Unauthorized\r\n'
                        mssg += 'Via: SIP/2.0/UDP branch=z9hG4bKnashds7\r\n'
                        mssg += 'WWW Authenticate: nonce="' + str(self.NONCE)
                        mssg += '"\r\n\r\n'
                        # Enviamos el mensaje de respuesta al REGISTER sin
                        # Autenticación
                        self.wfile.write(bytes(mssg, 'utf-8'))
                        # Escribimos los mensages de envio en el log
                        Event = ' Send to '
                        Datos_Log(PATH_LOG, Event, Ip, Port_UA, mssg)
                    elif len(lista) == 5:
                        Psswd_Salto_Linea = lista[2].split('response="')[1]
                        Psswd = Psswd_Salto_Linea.split('"')[0]
                        Found = self.CheckPsswd(DATA_PASSWDPATH, Psswd, Client,
                                                Ip, Puerto)
                        if Found == 'True':
                            try:
                                Expires = lista[1].split(' ')[1]
                                if Expires == '0':
                                    del self.dicc_client[Client]
                                    Event = ' Borrando ' + Client
                                    Datos_Log(PATH_LOG, Event, '', '', '')
                                else:
                                    Now = time.time()
                                    Exp = int(Expires)
                                    Time_Sum = float(Exp) + Now
                                    cliente = [Ip, Port_UA, Now, Exp, Time_Sum]
                                    self.dicc_client[Client] = cliente
                                messg = "SIP/2.0 200 OK\r\n\r\n"
                                self.wfile.write(bytes(messg, 'utf-8'))
                                # Escribimos el mensage de envio en el log
                                Event = ' Send to '
                                Datos_Log(PATH_LOG, Event, Ip, Puerto, messg)
                                self.register2txt(DATABASE_PATH, Ip, Client)

                            except:
                                messg = "Expires no es un entero\r\n\r\n"
                                self.wfile.write(bytes(messg, 'utf-8'))
                                # Escribimos el mensage de envio en el log
                                Event = ' Send to '
                                #Datos_Log(PATH_LOG, Event, Ip, Puerto, messg)
                                break

                elif METHOD == 'INVITE':
                    Sip_direccion = line_decod.split(' ')[1]
                    UA = Sip_direccion.split(':')[1]
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Regist = register2registered(self.dicc_client, UA)
                    # En función de si está registrado o no actuamos de
                    # diferente forma
                    if Usuario_Regist == '0':
                        mssg = "SIP/2.0 404 User Not Found\r\n\r\n"
                        # Ecribimos los datos que se envian en el log
                        Event = ' Send to '
                        Datos_Log(PATH_LOG, Event, Ip, Puerto, mssg)
                        self.wfile.write(bytes(mssg, 'utf-8'))
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Regist[0]
                        Port_Regist = Usuario_Regist[1]
                        # Miramos que la conexión sea segura y se envían datos
                        # o se hace sys.exit en función de la conexión
                        self.Conexion_Segura(PATH_LOG, Port_Regist, Ip_Regist,
                                             line)

                elif METHOD == 'ACK':
                    Sip_direccion = line_decod.split(' ')[1]
                    UA = Sip_direccion.split(':')[1]
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Regist = register2registered(self.dicc_client, UA)
                    if Usuario_Regist == '0':
                        mssg = "SIP/2.0 404 User Not Found\r\n\r\n"
                        # Ecribimos los datos que se envian en el log
                        Event = ' Send to '
                        Datos_Log(Path, Event, Ip, Puerto, mssg)
                        self.wfile.write(bytes(mssg, 'utf-8'))
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Regist[0]
                        Port_Regist = int(Usuario_Regist[1])

                        # Abrimos un socket y enviamos
                        Open_Socket(PATH_LOG, Ip_Regist, Port_Regist, line)

                elif METHOD == 'BYE':
                    Sip_direccion = line_decod.split(' ')[1]
                    UA = Sip_direccion.split(':')[1]
                    # Comprobación de si el usuario está registrado o no
                    Usuario_Regist = register2registered(self.dicc_client, UA)
                    if Usuario_Regist == '0':
                        mssg = "SIP/2.0 404 User Not Found\r\n\r\n"
                        # Ecribimos los datos que se envian en el log
                        Event = ' Send to '
                        Datos_Log(PATH_LOG, Event, Ip, Puerto, mssg)
                        self.wfile.write(bytes(mssg, 'utf-8'))
                    else:
                        # Datos de la ip y puerto del usuario registrado
                        Ip_Regist = Usuario_Regist[0]
                        Port_Regist = int(Usuario_Regist[1])
                        # Miramos que la conexión sea segura y se envían datos
                        # o se hace sys.exit en función de la conexión
                        self.Conexion_Segura(PATH_LOG, Port_Regist, Ip_Regist,
                                             line)

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

    def CheckPsswd(self, Path, Passwd, User_agent, Ip, Puerto):
        Found = 'False'
        fich = open(Path, 'r')
        lines = fich.readlines()
        for line in range(len(lines)):
            User = lines[line].split(' ')[1]
            Password = lines[line].split(' ')[3]
            Nonce = str(self.NONCE)
            m = hashlib.md5()
            m.update(bytes(Password + Nonce, 'utf-8'))
            RESPONSE = m.hexdigest()
            if User == User_agent:
                if RESPONSE == Passwd:
                    Found = 'True'
                else:
                    message = 'Acceso denegado: password is incorrect\r\n\r\n'
                    self.wfile.write(bytes(message, 'utf-8'))
                    # Escribimos en el log el mensaje acceso denegado
                    Event = ' Send to '
                    Datos_Log(PATH_LOG, Event, Ip, Puerto, message)
        fich.close()
        return Found

    def register2txt(self, Path, ip, direction):
        """
        Función de registro de usuarios en el archivo database.txt
        """
        fich = open(Path, "a")
        for Client in self.dicc_client:
            Ip = self.dicc_client[Client][0]
            Port = self.dicc_client[Client][1]
            Fecha_Registro = self.dicc_client[Client][2]
            Expiration = self.dicc_client[Client][3]
            Line = Client + "\t" + Ip + "\t" + str(Port) + "\t"
            Line += str(Fecha_Registro) + "\t\t" + str(Expiration) + "\r\n"
            fich.write(Line)
        fich.close()

    def Conexion_Segura(self, Path, Port, Ip, Line):
        Puerto = str(Port)
        try:
            # Abrimos un socket para reeenviar el mensaje a la
            # direccion que va dirigido
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET,  socket.SO_REUSEADDR, 1)
            my_socket.connect((Ip, int(Port)))
            my_socket.send(Line)
            # Escribimos el mensaje de envio en el archivo de log
            Puerto = str(Port)
            Event = ' Send to '
            Line_decod = Line.decode('utf-8')
            Datos_Log(PATH_LOG, Event, Ip, Puerto, Line_decod)
        except socket.error:
            Mssg_Error(Path, Ip, Puerto)
        try:
            data = my_socket.recv(1024)
            data_decod = data.decode('utf-8')
        except socket.error:
            Mssg_Error(Path, Ip, Puerto)
        try:
            # Escribimos mensages de recepción en el fichero de log
            Evento = ' Received from '
            Datos_Log(PATH_LOG, Evento, Ip, Puerto, data_decod)
            print("Recibimos" + data_decod)
            # Si hay un server escuchando seguimos y enviamos
            self.wfile.write(bytes(data_decod, 'utf-8'))
            # Escribimos en el log el mensage enviado
            Event = ' Send to '
            Datos_Log(PATH_LOG, Event, Ip, Puerto, data_decod)
        except:
            Mssg_Error(Path, Ip, Puerto)


if __name__ == "__main__":
    try:
        CONFIG = sys.argv[1]
        if len(sys.argv) != 2:
            sys.exit("Usage: python proxy_registrar.py config")
        # Comprobación de si existe el fichero pasado como parámetro
        if not os.path.exists(CONFIG):
            sys.exit("This name of file doesn´t exist")

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
        DATA_PASSWDPATH = lista[1]['database']['passwdpath']
        PATH_LOG = lista[2]['log']['path']

        fich = open(DATABASE_PATH, "a")
        Linea = "Usuario\tIP\tPuerto\t" + "Fecha de Registro\t"
        Linea += "Tiempo de expiracion\r\n"
        fich.write(Linea)
        fich.close()

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
        serv.serve_forever()
    except:
        sys.exit("Usage: Error")
