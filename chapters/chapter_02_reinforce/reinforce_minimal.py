"""Minimal REINFORCE implementation for CartPole-v1.

A direct, canonical translation of Chapter 2 (Code 2.1) from 'Foundations of
Deep Reinforcement Learning' (Graesser & Keng), modernized for Gymnasium.
Demonstrates vanilla policy gradient training without baseline variance reduction.
"""

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

DEFAULT_ENV_ID: str = "CartPole-v1"
DEFAULT_HIDDEN_DIM: int = 64
DEFAULT_GAMMA: float = 0.99
DEFAULT_LR: float = 0.01


class Pi(nn.Module):
    """Parameterized policy network for discrete action spaces (Code 2.1).

    Maps observation vectors to action logits via a two-layer multi-layer
    perceptron and stores on-policy episodic trajectory buffers.
    """

    def __init__(
        self, in_dim: int, out_dim: int, hidden_dim: int = DEFAULT_HIDDEN_DIM
    ) -> None:
        """Initialize policy network layers and episodic memory buffers.

        Args:
            in_dim: Dimension of the observation state vector.
            out_dim: Number of available discrete actions.
            hidden_dim: Number of hidden units in the linear layer. Defaults to
                DEFAULT_HIDDEN_DIM (64).
        """
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_dim),
        )
        self.log_probs: list[torch.Tensor] = []
        self.rewards: list[float] = []
        self.onpolicy_reset()
        self.train()

    def onpolicy_reset(self) -> None:
        """Clear stored episodic trajectory buffers."""
        self.log_probs = []
        self.rewards = []

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Compute unnormalized action logits for a given state tensor."""
        return self.model(x)

    def act(self, state: np.ndarray) -> int:
        """Sample an action stochastically and track its log probability.

        Args:
            state: Environment observation vector.

        Returns:
            Sampled discrete action index.
        """
        state_tensor = torch.as_tensor(state, dtype=torch.float32)
        logits = self.forward(state_tensor)
        dist = Categorical(logits=logits)
        action = dist.sample()

        log_prob = dist.log_prob(action)
        self.log_probs.append(log_prob)
        return int(action.item())


def train(
    pi: Pi, optimizer: optim.Optimizer, gamma: float = DEFAULT_GAMMA
) -> float:
    """Perform a vanilla REINFORCE policy gradient update on an episode.

    Computes discounted Monte Carlo returns without baseline subtraction,
    evaluates the policy gradient objective, and updates network parameters.

    Args:
        pi: Policy network containing recorded log probabilities and rewards.
        optimizer: PyTorch optimizer configured for the policy network.
        gamma: Discount factor for future rewards. Defaults to DEFAULT_GAMMA (0.99).

    Returns:
        Scalar loss value for the completed optimization step.
    """
    total_steps = len(pi.rewards)
    if total_steps == 0:
        return 0.0

    rets = np.empty(total_steps, dtype=np.float32)
    future_ret = 0.0
    for t in reversed(range(total_steps)):
        future_ret = pi.rewards[t] + gamma * future_ret
        rets[t] = future_ret

    returns_tensor = torch.as_tensor(rets, dtype=torch.float32)
    log_probs = torch.stack(pi.log_probs)

    # Negative log-likelihood weighted by return for gradient ascent
    loss = -(log_probs * returns_tensor).sum()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return float(loss.item())


def main(
    episodes: int = 300,
    lr: float = DEFAULT_LR,
    gamma: float = DEFAULT_GAMMA,
    env_name: str = DEFAULT_ENV_ID,
) -> Pi:
    """Train a minimal REINFORCE policy on CartPole-v1.

    Args:
        episodes: Maximum training episodes. Defaults to 300.
        lr: Learning rate for the Adam optimizer. Defaults to DEFAULT_LR (0.01).
        gamma: Discount factor. Defaults to DEFAULT_GAMMA (0.99).
        env_name: Gymnasium environment identifier. Defaults to DEFAULT_ENV_ID.

    Returns:
        The trained policy network instance.
    """
    env = gym.make(env_name)
    in_dim = env.observation_space.shape[0]
    out_dim = env.action_space.n
    pi = Pi(in_dim, out_dim)
    optimizer = optim.Adam(pi.parameters(), lr=lr)

    print(f"Starting Minimal REINFORCE training on {env_name}...")
    for epi in range(episodes):
        state, _ = env.reset()
        for _ in range(500):  # CartPole-v1 max timestep is 500
            action = pi.act(state)
            state, reward, terminated, truncated, _ = env.step(action)
            pi.rewards.append(float(reward))
            if terminated or truncated:
                break

        total_reward = sum(pi.rewards)
        loss = train(pi, optimizer, gamma=gamma)
        solved = total_reward >= 195.0
        pi.onpolicy_reset()

        if (epi + 1) % 10 == 0 or total_reward >= 450.0:
            print(
                f"Episode {epi + 1:3d} | Loss: {loss:8.2f} | "
                f"Total Reward: {total_reward:5.1f} | Solved (>=195): {solved}"
            )

        if total_reward >= 495.0:
            print(
                f"==> {env_name} consistently balanced (reward={total_reward:.1f}) "
                f"at episode {epi + 1}!"
            )
            break

    env.close()
    return pi


if __name__ == "__main__":
    main()
