import torch
import numpy as np
import cv2
from PIL import Image
from torchvision import models, transforms

device = "cuda" if torch.cuda.is_available() else "cpu"

_mobilenet = models.mobilenet_v2(pretrained=True)
_mobilenet.classifier = torch.nn.Identity()
_mobilenet.eval().to(device)

_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def _extract_cnn_feature(img_bgr):
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(img_rgb)

    tensor = _transform(pil).unsqueeze(0).to(device)

    with torch.no_grad():
        feat = _mobilenet(tensor).cpu().numpy().flatten()

    feat /= np.linalg.norm(feat) + 1e-8
    return feat

import requests
from io import BytesIO

def extract_feature_from_url(url):
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    img = Image.open(BytesIO(r.content)).convert("RGB")
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    return _extract_cnn_feature(img)

def extract_feature_from_file(file, model=None):
    img = Image.open(file).convert("RGB")
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    return _extract_cnn_feature(img)
