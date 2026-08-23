import torch
import torch.nn as nn


# -----------------------------------
# Double Convolution Block
# -----------------------------------
class DoubleConv(nn.Module):

    def __init__(self, in_channels, out_channels):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),

            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)


# -----------------------------------
# Down Block
# -----------------------------------
class Down(nn.Module):

    def __init__(self, in_channels, out_channels):
        super().__init__()

        self.block = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.block(x)


# -----------------------------------
# Up Block
# -----------------------------------
class Up(nn.Module):

    def __init__(self, in_channels, skip_channels, out_channels):
        super().__init__()

        self.up = nn.ConvTranspose2d(
            in_channels,
            out_channels,
            kernel_size=2,
            stride=2
        )

        self.conv = DoubleConv(
            out_channels + skip_channels,
            out_channels
        )

    def forward(self, x1, x2):

        x1 = self.up(x1)

        # Handle odd image sizes
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = nn.functional.pad(
            x1,
            [
                diffX // 2,
                diffX - diffX // 2,
                diffY // 2,
                diffY - diffY // 2,
            ],
        )

        x = torch.cat([x2, x1], dim=1)

        return self.conv(x)


# -----------------------------------
# Retina U-Net Autoencoder
# -----------------------------------
class RetinaUNet(nn.Module):

    def __init__(self):
        super().__init__()

        # ---------------- Encoder ----------------

        self.inc = DoubleConv(3, 32)

        self.down1 = Down(32, 64)

        self.down2 = Down(64, 128)

        self.down3 = Down(128, 256)

        self.down4 = Down(256, 512)

        # ---------------- Decoder ----------------

        self.up1 = Up(512, 256, 256)

        self.up2 = Up(256, 128, 128)

        self.up3 = Up(128, 64, 64)

        self.up4 = Up(64, 32, 32)

        self.out = nn.Conv2d(32, 3, kernel_size=1)

        self.activation = nn.Sigmoid()

    # ---------------- Encoder ----------------

    def encode(self, x):

        x1 = self.inc(x)

        x2 = self.down1(x1)

        x3 = self.down2(x2)

        x4 = self.down3(x3)

        x5 = self.down4(x4)

        return x1, x2, x3, x4, x5

    # ---------------- Decoder ----------------

    def decode(self, x1, x2, x3, x4, x5):

        x = self.up1(x5, x4)

        x = self.up2(x, x3)

        x = self.up3(x, x2)

        x = self.up4(x, x1)

        x = self.out(x)

        return self.activation(x)

    # ---------------- Forward ----------------

    def forward(self, x):

        x1, x2, x3, x4, x5 = self.encode(x)

        return self.decode(x1, x2, x3, x4, x5)


# -----------------------------------
# Test
# -----------------------------------
if __name__ == "__main__":

    model = RetinaUNet()

    x = torch.randn(1, 3, 224, 224)

    y = model(x)

    print("Input :", x.shape)

    print("Output:", y.shape)