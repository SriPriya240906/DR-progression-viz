import torch
from PIL import Image
from torchvision import transforms

from unet_autoencoder import RetinaUNet
from progression_network import ProgressionNetwork

# ----------------------------------
# Device
# ----------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----------------------------------
# Load Models
# ----------------------------------
unet = RetinaUNet().to(device)
unet.load_state_dict(
    torch.load(
        "progression_engine/retina_unet.pth",
        map_location=device
    )
)
unet.eval()

progression = ProgressionNetwork().to(device)
progression.load_state_dict(
    torch.load(
        "progression_engine/progression_network.pth",
        map_location=device
    )
)
progression.eval()

# ----------------------------------
# Transform
# ----------------------------------
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor()
])

inverse = transforms.ToPILImage()


# ----------------------------------
# Generate Future Retina
# ----------------------------------
def generate_progression(image_path, years=3):

    image = Image.open(image_path).convert("RGB")

    tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():

        x1, x2, x3, x4, latent = unet.encode(tensor)

        outputs = []

        current = latent

        for year in range(years):

            strength = torch.tensor(
                [[(year + 1) / years]],
                device=device
            )

            strength = strength.view(1, 1, 1, 1)

            current = progression(current, strength)

            generated = unet.decode(
                x1,
                x2,
                x3,
                x4,
                current
            )

            outputs.append(
                inverse(
                    generated.squeeze(0).cpu()
                )
            )

    return outputs