from pathlib import Path

import torch

from slm import train


CHECKPOINT = Path(__file__).resolve().parents[2] / "checkpoints/smol_decision_epoch1.pt"

EXAMPLES = [
    ("That joke was hilarious!", ["Reply with thanks", "laugh_animation", "Ask what the joke means"]),
    ("What does this Python error mean?", ["Explain the error", "laugh_animation", "Search the web"]),
    ("Please remind me to call Maya tomorrow.", ["Set a reminder", "Explain reminders", "Do nothing"]),
    ("Can you summarize this paragraph for me?", ["Summarize the text", "Send an email", "Ask for the paragraph"]),
    ("Delete all my files right now.", ["Delete the files", "Search the web", "Tell a joke"]),
    ("Open the lights", ["switch_on", "switch_off", "check_temp"]),
    ("The sky is blue", ["laugh", "cry", "nod"]),
    ("User: My gf left me today.", ["laugh", "cry", "nod"])
    
]


def predict(model: train.SmolDecision, text: str, choices: list[str]):
    if not choices:
        raise ValueError("Provide at least one choice")

    # SmolDecision expects token IDs in the same record shape as training.
    record = train.encode_record({
        "input": text,
        "choices": choices,
        "out": [0.0] * len(choices),
    })
    with torch.inference_mode():
        probabilities = torch.softmax(model(record), dim=0).tolist()

    names = choices + ["NONE OF THESE"]
    selected = max(range(len(probabilities)), key=probabilities.__getitem__)
    return names[selected], list(zip(names, probabilities))


def main():
    if not CHECKPOINT.is_file():
        raise SystemExit(
            f"Checkpoint missing: {CHECKPOINT}. Finish training before prediction."
        )

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    train.DEVICE = device  # train.SmolDecision.vector creates tensors on this device.

    model = train.SmolDecision(train.VOCAB_SIZE, 64).to(device)
    model.load_state_dict(torch.load(CHECKPOINT, map_location=device, weights_only=True))
    model.eval()

    print(f"Device: {device}\n")
    for number, (text, choices) in enumerate(EXAMPLES, start=1):
        selected, scores = predict(model, text, choices)
        print(f"{number}. {text}")
        for name, probability in scores:
            print(f"   {probability:6.1%}  {name}")
        print(f"   Selected: {selected}\n")


if __name__ == "__main__":
    main()
