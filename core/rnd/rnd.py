# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
import torch.optim as optim
from core.rnd.net import TargetNet, PredictorNet
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class RND(object):
  '''
  Class that instantiates the RND component
  '''
  def __init__(self, input_shape, encoding_shape, pop_size=10, device=None):
    self.input_shape = input_shape
    self.encoding_shape = encoding_shape
    self.device = device
    self.pop_size = pop_size
    # Nets
    self.target_model = TargetNet(self.input_shape, self.encoding_shape, pop_size=self.pop_size, device=self.device, fixed=True)
    self.predictor_model = PredictorNet(self.input_shape, self.encoding_shape, pop_size=self.pop_size, device=self.device, fixed=False)
    # Loss
    self.criterion = nn.MSELoss()
    # Optimizer
    self.learning_rate = 0.001
    self.optimizer = optim.Adam(self.predictor_model.parameters(), self.learning_rate)

  def _get_surprise(self, x, train=False):
    '''
    This function calculates the surprise given by the input
    :param x: Network input. Needs to be a torch tensor.
    :return: surprise as a 1 dimensional torch tensor
    '''
    target = self.target_model(x, train)
    prediction = self.predictor_model(x, train)
    return self.criterion(prediction, target)

  def get_bs_point(self, x):
    target = self.target_model(x, train=False)
    return target

  def __call__(self, x):
    return self._get_surprise(x)

  def training_step(self, x):
    '''
    This function performs the training step.
    :param x: Network input. Needs to be a torch tensor.
    :return: surprise as a 1 dimensional torch tensor
    '''
    self.optimizer.zero_grad()
    surprise = self._get_surprise(x, train=True)
    surprise.backward()
    # torch.nn.utils.clip_grad_norm_(self.predictor_model.parameters(), 0.1)
    self.optimizer.step()
    return surprise

  def save(self, filepath):
    save_ckpt = {
      'target_model': self.target_model.state_dict(),
      'predictor_model': self.predictor_model.state_dict(),
      'optimizer': self.optimizer.state_dict()
    }
    try:
      torch.save(save_ckpt, os.path.join(filepath, 'ckpt_rnd.pth'))
    except:
      print('Cannot save rnd networks.')




if __name__ == '__main__':
  device = torch.device('cpu')
  rnd = RND(6, 2, device)

  for _ in range(1000):
    x = torch.rand([1, 6])
    print(rnd.training_step(x))

  x = torch.Tensor([0.2, 0.4, 0.557, 0.36, 0, 1.5])
  print(rnd(x))

