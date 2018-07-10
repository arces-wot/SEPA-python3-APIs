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
        tablify(json.dumps(jdiff))
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
