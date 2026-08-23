import torch
import torch.nn as nn


class ProgressionNetwork(nn.Module):
    """
    Learns disease progression in the latent feature space.
    Compatible with RetinaUNet (512-channel bottleneck).
    """

    def __init__(self, latent_channels=512):
        super().__init__()

        self.net = nn.Sequential(

            nn.Conv2d(
                latent_channels + 1,
                latent_channels,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(latent_channels),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                latent_channels,
                latent_channels,
                kernel_size=3,
                padding=1
            ),
            nn.BatchNorm2d(latent_channels),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                latent_channels,
                latent_channels,
                kernel_size=3,
                padding=1
            )
        )

    def forward(self, latent, strength):

        # strength shape:
        # (B,1,1,1)

        strength_map = strength.expand(
            latent.size(0),
            1,
            latent.size(2),
            latent.size(3)
        )

        x = torch.cat(
            [latent, strength_map],
            dim=1
        )

        delta = self.net(x)

        # Residual Learning
        future_latent = latent + delta

        return future_latent


if __name__ == "__main__":

    model = ProgressionNetwork()

    latent = torch.randn(
        2,
        512,
        8,
        8
    )

    strength = torch.rand(
        2,
        1,
        1,
        1
    )

    output = model(latent, strength)

    print("Input :", latent.shape)
    print("Output:", output.shape)