# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 20:54:45 2016

@author: ganjalf
"""
import numpy as np
import json
from collections import deque

def createDocumentAndResetValues(document_contents, target_file):    
    documents.add(document_contents)
    
    


path= "C:\WestburyLab.NonRedundant.UsenetCorpus\WestburyLab.NonRedundant.UsenetCorpus.txt"
wpath="C:\WestburyLab.NonRedundant.UsenetCorpus\dump.txt"
r = open(path, "r")
w = open(wpath, "w")

separator = "---END.OF.DOCUMENT---\n"
documents=np.array([])
documents_to_read=8000


skip_documents=5000
chance_to_take_document=.5

documents_already_read=0

document_contents=""

while documents_already_read<documents_to_read:
    
     line = r.readline()
     
     
     if line==separator:
        if skip_documents==0:             
          rnd= np.random.random_sample()
          if rnd>chance_to_take_document:
             createDocumentAndResetValues(document_contents,w)             
             documents_already_read+=1
             print "docs read:{}".format(documents_already_read)
          document_contents=""
          continue
        else:
            document_contents=""
            skip_documents-=1
            continue
             
     document_contents+=line
             
         
         
     json.dump(list(documents), w, sort_keys = True, indent = 4,
     ensure_ascii=False)   
    
r.close()        
w.close()