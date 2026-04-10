import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
import numpy as np
from collections import deque

# ==========================================
# THE DEEP Q-NETWORK (The Neural Brain)
# ==========================================
class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        # Input layer looks at the intersection state (e.g., queues in all 4 directions)
        self.fc1 = nn.Linear(state_size, 24) 
        # Hidden layer to find complex traffic patterns
        self.fc2 = nn.Linear(24, 24)
        # Output layer gives a "score" for each possible action
        self.fc3 = nn.Linear(24, action_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

# ==========================================
# THE RL AGENT (The Player)
# ==========================================
class TrafficAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        
        # Memory to remember past traffic scenarios and learn from them
        self.memory = deque(maxlen=2000)
        
        # Hyperparameters (How the AI learns)
        self.gamma = 0.95           # Discount rate (cares about future rewards)
        self.epsilon = 1.0          # Exploration rate (starts by doing random things to learn)
        self.epsilon_min = 0.01     # Never stops exploring 1% of the time
        self.epsilon_decay = 0.995  # Gradually stops guessing and starts using its brain
        self.learning_rate = 0.001

        # The actual PyTorch Model
        self.model = DQN(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def remember(self, state, action, reward, next_state, done):
        """Saves a memory of what happened to train on later."""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """Decides whether to guess randomly or use the neural network."""
        # Random guess (Exploration)
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        # Ask the Neural Network (Exploitation)
        state_tensor = torch.FloatTensor(state)
        with torch.no_grad():
            action_values = self.model(state_tensor)
        return torch.argmax(action_values).item()

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            # 1. Prepare tensors and ensure they have a batch dimension (1, state_size)
            state_tensor = torch.FloatTensor(state).view(1, -1)
            next_state_tensor = torch.FloatTensor(next_state).view(1, -1)
            
            # 2. Get current predicted Q-values
            target_f = self.model(state_tensor) # Expected shape: [1, 2]
            
            # 3. Calculate the new target value
            target = reward
            if not done:
                # target = reward + gamma * max(predicted Q-values of next state)
                with torch.no_grad():
                    target = reward + self.gamma * torch.max(self.model(next_state_tensor)).item()
            
            # 4. Create a copy of the predictions to modify
            target_values = target_f.clone().detach()
            
            # 5. Update the value for the action we actually took
            # .view(-1) turns [[a, b]] into [a, b] so we can index it safely
            target_values[0][action] = target
            
            # 6. Training Step
            self.optimizer.zero_grad()
            current_output = self.model(state_tensor)
            loss = self.criterion(current_output, target_values)
            loss.backward()
            self.optimizer.step()

        # Decay exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay