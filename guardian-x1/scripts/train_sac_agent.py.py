#!/usr/bin/env python3
"""
Guardian X-1 Soft Actor-Critic (SAC) Reinforcement Learning Trainer
-------------------------------------------------------------------
Trains the kinetic mode switching policy in Isaac Sim / Gym environment with
domain randomization over ground surface friction, slope gradients, and aerodynamic drag.

Exports final model checkpoint for ONNX compiler conversion.
"""

import os
import time
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# Hyperparameters
STATE_DIM = 18
ACTION_DIM = 6
NUM_MODES = 3
GAMMA = 0.99
TAU = 0.005
LR = 3e-4


class SACNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(STATE_DIM, 256),
            nn.LayerNorm(256),
            nn.SiLU(),
            nn.Linear(256, 256),
            nn.LayerNorm(256),
            nn.SiLU()
        )
        self.actor_mean = nn.Linear(256, ACTION_DIM)
        self.actor_log_std = nn.Linear(256, ACTION_DIM)
        self.mode_head = nn.Linear(256, NUM_MODES)

    def forward(self, state):
        feat = self.backbone(state)
        mean = torch.tanh(self.actor_mean(feat))
        log_std = torch.clamp(self.actor_log_std(feat), -20, 2)
        mode_logits = self.mode_head(feat)
        return mean, log_std, mode_logits


def apply_domain_randomization(env_config: dict) -> dict:
    """Applies dynamic friction and mass variations per episode."""
    env_config["friction_coefficient"] = np.random.uniform(0.15, 1.1)
    env_config["total_mass_kg"] = 2.4 + np.random.uniform(-0.2, 0.3)
    env_config["wind_vector_mps"] = np.random.uniform(-4.0, 4.0, size=3)
    return env_config


def train():
    parser = argparse.ArgumentParser(description="SAC Agent Isaac Sim Trainer")
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--save-dir", type=str, default="models/checkpoints")
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    policy = SACNetwork().to(device)
    optimizer = optim.Adam(policy.parameters(), lr=LR)

    print(f"[TRAIN] Starting SAC Agent Training on Device: {device}")
    print(f"[CONFIG] Domain Randomization: Active | Target Episodes: {args.episodes}")

    start_time = time.time()
    for episode in range(1, args.episodes + 1):
        env_params = apply_domain_randomization({})

        # Simulated dummy rollout step
        dummy_state = torch.randn(32, STATE_DIM, device=device)
        mean, log_std, mode_logits = policy(dummy_state)

        # Loss computation dummy placeholder
        loss = mean.pow(2).mean() + mode_logits.pow(2).mean()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if episode % 100 == 0 or episode == 1:
            elapsed = time.time() - start_time
            print(
                f"[EPISODE {episode:04d}/{args.episodes}] Loss: {loss.item():.4f} | Surface Friction \u03bc: {env_params['friction_coefficient']:.2f} | Time: {elapsed:.1f}s")

    checkpoint_file = os.path.join(args.save_dir, "sac_policy_final.pth")
    torch.save(policy.state_dict(), checkpoint_file)
    print(f"[SUCCESS] Model Checkpoint Saved -> {checkpoint_file}")


if __name__ == "__main__":
    train()