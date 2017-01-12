
from sumo_environment import SumoEnv
from dqn_agent import Agent
import signal
import sys


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
    ["E:\\Sumo\\bin\\sumo.exe", "-c", "E:\\rilsa\\run.sumo.cfg"],
    "E:\\Sumo"
)

WinPythonPortableConfigGui = config(
    "E:\\Sumo\\bin\\sumo-gui.exe",
    ["E:\\Sumo\\bin\\sumo-gui.exe", "-c", "E:\\rilsa\\run.sumo.cfg"],
    "E:\\Sumo"
)

# define the environment
number_of_lights_to_control=2
#env = SumoEnv(LinuxConfig,number_of_lights_to_control)
env = SumoEnv(WinPythonPortableConfig,number_of_lights_to_control)
#env = SumoEnv(WinPythonPortableConfigGui,number_of_lights_to_control)

stateCnt = env.stateCnt
actionCnt = env.actionCnt

agent = Agent(stateCnt, actionCnt)


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
        s_, r, done, info = env.step(a)

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