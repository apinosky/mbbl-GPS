""" This file defines the replay buffer. """
import logging

import random

LOGGER = logging.getLogger(__name__)


class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0

    def push(self, sample_list):
        for samples in sample_list:
            if len(self.buffer) < self.capacity:
                self.buffer.append(None)
            self.buffer[self.position] = samples
            self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)
