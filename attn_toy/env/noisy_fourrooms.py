import numpy as np
import gym
from gym import spaces
from attn_toy.env.fourrooms import FourroomsNorender as Fourrooms


class ImageInputWarpper(gym.Wrapper):

    def __init__(self, env, max_steps=100):
        gym.Wrapper.__init__(self, env)
        screen_height = self.env.obs_height
        screen_width = self.env.obs_width
        self.observation_space = spaces.Box(low=0, high=255, shape=(screen_height, screen_width, 3), dtype=np.uint8)
        # self.num_steps = 0
        self.max_steps = max_steps
        # self.state_space_capacity = self.env.state_space_capacity
        self.mean_obs = None

    def step(self, action):
        state, reward, done, info = self.env.step(action)
        # self.num_steps += 1
        if self.num_steps >= self.max_steps:
            done = True
        obs = self.env.render(state)
        # print("step reporting",done)
        # if self.mean_obs is None:
        #     self.mean_obs = np.mean(obs)
        #     print("what is wrong?",self.mean_obs)
        # obs = obs - 0.5871700112336601
        # info['ori_obs'] = ori_obs
        info['s_tp1'] = state
        return obs, reward, done, info

    def reset(self, state=-1):
        if state < 0:
            state = np.random.randint(0, self.state_space_capacity)
        self.env.reset(state)
        # self.num_steps = self.env.num_steps
        obs = self.env.render(state)
        # print("reset reporting")
        # if self.mean_obs is None:
        #     self.mean_obs = np.mean(obs)
        # print("what is wrong? reset",self.mean_obs)
        # obs = obs - 0.5871700112336601
        # info['ori_obs'] = ori_obs
        return obs.astype(np.uint8)


class FourroomsDynamicNoise(Fourrooms):  # noise type = dynamic relevant
    def __init__(self, max_epilen=100, obs_size=128, seed=0):
        np.random.seed(seed)
        super(FourroomsDynamicNoise, self).__init__(max_epilen)
        self.obs_size = obs_size
        self.obs_height = obs_size
        self.obs_width = obs_size
        self.background = np.random.randint(0, 255, (10, 1, 1, 3))
        self.background[:, :, :, 2] = 0
        self.background = np.tile(self.background, (1, obs_size, obs_size, 1))
        self.seed = seed
        self.color = np.random.randint(100, 255, (200, 3))
        self.color[:, 2] = 100
        self.num_steps = 0
        self.observation_space = spaces.Discrete(self.num_pos * 3)
        self.state_space_capacity = self.observation_space.n

    def render(self, state=-1):
        which_background = state // self.num_pos
        # obs = np.zeros((self.obs_size, self.obs_size, 3))
        # obs[:12, :12, :] = self.color[state + 1]

        # obs = np.random.randint(0, 255, (self.obs_size, self.obs_size, 3))
        obs = np.tile(self.color[which_background][np.newaxis, np.newaxis, :], (self.obs_size, self.obs_size, 1))
        # obs = (state+100) * np.ones((self.obs_size,self.obs_size))

        arr = super(FourroomsDynamicNoise, self).render(state)
        padding_height, padding_width = (obs.shape[0] - arr.shape[0]) // 2, (obs.shape[1] - arr.shape[1]) // 2
        obs[padding_height:padding_height + arr.shape[0], padding_width:padding_width + arr.shape[1], :] = arr
        return obs.astype(np.uint8)

    def step(self, action):
        state, reward, done, info = super(FourroomsDynamicNoise, self).step(action)
        self.num_steps += 1
        state += self.num_pos * (self.num_steps % 3)
        return state, reward, done, info

    def reset(self, state=-1):
        self.num_steps = state % 3
        obs = super(FourroomsDynamicNoise, self).reset(state % self.num_pos)
        return state


class FourroomsDynamicNoise2(Fourrooms):  # noise type = state relevant
    def __init__(self, max_epilen=100, obs_size=128, seed=0):
        np.random.seed(seed)
        super(FourroomsDynamicNoise2, self).__init__(max_epilen)
        self.obs_size = obs_size
        self.obs_height = obs_size
        self.obs_width = obs_size
        self.background = np.random.randint(0, 255, (10, 1, 1, 3))
        self.background[:, :, :, 2] = 0
        self.background = np.tile(self.background, (1, obs_size, obs_size, 1))
        self.seed = seed
        self.color = np.random.randint(100, 255, (200, 3))
        self.color[:, 2] = 100
        self.num_steps = 0
        self.observation_space = spaces.Discrete(self.num_pos * max_epilen)
        self.state_space_capacity = self.num_pos * max_epilen
        self.last_action = -1

    def step(self, action):
        state, reward, done, info = super(FourroomsDynamicNoise2, self).step(action)
        self.num_steps += 1
        state += self.num_pos * self.num_steps
        return state, reward, done, info

    def reset(self, state=-1):
        self.num_steps = state // self.num_pos
        self.state = state
        obs = super(FourroomsDynamicNoise2, self).reset(state % self.num_pos)
        return state

    def render(self, state=-1):
        # which_background = self.num_steps % 3
        # obs = np.zeros((self.obs_size, self.obs_size, 3))
        # obs[:12, :12, :] = self.color[state + 1]
        obs = np.tile(self.color[self.num_steps + 1][np.newaxis, np.newaxis, :], (self.obs_size, self.obs_size, 1))
        # obs = np.random.randint(0, 255, (self.obs_size, self.obs_size, 3))
        # obs = np.tile(self.color[which_background][np.newaxis, np.newaxis, :], (self.obs_size, self.obs_size, 1))
        # obs = (state+100) * np.ones((self.obs_size,self.obs_size))

        arr = super(FourroomsDynamicNoise2, self).render(state % self.num_pos)
        padding_height, padding_width = (obs.shape[0] - arr.shape[0]) // 2, (obs.shape[1] - arr.shape[1]) // 2
        obs[padding_height:padding_height + arr.shape[0], padding_width:padding_width + arr.shape[1], :] = arr
        return obs.astype(np.uint8)


class FourroomsDynamicNoise3(Fourrooms):  # noise type = action relevant
    def __init__(self, max_epilen=100, obs_size=128, seed=0):
        np.random.seed(seed)
        super(FourroomsDynamicNoise3, self).__init__(max_epilen)
        self.obs_size = obs_size
        self.obs_height = obs_size
        self.obs_width = obs_size
        self.background = np.random.randint(0, 255, (10, 1, 1, 3))
        self.background[:, :, :, 2] = 0
        self.background = np.tile(self.background, (1, obs_size, obs_size, 1))
        self.seed = seed
        self.color = np.random.randint(100, 255, (200, 3))
        self.color[:, 2] = 100
        self.num_steps = 0
        self.observation_space = spaces.Discrete(self.num_pos * self.action_space.n)
        self.state_space_capacity = self.observation_space.n

    def render(self, state=-1):
        which_background = state // self.num_pos
        # obs = np.zeros((self.obs_size, self.obs_size, 3))
        # obs[:12, :12, :] = self.color[state + 1]
        # print(which_background, self.color[which_background])
        # obs = np.random.randint(0, 255, (self.obs_size, self.obs_size, 3))
        obs = np.tile(self.color[which_background][np.newaxis, np.newaxis, :], (self.obs_size, self.obs_size, 1))
        # obs = (state+100) * np.ones((self.obs_size,self.obs_size))

        arr = super(FourroomsDynamicNoise3, self).render(state)
        padding_height, padding_width = (obs.shape[0] - arr.shape[0]) // 2, (obs.shape[1] - arr.shape[1]) // 2
        obs[padding_height:padding_height + arr.shape[0], padding_width:padding_width + arr.shape[1], :] = arr
        return obs.astype(np.uint8)

    def step(self, action):
        state, reward, done, info = super(FourroomsDynamicNoise3, self).step(action)
        self.num_steps += 1
        state += self.num_pos * action
        # print("state in step",state)
        return state, reward, done, info

    def reset(self, state=-1):
        self.num_steps = state // self.num_pos
        obs = super(FourroomsDynamicNoise3, self).reset(state % self.num_pos)

        return state


class FourroomsRandomNoise(Fourrooms):  # noise type = random
    def __init__(self, max_epilen=100, obs_size=128, seed=0):
        np.random.seed(seed)
        super(FourroomsRandomNoise, self).__init__(max_epilen)
        self.obs_size = obs_size
        self.obs_height = obs_size
        self.obs_width = obs_size
        self.background = np.random.randint(0, 255, (10, 1, 1, 3))
        self.background[:, :, :, 2] = 0
        self.background = np.tile(self.background, (1, obs_size, obs_size, 1))
        self.seed = seed
        self.color = np.random.randint(100, 255, (200, 3))
        self.color[:, 2] = 100
        self.num_steps = 0
        self.rand_range = 4
        self.observation_space = spaces.Discrete(self.num_pos * self.rand_range)
        self.state_space_capacity = self.observation_space.n

    def render(self, state=-1):
        which_background = np.random.randint(0, self.rand_range)
        # obs = np.zeros((self.obs_size, self.obs_size, 3))
        # obs[:12, :12, :] = self.color[state + 1]

        # obs = np.random.randint(0, 255, (self.obs_size, self.obs_size, 3))
        obs = np.tile(self.color[which_background][np.newaxis, np.newaxis, :], (self.obs_size, self.obs_size, 1))
        # obs = (state+100) * np.ones((self.obs_size,self.obs_size))

        arr = super(FourroomsRandomNoise, self).render(state)
        padding_height, padding_width = (obs.shape[0] - arr.shape[0]) // 2, (obs.shape[1] - arr.shape[1]) // 2
        obs[padding_height:padding_height + arr.shape[0], padding_width:padding_width + arr.shape[1], :] = arr
        return obs.astype(np.uint8)

    def step(self, action):
        state, reward, done, info = super(FourroomsRandomNoise, self).step(action)
        self.num_steps += 1
        state += self.num_pos * action
        return state, reward, done, info

    def reset(self, state=-1):
        self.num_steps = state % 3
        obs = super(FourroomsRandomNoise, self).reset(state % self.num_pos)

        return state
