"""
Guardian X-1 Soft Actor-Critic (SAC) Kinetic Mode Policy Exporter
-----------------------------------------------------------------
Defines the dual-head actor network for ground-to-flight mode switching
and exports the compiled PyTorch graph to dynamic ONNX format (`sac_mode_policy.onnx`).

Inputs:
    state (Tensor): [Batch, 18] -> Kinematic vector (POS, VEL, ATT, WHEEL_SLIP, BATTERY, RSSI)
Outputs:
    action_mean (Tensor): [Batch, 6] -> Continuous control (Left/Right Motors + 4 Quad Rotors)
    mode_probs  (Tensor): [Batch, 3] -> Discrete state probabilities [0: Rover, 1: Hybrid, 2: Aerial]
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F


class SACModePolicy(nn.Module):
    def __init__(self, state_dim: int = 18, action_dim: int = 6, num_modes: int = 3):
        super().__init__()
        # Shared Feature Extractor
        self.fc1 = nn.Linear(state_dim, 256)
        self.fc2 = nn.Linear(256, 256)
        self.ln1 = nn.LayerNorm(256)
        self.ln2 = nn.LayerNorm(256)

        # Continuous Actuator Controller Head
        self.mean_head = nn.Linear(256, action_dim)
        self.log_std_head = nn.Linear(256, action_dim)

        # Discrete Mode Transition Head (Rover, Hybrid, Flight)
        self.mode_head = nn.Linear(256, num_modes)

    def forward(self, state: torch.Tensor):
        x = F.silu(self.ln1(self.fc1(state)))
        x = F.silu(self.ln2(self.fc2(x)))

        # Actuation distribution parameters
        action_mean = torch.tanh(self.mean_head(x))
        log_std = torch.clamp(self.log_std_head(x), -20.0, 2.0)

        # Categorical distribution over kinetic operating modes
        mode_logits = self.mode_head(x)
        mode_probs = F.softmax(mode_logits, dim=-1)

        return action_mean, log_std, mode_probs


def export_sac_onnx(output_path: str = "models/onnx/sac_mode_policy.onnx"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    model = SACModePolicy(state_dim=18, action_dim=6, num_modes=3)
    model.eval()

    # Dummy tensor for trace generation
    dummy_state = torch.randn(1, 18, dtype=torch.float32)

    torch.onnx.export(
        model,
        dummy_state,
        output_path,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["robot_state"],
        output_names=["action_mean", "action_log_std", "mode_probabilities"],
        dynamic_axes={
            "robot_state": {0: "batch_size"},
            "action_mean": {0: "batch_size"},
            "action_log_std": {0: "batch_size"},
            "mode_probabilities": {0: "batch_size"},
        },
    )
    print(f"[OK] Successfully exported SAC Mode Policy -> {output_path}")


if __name__ == "__main__":
    export_sac_onnx()