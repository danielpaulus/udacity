# -*- coding: utf-8 -*-
"""
Create a dataset from SUMO .net.xml files
This code is very slow, I guess it is because of the rather large amount 
of xpath queries I am using. But the code is quite elegant this way and 
it only needs to run once, so optimizing it would be a waste of time.
"""
from lxml import etree
import numpy as np
import csv
from multiprocessing.dummy import Pool as ThreadPool

#Determine if a given Lane is part of a roundabout
def isRoundAbout (r_id):    
    roundabout=None
    roundabout= findRoundAboundTag(tree,id=r_id)
    return len(roundabout)!=0


def processIncomingLanes(lane_ids_as_string, row, junction):
    processLanes (lane_ids_as_string, row, junction, True)

def processInternalLanes(lane_ids_as_string, row, junction):
    processLanes (lane_ids_as_string, row, junction, False)

def appendEmptyValuesToRow(row):
    row.append(None)            
    row.append(0)
    row.append(0)
    row.append(0)
    row.append(0)
    row.append(None)
    row.append(0)
    row.append(0)

#retrieve statistics for a junction including lanes and traffic lights,     
def processLanes (lane_ids_as_string, row, junction,isIncomingLane):
    #append an empty row if there are no lanes in this junction    
    if (lane_ids_as_string==""):
        appendEmptyValuesToRow(row)
        return
        
    edge_prios=[]
    edge_types=[]
    lane_lengths=[]
    lane_speeds=[]
    connection_info=[]
    lane_id_list= lane_ids_as_string.split(" ")    
    for l_id in lane_id_list:
        try:            
            lane= lane_table[l_id]
            edge= lane.getparent()            
            if isIncomingLane:    
                edge_types.append( edge.get("type"))
                edge_prios.append(float(edge.get("priority")))
            #only check connections that connect with an internal lane
                #need lane.index and edge.id for that
            
                connection_info.append( findConnections (edge.get("id"), lane.get("index")))
            
                
            lane_lengths.append(float(lane.get("length")))
            lane_speeds.append(float(lane.get("speed")))
        except:
            print ("error with lane_ids: '{}', l_id:'{}' junction_id:'{}'".format(lane_ids_as_string,
                   l_id, row[0]))
    row.append(connection_info)    
    row.append(np.average(lane_speeds))
    row.append(np.std(lane_speeds))
    row.append(np.average(lane_lengths))
    row.append(np.std(lane_lengths))
    if isIncomingLane:        
        row.append(edge_types)
        row.append(np.average(edge_prios))
    else:
        row.append(None)
        row.append(-1)
    row.append(len(lane_id_list))

#only find connections that use an internal lane
def findConnections (edge_id, lane_index):
    result=[]
    if edge_id in connectiontable_to:    
        con=     connectiontable_to[edge_id]
        if con.get('tl')!=None:
            result.append([con.get('from'), con.get('to'), con.get('tl'),con.get('dir'), con.get('state')])
    
    if edge_id in connectiontable_from:    
        con=     connectiontable_from[edge_id]
        if con.get('tl')!=None:
            result.append([con.get('from'), con.get('to'), con.get('tl'),con.get('dir'), con.get('state')])
            
      
    via_id="{}_{}".format(edge_id, lane_index)    
    if via_id in connectiontable_via:
        con= connectiontable_via[via_id]         
        if con.get('tl')!=None:
                result.append([con.get('from'), con.get('to'), con.get('tl'),con.get('dir'), con.get('state')])
    
    #if tl isdefined add :

    #[connection.get("tl"),connection.get("dir"),connection.get("state")]
    #example connection xml:    
    #<connection from="-31648#1" to="-31648#2" fromLane="0" toLane="0" via=":-5432_0_0" 
    #tl="-5432" linkIndex="0" dir="s" state="o"/>
    return result


def evaluateJunction(junction_id_tuple):
    child=junction_id_tuple[1]
    #print (junction_id_tuple[0])
    row= []        
    row.append(child.get("id"))
    #maybe filter junctions of type other than "traffic_light"        
    row.append(child.get("type"))
    row.append(child.get("x"))
    row.append(child.get("y"))
    row.append(child.get("z"))
    row.append(isRoundAbout(row[0]))
    processIncomingLanes (child.get("incLanes"), row, child)
    processInternalLanes (child.get("intLanes"), row, child)
    return row


# function to be mapped over
def calculateParallel(numbers, threads):
    pool = ThreadPool(threads)
    results = pool.map(evaluateJunction, numbers)
    pool.close()
    pool.join()
    return results


def runDataExtraction (xml, output_filename):
    global tree
    tree = etree.parse(xml)
    global findRoundAboundTag
    findRoundAboundTag= etree.XPath("//net/roundabout[contains(@nodes,$id)]")
    
    root = tree.getroot()
    print "imported filed, found root element {}".format(root.tag)
    #junctions= tree.xpath("/net/junction")
    junctions= tree.xpath("/net/junction[@type='traffic_light']")
    
    print ("building connection tables for faster lookup..")
    connections=tree.xpath("/net/connection")
    global connectiontable_from
    connectiontable_from={}
    global connectiontable_to
    connectiontable_to={}
    global connectiontable_via
    connectiontable_via={}
    for con in connections:
        connectiontable_from[con.get('from')]=con
        connectiontable_to[con.get('to')]=con    
        connectiontable_via[con.get('via')]=con
    print ("done!")
    
    print ("building lane table for faster lookup..")
    lanes=tree.xpath("/net/edge/lane")
    global lane_table
    lane_table={}
    for lane in lanes:
        lane_table[lane.get('id')]=lane
    print ("done!")
        
    junction_count= len(junctions)
    #print enumerate([1,2,3])
    print "processing {} junctions..".format(junction_count)
    
    #dataset = calculateParallel(enumerate(junctions), 4)
    
    n=0
    for pair in enumerate(junctions):
        dataset.append(evaluateJunction( pair ))
        n=n+1 
        if (n%10==0):    
           print ("{}/{} junctions processed..".format(n, junction_count)) 
            
        
    
    
    print ("done processing, writing file {}..".format(output_filename))
    with open(output_filename,"wb") as f:
        writer=csv.writer(f)
        writer.writerows(dataset)
    print ("done")


xml="D:\\verkehr\TAPASCologne-0.24.0\TAPASCologne-0.24.0\cologne2.net.xml"
output_filename= "dataset-cgn-tl.csv"
dataset= []

print("processing cologne..")
runDataExtraction(xml, output_filename)
dataset=[]
print ("processing lust scenario..")
#xml ="/home/ganjalf/sumo/TAPASCologne-0.24.0/cologne2.net.xml"
xml ="C:\LuSTScenario\scenario\lust.net.xml"
output_filename= "dataset-lust-tl.csv"
runDataExtraction(xml, output_filename)

#df = pd.DataFrame(list1, columns=('lib', 'qty1', 'qty2'))
