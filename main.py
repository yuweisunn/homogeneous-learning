import numpy as np
import pickle
from tensorflow.keras.datasets import mnist
from node import * 
from environment import *

np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) 

"""The Task for the AI
Our goal is to construct and train a local foundation model 
on thousands of images of handwritten digits so that it can 
successfully identify others when presented. The data that 
will be incorporated is the MNIST database which contains 
60,000 images for training and 10,000 test images. We will 
use TensorFlow as the backend.
"""

# Loading Training data from tensorflow keras
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = (x_train.astype('float32')/255.0).reshape(-1,28,28,1)
x_test = (x_test.astype('float32')/255.0).reshape(-1,28,28,1)


# Total Training Episodes 
EPISODES = 120

"""Exploration settings
Not a constant, going to be decayed
"""
epsilon = 1 
EPSILON_DECAY = 0.02


# Restart experiments
env = Env() 
agent = DQNAgent(env.ACTION_SPACE_SIZE)
ep_rewards = []
reward_list = []
starter = 0 # Set the starter node


# Iterate over episodes
for episode in range(1, EPISODES + 1):
    print("episode:%s" %episode)
    former_action = starter
    round = 0
    # Total actions of each step
    action_num = 1
    
    # Restarting episode - reset episode reward and step number
    episode_reward = 0
    # Reset environment and get initial state
    current_state = env.reset(x_train, y_train, x_test, y_test)
    # Reset flag and start iterating until episode ends
    done = False
    
    while not done:
        round =round+1
        action = []
        # If it is the first step, the starter node will be selected. 
        if round == 1: 
          action = [starter]
          print("================ %s =================" %action)

        # Policy Exploration
        # Based on the current epsilon, either a random action is 
        # performed or a DQN agent-based action is perfomed.   
        elif np.random.random() > epsilon: # Get an action from the DQN agent
            inference = agent.get_qs(current_state)

            for j in range(action_num):
              loc = list(inference).index(max(inference))
              action.append(loc)
              inference[loc] = min(inference) - 1
            print("================** %s **=================" %action)
        
        else: # Get a random action
            j = action_num
            while j > 0 :
              temp_action = np.random.randint(0, env.ACTION_SPACE_SIZE)
              if temp_action not in action:
                  action.append(temp_action)
                  j = j - 1
            print("================ %s =================" %action)

        new_state, reward, done = env.step(former_action, action, done)
        former_action = action[0]

        # Every step we update replay memory
        if round >1:
          agent.update_replay_memory((current_state.reshape(-1, 100), action, reward, new_state.reshape(-1, 100), done))

        # Transform new state and count reward
        current_state = new_state
        episode_reward += reward

        if done:
            print('Total training rewards: {} after n steps = {} with final reward = {}'.format(episode_reward, episode, reward))
            reward_list.append(episode_reward)
            # Save the training results for every 20 episodes
            if episode % 20 == 0:
                np.save('reward.npy', np.array((reward_list)), allow_pickle=True)
                np.save('acc.npy', env.acc_list, allow_pickle = True)

    # Every episode we train the DQN agent and decay epsilon
    agent.train()
    epsilon = epsilon * np.exp(-EPSILON_DECAY)
