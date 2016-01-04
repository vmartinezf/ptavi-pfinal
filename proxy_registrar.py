#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Programa Proxy registrar y clase del proxy
"""

import socketserver
import sys
import json
import time
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib


class XMLHandler(ContentHandler):
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
        

if __name__ == "__main__":
    try:
    	CONFIG = int(sys.argv[1])

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

        # Meto los valores del xml en variables
        SERVER_NAME = lista[0]['server']['name']
        SERVER_IP = lista[0]['server']['ip']
        SERVER_PORT = lista[0]['server']['puerto']
        DATABASE_PATH = lista[1]['database']['path']
        DATABASE_PASSWDPATH = lista[1]['database']['passwdpath']]
        PATHLOG = lista[2]['log']['path']]

	except:
		sys.exit("Usage: python proxy_registrar.py config")
	message = 'Server ' + USER + ' listening at port ' + PORT + '...'
	print(message)
