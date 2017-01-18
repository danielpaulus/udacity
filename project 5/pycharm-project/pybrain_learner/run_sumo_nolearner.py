from sumo_environment import SumoEnv
import sys

max_num_steps=3500
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

env = SumoEnv(LinuxConfig, [])

for i in range(max_num_steps):
    env.step()

env.close()