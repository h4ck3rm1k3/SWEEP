#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Application ...
"""
#    Copyright (C) 2017 by
#    Emmanuel Desmontils <emmanuel.desmontils@univ-nantes.fr>
#    Patricia Serrano-Alvarado <patricia.serrano-alvarado@univ-nantes.fr>
#    All rights reserved.
#    GPL v 2.0 license.

# import sys
import socket
from threading import *

# import multiprocessing as mp

import datetime as dt
import iso8601 # https://pypi.python.org/pypi/iso8601/     http://pyiso8601.readthedocs.io/en/latest/
import time

# import re
import argparse

from tools.tools import *
from tools.Endpoint import *

from lxml import etree  # http://lxml.de/index.html#documentation
# from lib.bgp import *

# from io import StringIO


#==================================================

class Query(object):
	"""docstring for Query"""
	def __init__(self, q, time):
		super(Query, self).__init__()
		self.q = q
		self.time = time

#==================================================	

def queryThread(conn,sp, doPR, query,ref):
	duration = query.time - ref
	print(duration.total_seconds())
	time.sleep(duration.total_seconds())
	print('Query:',query.q)
	(ip,port) = conn.getsockname()
	try:
		if doPR:
			print("Envoie test:")
			mess = '<query time="'+date2str(query.time)+'" client="'+str(ip)+'"><![CDATA['+query.q+']]></query>'
			conn.send(mess.encode('utf8'))
		print(sp.query(query.q))
	except Exception as e:
		print('Exception',e)

#==================================================

def play(file):
    print('Traitement de %s' % file)
    parser = etree.XMLParser(recover=True, strip_cdata=True)
    tree = etree.parse(file, parser)
    #---
    dtd = etree.DTD('http://documents.ls2n.fr/be4dbp/log.dtd')
    assert dtd.validate(tree), '%s non valide au chargement : %s' % (
        file, dtd.error_log.filter_from_errors()[0])
    #---
    #print('DTD valide !')
    nbe = 0
    date = 'no-date'
    ip = 'ip-'+tree.getroot().get('ip').split('-')[0]
    #print('ranking building')
    for entry in tree.getroot():
        nbe += 1
        #print('(%d) new entry to add' % nbe)
        if nbe == 1:
        	date_ref = fromISO(entry.get('datetime'))
        date = fromISO(entry.get('datetime'))
        ide = entry.get('logline')
        valid = entry.get("valid")
        if valid is not None :
        	if valid == 'TPF' :
        		query = entry.find('request').text
        		t = Thread(target=queryThread ,args=(s,sp,args.valid,Query(query,date),date_ref))
        		t.start()

#==================================================
#==================================================
#==================================================

parser = argparse.ArgumentParser(description='Linked Data Query simulator (for a modified TPF server)')
parser.add_argument('files', metavar='file', nargs='+', help='files to analyse')
parser.add_argument("--port", type=int, default=5002, dest="port", help="Port (5002 by default)")
parser.add_argument("--host", default='127.0.0.1', dest="host", help="Host ('127.0.0.1' by default)")
parser.add_argument("-s","--server", default='http://localhost:5000/lift', dest="tpfServer", help="TPF Server ('http://localhost:5000/lift' by default)")
parser.add_argument("-c", "--client", default='/Users/desmontils-e/Programmation/TPF/Client.js-master/bin/ldf-client', dest="tpfClient", help="TPF Client ('...' by default)")
parser.add_argument("-t", "--time", default='', dest="now", help="Time reference (now by default)")
parser.add_argument("-v", "--valid", default='', dest="valid", action="store_true", help="Do precision/recall")
# parser.add_argument("-to", "--timeout", type=float, default=0, dest="timeout",
#                     help="TPF server Time Out in minutes (%d by default). If '-to 0', the timeout is the gap." % 0)

args = parser.parse_args()

# http://localhost:5000/lift : serveur TPF LIFT (exemple du papier)
# http://localhost:5001/dbpedia_3_9 server dppedia si : ssh -L 5001:172.16.9.3:5001 desmontils@172.16.9.15
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.host, args.port))
sp = TPFEP(service = args.tpfServer ) #'http://localhost:5000/lift') 
sp.setEngine(args.tpfClient) #'/Users/desmontils-e/Programmation/TPF/Client.js-master/bin/ldf-client')

if args.now =='':
	now = now()
else: now = dt.datetime(args.now)

file_set = args.files
for file in file_set:
    if existFile(file):
    	play(file)
