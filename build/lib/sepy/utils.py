#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
#  
#  Copyright 2018 Francesco Antoniazzi <francesco.antoniazzi@unibo.it>
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
import logging
import os
from .tablaze import tablify
from .YSparqlObject import YSparqlObject

logger = logging.getLogger("sepaLogger")

def cfr_bindings(bA,bB,ignorance):
    """
    bA is a list of bindings
    bB is another list of bindings
    ignorance is a list of keys which you want to ignore in the bindings
    returns True if bindings are equal, False otherwise
    """
    for key in bA:
        if ((not (key in bB)) or ((bA[key]["type"] != bB[key]["type"]) or 
            ((not (key in ignorance)) and (bA[key]["value"] != bB[key]["value"])))):
            return False
    return True
    
def diff_JsonQuery(jA,jB,ignore_val=[],show_diff=False,log_message=""):
    """
    Compares outputs of query json jA towards jB. You can ignore bindings values in 'ignore_val'.
    When 'show_diff' is true, tablaze.py is called for nicer visualization of differences.
    'log_message' can be used for verbose notification.
    Returns True or False as comparison result.
    """
    result = True
    diff = []
    for bindingA in jA["results"]["bindings"]:
        eq_binding = False
        for bindingB in jB["results"]["bindings"]:
            eq_binding = cfr_bindings(bindingA,bindingB,ignore_val)
            if eq_binding:
                break
        if not eq_binding:
            diff.append(bindingA)
            result = False
    if show_diff and len(diff)>0: 
        jdiff=json.loads('{}')
        jdiff["head"]={"vars": jA["head"]["vars"]}
        jdiff["results"]={"bindings": diff}
        logger.info("{} Differences".format(log_message))
        tablify(jdiff)
    return result

def compare_queries(i_jA,i_jB,show_diff=False,ignore_val=[]):
    """
    This function compares two json outputs of a SPARQL query.
    jA, jB params are the two json objects containing the results of the query.
    They may also be paths to json files.
    show_diff param, usually false, when set to true will show the entries that
    A has, but not B;
    B has, but not A.
    A boolean is returned, to notify whether jA==jB or not.
    You can ignore the binding value by specifying its name in the ignore_val list. 
    Ignoring the value means that the binding must be there, but that you don't care about its
    actual value.
    """
    # Dealing with paths vs json objects as arguments
    if isinstance(i_jA,str) and os.path.isfile(i_jA):
        with open(i_jA,"r") as fA:
            jA = json.load(fA)
    else:
        jA = i_jA
    if isinstance(i_jB,str) and os.path.isfile(str(i_jB)):
        with open(i_jB,"r") as fB:
            jB = json.load(fB)
    else:
        jB = i_jB
        
    # Checking if every variable in jA is also present in jB and vice versa
    setVarA = set(jA["head"]["vars"])
    setVarB = set(jB["head"]["vars"])
    if setVarA != setVarB:
        for item in (setVarA-setVarB):
            logging.error("A->B Variable '{}'  not found!".format(item))
        for item in (setVarB-setVarA):
            logging.error("B->A Variable '{}'  not found!".format(item))
        return False
            
    # A->B
    # Check if every binding in A exists also in B
    result = diff_JsonQuery(jA,jB,show_diff=show_diff,ignore_val=ignore_val,log_message="A->B")
    # B->A
    result = result and diff_JsonQuery(jB,jA,show_diff=show_diff,ignore_val=ignore_val,log_message="B->A")
    return result
    
def notify_result(name,result):
    """
    This function just logs a result in the form
    {name} - {result}
    where name is a string, and result a boolean.
    Returns result (True or False) to the caller.
    """
    logger.setLevel(logging.INFO)
    if result:
        logger.info("{} - {}".format(name,result))
    else:
        logger.error("{} - {}".format(name,result))
    return result
    
def query_CompareUpdate(graph,
                        query_path,
                        fBindings,
                        reset,
                        update_path,
                        log_message="",
                        replace={},
                        ignore=[],
                        prefixes=""):
    """
    If reset is true, we perform the query available into 'query_path' to 'graph' with the
    forced bindings in 'fBindings'.
    The sparql obtained is elaborated replacing keys with indexes available in 'replace'.
    We redirect the output of the query towards 'update_path'.
    
    If reset is false, we make the substitution and the query. Then we compare the 
    query output to the file into 'update_path', ignoring the actual value of the 
    bindings in 'ignore' and outputting the message in 'log_message'.
    Returns True or False according to check result.
    """
    sparql,fB = YSparqlObject(query_path,external_prefixes=prefixes).getData(fB_values=fBindings)
    for key in replace:
        sparql = sparql.replace(key,replace[key])
    if reset:
        logging.warning("Rebuilding "+update_path)
        return bool(graph.query(sparql,fB=fB,destination=update_path))
    else:
        return query_FileCompare(   graph,
                                    sparql=sparql,
                                    fB=fB,
                                    message=log_message,
                                    fileAddress=update_path,
                                    ignore_val=ignore)


def query_FileCompare(  graph,
                        sparql="select * where {?a ?b ?c}",
                        fB={},
                        message="query_all",
                        fileAddress="",
                        show_diff=False,
                        ignore_val=[]):
    """
    This function performs a 'sparql' query to 'graph', then calls for comparison 
    with the content of 'fileAddress'.
    You can ignore differences in bindings into the 'ignore_val' parameter.
    Then, it notifies the result using the tag contained in 'message' parameter.
    The default behaviour is SELECT * WHERE {?a ?b ?c}.
    'show_diff' parameter will call tablaze.py to print differences to stdout.
    Returns True or False according to check result.
    """
    with open(fileAddress,"r") as result:
        template = json.load(result)
    result = graph.query(sparql,fB)
    message = "{} ({} bindings)".format(message,len(result["results"]["bindings"]))
    
    return notify_result(   message,
                            compare_queries(template,
                                            result,
                                            show_diff=show_diff,
                                            ignore_val=ignore_val))

def uriFormat(uri):
    """
    TODO - Still naive uri detection
    """
    return "<"+uri+">" if "//" in uri else uri
