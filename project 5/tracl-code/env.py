# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 12:30:15 2016

@author: Daniel1Paulus
"""



from __future__ import division
import numpy as np
import pandas as pd

import ast
import itertools
import sys
import os
from gym import spaces


"""portable config"""
# sys.path.append('e:\\Sumo\\tools')
# os.environ["SUMO_HOME"]="E:\\Sumo"
# sumoBinary = "E:\\Sumo\\bin\\sumo-gui.exe"
# sumoCmd = [sumoBinary, "-c", "E:\\rilsa\\run.sumo.cfg"]



"""Laptop config"""
#sumoBinary = "C:\\Program Files (x86)\\DLR\\Sumo\\bin\\sumo.exe"
#sumoCmd = [sumoBinary, "-c", "D:\\verkehr\\RiLSA_example4\\run.sumo.cfg"]


import traci
# Note: the API of the `Env` and `Space` classes are taken from the OpenAI Gym implementation.
# https://github.com/openai/gym/blob/master/gym/core.py

# read: https://gym.openai.com/docs

#os.environ["SUMO_HOME"] = "/usr/share/sumo"

class FickDich(object):
    """Ubuntu Config"""
    # sys.path.append('/usr/share/sumo/tools')

    sumoBinary = "/usr/bin/sumo"
    sumoCmd = [sumoBinary, "-c", "/home/ganjalf/sumo/rilsa/run.sumo.cfg"]

    """interesting functions:
        gui: screenshot()
            trackVehicle()
    """

    """The abstract environment class that is used by all agents. This class has the exact
    same API that OpenAI Gym uses so that integrating with it is trivial. In contrast to the
    OpenAI Gym implementation, this class only defines the abstract methods without any actual
    implementation.
    """
    reward_range = (-np.inf, np.inf)
    action_space = None
    observation_space = spaces.Box(low=0,high=1000, shape=(1,19))

    #spaces.Discrete(7) 0-6
    possible_actions = ['r', 'g', 'G', 'y', 'o', 'O', 'u']
    edges = []
    TLSID = "0"
    def __init__(self, lanes):
        self.lanes = lanes
        space_init=[]

        for i in range(0,lanes):
            space_init.append([0, 6])
        action_space = spaces.MultiDiscrete(space_init)


    def step(self, action):
        """Run one timestep of the environment's dynamics.
        Accepts an action and returns a tuple (observation, reward, done, info).
        Args:
            action (object): an action provided by the environment
        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (boolean): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """

        traci.simulationStep()
        # read global info
        arrived_vehicles_in_last_step = traci.simulation.getArrivedNumber()
        departed_vehicles_in_last_step = traci.simulation.getDepartedNumber()
        current_simulation_time_ms = traci.simulation.getCurrentTime()
        vehicles_started_to_teleport = traci.simulation.getStartingTeleportNumber()
        vehicles_ended_teleport = traci.simulation.getEndingTeleportNumber()
        vehicles_still_expected = traci.simulation.getMinExpectedNumber()
        traci.trafficlights.setRedYellowGreenState(self.TLSID, action)
        observation = [arrived_vehicles_in_last_step, departed_vehicles_in_last_step,
                       current_simulation_time_ms, vehicles_started_to_teleport,
                       vehicles_ended_teleport, vehicles_still_expected]

        reward = 0
        avg_edge_values = np.zeros(13)
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
            #scale using the amount of vehicles
            if edge_values[11]>0:
                edge_values[7] /= edge_values[11]
                edge_values[1] /= edge_values[11]
                edge_values[0] /= edge_values[11]
            avg_edge_values = np.add(avg_edge_values, edge_values)


        avg_edge_values /= len(self.edges)

        observation.extend(avg_edge_values)

        waitingFactor = -avg_edge_values[0] / 100
        if waitingFactor == 0:
            waitingFactor += 1
        co2_factor = -avg_edge_values[1] / 3000
        fuel_factor = -avg_edge_values[7]
        green_factor=7*(action.count("g")+action.count("G"))/self.lanes
        yellow_factor=-0.5*action.count("y")/self.lanes
        red_factor=-2*action.count("r")/self.lanes
        reward += waitingFactor+co2_factor+fuel_factor+green_factor+yellow_factor+red_factor

        done = False
        info = {"waitingFactor": waitingFactor, "co2_factor":co2_factor,"fuel_factor":fuel_factor,
                "green_factor":green_factor,"yellow_factor":yellow_factor,"red_factor":red_factor,"total_reward":reward}


        return observation, reward, done, info

    def reset(self):
        """
        Resets the state of the environment and returns an initial observation.
        Returns:
            observation (object): the initial observation of the space. (Initial reward is assumed to be 0.)
        """

        traci.start(self.sumoCmd)
        lanes = traci.trafficlights.getControlledLanes(self.TLSID)
        for lane in lanes:
            self.edges.append(traci.lane.getEdgeID(lane))

        #lust = import_datasets()
        step = 0
        tl = traci.trafficlights

    def render(self, mode='human', close=False):
        """Renders the environment.
        The set of supported modes varies per environment. (And some
        environments do not support rendering at all.) By convention,
        if mode is:
        - human: render to the current display or terminal and
          return nothing. Usually for human consumption.
        - rgb_array: Return an numpy.ndarray with shape (x, y, 3),
          representing RGB values for an x-by-y pixel image, suitable
          for turning into a video.
        - ansi: Return a string (str) or StringIO.StringIO containing a
          terminal-style text representation. The text can include newlines
          and ANSI escape sequences (e.g. for colors).
        Note:
            Make sure that your class's metadata 'render.modes' key includes
              the list of supported modes. It's recommended to call super()
              in implementations to use the functionality of this method.
        Args:
            mode (str): the mode to render with
            close (bool): close all open renderings
        """
        return

    def close(self):
        """Override in your subclass to perform any necessary cleanup.
        Environments will automatically close() themselves when
        garbage collected or when the program exits.
        """
        traci.close()

    def seed(self, seed=None):
        """Sets the seed for this env's random number generator(s).
        Note:
            Some environments use multiple pseudorandom number generators.
            We want to capture all such seeds used in order to ensure that
            there aren't accidental correlations between multiple generators.
        Returns:
            list<bigint>: Returns the list of seeds used in this env's random
              number generators. The first value in the list should be the
              "main" seed, or the value which a reproducer should pass to
              'seed'. Often, the main seed equals the provided 'seed', but
              this won't be true if seed=None, for example.
        """
        raise NotImplementedError()

    def configure(self, *args, **kwargs):
        """Provides runtime configuration to the environment.
        This configuration should consist of data that tells your
        environment how to run (such as an address of a remote server,
        or path to your ImageNet data). It should not affect the
        semantics of the environment.
        """
        raise NotImplementedError()

    def __del__(self):
        self.close()

    def __str__(self):
        return '<{} instance>'.format(type(self).__name__)

    def import_datasets():
        csv_dir = "..\\code\\"
        lust_file_name = "dataset-lust-tl-clusters.csv"
        df = pd.read_csv(csv_dir + lust_file_name)
        df['connections'] = df['connections'].map(lambda x: ast.literal_eval(x))
        return df

    def extract_tl_ids(connection_list):
        tl_list = []
        for connection in connection_list:
            tl_list.append(connection[2])
        return tl_list

"""
e = Env(12)
print e.action_space
e.reset()
for i in range(1,1000):
    result= e.step('rrrrGgrrrrGg')

    print result[3]
e.close()

"""