"""Improved REINFORCE implementation for CartPole-v1.

Implements key algorithmic improvements from Chapter 2 of 'Foundations of
Deep Reinforcement Learning' (Graesser & Keng):
1. Action-independent baseline (return mean-centering / standardization) to
   reduce gradient variance (Sections 2.5.1 & 2.6.4).
2. Entropy bonus to encourage exploration and prevent premature policy
   collapse (Section 2.6.4).
"""

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

DEFAULT_ENV_ID: str = "CartPole-v1"
DEFAULT_HIDDEN_DIM: int = 64


class PolicyNet(nn.Module):
    """Parameterized neural network policy for discrete action spaces.

    Maps observation states to action logits via a multi-layer perceptron,
    and maintains rollout memory (log probabilities, entropies, rewards)
    for policy gradient updates.
    """

    def __init__(
        self, state_dim: int, action_dim: int, hidden_dim: int = DEFAULT_HIDDEN_DIM
    ) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
        )
        self.log_probs: list[torch.Tensor] = []
        self.entropies: list[torch.Tensor] = []
        self.rewards: list[float] = []
        self.reset_memory()

    def reset_memory(self) -> None:
        """Clear stored episodic rollout buffers."""
        self.log_probs = []
        self.entropies = []
        self.rewards = []

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Compute unnormalized action logits for a state tensor."""
        return self.net(x)

    def select_action(self, state: np.ndarray) -> int:
        """Sample an action stochastically and track policy distribution statistics.

        Args:
            state: Environment observation vector.

        Returns:
            Selected discrete action index.
        """
        state_t = torch.as_tensor(state, dtype=torch.float32)
        logits = self.forward(state_t)
        dist = Categorical(logits=logits)
        action = dist.sample()

        self.log_probs.append(dist.log_prob(action))
        self.entropies.append(dist.entropy())
        return int(action.item())


class REINFORCEAgent:
    """REINFORCE policy gradient agent with baseline and entropy regularizers.

    Coordinates policy execution, reward tracking, and policy gradient optimization
    using discounted Monte Carlo returns, variance-reduction baselines, and
    entropy bonuses.
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dim: int = DEFAULT_HIDDEN_DIM,
        gamma: float = 0.99,
        lr: float = 0.002,
        use_baseline: bool = True,
        entropy_coef: float = 0.001,
    ) -> None:
        """Initialize the REINFORCE agent and Adam optimizer.

        Args:
            state_dim: Dimension of the observation state vector.
            action_dim: Number of available discrete actions.
            hidden_dim: Number of hidden units in the policy network MLP.
                Defaults to DEFAULT_HIDDEN_DIM (64).
            gamma: Discount factor for future rewards. Defaults to 0.99.
            lr: Learning rate for the Adam optimizer. Defaults to 0.002.
            use_baseline: Whether to standardize returns for variance reduction.
                Defaults to True.
            entropy_coef: Coefficient weighting the entropy exploration bonus.
                Defaults to 0.001.
        """
        self.gamma = gamma
        self.use_baseline = use_baseline
        self.entropy_coef = entropy_coef
        self.policy = PolicyNet(state_dim, action_dim, hidden_dim=hidden_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)

    def step_action(self, state: np.ndarray) -> int:
        """Select a discrete action for the given state using the current policy."""
        return self.policy.select_action(state)

    def record_reward(self, reward: float) -> None:
        """Record a step reward into the current episodic rollout buffer."""
        self.policy.rewards.append(reward)

    def train_step(self) -> float:
        """Perform a policy gradient update step on the recorded episode rollout.

        Calculates discounted returns, applies baseline standardization if enabled,
        computes policy loss and entropy bonus, and steps the optimizer.

        Returns:
            Scalar total loss for the completed optimization step.
        """
        step_count = len(self.policy.rewards)
        if step_count == 0:
            return 0.0

        # Compute discounted returns Rt(tau)
        rets = np.empty(step_count, dtype=np.float32)
        future_ret = 0.0
        for t in reversed(range(step_count)):
            future_ret = self.policy.rewards[t] + self.gamma * future_ret
            rets[t] = future_ret

        returns_tensor = torch.as_tensor(rets, dtype=torch.float32)

        # Baseline: center returns to reduce variance (Section 2.5.1 & 2.6.4)
        if self.use_baseline and len(returns_tensor) > 1:
            returns_tensor = (returns_tensor - returns_tensor.mean()) / (
                returns_tensor.std() + 1e-8
            )

        log_probs = torch.stack(self.policy.log_probs)
        entropies = torch.stack(self.policy.entropies)

        # Policy loss: - E [ log pi(a|s) * R ] - entropy_coef * H(pi)
        policy_loss = -(log_probs * returns_tensor).sum()
        entropy_bonus = -self.entropy_coef * entropies.sum()
        total_loss = policy_loss + entropy_bonus

        self.optimizer.zero_grad()
        total_loss.backward()
        self.optimizer.step()

        self.policy.reset_memory()
        return float(total_loss.item())


def train_cartpole(
    episodes: int = 300,
    hidden_dim: int = DEFAULT_HIDDEN_DIM,
    use_baseline: bool = True,
    entropy_coef: float = 0.001,
    lr: float = 0.002,
    gamma: float = 0.99,
    seed: int = 42,
    verbose: bool = True,
    env_name: str = DEFAULT_ENV_ID,
) -> tuple[REINFORCEAgent, list[float], list[float]]:
    """Train a REINFORCE agent on CartPole-v1 until solved or max episodes reached.

    Args:
        episodes: Maximum training episodes to run. Defaults to 300.
        hidden_dim: Number of hidden units in the policy network MLP.
            Defaults to DEFAULT_HIDDEN_DIM (64).
        use_baseline: Whether to center/standardize returns. Defaults to True.
        entropy_coef: Coefficient for entropy bonus exploration. Defaults to 0.001.
        lr: Learning rate for Adam optimizer. Defaults to 0.002.
        gamma: Discount factor. Defaults to 0.99.
        seed: Random seed for PyTorch, NumPy, and environment. Defaults to 42.
        verbose: Whether to print progress logs. Defaults to True.
        env_name: Gymnasium environment identifier. Defaults to DEFAULT_ENV_ID.

    Returns:
        A tuple of (trained_agent, reward_history, moving_average_history).
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    env = gym.make(env_name)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    agent = REINFORCEAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        hidden_dim=hidden_dim,
        gamma=gamma,
        lr=lr,
        use_baseline=use_baseline,
        entropy_coef=entropy_coef,
    )

    reward_history: list[float] = []
    moving_avg_history: list[float] = []

    for ep in range(episodes):
        state, _ = env.reset(seed=seed + ep)
        ep_reward = 0.0

        while True:
            action = agent.step_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            agent.record_reward(float(reward))
            ep_reward += float(reward)
            state = next_state

            if terminated or truncated:
                break

        loss = agent.train_step()
        reward_history.append(ep_reward)

        window = reward_history[-min(len(reward_history), 20) :]
        moving_avg = float(np.mean(window))
        moving_avg_history.append(moving_avg)

        if verbose and ((ep + 1) % 25 == 0 or moving_avg >= 475.0):
            print(
                f"Episode {ep + 1:3d} | Total Reward: {ep_reward:5.1f} | "
                f"Moving Avg (20): {moving_avg:5.1f} | Loss: {loss:8.2f}"
            )

        if moving_avg >= 475.0:
            if verbose:
                print(
                    f"CartPole solved! 20-episode moving average reached {moving_avg:.1f} at episode {ep + 1}!"
                )
            break

    env.close()
    return agent, reward_history, moving_avg_history


def main() -> None:
    """Run an interactive demonstration training session."""
    print("Running Improved REINFORCE (with baseline centering & entropy bonus)...")
    train_cartpole(episodes=300, use_baseline=True, entropy_coef=0.001)


if __name__ == "__main__":
    main()
