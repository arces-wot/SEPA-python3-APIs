#!/usr/bin python3
# -*- coding: utf-8 -*-
#
#  test.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi1991@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import json

class JSAPObject:
    def __init__(self,path_to_jsap_file):
        with open(path_to_jsap_file) as jsap:
            self.parsed_jsap = json.load(jsap)
        
        for key in self.parsed_jsap.keys():
            print(key)
            
    @property
    def host(self):
        return self.parsed_jsap["host"]
        
    def explore(self,subObject_tag,path):
        item = self.parsed_jsap[subObject_tag]
        for tag in path:
            item = item[tag]
        return item
        
    def sparql11protocol(self,path=[]):
        return self.explore("sparql11protocol",path)
        
    def sparql11seprotocol(self,path=[]):
        return self.explore("sparql11seprotocol",path)
    
    def _url_builder(self,protocol,ip_address,port,path):
        return "{}://{}:{}{}".format(protocol,ip_address,port,path)
        
    def oauth(self,path=[]):
        return self.explore("oauth",path)
        
    @property
    def registration_url(self):
        return self.oauth(["register"])
        
    @property
    def tokenRequest_url(self):
        return self.oauth(["tokenRequest"])
    
    @property
    def query_url(self):
        return self._url_builder(self.sparql11protocol(["protocol"]),
            self.host, self.sparql11protocol(["port"]),
            self.sparql11protocol(["query","path"]))
            
    @property
    def update_url(self):
        return self._url_builder(self.sparql11protocol(["protocol"]),
            self.host, self.sparql11protocol(["port"]),
            self.sparql11protocol(["update","path"]))
            
    @property
    def subscribe_url(self):
        use_protocol = self.sparql11seprotocol(["protocol"])
        return self._url_builder(use_protocol,
            self.host, self.sparql11seprotocol(["availableProtocols", use_protocol,"port"]),
            self.sparql11seprotocol(["availableProtocols", use_protocol, "path"]))
    
    def namespace(self,prefix=None):
        if prefix is None:
            return self.explore("namespaces",[])
        return self.explore("namespaces",[prefix])
        
    def getUpdate(self,identifier):
        pass
        
    def getQuery():
        pass

def main(args):
    js=JSAPObject("./example.jsap")
    print(js.host)
    print(js.sparql11protocol())
    print(js.sparql11protocol(path=["protocol"]))
    print(js.sparql11protocol(path=["query"]))
    print(js.sparql11protocol(path=["query","method"]))
    print(js.query_url)
    print(js.update_url)
    print(js.subscribe_url)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
