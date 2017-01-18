# -*- coding: utf-8 -*-
"""
Create a dataset from SUMO .net.xml files
"""
from lxml import etree
import numpy as np
import csv

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
    row.append(0)
    row.append(0)
    row.append(0)
    row.append(0)
    row.append(None)
    row.append(0)
    row.append(0)

#retrieve statistics for lanes of a junction,     
def processLanes (lane_ids_as_string, row, junction,isIncomingLane):
    #append an empty row if there are no lanes in this junction    
    if (lane_ids_as_string==""):
        appendEmptyValuesToRow(row)
        return
    edge_prios=[]
    edge_types=[]
    lane_lengths=[]
    lane_speeds=[]    
    lane_id_list= lane_ids_as_string.split(" ")    
    for l_id in lane_id_list:
        try:            
            lane= lane_table[l_id]
            edge= lane.getparent()
            if isIncomingLane:    
                edge_types.append( edge.get("type"))
                edge_prios.append(float(edge.get("priority")))
            lane_lengths.append(float(lane.get("length")))
            lane_speeds.append(float(lane.get("speed")))
        except:
            print ("error with lane_ids: '{}', l_id:'{}' junction_id:'{}'".format(lane_ids_as_string,
                   l_id, row[0]))
            raise
        
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

"""
Find connections using the global nodes_table and connection_tl table
we need to find the "tl"-id for a corresponding junction id. 
Using this id, we can figure out how many traffic lights this junction controlls because
number of connections with tl == tl_id of junction equals the number of traffic lights

"""
def findConnections (junction_id):    
           # tl[0].get("id")
           tl= nodes_table[junction_id]
           number_of_traffic_lights=0
           for tllogic in tlLogicTable:
                if (tllogic.get("id")==tl):               
                    number_of_traffic_lights=len(tllogic.getchildren()[0].get("state"))
                    break
           results= map(lambda con: [con.get('from'), con.get('to'), con.get('tl'),con.get('dir'), con.get('state')], connectiontable_tl[tl])
           return [number_of_traffic_lights,tl,results]

"""
Reads the number of traffic light controlled by this junction from xml 
"""
def processConnections(row):
    trafficlightinfo=findConnections(row[0])
    row.append(trafficlightinfo)

"""
Reads data from xml for one junction
"""
def evaluateJunction(junction):    
    row= []        
    row.append(junction.get("id"))
    row.append(junction.get("type"))
    row.append(junction.get("x"))
    row.append(junction.get("y"))
    row.append(junction.get("z"))
    row.append(isRoundAbout(row[0]))
    processConnections(row)
    processIncomingLanes (junction.get("incLanes"), row, junction)
    processInternalLanes (junction.get("intLanes"), row, junction)
    return row

"""
This method creates some hash tables for fast xml lookup. 
Using xpath was horribly slow. 
"""
def createXmlEntityCaches(tree, nodes_tree):
    
    root = tree.getroot()
    print "imported net.xml-file, found root element {}".format(root.tag)
    
    #compile the query for roundabouts for faster execution times
    global findRoundAboundTag
    findRoundAboundTag= etree.XPath("//net/roundabout[contains(@nodes,$id)]")

    junctions= tree.xpath("/net/junction[@type='traffic_light']")
    
    print ("building connection tables for faster lookup..")
    connections=tree.xpath("/net/connection")
    
    #i am not too happy with using global variables, but there is no time left to refactor this script :-)
    global connectiontable_from
    connectiontable_from={}
    global connectiontable_to
    connectiontable_to={}  
    global node_table
    
    global connectiontable_tl
    connectiontable_tl={}   
    for con in connections:
        tlid= con.get("tl")
        if tlid is not None:            
            tlid= con.get('tl')
            if tlid not in connectiontable_tl.keys():
                connectiontable_tl[tlid]=[]
            connectiontable_tl[tlid].append(con)

        connectiontable_from[con.get('from')]=con
        connectiontable_to[con.get('to')]=con  
    
    global tlLogicTable
    tlLogicTable=tree.xpath("/net/tlLogic")
    print ("done!")
    
    print ("building node table for faster lookup..")
    global nodes_table
    nodes_table={}
    nodes=nodes_tree.xpath("/nodes/node[@type='traffic_light']")
    for node in nodes:
        id= node.get('id')
        nodes_table[id]=node.get('tl')
    
    print ("building lane table for faster lookup..")
    lanes=tree.xpath("/net/edge/lane")
    global lane_table
    lane_table={}
    for lane in lanes:
        lane_table[lane.get('id')]=lane
    print ("done!")
        
    junction_count= len(junctions)
    return junction_count, junctions

def runDataExtraction (xml,node_xml, output_filename):
    global tree
    tree = etree.parse(xml)
    nodes_tree= etree.parse(node_xml)   
    
    junction_count, junctions= createXmlEntityCaches(tree, nodes_tree)
    
    print "processing {} junctions..".format(junction_count)
    
    n=0
    for junction in junctions:
        dataset.append(evaluateJunction( junction ))
        n=n+1 
        if (n%10==0):    
           print ("{}/{} junctions processed..".format(n, junction_count)) 
    
    print ("done processing, writing file {}..".format(output_filename))
    with open(output_filename,"wb") as f:
        writer=csv.writer(f)
        writer.writerows(dataset)
    print ("done")


print("processing cologne..")
xml="E:\\TAPASCologne-0.24.0\\cologne2.net.xml"
node_xml= "E:\\TAPASCologne-0.24.0\\true.nod.xml"

xml= "/home/ganjalf/sumo/TAPASCologne-0.24.0/cologne2.net.xml"
node_xml="/home/ganjalf/sumo/TAPASCologne-0.24.0/true.nod.xml"

output_filename= "dataset-cgn-tl.csv"
dataset= []
runDataExtraction(xml,node_xml, output_filename)


print ("processing lust scenario..")
#xml ="/home/ganjalf/sumo/TAPASCologne-0.24.0/cologne2.net.xml"
xml ="E:\\LuSTScenario\\scenario\\lust.net.xml"
node_xml= "E:\\LuSTScenario\\scenario\\true.nod.xml"

xml="/home/ganjalf/sumo/LuSTScenario/scenario/lust.net.xml"
node_xml="/home/ganjalf/sumo/LuSTScenario/scenario/true.nod.xml"
output_filename= "dataset-lust-tl.csv"
dataset=[]
runDataExtraction(xml,node_xml, output_filename)

