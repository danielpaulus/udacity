# -*- coding: utf-8 -*-
"""
Create a dataset from SUMO .net.xml files
"""
from lxml import etree
from io import StringIO, BytesIO
import pandas as pd
import numpy as np


list1= []

xml ="/home/ganjalf/sumo/TAPASCologne-0.24.0/cologne2.net.xml"
tree = etree.parse(xml)
root = tree.getroot()
print "imported filed, found root element {}".format(root.tag)
for child in root:
    if child.tag == "junction"    :
        print(child.tag)
        list1.append([1,2,3])
        for child in child:         
         print("\t"+child.tag)
         break
    
df = pd.DataFrame(list1, columns=('lib', 'qty1', 'qty2'))
print df