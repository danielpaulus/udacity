# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import sys,os
sys.path.append('e:\\Sumo\\tools')
os.environ["SUMO_HOME"]="E:\\Sumo"
sumoBinary = "E:\\Sumo\\bin\\sumo-gui.exe"
sumoCmd = [sumoBinary, "-c", "E:\\rilsa\\run.sumo.cfg"]

import traci
traci.start(sumoCmd) 
step = 0
tl = traci.trafficlights
      
TLSID= "0"
while step < 1000:
   traci.simulationStep()
   phase= traci.trafficlights.getPhase(TLSID)   
   traci.trafficlights.setPhase(TLSID, 0)
   lanes= traci.trafficlights.getControlledLanes(TLSID)
   for lane in lanes:
       print lane
   print phase
   #if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
    #   traci.trafficlights.setRedYellowGreenState("0", "GrGr")
   step += 1

traci.close()