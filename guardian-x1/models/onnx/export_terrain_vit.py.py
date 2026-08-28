"""
Guardian X-1 Vision Transformer (ViT-Nano) Terrain Classifier Exporter
-----------------------------------------------------------------------
Lightweight patch-based Transformer that consumes camera surface frames and
outputs real-time friction coefficient predictions ($\mu \in [0.1, 1.2]$) for wheel-slip compensation.

Inputs:
    image (Tensor): [Batch, 3, 64, 64] -> High-speed terrain surface patches
Outputs:
    friction_coefficient (Tensor): [Batch, 1] -> Estimated friction coefficient (\mu)
    surface_class_logits (Tensor): [Batch, 4] -> Surface types (Asphalt, Gravel, Grass, Mud)
"""

import os
import torch
import torch.nn as nn


class TerrainViTNano(nn.Module):
    def __init__(
            self,
            img_size: int = 64,
            patch_size: int = 8,
            in_channels: int = 3,
            embed_dim: int = 64,
            depth: int = 2,
            heads: int = 4,
            num_classes: int = 4,
    ):
        super().__init__()
        self.patch_size = patch_size
        self.num_patches = (img_size // patch_size) ** 2

        # Linear Patch Embedding via Strided Convolution
        self.patch_proj = nn.Conv2d(
            in_channels, embed_dim, kernel_size=patch_size, stride=patch_size
        )

        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches + 1, embed_dim))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=heads,
            dim_feedforward=128,
            activation="gelu",
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=depth)

        # Regression Head for Friction Coefficient (\mu)
        self.friction_head = nn.Sequential(
            nn.Linear(embed_dim, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),  # Output normalized [0.0, 1.0]
        )

        # Surface Classification Head
        self.class_head = nn.Linear(embed_dim, num_classes)

    def forward(self, x: torch.Tensor):
        batch_size = x.shape[0]

        # Extract and flatten patches
        x = self.patch_proj(x).flatten(2).transpose(1, 2)  # [B, Num_Patches, Embed_Dim]

        # Prepend Class Token
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        x = x + self.pos_embed

        # Pass through Transformer blocks
        x = self.transformer(x)
        cls_rep = x[:, 0]

        # Rescale Sigmoid output to physical friction bounds \mu \in [0.1, 1.2]
        friction_coef = self.friction_head(cls_rep) * 1.1 + 0.1
        class_logits = self.class_head(cls_rep)

        return friction_coef, class_logits


def export_vit_onnx(output_path: str = "models/onnx/terrain_vit_nano.onnx"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    model = TerrainViTNano()
    model.eval()

    dummy_img = torch.randn(1, 3, 64, 64, dtype=torch.float32)

    torch.onnx.export(
        model,
        dummy_img,
        output_path,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["terrain_patch"],
        output_names=["friction_coefficient", "surface_class_logits"],
        dynamic_axes={
            "terrain_patch": {0: "batch_size"},
            "friction_coefficient": {0: "batch_size"},
            "surface_class_logits": {0: "batch_size"},
        },
    )
    print(f"[OK] Successfully exported Terrain ViT-Nano -> {output_path}")


if __name__ == "__main__":
    export_vit_onnx()