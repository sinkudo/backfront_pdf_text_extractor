from typing import List

import torch
import torch.nn.functional as f
from torch import nn
from huggingface_hub import hf_hub_download



class CNNModel(nn.Module):

    def __init__(self, num_classes: int) -> None:
        super(CNNModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.dropout1 = nn.Dropout(0.2)
        self.fc1 = nn.Linear(64 * 5 * 5, 256)  # For input size 28x28
        self.dropout2 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool1(f.relu(self.conv1(x)))
        x = self.pool2(f.relu(self.conv2(x)))
        self.view = x.view(x.size(0), -1)
        x = self.view
        x = self.dropout1(x)
        x = f.relu(self.fc1(x))
        x = self.dropout2(x)
        x = self.fc2(x)
        return x


class Model:
    """
    PyTorch CNN model for font's glyphs prediction.
    Used in PDFBrokenEncodingReader.
    """

    def __init__(self) -> None:
        from .config import Language
        self.model = None
        self.__load_weights()
        s = sorted(Language.Russian_and_English.value, key=lambda i: str(ord(i)))
        self.labels = [ord(i) for i in s]

    def __assert_labels_and_model(self) -> None:
        assert self.model.fc1.out_features == len(self.labels)

    def recognize_glyph(self, images: List[str]) -> list:
        import cv2
        import numpy as np
        import torch

        images_readen = []
        for png in images:
            with open(png, "rb") as stream:
                bytes_data = bytearray(stream.read())
                numpyarray = np.asarray(bytes_data, dtype=np.uint8)
                img = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
                img = np.array(img).reshape(28, 28)
                images_readen.append(img)

        images_readen = np.array(images_readen, dtype=np.float32)
        images_readen = images_readen / 255.0

        images_tensor = torch.tensor(images_readen).unsqueeze(1)

        with torch.no_grad():
            probs = self.model(images_tensor)
            problabels = probs.argmax(dim=-1).tolist()

        predictions = [self.labels[label] for label in problabels]
        return predictions

    def __load_weights(self) -> None:
        cache_dir = "models"
        filename = "rus_eng.pt"  # Имя файла с весами

        weights_path = hf_hub_download(
            repo_id="sinkudo/torch_cnn",
            filename=filename,
            cache_dir=cache_dir
        )

        self.model = CNNModel(160)
        self.model.load_state_dict(torch.load(weights_path))
        self.model.eval()
