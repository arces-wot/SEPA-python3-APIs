#!/usr/bin/python3

# local requirements
import KP
import time
import uuid
from Exceptions import *

class Handler:
    def __init__(self):
        pass
        
    def handle(self):
        print("HANDLER")


idd = str(uuid.uuid4())
print(idd)
k = KP.LowLevelKP("localhost", "/sparql", "/oauth/register", "/oauth/token", 8000, 8443, 9000, 9443, False, idd)
# subid = k.subscribe("SELECT ?s WHERE { ?s ?p ?o }", "alias", Handler())
# for x in range(1,4):
#     print(".")
#     time.sleep(1)
# k.unsubscribe(subid)
# while True:
#     print(".",)
#     time.sleep(2)

# while True:
#     try:
#         r,s = k.query("SELECT ?s WHERE { ?s ?p ?o }")
#         print(r)
#         print(s)    
#         time.sleep(40)
#     except TokenExpiredException:
#         print("token scaduto, riprovo")    


"""PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
PREFIX ns: <http://ns#> . 
INSERT DATA { 
<http://ns#f2c57e34-40d1-46cb-8ea5-f1cbb9c3b671> rdf:type ns:Rect . 
<http://ns#f2c57e34-40d1-46cb-8ea5-f1cbb9c3b671> ns:hasWidth "1" . 
<http://ns#f2c57e34-40d1-46cb-8ea5-f1cbb9c3b671> ns:hasHeight "1" . 
<http://ns#f2c57e34-40d1-46cb-8ea5-f1cbb9c3b671> ns:startsAtX "1" . 
<http://ns#f2c57e34-40d1-46cb-8ea5-f1cbb9c3b671> ns:startsAtY "1" }"""

print("================================================") 
print(k.update('DELETE DATA { <http://sonoIo#oppureNo> <http://nonLoSo> "xxx" }'))
print("================================================") 
print(k.update('DELETE DATA { <http://sonoIo#oppureNo> <http://nonLoSo> "xxx" }'))
print("================================================") 
# r,s = k.query("SELECT ?s WHERE { ?s ?p ?o }")
# print(r)
# print(s)
# print("================================================") 
# r, s = k.update('DELETE DATA { <http://sonoIo#oppureNo> <http://nonLoSo> "xxx" }')
# print(r)
# print(s)
