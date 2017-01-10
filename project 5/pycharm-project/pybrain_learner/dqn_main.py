
from sumo_environment import SumoEnv
from dqn_agent import Agent



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
#env = SumoEnv(LinuxConfig)
#env = SumoEnv(WinPythonPortableConfig)
env = SumoEnv(WinPythonPortableConfigGui)

stateCnt = env.stateCnt
actionCnt = env.actionCnt

agent = Agent(stateCnt, actionCnt)

try:
    s = env.reset()
    R = 0

    while True:
        #env.render()

        a = agent.act(s)

        s_, r, done, info = env.step(a)

        if done:  # terminal state
            s_ = None

        agent.observe((s, a, r, s_))
        agent.replay()

        s = s_
        R += r

        if done:
            break

    print("Total reward:", R)

finally:
    agent.brain.model.save("cartpole-basic.h5")