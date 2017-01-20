
"""
Sadly, traci has no method to gather aggregated simulation statistics
That's why I wrote this simple parser.

"""
import pandas as pd
import re
import glob


def to_number(n):
    if not n.strip():
        return 0
    try:
        return  float(n)
    except:
        return n.strip()

def processEntry(entry):
    lines = entry.split("\n")
    lines = filter(lambda x: x != '', lines)
    splitted = map(lambda x: [x.split(":")[0].strip(), x.split(":")[1].strip()], lines)
    values = map(lambda x: to_number(x[1]), splitted)
    labels= map(lambda x: x[0], splitted)
    dict={}
    for l, v in zip(labels, values):
        dict[l]=v
    return dict

def processSections(sections, rows):
    for section in sections:
        simulation_steps=section[0:section.index(" steps")]
        # I admit this code is beyond lazy.. ;-)

        if section.find("Simulation ended at time:")==-1:
            continue

        if section.find("applied full dqn algorithm")==-1:
            dqn="simple"
        else:
            dqn="full"

        position= re.search("trafficlight counts\[.*\]", section).regs[0]
        lights= section[position[0]+19:position[1]]
        position= re.search("scenario \'.*\'",section).regs[0]
        scenario = section[position[0] + 9:position[1]].replace("\'",'')
        position= re.search("clustering result: .*",section).regs[0]
        cluster=section[position[0] + 19:position[1]]
        position = re.search("reward function used:.*", section).regs[0]
        rewardfunction=section[position[0] + 21:position[1]]
        entry= section.split("Simulation ended at time:")[1]
        entry= entry.split("\n\n")[0]
        entry= entry[entry.index("\n")+1:]
        entry = entry.replace("ms\n","\n")
        entry = entry.replace("Vehicles: \n","")
        entry = entry.replace("Performance: \n", "")
        entry = entry.replace("Statistics (avg):\n", "")
        entry=entry.replace("Inserted","vehicles_inserted")
        entry = entry.replace("(Loaded:","\nvehicles_loaded:")
        entry = entry.replace("(Collisions:","\nCollisions:")
        entry = entry.replace(")", "")

        row= processEntry(entry)
        row["simulation_steps"] = simulation_steps
        row["traffic_light_counts"]= lights
        row["scenario"] = scenario
        row["clustering_algorithm"] = cluster
        row["reward_function"] = rewardfunction
        row["dqn"]=dqn

        rows.append(row)


path = "/home/ganjalf/Documents/project 5 brains/*.txt"
rows=[]
for filename in glob.glob(path):
    with open(filename, 'r') as file:
        content= file.read()
        sections= content.split("Running simulation(")
        del sections[0]
        processSections(sections, rows)



df= pd.DataFrame(rows)

df.to_csv("../../reinforcement-result-analysis/simulation-statistics.csv")