#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Programa Proxy registrar
"""

import socketserver
import sys
import json
import time
import os.path


if __name__ == "__main__":
    try:
    	CONFIG = int(sys.argv[1])
	except:
		sys.exit("Usage: python proxy_registrar.py config")
	message = 'Server ' + USER + ' listening at port ' + PORT + '...'
	print(message)
