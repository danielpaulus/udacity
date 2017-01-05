from sumo_task import SumoTask
from sumo_environment import SumoEnv
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import Q
from pybrain.rl.experiments import ContinuousExperiment
from pybrain.rl.explorers import EpsilonGreedyExplorer


# define action-value table
# number of states is:
#
#    current value: 1-21
#
# number of actions:
#
#    Stand=0, Hit=1

class config():
    def __init__(self,sumoBinary,sumoCmd):
        self.sumoBinary = sumoBinary
        self.sumoCmd = sumoCmd


LinuxConfig = config(
    "/usr/bin/sumo",
    ["/usr/bin/sumo", "-c", "/home/ganjalf/sumo/rilsa/run.sumo.cfg"]
)


# define the environment
env = SumoEnv(LinuxConfig)

# define the task
task = SumoTask(env)


av_table = ActionValueTable(task.outdim, task.indim)
av_table.initialize(0.)

# define Q-learning agent
learner = Q(0.5, 0.0)
learner._setExplorer(EpsilonGreedyExplorer(0.0))
agent = LearningAgent(av_table, learner)


# finally, define experiment
experiment = ContinuousExperiment(task, agent)

# ready to go, start the process
while True:
    experiment.doInteractionsAndLearn(1000)
