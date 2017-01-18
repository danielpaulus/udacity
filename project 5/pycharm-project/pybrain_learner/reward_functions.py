import numpy as np


def simpleRewardFunction(action, observation, edges):
    r = 0

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
