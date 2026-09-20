"""
Comparative experiment script for REINFORCE on CartPole-v1.
Directly reproduces the comparison in Chapter 2 (Section 2.8.2 / Figure 2.4):
- Baseline (Centered returns) vs No Baseline
- Generates a comparison plot 'reinforce_comparison.png'
- Evaluates the trained agent on test episodes
"""

from pathlib import Path

import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import torch

try:
    from .reinforce_improved import train_cartpole
except ImportError:
    from reinforce_improved import train_cartpole

# Directory paths
MODULE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = MODULE_DIR / "artifacts"


def evaluate_agent(agent, num_episodes: int = 10, render: bool = False):
    render_mode = "human" if render else None
    env = gym.make("CartPole-v1", render_mode=render_mode)
    eval_rewards = []

    for ep in range(num_episodes):
        state, _ = env.reset(seed=1000 + ep)
        ep_reward = 0.0
        while True:
            state_t = torch.as_tensor(state, dtype=torch.float32)
            with torch.no_grad():
                logits = agent.policy(state_t)
                action = torch.argmax(logits).item()  # greedy action for eval
            state, reward, terminated, truncated, _ = env.step(action)
            ep_reward += reward
            if terminated or truncated:
                break
        eval_rewards.append(ep_reward)

    env.close()
    return np.mean(eval_rewards), np.std(eval_rewards)


def run_comparative_experiment():
    print("=" * 60)
    print("Recreating Chapter 2 Experiment: Baseline vs No Baseline")
    print("=" * 60)

    episodes = 250
    seed = 42

    print("\n--- Training WITHOUT Baseline (Raw Returns) ---")
    _, raw_rewards, raw_ma = train_cartpole(
        episodes=episodes,
        use_baseline=False,
        entropy_coef=0.0,
        lr=0.005,
        seed=seed,
        verbose=True
    )

    print("\n--- Training WITH Baseline (Centered/Standardized Returns) ---")
    agent_with_bl, bl_rewards, bl_ma = train_cartpole(
        episodes=episodes,
        use_baseline=True,
        entropy_coef=0.001,
        lr=0.005,
        seed=seed,
        verbose=True
    )

    # Plot results to match Figure 2.4
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # (a) Episode Rewards
    ax1.plot(raw_rewards, label="Without Baseline", alpha=0.45, color="coral")
    ax1.plot(bl_rewards, label="With Baseline", alpha=0.45, color="teal")
    ax1.plot(raw_ma, label="Without Baseline (MA 20)", color="darkred", linewidth=2)
    ax1.plot(bl_ma, label="With Baseline (MA 20)", color="darkslategray", linewidth=2)
    ax1.set_title("(a) Episode Rewards & Moving Average")
    ax1.set_xlabel("Episode")
    ax1.set_ylabel("Total Reward")
    ax1.axhline(195.0, color="grey", linestyle="--", alpha=0.7, label="Solved threshold (195)")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # (b) Moving Average Comparison
    ax2.plot(raw_ma, label="Without Baseline", color="darkred", linewidth=2)
    ax2.plot(bl_ma, label="With Baseline", color="teal", linewidth=2)
    ax2.set_title("(b) Smoothed Return Comparison (MA Window 20)")
    ax2.set_xlabel("Episode")
    ax2.set_ylabel("Mean Return (MA)")
    ax2.axhline(195.0, color="grey", linestyle="--", alpha=0.7, label="Solved threshold (195)")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    plt.suptitle("REINFORCE on CartPole-v1: Effect of Baseline (Chapter 2 Reproduction)", fontsize=14)
    plt.tight_layout()
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    plot_filename = str(ARTIFACTS_DIR / "reinforce_comparison.png")
    plt.savefig(plot_filename, dpi=150)
    plt.close()
    print(f"\n[Saved Plot]: {plot_filename}")

    # Evaluate best agent
    mean_r, std_r = evaluate_agent(agent_with_bl, num_episodes=10)
    print("\n" + "=" * 60)
    print("Final Evaluation of Trained Agent (10 episodes):")
    print(f"Mean Reward: {mean_r:.1f} +/- {std_r:.1f} (Max possible: 500.0)")
    print("=" * 60)


if __name__ == "__main__":
    run_comparative_experiment()
