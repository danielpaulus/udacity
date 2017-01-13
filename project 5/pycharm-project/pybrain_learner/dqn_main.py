
from sumo_environment import SumoEnv
from dqn_agent import Agent
import signal
import sys
import numpy as np
import pandas as pd
import ast

class config():
    def __init__(self,sumoBinary,sumoCmd, sumo_home=None):
        self.sumoBinary = sumoBinary
        self.sumoCmd = sumoCmd
        self.sumo_home = sumo_home


LinuxConfig = config(
    "/usr/bin/sumo",
    ["/usr/bin/sumo", "-c", "/home/ganjalf/sumo/rilsa/run.sumo.cfg"]
)

WinPythonPortableConfig = config(
    "E:\\Sumo\\bin\\sumo.exe",
    ["E:\\Sumo\\bin\\sumo.exe", "-c", "E:\\LuSTScenario\\scenario\\lust.net.xml"],
    "E:\\Sumo"
)

WinPythonPortableConfigGui = config(
    "E:\\Sumo\\bin\\sumo-gui.exe",
    ["E:\\Sumo\\bin\\sumo-gui.exe", "-c", "E:\\rilsa\\run.sumo.cfg"],
    "E:\\Sumo"
)

lust_file_name = "../../code/dataset-lust-tl-clusters.csv"

lust_raw_df = pd.read_csv(lust_file_name)

lust_raw_df['trafficlight_count'] = lust_raw_df['trafficlight_count'].map(lambda x: ast.literal_eval(x))
#find tls with 4 lanes and put them into (count, tl_id) tuples
traffic_lights= filter(lambda x: x[0]==4, lust_raw_df['trafficlight_count'])
traffic_lights= map(lambda x: (x[0],x[1]), traffic_lights)


# define the environment

#env = SumoEnv(LinuxConfig,number_of_lights_to_control)


env = SumoEnv(WinPythonPortableConfig,traffic_lights)
#env = SumoEnv(WinPythonPortableConfigGui,number_of_lights_to_control)

stateCnt = env.stateCnt
actionCnt = env.actionCnt

agents=[]
for i in range(len(traffic_lights)):
    agents.append( Agent(stateCnt, actionCnt))


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
steps=0
try:
    s = env.reset()
    R = 0

    while True:
        a = agent.act(s)
        steps+=1
        tlsid=None
        s_, r, done, info = env.step(a,tlsid)

        if done:  # terminal state
            s_ = None

        agent.observe((s, a, r, s_))
        agent.replay()

        s = s_
        R += r
        if steps%500==0:
            agent.brain.model.save("cartpole-basic.h5")
        if done:
            break

    print("Total reward:", R)

finally:
    agent.brain.model.save("cartpole-basic.h5")