from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.txt").read_text(encoding="utf-8")
