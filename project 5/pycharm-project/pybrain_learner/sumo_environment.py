from __future__ import division
from pybrain.rl.environments.environment import Environment
from scipy import zeros
import sys
import os
import imp
try:
    import traci
except ImportError:
    if "SUMO_HOME" in os.environ:
        print os.path.join(os.environ["SUMO_HOME"], "tools")
        sys.path.append(
            os.path.join(os.environ["SUMO_HOME"], "tools")
        )
        import traci
    else:
        raise EnvironmentError("Please set SUMO_HOME environment variable or install traci as python module!")
import itertools
import os
import numpy as np
import csv

class SumoEnv(Environment):
    """ A (terribly simplified) Blackjack game implementation of an environment. """

    # the number of action values the environment accepts
    actionCnt = 2

    # the number of sensor values the environment produces
    stateCnt = 5*12

    possible_actions = ['r', 'g', 'G', 'y', 'o', 'O', 'u']
    action_space = []
    edges = []
    TLSID = "0"


    def __init__(self, config):
        self.config = config
        self.action_space = map(''.join, itertools.product("rgy", repeat=12))
        self.actionCnt = len(self.action_space)
        f = open('out.csv', 'w+')
        self.csv_file=csv.writer(f)


    def write_csv_head(self):
        head=["reward"]
        for e_id in self.edges:
            head.append("waitingtime_"+e_id)
            head.append("co2_" + e_id)
            head.append("fuelconsumption_" + e_id)
            head.append("laststepmeanspeed_" + e_id)
            head.append("laststepvehiclenumber_" + e_id)

        self.csv_file.writerow(head)

    def step(self, a):
        self.performAction(a)
        observation=self.getSensors()
        reward= self.computeReward(a,observation)
        c=[reward]
        c.extend(observation)
        #self.csv_file.writerow(c)
        return observation, reward, False, {}


    def computeReward(self, action, observation):
        x = np.matrix(observation.reshape((12, 5)))
        means= x.mean(0).tolist()[0]
        r=0
        a= self.action_space[action]

        if means[0]==0:
            r+=1
        else:
            if means[0]/10<0.2:
                r+=-.5

        if means[0]/10>0.5:
            r+=-1
        r+=0.2*a.count("g")
        r += -0.2 * a.count("r")
        return r
    def getSensors(self):
        # read global info
        """arrived_vehicles_in_last_step = traci.simulation.getArrivedNumber()
        departed_vehicles_in_last_step = traci.simulation.getDepartedNumber()
        current_simulation_time_ms = traci.simulation.getCurrentTime()
        vehicles_started_to_teleport = traci.simulation.getStartingTeleportNumber()
        vehicles_ended_teleport = traci.simulation.getEndingTeleportNumber()
        vehicles_still_expected = traci.simulation.getMinExpectedNumber()

        observation = np.array( [arrived_vehicles_in_last_step, departed_vehicles_in_last_step,
                       current_simulation_time_ms, vehicles_started_to_teleport,
                       vehicles_ended_teleport, vehicles_still_expected])


        self.f.write("{},{},{},{},{},{}\n".format(arrived_vehicles_in_last_step, departed_vehicles_in_last_step,
                       current_simulation_time_ms, vehicles_started_to_teleport,
                       vehicles_ended_teleport, vehicles_still_expected))
        """
        observation=[]
        for e_id in self.edges:
            edge_values = [
                traci.edge.getWaitingTime(e_id),
                traci.edge.getCO2Emission(e_id),
                #traci.edge.getCOEmission(e_id),
                #traci.edge.getHCEmission(e_id),
                #traci.edge.getPMxEmission(e_id),
                #traci.edge.getNOxEmission(e_id),
                traci.edge.getFuelConsumption(e_id),
                traci.edge.getLastStepMeanSpeed(e_id),
                #traci.edge.getLastStepOccupancy(e_id),
                #traci.edge.getLastStepLength(e_id),
                #traci.edge.getTraveltime(e_id),
                traci.edge.getLastStepVehicleNumber(e_id),
                #traci.edge.getLastStepHaltingNumber(e_id)
            ]
            observation.extend(edge_values)

        return np.array(observation)

    def performAction(self, action):
        """ perform an action on the world that changes it's internal state (maybe stochastically).
            :key action: an action that should be executed in the Environment.
            :type action: by default, this is assumed to be a numpy array of doubles
        """

        traci.trafficlights.setRedYellowGreenState(self.TLSID, self.action_space[action])
        traci.simulationStep()


    def startTraci(self):
        if self.config.sumo_home is not None:
            os.environ["SUMO_HOME"] = self.config.sumo_home

        traci.start(self.config.sumoCmd)
        lanes = traci.trafficlights.getControlledLanes(self.TLSID)
        for lane in lanes:
            self.edges.append(traci.lane.getEdgeID(lane))
        self.write_csv_head()

    def reset(self):
        """ Most environments will implement this optional method that allows for reinitialization.
        """
        #traci.close()
        self.startTraci()
        return np.zeros(self.stateCnt)
