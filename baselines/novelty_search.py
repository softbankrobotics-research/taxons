import numpy as np
from core.utils import utils
from baselines.baseline import BaseBaseline
import gc

class NoveltySearch(BaseBaseline):
  """
  Performs standard NS with handcrafted fetures
  """

  # ---------------------------------------------------
  def evaluate_agent(self, agent):
    """
    This function evaluates the agent in the environment. This function should be run in parallel
    :param agent: agent to evaluate
    :return:
    """
    done = False
    cumulated_reward = 0

    obs = self.env.reset()
    t = 0
    while not done:
      if 'FastsimSimpleNavigation' in self.params.env_tag:
        agent_input = [t/self.params.max_episode_len, obs] # Observation and time. The time is used to see when to stop the action. TODO move the action stopping outside of the agent
      elif 'Ant' in self.params.env_tag:
        agent_input = [t]
      else:
        agent_input = [t/self.params.max_episode_len]
      action = utils.action_formatting(self.params.env_tag, agent['agent'](agent_input))

      obs, reward, done, info = self.env.step(action)
      t += 1
      cumulated_reward += reward
      if t >= self.params.max_episode_len:
        done = True

      if 'Ant' in self.params.env_tag:
        CoM = np.array([self.env.robot.body_xyz[:2]])
        if np.any(np.abs(CoM) >= np.array([3, 3])):
          done = True

    agent['bs'] = utils.extact_hd_bs(self.env, obs, reward, done, info)
    agent['reward'] = cumulated_reward
    agent['features'] = [agent['bs'][0], None] # NS uses the actual position as feature to calculate the BD
    return cumulated_reward
  # ---------------------------------------------------











