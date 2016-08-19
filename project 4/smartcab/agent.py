import numpy as np
from numpy import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class StateMapper:
    def __init__(self):
        self.availableStates=['good_move_possible','good_or_bad_move_possible','bad_move_possible','cannot_move']        

    #convert a set of inputs to a state and return a 2-tuple
    #(current_state, [possible_actions])    
    def mapDataToState(self, next_waypoint, inputs, deadline):
        if inputs['light']=='red':
            if inputs['left']==None and next_waypoint=='right':
                return (self.availableStates[0], ['right',None])
            elif next_waypoint!='right':
                return (self.availableStates[2], ['right',None])
            else:
                return (self.availableStates[3],[None])
        #light is green
        else:
            if inputs['oncoming']==None and inputs['right']==None:
                return (self.availableStates[0],['all'])
            elif inputs['oncoming']!=None or inputs['right']!=None:
                return (self.availableStates[0],['right','forward',None])
        
        

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    
    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.possible_actions=[None, 'forward', 'left', 'right']
        self.mapper= StateMapper()
        # TODO: Initialize any additional variables here

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        print "next waypoint is:{}".format(self.next_waypoint)
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        random_action= self.possible_actions[np.random.randint(0,3)]
        # TODO: Select action according to your policy
        action=random_action
        action= self.possible_actions[0 ]

        # Execute action and get reward
        reward = self.env.act(self, action)
        
        state= self.mapper.mapDataToState(self.next_waypoint,inputs,deadline)
        
        # TODO: Learn policy based on state, action, reward

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        print "State:{}".format(state)

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
