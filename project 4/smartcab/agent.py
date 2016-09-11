import numpy as np
from numpy import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from my_utils import form_input_space
"""
Sources:
    http://burlap.cs.brown.edu/tutorials_v1/cpl/p3.html
"""

successes=0


class Q_Matrix():
    def __init__(self):
         self.possible_actions=[None, 'forward', 'left', 'right']
         self.availableStates=form_input_space()        
         state_count=len (self.availableStates)
         a = np.empty((state_count,4,))
         a[:] = 2
         self.matrix=a

class StateMapper:
    def __init__(self, q_learner):        
        self.q_learner=q_learner

    #convert a set of inputs to a state and return the state
    #current_state
    def mapDataToState(self, next_waypoint, inputs, deadline):

        #get the qmatrix for easier access
        matrix=self.q_learner.q_matrix                
        
        #init the variables for filtering out the correct state        
        if inputs['oncoming']== None:        
            oncoming='on_none'
        else:
            oncoming='on_'+inputs['oncoming']
        
        if inputs['left']== None:        
            left='lf_none'
        else:
            left='lf_'+inputs['left']
            
        if inputs['right']== None:        
            right='rg_none'
        else:
            right='rg_'+inputs['right']
        

        #select correct state from q_matrix        
        filteredbywaypoint = [(i,x) for (i,x) in enumerate(matrix.availableStates) if 
        x[0]=="wp_"+next_waypoint 
        and x[1]==inputs['light']
        and x[2]==oncoming        
        and x[3]==left 
        and x[4]==right
        ]        
        #should be only one value in the result list     
        #tuple (index, state)
        return filteredbywaypoint[0]
                
class Q_Learner:
    def __init__(self):
        #according to wikipedia a learning rate of 1 is ptimal in deterministic environments
        self.learning_rate=0.7
        self.discount=.8
        self.current_state=None
        self.q_matrix = Q_Matrix()
        
    def q(self, s, a):
        state= s[0]
        action= self.q_matrix.possible_actions.index(a)
        return self.q_matrix.matrix[state, action]
        
    def setq(self, s, a, val):
        state= s[0]
        action= self.q_matrix.possible_actions.index(a)
        self.q_matrix.matrix[state, action]= val
    
    def maxFutureValue(self):
        state=self.outcome_state[0]
        row= np.argmax(self.q_matrix.matrix[state,:])
        return self.q_matrix.matrix[state, row]
        
    def maxFutureAction(self):
        state=self.current_state[0]
        row = self.q_matrix.matrix[state,:]
        index= np.argmax(row)        
        return index
        
        
    def update(self):        
        old_value=self.q(self.current_state,self.action)        
        result=  old_value+ self.learning_rate* (self.reward+self.discount*self.maxFutureValue() - old_value)
        self.setq(self.current_state,self.action, result)            
        #print self.q_matrix.matrix
        
        
        
    
    
        
        
class ActionChooser:           
    def __init__(self, qlearner):        
        self.qlearner=qlearner
        
    def chooseAction(self): raise NotImplementedError
        

class RandomActionChooser(ActionChooser):    
        
    def chooseAction(self):
        return self.qlearner.q_matrix.possible_actions[np.random.randint(0,3)]


class QValueRandomMixActionChooser(ActionChooser):    
    def __init__(self, qlearner):        
        self.qlearner=qlearner
        self.epsilon= 0.1
        
    def chooseAction(self):
       rnd= np.random.random_sample()
       if rnd>self.epsilon:
           index= self.qlearner.maxFutureAction()
           return self.qlearner.q_matrix.possible_actions[index]
       else:
           return self.qlearner.q_matrix.possible_actions[np.random.randint(0,4)]
        
       
        

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    
    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint        
        
        #self.actionChooser= RandomActionChooser()
        
        self.learner=Q_Learner()
        self.mapper= StateMapper(self.learner)                        
        self.actionChooser= QValueRandomMixActionChooser(self.learner)
        
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

        location = self.env.agent_states[self]["location"] 
        destination = self.env.agent_states[self]["destination"]
        if location==destination:
            global successes
            successes= successes+1
        
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

    sim.run(n_trials=5000)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line
    matrix= a.learner.q_matrix.matrix
    f = open('q_matrix.npy', 'w')    
    np.save(f,matrix)
    f.close()
    f = open('q_matrix.txt', 'w')    
    matrix.tofile(f, ";")
    f.close()
    print "successrate: {}".format(successes/5000.0)

if __name__ == '__main__':
    run()
