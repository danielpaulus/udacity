import numpy as np
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from my_utils import form_state_space
"""
Sources:
    http://burlap.cs.brown.edu/tutorials_v1/cpl/p3.html
    https://en.wikipedia.org/wiki/Q-learning
"""


"""i wrote a wrapper class for the numpy matrix
   to better keep track of all states and actions
   which logically belong to the Q-matrix I think. 
"""
class Q_Matrix():
    def __init__(self):
         self.possible_actions=[None, 'forward', 'left', 'right']
         #build the state space by using the cartesian of all inputs
         #I put the code in my_utils.py
         self.availableStates=form_state_space() 
         
         state_count=len (self.availableStates)
         #create a simple 512 by 4 numpy matrix         
         a = np.empty((state_count,4,))
         #initialize with 2, the value of the reward for 
         #going in the right direction
         a[:] = 2
         self.matrix=a

"""I wrote a class to map inputs to states. I initially tried different approaches
to reduce the state space by using logic and created states like "left is the right way"
but my algorithm was not very successful and the forum discussions indicated that
hard coding traffic rules is not the way to go here.
So the final StateMapper just uses the cartesian product of the available inputs.
"""
class StateMapper:
    def __init__(self, q_learner):        
        self.q_learner=q_learner

    """convert a set of inputs to a state and return the state
    deadline is not currently in use.
    returns: state as a tuple (index in the q Matrix, human readable state array)
    """
    def mapDataToState(self, next_waypoint, inputs, deadline):
        #get the qmatrix for easier access
        matrix=self.q_learner.q_matrix                
        
        #I will use strings and list comprehension to get the correct
        #state index from my q_matrix
        #to do that I need to ensure the inputs are not equal to None
        if next_waypoint==None:            
            nwp="wp_none"
        else:
            nwp="wp_"+next_waypoint

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
        x[0]==nwp 
        and x[1]==inputs['light']
        and x[2]==oncoming        
        and x[3]==left 
        and x[4]==right
        ]        
        #should be only one value in the result list     
        #it is a tuple (index, state)
        return filteredbywaypoint[0]
                
class Q_Learner:
    def __init__(self):
        self.learning_rate=0.5
        self.discount=.6
        self.prior_state=None
        self.q_matrix = Q_Matrix()
        
        #get the q value for state s and action a
    def q(self, s, a):
        #conveniently, states are tuples carrying their index as the first value        
        state= s[0]
        #resolve the index of the action using python's list.index()
        action= self.q_matrix.possible_actions.index(a)
        return self.q_matrix.matrix[state, action]
        
        #set the q value for state s and action a
    def setq(self, s, a, val):
        state= s[0]
        action= self.q_matrix.possible_actions.index(a)
        self.q_matrix.matrix[state, action]= val
        
        #get the maximum q value for the current state over all possible 
        #actions
    def maxFutureValue(self):
        state=self.current_state[0]
        row= np.argmax(self.q_matrix.matrix[state,:])
        return self.q_matrix.matrix[state, row]
        
        #get the action with the highest Q value based on the current state
    def maxFutureAction(self):
        state=self.current_state[0]
        row = self.q_matrix.matrix[state,:]
        index= np.argmax(row)        
        return index
        
        #apply Q learning update        
    def update(self):        
        old_value=self.q(self.prior_state,self.action)        
        #the q learning formula        
        result=  old_value+ self.learning_rate* (self.reward+self.discount*self.maxFutureValue() - old_value)
        self.setq(self.prior_state,self.action, result)            
        
#Chooses Actions based on q values with a epsilon chance 
# of taking a random action
class QValueRandomMixActionChooser():    
    def __init__(self, qlearner):        
        self.qlearner=qlearner
        self.epsilon= 0.05
        #first selection must be random because the q learner has not current state        
        #this is not optimal, should be fixed
        self.first=True
    def chooseAction(self):
       rnd= np.random.random_sample()
       if self.first:
           self.first=False
           rnd=-1
       if rnd>self.epsilon:
           index= self.qlearner.maxFutureAction()
           return self.qlearner.q_matrix.possible_actions[index]
       else:
           return self.qlearner.q_matrix.possible_actions[np.random.randint(0,4)]
        

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""
    
    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.successes=0
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint        
        self.learner=Q_Learner()
        self.mapper= StateMapper(self.learner)                        
        self.actionChooser= QValueRandomMixActionChooser(self.learner)
        self.negative_rewards=0

    def reset(self, destination=None):
        self.learner.prior_state=None
        self.actionChooser.first=True        
        self.planner.route_to(destination)
        
    def update(self, t):
        # Gather inputs
        learner= self.learner        
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        if learner.prior_state==None:
            learner.prior_state= self.mapper.mapDataToState(self.next_waypoint,inputs,deadline)           
            self.state=learner.prior_state[1]
        else:        
            learner.update()
            learner.prior_state=learner.current_state                
        
        # Select action according to your policy
        action= self.actionChooser.chooseAction()
        learner.action=action
        # Execute action and get reward
        learner.reward = self.env.act(self, action)
        if learner.reward<0:
            self.negative_rewards+=learner.reward
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        location = self.env.agent_states[self]["location"] 
        destination = self.env.agent_states[self]["destination"]
        inputs = self.env.sense(self)
        learner.current_state= self.mapper.mapDataToState(self.next_waypoint,inputs,deadline)
        self.state=learner.current_state[1]
        #keep track of how often we were successful for later evaluation        
        if location==destination:
            self.successes= self.successes+1

def run():
    """Run the agent for a finite number of trials."""

    #learning rate, discount, exploration value  
    #i could have written a loop to generate these, something smart like
    #grid search from sklearn but.. you know..sometimes.. ;-)  
    
    """final parameter set:
after running 100,000 trials I got an accuracy of 0.96141.
I think that is quite good. 
successrate: 0.96141 for params:[0.19, 0.25, 0.05]            
    """
    params=[[
        0.19, 0.25, 0.05
    ]]
    
    params=[]
    for i in range(0,10):
        p=[i/10.0,0.8,0]
        params.append(p)

    
    
    for paramset in params:
        # Set up environment and agent
        #learning rate, discount, exploration value    
          
        e = Environment()  # create environment (also adds some dummy traffic)
        a = e.create_agent(LearningAgent)  # create agent
        
        #set the q learning params
        a.learner.learning_rate=paramset[0]
        a.learner.discount=paramset[1]
        a.actionChooser.epsilon=paramset[2]


        e.set_primary_agent(a, enforce_deadline=False)  # specify agent to track
        # NOTE: You can set enforce_deadline=False while debugging to allow longer trials
    
        # Now simulate it
        sim = Simulator(e, update_delay=0, display=False)  # create simulator (uses pygame when display=True, if available)
        # NOTE: To speed up simulation, reduce update_delay and/or set display=False
    
        sim.run(n_trials=100)  # run for a specified number of trials
        # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line
        
        #save the matrix to a file        
        matrix= a.learner.q_matrix.matrix
        f = open('q_matrix.npy', 'w')    
        np.save(f,matrix)
        f.close()
        f = open('q_matrix.txt', 'w')    
        matrix.tofile(f, ";")
        f.close()
        print "successrate: {} for params:{}".format(a.successes/100.0, paramset)
        print "negative accumulated rewards:{}".format(a.negative_rewards)

if __name__ == '__main__':
    run()
