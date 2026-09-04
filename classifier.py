import torch
import torch.nn as nn

class FailureClassifier(nn.Module):
    def __init__(self):
        super(FailureClassifier, self).__init__()
        self.fc = nn.Linear(2, 2)
        
    def forward(self, x):
        return self.fc(x)

# Simple untrained model for categorization
model = FailureClassifier()

def classify_failure(features: list) -> str:
    """Categorizes the synthetic failures as 'hard faults' or 'soft declines'.
    
    Args:
        features: List of 2 numerical features representing the failure.
    """
    input_tensor = torch.tensor(features, dtype=torch.float32)
    output = model(input_tensor)
    predicted_class = torch.argmax(output).item()
    return 'soft decline' if predicted_class == 1 else 'hard fault'
