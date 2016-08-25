import numpy as np
from numpy import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator



class Q_Matrix():
    def __init__(self):
         a = np.empty((5,4,))
         a[:] = .5
         print a

class StateMapper:
    def __init__(self):        
        self.availableStates=['rg','fg','lg','ngm','n']  

    #convert a set of inputs to a state and return the state
    #current_state
    def mapDataToState(self, next_waypoint, inputs, deadline):
        if inputs['light']=='red':
            if inputs['left']!=None:                 
                return self.availableStates[4]
            else:
                if next_waypoint=='right':
                    return self.availableStates[0]
                else:
                    return self.availableStates[3]
        #light is green
        else:
            if inputs['oncoming']==None and inputs['right']==None:
                if next_waypoint=='right':
                    return self.availableStates[0]
                if next_waypoint=='left':
                    return self.availableStates[2]
                if next_waypoint=='forward':
                    return self.availableStates[1]    
            elif inputs['oncoming']!=None or inputs['right']!=None:
                if next_waypoint=='right':
                    return self.availableStates[0]
                if next_waypoint=='forward':
                    return self.availableStates[1]    
                if next_waypoint=='left':
                    return self.availableStates[3]    
        print "this is bad"
                
class Q_Learner:
    def __init__(self):
        self.mapper= StateMapper()        
        self.gamma=0.09
        self.discount=.7
        self.current_state=None
        self.q_matrix = np.empty((5,4,))
        self.q_matrix[:] = 0
        self.q_matrix= np.matrix(
        [[ 0.1128092,  -0.79040805, -0.13417554,  1.40701109,],
        [ 0.05329855,  0.41352354, -0.58306539,  0.32728871,],
        [ 0.01045175, -0.50919896,  0.17989968, -0.41996765,],
        [ 0.04037663, -0.73653675, -0.64571302, -0.25909267,],
        [ 0.06841565, -0.67349922, -0.69575951, -0.08544277,]]        
        )
        
        
        
        
    def q(self, s, a):
        state= self.mapper.availableStates.index(s)
        possible_actions=[None, 'forward', 'left', 'right']
        action= possible_actions.index(a)
        return self.q_matrix[state, action]
        
    def setq(self, s, a, val):
        state= self.mapper.availableStates.index(s)
        possible_actions=[None, 'forward', 'left', 'right']
        action= possible_actions.index(a)
        #print "state:{} action:{} s_i:{} a_i{}".format(s, a, state, action)
        self.q_matrix[state, action]= val
    
    def maxFutureValue(self):
        state= self.mapper.availableStates.index(self.outcome_state)
        row= np.argmax(self.q_matrix[state,:])
        return self.q_matrix[state, row]
        
    def maxFutureAction(self):
        state= self.mapper.availableStates.index(self.current_state)
        row = self.q_matrix[state,:]
        index= np.argmax(row)
        print "curr_state:{} row:{} max_index:{}".format(self.current_state, row, index)
        return index
        
        
    def update(self):        
        old_value=self.q(self.current_state,self.action)        
        result=  old_value+ self.gamma* (self.reward+self.discount*self.maxFutureValue() - old_value)
        self.setq(self.current_state,self.action, result)    
        print [None, 'forward', 'left', 'right']        
        print self.q_matrix
        print ['rg','fg','lg','ngm','n']          
        
        
    
    
        
        
class ActionChooser:
    def __init__(self):
        self.possible_actions=[None, 'forward', 'left', 'right']
        
    def chooseAction(self): raise NotImplementedError
        

class RandomActionChooser(ActionChooser):    
        
    def chooseAction(self):
        return self.possible_actions[np.random.randint(0,3)]


class QValueRandomMixActionChooser(ActionChooser):    
    def __init__(self, qlearner):
        self.possible_actions=[None, 'forward', 'left', 'right']
        self.qlearner=qlearner
        self.epsilon= 0.2
        
    def chooseAction(self):
       rnd= np.random.random_sample()
       if rnd>self.epsilon:
           index= self.qlearner.maxFutureAction()
           return self.possible_actions[index]
       else:
           return self.possible_actions[np.random.randint(0,4)]
        
class QValueActionChooser(ActionChooser):    
    def __init__(self, qlearner):
        self.possible_actions=[None, 'forward', 'left', 'right']
        self.qlearner=qlearner
        
    def chooseAction(self):
        index= self.qlearner.maxFutureAction()
        return self.possible_actions[index]
       
        

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    
    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint        
        self.mapper= StateMapper()                
        #self.actionChooser= RandomActionChooser()
        
        self.learner=Q_Learner()
        self.actionChooser= QValueActionChooser(self.learner)
       # self.actionChooser= QValueRandomMixActionChooser(self.learner)
        
        # TODO: Initialize any additional variables here

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        learner= self.learner        
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        print "next waypoint is:{}".format(self.next_waypoint)
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        if learner.current_state==None:
            learner.current_state= self.mapper.mapDataToState(self.next_waypoint,inputs,deadline)
        else:        
            learner.update()
            learner.current_state=learner.outcome_state                
        
        # Select action according to your policy
        action= self.actionChooser.chooseAction()
        learner.action=action
        # Execute action and get reward
        learner.reward = self.env.act(self, action)        
        learner.outcome_state= self.mapper.mapDataToState(self.next_waypoint,inputs,deadline)
        
        
        # TODO: Learn policy based on state, action, reward

        #print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
#        print "State:{}".format(state)

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=1000)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
