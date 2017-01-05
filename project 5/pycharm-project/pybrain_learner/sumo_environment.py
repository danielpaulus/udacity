from __future__ import division
from pybrain.rl.environments.environment import Environment
from scipy import zeros
import traci
import itertools


class SumoEnv(Environment):
    """ A (terribly simplified) Blackjack game implementation of an environment. """

    # the number of action values the environment accepts
    indim = 2

    # the number of sensor values the environment produces
    outdim = 6 + 12 * 13

    possible_actions = ['r', 'g', 'G', 'y', 'o', 'O', 'u']
    state_space = []
    edges = []
    TLSID = "0"

    def __init__(self, config):
        self.config = config
        self.state_space = map(''.join, itertools.product("rgy", repeat=12))
        self.indim = len(self.state_space)
        self.startTraci()

    def getSensors(self):
        # read global info
        arrived_vehicles_in_last_step = traci.simulation.getArrivedNumber()
        departed_vehicles_in_last_step = traci.simulation.getDepartedNumber()
        current_simulation_time_ms = traci.simulation.getCurrentTime()
        vehicles_started_to_teleport = traci.simulation.getStartingTeleportNumber()
        vehicles_ended_teleport = traci.simulation.getEndingTeleportNumber()
        vehicles_still_expected = traci.simulation.getMinExpectedNumber()

        observation = [arrived_vehicles_in_last_step, departed_vehicles_in_last_step,
                       current_simulation_time_ms, vehicles_started_to_teleport,
                       vehicles_ended_teleport, vehicles_still_expected]

        for e_id in self.edges:
            edge_values = [
                traci.edge.getWaitingTime(e_id),
                traci.edge.getCO2Emission(e_id),
                traci.edge.getCOEmission(e_id),
                traci.edge.getHCEmission(e_id),
                traci.edge.getPMxEmission(e_id),
                traci.edge.getNOxEmission(e_id),
                traci.edge.getFuelConsumption(e_id),
                traci.edge.getLastStepMeanSpeed(e_id),
                traci.edge.getLastStepOccupancy(e_id),
                traci.edge.getLastStepLength(e_id),
                traci.edge.getTraveltime(e_id),
                traci.edge.getLastStepVehicleNumber(e_id),
                traci.edge.getLastStepHaltingNumber(e_id)
            ]
            observation.extend(edge_values)
        return observation

    def performAction(self, action):
        """ perform an action on the world that changes it's internal state (maybe stochastically).
            :key action: an action that should be executed in the Environment.
            :type action: by default, this is assumed to be a numpy array of doubles
        """
        traci.trafficlights.setRedYellowGreenState(self.TLSID, self.state_space[action])
        traci.simulationStep()
        print "Action performed: ", action

    def startTraci(self):
        traci.start(self.config.sumoCmd)
        lanes = traci.trafficlights.getControlledLanes(self.TLSID)
        for lane in lanes:
            self.edges.append(traci.lane.getEdgeID(lane))

    def reset(self):
        """ Most environments will implement this optional method that allows for reinitialization.
        """
        traci.close()
        self.startTraci()
