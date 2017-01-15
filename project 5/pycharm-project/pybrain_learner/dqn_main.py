from sumo_environment import SumoEnv
from dqn_agent import Agent
import signal
import sys
import numpy as np
import pandas as pd
import ast

#scenario="cgn"
scenario="lust"

class config():
    def __init__(self, sumoBinary, sumoCmd, sumo_home=None):
        self.sumoBinary = sumoBinary
        self.sumoCmd = sumoCmd
        self.sumo_home = sumo_home


LinuxConfig = config(
    "/usr/bin/sumo",
    ["/usr/bin/sumo","-c","/home/ganjalf/sumo/LuSTScenario/scenario/dua.static.sumocfg"]
#["/usr/bin/sumo", "-n", "/home/ganjalf/sumo/TAPASCologne-0.24.0/cologne.sumocfg", "--duration-log.statistics", "-l test.log"]
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
df=None
if scenario=="lust":
    lust_file_name = "../../code/dataset-lust-tl-clusters.csv"
    lust_raw_df = pd.read_csv(lust_file_name)
    lust_raw_df['trafficlight_count'] = lust_raw_df['trafficlight_count'].map(lambda x: ast.literal_eval(x))
    # find tls with 4 lanes and put them into (count, tl_id) tuples
    df=lust_raw_df
else:
    cgn_file_name = "../../code/dataset-cgn-tl-clusters.csv"
    cgn_raw_df = pd.read_csv(cgn_file_name)
    cgn_raw_df['trafficlight_count'] = cgn_raw_df['trafficlight_count'].map(lambda x: ast.literal_eval(x))
    df=cgn_raw_df

possible_clustering_results=['clusters_maxabs_3dimensions','clusters_robust_3dimensions','clusters_combined_3dimensions','clusters_combined_robust_3dimensions']
cl=possible_clustering_results[0]

traffic_light_counts_to_include=[4,6]
traffic_lights = filter(lambda x: x[1][0][0] in traffic_light_counts_to_include, df[['trafficlight_count',cl]].iterrows())
#traffic_lights[0][1][cl]
traffic_lights = map(lambda x: (x[0], x[1]), traffic_lights)


c= traffic_lights

#clusters=[(cluster_id, [tl_ids], tl_count)]



# define the environment

# env = SumoEnv(LinuxConfig,number_of_lights_to_control)


env = SumoEnv(LinuxConfig, traffic_lights)
# env = SumoEnv(WinPythonPortableConfigGui,number_of_lights_to_control)


agent_infos = []
for (cluster_id, tl_ids, count) in clusters:
    stateCnt = env.stateCnt(tl_ids[0])
    actionCnt = env.actionCnt(tl_ids[0])

    iniStates=[]
    for i in range(len(tl_ids)):
        iniStates.append(env.emptyState(tl_ids[0]))

    agent_infos.append(
        [
            Agent(stateCnt, actionCnt),
            tl_ids,
            iniStates,
            None
        ]
    )


"""
import signal
import time
def signal_handler(signal, frame):
        print('Manual abort...')
        global manual_stop
        manual_stop=True


signal.signal(signal.SIGINT, signal_handler)
global manual_stop
manual_stop=False
"""

steps = 0
try:
    R = 0

    while True:
        # let all agents perform their actions
        for agent_info in agent_infos:
            agent = agent_info[0]
            tl_id = agent_info[1]
            s = agent_info[2]
            action = agent.act(s)
            agent_info[3]= action
            env.setAction(action, tl_id)
        steps += 1

        # advance the simulation by one step
        env.step()

        # let all agents make their observations and learning
        for agent_info in agent_infos:
            agent = agent_info[0]
            tl_id = agent_info[1]
            s = agent_info[2]
            a=agent_info[3]
            s_, r, done, info = env.actionResults(tl_id)
            agent.observe((s, a, r, s_))
            agent.replay()
            agent_info[2] = s_

        if done:  # terminal state
            s_ = None

        if steps % 10000 == 0:
            env.close()
            agent.brain.model.save("sumo_brain.h5")
            break

        if done:
            break

finally:
    print "bye bye!"
