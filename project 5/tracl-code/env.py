# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 12:30:15 2016

@author: Daniel1Paulus
"""
import numpy as np
import pandas as pd
import traci
import ast
# Note: the API of the `Env` and `Space` classes are taken from the OpenAI Gym implementation.
# https://github.com/openai/gym/blob/master/gym/core.py

#read: https://gym.openai.com/docs

class Env(object):
    """portable config"""
    #sys.path.append('e:\\Sumo\\tools')
    #os.environ["SUMO_HOME"]="E:\\Sumo"
    #sumoBinary = "E:\\Sumo\\bin\\sumo-gui.exe"
    #sumoCmd = [sumoBinary, "-c", "E:\\rilsa\\run.sumo.cfg"]
    
    
    
    """Laptop config"""
    sumoBinary = "C:\\Program Files (x86)\\DLR\\Sumo\\bin\\sumo.exe"
    sumoCmd = [sumoBinary, "-c", "D:\\verkehr\\RiLSA_example4\\run.sumo.cfg"]
    
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
    observation_space = None

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
        TLSID= "0"        
        traci.simulationStep()
        arrived_vehicles_in_last_step= traci.simulation.getArrivedNumber()
        departed_vehicles_in_last_step=traci.simulation.getDepartedNumber()
        current_simulation_time_ms=traci.simulation.getCurrentTime()
        print arrived_vehicles_in_last_step
        phase= traci.trafficlights.getPhase(TLSID)   
        traci.trafficlights.setPhase(TLSID, 0)
        lanes= traci.trafficlights.getControlledLanes(TLSID)
        reward=1
        done= False        
        info= {"info": "none"}
        return (observation, reward, done, info)

    def reset(self):
        """
        Resets the state of the environment and returns an initial observation.
        Returns:
            observation (object): the initial observation of the space. (Initial reward is assumed to be 0.)
        """
        traci.start(sumoCmd) 
        lust= import_datasets()
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
        csv_dir="..\\code\\"    
        lust_file_name="dataset-lust-tl-clusters.csv"
        df= pd.read_csv(csv_dir+lust_file_name)    
        df['connections']= df['connections'].map(lambda x: ast.literal_eval(x))
        return df

    def extract_tl_ids(connection_list):
        tl_list=[]    
        for connection in connection_list:
            tl_list.append( connection[2])
        return tl_list
        



class Space(object):
    """Abstract model for a space that is used for the state and action spaces. This class has the
    exact same API that OpenAI Gym uses so that integrating with it is trivial.
    """

    def sample(self, seed=None):
        """Uniformly randomly sample a random element of this space.
        """
        raise NotImplementedError()

    def contains(self, x):
        """Return boolean specifying if x is a valid member of this space
        """
        raise NotImplementedError()