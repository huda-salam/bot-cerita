from pathlib import Path

ROOT = Path(__file__).parent / "skills"


def load_skill(name: str) -> str:
    path = ROOT / f"{name}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_skill_context(*names: str) -> str:
    parts = [load_skill(name) for name in names]
    parts = [p.strip() for p in parts if p.strip()]
    return "\n\n--- SKILL ---\n\n".join(parts)
