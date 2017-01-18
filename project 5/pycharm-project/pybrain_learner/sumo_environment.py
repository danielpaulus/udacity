from __future__ import division
import sys
import os


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


class Agent_Info(object):
    pass


class SumoEnv():
    """ A (terribly simplified) Blackjack game implementation of an environment. """

    # the number of action values the environment accepts


    # the number of sensor values the environment produces


    # possible_actions = ['r', 'g', 'G', 'y', 'o', 'O', 'u']
    action_spaces = [None] * 12  # initialize a list for storing action spaces on demand
    edges = []
    agent_data = {}

    def actionCnt(self,tl_id):
        agent = self.agent_data[tl_id]
        return len (self.action_spaces[agent.tl_count])

    def stateCnt(self,tl_id):
        #agent=self.agent_data[tl_id]
        #this is determined by the getSensors() method
        #currently its 5 measurements per edge
        return 6

    def __init__(self, config, traffic_light_info,reward_function, dump_csv=False):
        self.reward_function=reward_function
        self.config = config
        self.startTraci()
        self.current_step=0
        for (count, tl_id) in (traffic_light_info):
            info = Agent_Info()
            info.tl_count = count
            info.tl_id = tl_id
            info.edges = self.getSumoEdgeInformationFromTraci(tl_id)
            self.intializeActionSpace(count)
            self.agent_data[tl_id] = info
        self.dump_csv = dump_csv
        if (dump_csv):
            f = open('out.csv', 'w+')
            self.csv_file = csv.writer(f)
            self.write_csv_head()

    def getSumoEdgeInformationFromTraci(self, tl_id):
        lanes = traci.trafficlights.getControlledLanes(tl_id)
        result = []
        for lane in lanes:
            result.append(traci.lane.getEdgeID(lane))
        return result

    """
            problem, action space is obviously 6^(#of traffic lights)+1
            nof lights | action space size
            1               6 items
            2               36 items
            3               216 items
            4               1296 items
            5               7776 items
            6               46656 items
            7               279936 items <-- very slow
            8               1679616 items <-- too slow to realistically use
            9               10077696 items <-- not working, memory needs to be increased, gpu or multithreading might help
            10
            11
            12
            """

    def intializeActionSpace(self, size):
        if self.action_spaces[size] is not None:
            return
        space = map(''.join, itertools.product("rgyGu", repeat=size))
        self.action_spaces[size] = space
        print "Created Action Space with:{} items".format(len(space))

    def write_csv_head(self):
        head = ["reward"]
        for e_id in self.edges:
            head.append("waitingtime_" + e_id)
            head.append("co2_" + e_id)
            head.append("fuelconsumption_" + e_id)
            head.append("laststepmeanspeed_" + e_id)
            head.append("laststepvehiclenumber_" + e_id)

        self.csv_file.writerow(head)

    def actionResults(self, tl_id):
        agent_info= self.agent_data[tl_id]
        return agent_info.observation, agent_info.reward, False, {}

    def step(self):
        self.performActions()
        traci.simulationStep()
        if self.gui:
            traci.gui.screenshot("View #0", "../../images/" + str(self.current_step) + ".png")
        self.current_step+=1
        self.makeObservations()
        self.computeRewards()


    def computeRewards(self):
        for tl_id, agent in self.agent_data.iteritems():
            action = self.action_spaces[agent.tl_count][agent.action]
            agent.reward= self.reward_function(action, agent.observation, agent.edges)

    def makeObservations(self):
        for tl_id, agent in self.agent_data.iteritems():
            agent.observation= self.getSensors(agent.tl_id)

    def performActions(self):
        for tl_id, agent in self.agent_data.iteritems():
            action_space= self.action_spaces[agent.tl_count]
            traci.trafficlights.setRedYellowGreenState(tl_id, action_space[agent.action])


    def setAction(self, action, tl_id):
        self.agent_data[tl_id].action=action




    def getSensors(self,tl_id):
        # read global info
        edges=self.agent_data[tl_id].edges
        """arrived_vehicles_in_last_step = traci.simulation.getArrivedNumber()
        departed_vehicles_in_last_step = traci.simulation.getDepartedNumber()
        current_simulation_time_ms = traci.simulation.getCurrentTime()"""

        vehicles_started_to_teleport = traci.simulation.getStartingTeleportNumber()

        """ #vehicles_ended_teleport = traci.simulation.getEndingTeleportNumber()
        #vehicles_still_expected = traci.simulation.getMinExpectedNumber()

        observation = np.array( [arrived_vehicles_in_last_step, departed_vehicles_in_last_step,
                       current_simulation_time_ms, vehicles_started_to_teleport,
                       vehicles_ended_teleport, vehicles_still_expected])


        self.f.write("{},{},{},{},{},{}\n".format(arrived_vehicles_in_last_step, departed_vehicles_in_last_step,
                       current_simulation_time_ms, vehicles_started_to_teleport,
                       vehicles_ended_teleport, vehicles_still_expected))
        """
        observation = []
        for e_id in edges:
            edge_values = [
                traci.edge.getWaitingTime(e_id),
                traci.edge.getCO2Emission(e_id),
                # traci.edge.getCOEmission(e_id),
                # traci.edge.getHCEmission(e_id),
                # traci.edge.getPMxEmission(e_id),
                # traci.edge.getNOxEmission(e_id),
                traci.edge.getFuelConsumption(e_id),
                traci.edge.getLastStepMeanSpeed(e_id),
                # traci.edge.getLastStepOccupancy(e_id),
                # traci.edge.getLastStepLength(e_id),
                # traci.edge.getTraveltime(e_id),
                traci.edge.getLastStepVehicleNumber(e_id),
                # traci.edge.getLastStepHaltingNumber(e_id)
            ]
            if edge_values[4]!=0:
                edge_values[0]/=edge_values[4]
                edge_values[1] /= edge_values[4]
                edge_values[2] /= edge_values[4]

            observation.append(edge_values)

        #x = np.matrix(observation.reshape(len(edges), 5))
        observation = np.matrix(observation).mean(0).tolist()[0]

        observation.append(vehicles_started_to_teleport)

        return np.array(observation)



    def close(self):
        traci.close()

    def startTraci(self):
        if self.config.sumo_home is not None:
            os.environ["SUMO_HOME"] = self.config.sumo_home
        if "-gui" in self.config.sumoCmd[0]:
            self.gui=True
        else:
            self.gui=False
        traci.start(self.config.sumoCmd)

    def emptyState(self, tl_id):
        return np.zeros(self.stateCnt(tl_id))
