import torch
import torch.nn as nn
import torch.optim as optim

class FailureClassifier(nn.Module):
    def __init__(self):
        super(FailureClassifier, self).__init__()
        self.fc1 = nn.Linear(2, 8)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(8, 2)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)


def _label(record):
    """Ground-truth rule used to generate training labels: 1 = soft decline, 0 = hard fault."""
    return 1 if (record["error_code"] in (502, 504) or record["latency_sec"] >= 2.5) else 0


def train_model(data, epochs=100, lr=0.05):
    model = FailureClassifier()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    X = torch.tensor(
        [[r["latency_sec"], r["error_code"] / 1000.0] for r in data],
        dtype=torch.float32,
    )
    y = torch.tensor([_label(r) for r in data], dtype=torch.long)

    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        preds = torch.argmax(model(X), dim=1)
        accuracy = (preds == y).float().mean().item() * 100
    print(f"Training completed. Final Training Accuracy: {accuracy:.2f}%")

    return model


def predict(model, latency_sec: float, error_code: int) -> int:
    """Classifies a single failure. Returns 1 for Soft Decline, 0 for Hard Fault."""
    input_tensor = torch.tensor([[latency_sec, error_code / 1000.0]], dtype=torch.float32)
    with torch.no_grad():
        output = model(input_tensor)
    return torch.argmax(output, dim=1).item()
