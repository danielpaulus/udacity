from sumo_environment import SumoEnv
from dqn_agent import Agent
import signal
import sys
import numpy as np
import pandas as pd
import ast
import time

start_time = time.time()
max_num_steps=500
if len(sys.argv)==2:
    param= sys.argv[1]
    max_num_steps= int(param)



# scenario="cgn"
scenario = "lust"


class config():
    def __init__(self, sumoBinary, sumoCmd, sumo_home=None):
        self.sumoBinary = sumoBinary
        self.sumoCmd = sumoCmd
        self.sumo_home = sumo_home


LinuxConfig = config(
    "/usr/bin/sumo",
    ["/usr/bin/sumo", "-c", "/home/ganjalf/sumo/LuSTScenario/scenario/dua.static.sumocfg"]
    # ["/usr/bin/sumo", "-n", "/home/ganjalf/sumo/TAPASCologne-0.24.0/cologne.sumocfg", "--duration-log.statistics", "-l test.log"]
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
df = None
if scenario == "lust":
    lust_file_name = "../../code/dataset-lust-tl-clusters.csv"
    lust_raw_df = pd.read_csv(lust_file_name)
    lust_raw_df['trafficlight_count'] = lust_raw_df['trafficlight_count'].map(lambda x: ast.literal_eval(x))
    # find tls with 4 lanes and put them into (count, tl_id) tuples
    df = lust_raw_df
else:
    cgn_file_name = "../../code/dataset-cgn-tl-clusters.csv"
    cgn_raw_df = pd.read_csv(cgn_file_name)
    cgn_raw_df['trafficlight_count'] = cgn_raw_df['trafficlight_count'].map(lambda x: ast.literal_eval(x))
    df = cgn_raw_df

# set which clusters to use depending on the name of the columns
possible_clustering_results = ['clusters_maxabs_3dimensions', 'clusters_robust_3dimensions',
                               'clusters_combined_3dimensions', 'clusters_combined_robust_3dimensions']
cl = possible_clustering_results[0]

# set which traffic light counts/ junction sizes to use
traffic_light_counts_to_include = [4,6,7]

print "Running simulation scenario '{}' for trafficlight counts{}: and clustering result: {}".format(scenario, traffic_light_counts_to_include, cl)

# create an extra column only containing the number of traffic lights for the junctinos for easier access
df['tl_counts'] = df['trafficlight_count'].map(lambda x: x[0])

# filter the dataframe, take only the rows that are of specified size (number of traffic lights)
clusters = []
for tl_count in traffic_light_counts_to_include:
    filtered_df = df[df['tl_counts'] == tl_count]
    # group by cluster ids
    g = filtered_df.groupby(filtered_df[cl])
    # iterate through resulting groups
    for name, group in g:
        tl_ids = group['trafficlight_count'].map(lambda x: x[1])
        # save traffic light ids, grouped by clusters as a tuple and append to the clusters list
        # tuple is like (cluster_id, [tl_ids],  number of traffic lights)
        clusters.append((name, list(tl_ids), tl_count))

# traffic_lights[0][1][cl]
filtered_df= df[df['tl_counts'].isin(traffic_light_counts_to_include)]
traffic_lights = map(lambda x: (x[0], x[1]), filtered_df["trafficlight_count"] )

# clusters=[(cluster_id, [tl_ids], tl_count)]



# define the environment

# env = SumoEnv(LinuxConfig,number_of_lights_to_control)


env = SumoEnv(LinuxConfig, traffic_lights)
# env = SumoEnv(WinPythonPortableConfigGui,number_of_lights_to_control)


agent_infos = []
for (cluster_id, tl_ids, count) in clusters:

    stateCnt = env.stateCnt(tl_ids[0])
    actionCnt = env.actionCnt(tl_ids[0])
    print "setting up new agent traffic_light_count {} for cluster_id {} using trafficlight_ids:{} with statecnt {} and actioncnt {}".format(count,
                                                                                                           cluster_id,
                                                                                                           tl_ids, stateCnt, actionCnt)
    iniStates = []
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

brainFileName="scen_{}_sizes_{}_cluster_{}_iterations_{}_sumo_brain.h5".format(scenario,traffic_light_counts_to_include,cl,max_num_steps)


steps = 0
try:
    R = 0

    while True:
        # let all agents perform their actions
        for agent_info in agent_infos:
            agent = agent_info[0]
            tl_id_list = agent_info[1]
            state_list = agent_info[2]
            action_list=[]
            #set an action for each controlled junction in the agents cluster
            for i, tl_id in enumerate(tl_id_list):
                action = agent.act(state_list[i])
                env.setAction(action, tl_id)
                action_list.append(action)

            agent_info[3] = action_list

        steps += 1

        # advance the simulation by one step
        env.step()

        # let all agents make their observations and learning
        for agent_info in agent_infos:
            agent = agent_info[0]
            tl_id_list = agent_info[1]
            state_list = agent_info[2]
            action_list = agent_info[3]
            new_state_list=[]
            for i, tl_id in enumerate(tl_id_list):
                s=state_list[i]
                a=action_list[i]
                s_, r, done, info = env.actionResults(tl_id)
                agent.observe((s, a, r, s_))
                agent.replay()
                new_state_list.append(s_)
            agent_info[2] = new_state_list

        if done:  # terminal state
            s_ = None

        if steps == max_num_steps:
            env.close()
            agent.brain.model.save(brainFileName)
            break

        if done:
            break

finally:
    print "bye bye!"

elapsed_time = time.time() - start_time
print "elapsed time: {}s".format(elapsed_time)