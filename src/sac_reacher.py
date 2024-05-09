# import os
# import random
# import numpy as np
# import gymnasium as gym

# import torch
# import torch.nn as nn
# import torch.optim as optim
# import torch.nn.functional as F
# from torch.distributions import Normal

# import matplotlib.pyplot as plt

# GPU = True
# device_idx = 0
# if GPU:
#     device = torch.device("cuda:" + str(device_idx) if torch.cuda.is_available() else "cpu")
# else:
#     device = torch.device("cpu")
# print(device)

# class ReplayBuffer:
#     def __init__(self, capacity):
#         self.capacity = capacity
#         self.buffer = []
#         self.position = 0

#     def push(self, state, action, reward, next_state, done):
#         if len(self.buffer) < self.capacity:
#             self.buffer.append(None)
#         self.buffer[self.position] = (state, action, reward, next_state, done)
#         self.position = (self.position + 1) % self.capacity

#     def sample(self, batch_size):
#         batch = random.sample(self.buffer, batch_size)
#         state, action, reward, next_state, done = map(np.stack, zip(*batch))

#         return state, action, reward, next_state, done
    
#     def __len__(self):
#         return len(self.buffer)


# class ValueNetwork(nn.Module):
#     def __init__(self, state_dim, hidden_dim, activation = F.relu, init_w = 3e-3):
#         super(ValueNetwork, self).__init__()

#         self.linear1 = nn.Linear(state_dim, hidden_dim)
#         self.linear2 = nn.Linear(hidden_dim, hidden_dim)
#         self.linear3 = nn.Linear(hidden_dim, 1)

#         # weights initialization
#         self.linear3.weight.data.uniform_(-init_w, init_w)
#         self.linear3.bias.data.uniform_(-init_w, init_w)

#         self.activation = activation

#     def forward(self, state):
#         x = self.activation(self.linear1(state))
#         x = self.activation(self.linear2(x))
#         x = self.linear3(x)

#         return x
    
# class SoftQNetwork(nn.Module):
#     def __init__(self, num_inputs, num_actions, hidden_size, activation = F.relu, init_w = 3e-3):
#         super(SoftQNetwork, self).__init__()

#         self.linear1 = nn.Linear(num_inputs + num_actions, hidden_size)
#         self.linear2 = nn.Linear(hidden_size, hidden_size)
#         self.linear3 = nn.Linear(hidden_size, 1)

#         self.linear3.weight.data.uniform_(-init_w, init_w)
#         self.linear3.bias.data.uniform_(-init_w, init_w)

#         self.activation = activation

#     def forward(self, state, action):
#         x = torch.cat([state, action], 1) # the dim 0 is number of samples
#         x = self.activation(self.linear1(x))
#         x = self.activation(self.linear2(x))
#         x = self.linear3(x)

#         return x
    
# class PolicyNetwork(nn.Module):
#     def __init__(self, num_inputs, num_actions, hidden_size, activation=F.relu, init_w=3e-3, log_std_min=-20, log_std_max=2):
#         super(PolicyNetwork, self).__init__()

#         self.log_std_min = log_std_min
#         self.log_std_max = log_std_max

#         self.linear1 = nn.Linear(num_inputs, hidden_size)
#         self.linear2 = nn.Linear(hidden_size, hidden_size)
#         self.linear3 = nn.Linear(hidden_size, hidden_size)
#         self.linear4 = nn.Linear(hidden_size, hidden_size)

#         self.mean_linear = nn.Linear(hidden_size, num_actions) # output: action
#         self.mean_linear.weight.data.uniform_(-init_w, init_w)
#         self.mean_linear.bias.data.uniform_(-init_w, init_w)

#         self.log_std_linear = nn.Linear(hidden_size, num_actions) # output: action
#         self.log_std_linear.weight.data.uniform_(-init_w, init_w)
#         self.log_std_linear.bias.data.uniform_(-init_w, init_w)

#         self.action_range = 10.
#         self.num_actions = num_actions
#         self.activation = activation

#     def forward(self, state):
#         x = self.activation(self.linear1(state))
#         x = self.activation(self.linear2(x))
#         x = self.activation(self.linear3(x))
#         x = self.activation(self.linear4(x))

#         mean = self.mean_linear(x)
#         log_std = self.log_std_linear(x)
#         log_std = torch.clamp(log_std, self.log_std_min, self.log_std_max)

#         return mean, log_std

#     def evaluate(self, state, epsilon = 1e-6):
#         mean, log_std = self.forward(state)
#         std = log_std.exp()

#         normal   = Normal(0,1)
#         z        = normal.sample(mean.shape)
#         action_0 = torch.tanh(mean + std * z.to(device))
#         action   = self.action_range * action_0

#         log_prob = Normal(mean,std).log_prob(mean + std * z.to(device)) - torch.log(1. - action_0.pow(2) + epsilon) -  np.log(self.action_range)

#         log_prob = log_prob.sum(dim = -1, keepdim = True)

#         return action, log_prob, z, mean, log_std
    
#     def get_action(self, state):
#         state         = torch.FloatTensor(state).unsqueeze(0).to(device)
#         mean, log_std = self.forward(state)
#         std           = log_std.exp()

#         normal = Normal(0,1)
#         z      = normal.sample(mean.shape).to(device)
#         action = self.action_range * torch.tanh(mean + std * z)
#         action = action.detach().cpu().numpy()[0]

#         return action
    
#     def sample_action(self,):
#         a = torch.FloatTensor(self.num_actions).uniform_(-1, 1)
#         return (self.action_range * a).numpy()
    
# def update(batch_size, reward_scale, gamma=0.95,soft_tau=1e-2):
#     alpha = 1.0  # trade-off between exploration (max entropy) and exploitation (max Q)
    
#     state, action, reward, next_state, done = replay_buffer.sample(batch_size)
#     # print('sample:', state, action,  reward, done)

#     state      = torch.FloatTensor(state).to(device)
#     next_state = torch.FloatTensor(next_state).to(device)
#     action     = torch.FloatTensor(action).to(device)
#     reward     = torch.FloatTensor(reward).unsqueeze(1).to(device)  # reward is single value, unsqueeze() to add one dim to be [reward] at the sample dim;
#     done       = torch.FloatTensor(np.float32(done)).unsqueeze(1).to(device)

#     predicted_q_value1 = soft_q_net1(state, action)
#     predicted_q_value2 = soft_q_net2(state, action)
#     predicted_value    = value_net(state)
#     new_action, log_prob, z, mean, log_std = policy_net.evaluate(state)

#     # reward = reward_scale*(reward - reward.mean(dim=0)) /reward.std(dim=0) # normalize with batch mean and std

#     # Training Q Function
#     target_value = target_value_net(next_state)
#     target_q_value = reward + (1 - done) * gamma * target_value # if done==1, only reward
#     q_value_loss1 = soft_q_criterion1(predicted_q_value1, target_q_value.detach())  # detach: no gradients for the variable
#     q_value_loss2 = soft_q_criterion2(predicted_q_value2, target_q_value.detach())


#     soft_q_optimizer1.zero_grad()
#     q_value_loss1.backward()
#     soft_q_optimizer1.step()
#     soft_q_optimizer2.zero_grad()
#     q_value_loss2.backward()
#     soft_q_optimizer2.step()  

#     # Training Value Function
#     predicted_new_q_value = torch.min(soft_q_net1(state, new_action),soft_q_net2(state, new_action))
#     target_value_func = predicted_new_q_value - alpha * log_prob # for stochastic training, it equals to expectation over action
#     value_loss = value_criterion(predicted_value, target_value_func.detach())

    
#     value_optimizer.zero_grad()
#     value_loss.backward()
#     value_optimizer.step()

#     # Training Policy Function
#     ''' implementation 1 '''
#     policy_loss = (alpha * log_prob - predicted_new_q_value).mean()
#     ''' implementation 2 '''
#     # policy_loss = (alpha * log_prob - soft_q_net1(state, new_action)).mean()  # Openai Spinning Up implementation
#     ''' implementation 3 '''
#     # policy_loss = (alpha * log_prob - (predicted_new_q_value - predicted_value.detach())).mean() # max Advantage instead of Q to prevent the Q-value drifted high

#     ''' implementation 4 '''  # version of github/higgsfield
#     # log_prob_target=predicted_new_q_value - predicted_value
#     # policy_loss = (log_prob * (log_prob - log_prob_target).detach()).mean()
#     # mean_lambda=1e-3
#     # std_lambda=1e-3
#     # mean_loss = mean_lambda * mean.pow(2).mean()
#     # std_loss = std_lambda * log_std.pow(2).mean()
#     # policy_loss += mean_loss + std_loss


#     policy_optimizer.zero_grad()
#     policy_loss.backward()
#     policy_optimizer.step()
    
#     # print('value_loss: ', value_loss)
#     # print('q loss: ', q_value_loss1, q_value_loss2)
#     # print('policy loss: ', policy_loss )


#     # Soft update the target value net
#     for target_param, param in zip(target_value_net.parameters(), value_net.parameters()):
#         target_param.data.copy_(  # copy data value into target parameters
#             target_param.data * (1.0 - soft_tau) + param.data * soft_tau
#         )
#     return predicted_new_q_value.mean()


# def plot(rewards):
#     # clear_output(True)
#     plt.figure(figsize=(800,10))
#     fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
#     ax1.plot(rewards)
#     ax2.plot(rewards)

#     ax1.set_ylim(-100, 20)
#     ax2.set_ylim(-7000,-500)

#     ax1.spines['bottom'].set_visible(False)
#     ax2.spines['top'].set_visible(False)
#     ax1.xaxis.tick_top()
#     ax1.tick_params(labeltop=False)
#     ax2.xaxis.tick_bottom()

#     kwargs = dict(marker=[(-1, -0.5), (1, 0.5)], markersize=12,
#               linestyle="none", color='k', mec='k', mew=1, clip_on=False)
#     ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
#     ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

#     # plt.plot(rewards)
#     ax2.set_xlabel('Episode #')
#     fig.text(0.02, 0.50, "Reward", va='center', rotation = 'vertical', fontsize = 16)
#     ax1.set_title('Reward of Each Episode')
#     ax1.grid(True)
#     ax2.grid(True)
#     plt.savefig('sac_reacher1.png')
#     # plt.show()

# '''
# Reacher:
#     https://gymnasium.farama.org/environments/mujoco/reacher/
#     Reacher is a two-jointed robot arm.
#     The goal is to move the robot's end-effector (called fingertip) close to a target that is spawned at a random position!
# '''
# env = gym.make('Reacher-v4', render_mode="human")

# total_num_episodes = int(5e3)
# action_dim = env.action_space.shape[0] # 2
# state_dim = env.observation_space.shape[0] # 11

# rewards_over_seeds = []

# hidden_dim = 512

# value_net        = ValueNetwork(state_dim, hidden_dim, activation=F.relu).to(device)
# target_value_net = ValueNetwork(state_dim, hidden_dim, activation=F.relu).to(device)

# soft_q_net1 = SoftQNetwork(state_dim, action_dim, hidden_dim, activation=F.relu).to(device)
# soft_q_net2 = SoftQNetwork(state_dim, action_dim, hidden_dim, activation=F.relu).to(device)
# policy_net = PolicyNetwork(state_dim, action_dim, hidden_dim, activation=F.relu).to(device)

# print('(Target) Value Network: ', value_net)
# print('Soft Q Network (1,2): ', soft_q_net1)
# print('Policy Network: ', policy_net)


# for target_param, param in zip(target_value_net.parameters(), value_net.parameters()):
#     target_param.data.copy_(param.data)

# value_criterion  = nn.MSELoss()
# soft_q_criterion1 = nn.MSELoss()
# soft_q_criterion2 = nn.MSELoss()

# value_lr  = 3e-4
# soft_q_lr = 3e-4
# policy_lr = 3e-4

# value_optimizer  = optim.Adam(value_net.parameters(), lr=value_lr)
# soft_q_optimizer1 = optim.Adam(soft_q_net1.parameters(), lr=soft_q_lr)
# soft_q_optimizer2 = optim.Adam(soft_q_net2.parameters(), lr=soft_q_lr)
# policy_optimizer = optim.Adam(policy_net.parameters(), lr=policy_lr)


# replay_buffer_size = int(1e6)
# replay_buffer = ReplayBuffer(replay_buffer_size)

# # hyper-parameters
# max_episodes   = 1000
# max_steps      = 50
# frame_idx      = 0
# batch_size     = 256
# explore_steps  = 0
# rewards        = []
# reward_scale   = 10.0
# model_path     = 'model/sac/sac_reacher1.pth'

# # training loop
# for eps in range(max_episodes):
#     state, _ = env.reset()

#     episode_reward = 0
    
    
#     for step in range(max_steps):
#         if frame_idx >= explore_steps:
#             action = policy_net.get_action(state)
#         else:
#             action = policy_net.sample_action()

#         next_state, reward, terminated, truncated, info = env.step(action)
#         done = terminated or truncated

#         env.render()

#         replay_buffer.push(state, action, reward, next_state, done)
        
#         state = next_state
#         episode_reward += reward
#         frame_idx += 1
        
#         if len(replay_buffer) > batch_size:
#             _ = update(batch_size, reward_scale)
        
#         if done:
#             break

#     if eps % 20 == 0 and eps>0:
#         plot(rewards)
#         torch.save(policy_net.state_dict(), os.path.join(model_path))

#     print('Episode: ', eps, '| Episode Reward: ', episode_reward)
#     rewards.append(episode_reward)
# torch.save(policy_net.state_dict(), os.path.join(model_path))

# test loop
# policy_net.load_state_dict(torch.load(os.path.join(model_path)))
# policy_net.eval()
# for eps in range(10):
#     state, _ = env.reset()
#     episode_reward = 0

#     for step in range(max_steps):
#         action = policy_net.get_action(state)
#         next_state, reward, terminated, truncated, info = env.step(action)
#         done = terminated or truncated
#         env.render() 

#         episode_reward += reward
#         state = next_state

#     print('Episode: ', eps, '| Episode Reward: ', episode_reward)


##############################################################################################
##############################################################################################

import gymnasium as gym

from stable_baselines3 import SAC

env = gym.make("Reacher-v4", render_mode="human")

model = SAC("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=1e6, log_interval=4)
model.train(batch_size=256)
model.save("sac_reacher_stbl")

# del model # remove to demonstrate saving and loading

model = SAC.load("sac_reacher_stbl")

obs, info = env.reset()

episode_rewards = []
episode_reward = 0

while True:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    episode_reward += reward
    print(episode_reward)
    if terminated or truncated:
        print(episode_reward)
        episode_rewards.append(episode_reward)
        episode_reward = 0
        obs, info = env.reset()
    

