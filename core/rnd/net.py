import torch
import torch.nn as nn
import torch.optim as optim

class TargetNet(nn.Module):
  '''
  This class defines the networks used for the RND
  '''
  def __init__(self, output_shape, device=None, fixed=True):
    super(TargetNet, self).__init__()
    if device is not None:
      self.device = device
    else:
      self.device = torch.device("cpu")

    self.output_shape = output_shape
    self.hidden_dim = 16
    self.fixed = fixed

    self.subsample = nn.AvgPool2d(7)

    self.conv = nn.Sequential(nn.Conv2d(in_channels=3, out_channels=8, kernel_size=5, stride=2), nn.ReLU(),
                              nn.Conv2d(in_channels=8, out_channels=16, kernel_size=5, stride=2), nn.ReLU(),
                              nn.Conv2d(in_channels=16, out_channels=8, kernel_size=3), nn.ReLU())
    self.linear = nn.Sequential(nn.Linear(2312, 512), nn.Tanh(),
                                nn.Linear(512, 64), nn.Tanh(),
                                nn.Linear(64, 32))

    self.linear.apply(self.init_layers)

    self.to(device)
    for l in self.parameters():
      l.requires_grad = not self.fixed
    self.zero_grad()

  def init_layers(self, m):
    '''
    Initializes layer m with uniform distribution
    :param m: layer to initialize
    :return:
    '''
    if type(m) == nn.Linear:
      nn.init.normal_(m.weight)
    elif type(m) == nn.LSTM:
      nn.init.normal_(m.weight_ih_l0)
      nn.init.normal_(m.weight_hh_l0)

  def init_hidden(self, train=False):
    # The axes semantics are (num_layers, minibatch_size, hidden_dim)
    # For the target we init the hidden layers as zeros cause every run with the same inputs has to give the same result
    if not train:
      return (torch.zeros(1, 1, self.hidden_dim, device=self.device),
            torch.zeros(1, 1, self.hidden_dim, device=self.device))
    else:
      return (torch.zeros(1, self.batch_dim, self.hidden_dim, device=self.device),
              torch.zeros(1, self.batch_dim, self.hidden_dim, device=self.device))

  def forward(self, x, train=False):
    x = self.subsample(x)
    x = self.conv(x)
    x = x.view(x.size(0), -1)
    x = self.linear(x)
    return x


class PredictorNet(nn.Module):
  '''
  This class defines the networks used for the RND
  '''
  def __init__(self, output_shape, device=None, fixed=False):
    super(PredictorNet, self).__init__()
    if device is not None:
      self.device = device
    else:
      self.device = torch.device("cpu")

    self.output_shape = output_shape
    self.fixed = fixed

    self.subsample = nn.AvgPool2d(10)

    self.conv = nn.Sequential(nn.Conv2d(in_channels=3, out_channels=8, kernel_size=5, stride=2), nn.ReLU(),
                              nn.Conv2d(in_channels=8, out_channels=4, kernel_size=3), nn.ReLU())
    self.linear = nn.Sequential(nn.Linear(2704, 512), nn.Tanh(),
                                nn.Linear(512, 32))

    self.to(device)
    for l in self.parameters():
      l.requires_grad = not self.fixed
    self.zero_grad()

  def init_layers(self, m):
    '''
    Initializes layer m with uniform distribution
    :param m:
    :return:
    '''
    if type(m) == nn.Linear:
      nn.init.normal_(m.weight, mean=0, std=5)
    elif type(m) == nn.LSTM:
      nn.init.normal_(m.weight_ih_l0, mean=0, std=1)
      nn.init.normal_(m.weight_hh_l0, mean=0, std=1)

  def init_hidden(self, train=False):
    # The axes semantics are (num_layers, minibatch_size, hidden_dim)
    if not train:
      return (torch.zeros(1, 1, self.hidden_dim, device=self.device),
              torch.zeros(1, 1, self.hidden_dim, device=self.device))
    else:
      return (torch.zeros(1, self.batch_dim, self.hidden_dim, device=self.device),
              torch.zeros(1, self.batch_dim, self.hidden_dim, device=self.device))

  def forward(self, x, train=False):
    x = self.subsample(x)
    x = self.conv(x)
    x = x.view(x.size(0), -1)
    x = self.linear(x)

    try:
      assert not torch.isnan(x).any()
    except:
      print('Getting NAN.')
      raise
    return x
