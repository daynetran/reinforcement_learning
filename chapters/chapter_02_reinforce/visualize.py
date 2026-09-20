"""Visual asset and trajectory export utilities for CartPole REINFORCE.

This module provides functions to evaluate and visualize a trained CartPole-v1
agent by:
1. Exporting policy weights and comparative trajectories (untrained baseline vs.
   trained agent) to JSON for interactive web visualizers.
2. Rendering and recording an evaluation episode as an animated GIF.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import gymnasium as gym
import torch
from PIL import Image

try:
    from .reinforce_improved import REINFORCEAgent, train_cartpole
except ImportError:
    from reinforce_improved import REINFORCEAgent, train_cartpole

# Directory paths
MODULE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = MODULE_DIR / "artifacts"

# Default environment and visualization artifact configurations
DEFAULT_ENV_ID: str = "CartPole-v1"
DEFAULT_DATA_FILENAME: str = str(ARTIFACTS_DIR / "cartpole_data.json")
DEFAULT_GIF_FILENAME: str = str(ARTIFACTS_DIR / "cartpole_trained.gif")


@dataclass(slots=True)
class StepTransition:
    """Represents a single environment transition in an evaluation rollout.

    Attributes:
        state: State observation vector at this time step.
        action: Action index selected at this step.
        reward: Scalar reward received from the environment.
        probs: Optional policy action probability distribution.
    """

    state: list[float]
    action: int
    reward: float
    probs: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert transition fields to a JSON-serializable dictionary."""
        data: dict[str, Any] = {
            "state": self.state,
            "action": self.action,
            "reward": self.reward,
        }
        if self.probs is not None:
            data["probs"] = self.probs
        return data


def extract_policy_weights(agent: REINFORCEAgent) -> dict[str, list]:
    """Extract policy network weights into JSON-serializable lists for web inference.

    Args:
        agent: Trained REINFORCE agent containing the policy network.

    Returns:
        A dictionary mapping layer parameter names to nested lists of floats.
    """
    layers = agent.policy.net
    return {
        "fc1_weight": layers[0].weight.detach().cpu().numpy().tolist(),
        "fc1_bias": layers[0].bias.detach().cpu().numpy().tolist(),
        "fc2_weight": layers[2].weight.detach().cpu().numpy().tolist(),
        "fc2_bias": layers[2].bias.detach().cpu().numpy().tolist(),
    }


def record_untrained_trajectory(
    env_name: str = DEFAULT_ENV_ID,
    seed: int = 42,
    max_steps: int = 500,
) -> list[StepTransition]:
    """Record a baseline rollout in the environment using uniform random actions.

    Args:
        env_name: Gymnasium environment identifier. Defaults to DEFAULT_ENV_ID.
        seed: Random seed for environment reset reproducibility. Defaults to 42.
        max_steps: Maximum environment steps to simulate. Defaults to 500.

    Returns:
        A list of recorded step transitions.
    """
    trajectory: list[StepTransition] = []
    with gym.make(env_name) as env:
        state, _ = env.reset(seed=seed)
        for _ in range(max_steps):
            action = env.action_space.sample()
            next_state, reward, terminated, truncated, _ = env.step(action)
            trajectory.append(
                StepTransition(
                    state=state.tolist(),
                    action=int(action),
                    reward=float(reward),
                )
            )
            state = next_state
            if terminated or truncated:
                break
    return trajectory


def record_trained_trajectory(
    agent: REINFORCEAgent,
    env_name: str = DEFAULT_ENV_ID,
    seed: int = 123,
    max_steps: int = 500,
) -> list[StepTransition]:
    """Record an evaluation rollout using the agent's greedy policy.

    Captures state transitions, chosen actions, rewards, and action probabilities
    for visualizer telemetry.

    Args:
        agent: Trained REINFORCE agent containing the policy network.
        env_name: Gymnasium environment identifier. Defaults to DEFAULT_ENV_ID.
        seed: Random seed for environment reset reproducibility. Defaults to 123.
        max_steps: Maximum environment steps to simulate. Defaults to 500.

    Returns:
        A list of recorded step transitions with policy probabilities.
    """
    trajectory: list[StepTransition] = []
    with gym.make(env_name) as env:
        state, _ = env.reset(seed=seed)
        for _ in range(max_steps):
            state_tensor = torch.as_tensor(state, dtype=torch.float32)
            with torch.no_grad():
                logits = agent.policy(state_tensor)
                probs = torch.softmax(logits, dim=-1).cpu().numpy().tolist()
                action = int(torch.argmax(logits).item())

            next_state, reward, terminated, truncated, _ = env.step(action)
            trajectory.append(
                StepTransition(
                    state=state.tolist(),
                    action=action,
                    reward=float(reward),
                    probs=probs,
                )
            )
            state = next_state
            if terminated or truncated:
                break
    return trajectory


def export_agent_and_trajectories(
    agent: REINFORCEAgent,
    output_json: str = DEFAULT_DATA_FILENAME,
    env_name: str = DEFAULT_ENV_ID,
    untrained_seed: int = 42,
    trained_seed: int = 123,
    max_steps: int = 500,
) -> None:
    """Export policy weights and comparative rollouts to a JSON file for visualization.

    Saves model parameters alongside an untrained baseline rollout and a trained
    policy rollout with metadata.

    Args:
        agent: Trained REINFORCE agent containing the policy network.
        output_json: Output JSON destination path. Defaults to DEFAULT_DATA_FILENAME.
        env_name: Gymnasium environment identifier. Defaults to DEFAULT_ENV_ID.
        untrained_seed: Seed for the untrained baseline rollout. Defaults to 42.
        trained_seed: Seed for the trained agent rollout. Defaults to 123.
        max_steps: Maximum steps per trajectory rollout. Defaults to 500.
    """
    weights = extract_policy_weights(agent)
    untrained_traj = record_untrained_trajectory(
        env_name=env_name, seed=untrained_seed, max_steps=max_steps
    )
    trained_traj = record_trained_trajectory(
        agent=agent, env_name=env_name, seed=trained_seed, max_steps=max_steps
    )

    payload = {
        "weights": weights,
        "untrained_trajectory": [step.to_dict() for step in untrained_traj],
        "trained_trajectory": [step.to_dict() for step in trained_traj],
        "metadata": {
            "untrained_steps": len(untrained_traj),
            "trained_steps": len(trained_traj),
        },
    }

    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(
        f"[Exported Data]: {output_json} "
        f"(Untrained: {len(untrained_traj)} steps, Trained: {len(trained_traj)} steps)"
    )


def record_gif(
    agent: REINFORCEAgent,
    filename: str = DEFAULT_GIF_FILENAME,
    env_name: str = DEFAULT_ENV_ID,
    max_steps: int = 500,
    fps: int = 50,
) -> None:
    """Record an evaluation rollout of the agent and save as an animated GIF.

    Executes the greedy policy in the environment and writes an optimized,
    looping GIF of rendered RGB frames.

    Args:
        agent: Trained REINFORCE agent containing the policy network.
        filename: Output filepath for the animated GIF. Defaults to
            DEFAULT_GIF_FILENAME.
        env_name: Gymnasium environment identifier. Defaults to DEFAULT_ENV_ID.
        max_steps: Maximum environment steps to record. Defaults to 500.
        fps: Target playback frame rate in frames per second. Defaults to 50.
    """
    env = gym.make(env_name, render_mode="rgb_array")
    state, _ = env.reset(seed=42)
    frames = []

    for _ in range(max_steps):
        frame = env.render()
        frames.append(Image.fromarray(frame))

        state_t = torch.as_tensor(state, dtype=torch.float32)
        with torch.no_grad():
            action = torch.argmax(agent.policy(state_t)).item()
        
        state, _, terminated, truncated, _ = env.step(action)
        if terminated or truncated:
            break

    env.close()

    # Save as animated GIF (sample every 2nd frame to keep size compact)
    sampled_frames = frames[::2]
    duration_ms = int(1000 / (fps / 2))
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    sampled_frames[0].save(
        filename,
        save_all=True,
        append_images=sampled_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True
    )
    print(f"[Saved GIF]: {filename} ({len(sampled_frames)} frames)")


def main() -> None:
    """Train a CartPole agent and generate all visualization artifacts."""
    print("Training high-performing agent for visualizer...")
    agent, rewards, ma = train_cartpole(
        episodes=260,
        use_baseline=True,
        entropy_coef=0.001,
        lr=0.005,
        seed=42,
        verbose=False
    )
    print("Agent trained! Exporting assets...")
    export_agent_and_trajectories(agent)
    record_gif(agent)


if __name__ == "__main__":
    main()
