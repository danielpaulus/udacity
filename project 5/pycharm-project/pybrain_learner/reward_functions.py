import numpy as np
import itertools

#thanks to: http://code.activestate.com/recipes/499304-hamming-distance/
def hamming(str1, str2):
  return sum(itertools.imap(str.__ne__, str1, str2))

def simpleRewardFunction(action, observation, last_action):
    r = 0

    #observation[0] is the waiting time over all lanes
    if observation[0] == 0:
        r += 1
    else:
        if observation[0] / 10 < 0.2:
            r += -.5

    if observation[0] / 10 > 0.5:
        r += -1
    r += 0.2 * action.count("g")
    r += -0.2 * action.count("r")
    return r




"""                traci.edge.getLastStepOccupancy(e_id),
                traci.edge.getLastStepVehicleNumber(e_id),
                traci.edge.getLastStepHaltingNumber(e_id)

        observation.append(vehicles_started_to_teleport)
        observation.append(emergency_stops)
"""
def secondRewardFunction(action, observation,last_action):
    if (last_action is None):
        return 0
    reward= -0.5*hamming(last_action, action)-2*observation[4]+ observation[0]/(observation[2]+0.1)

    return  reward
