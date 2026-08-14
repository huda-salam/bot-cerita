#!/usr/bin/env python3
"""Cross-platform smoke test for Bot Cerita.

Usage:
    python scripts/smoke_test.py
    python scripts/smoke_test.py --base-url http://127.0.0.1:8000
    python scripts/smoke_test.py --skip-ai
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def post_json(base_url: str, path: str, payload: dict) -> dict:
    url = f"{base_url.rstrip('/')}{path}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=180) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        print("\n===== HTTP ERROR =====")
        print(f"URI    : {url}")
        print(f"Status : {exc.code} {exc.reason}")
        print("\n----- RESPONSE BODY -----")
        print(raw)
        print("-------------------------")
        print("\n----- REQUEST BODY -----")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("------------------------")
        raise
    except URLError as exc:
        raise RuntimeError(f"Cannot reach {url}: {exc.reason}") from exc


def get_json(base_url: str, path: str) -> dict:
    url = f"{base_url.rstrip('/')}{path}"
    request = Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code} from {url}: {raw}")
        raise


def show_step(name: str, value: object) -> None:
    print(f"\n=== {name} ===")
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(description="Bot Cerita cross-platform smoke test")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--skip-ai", action="store_true", help="Skip the /stories AI workflow")
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d-%H%M%S%f")[:-3]
    universe_name = f"Arunika-Smoke-{run_id}"

    print(f"Bot Cerita Smoke Test - {run_id}")

    health = get_json(args.base_url, "/health")
    show_step("HEALTH", health)
    if health.get("status") != "ok":
        raise RuntimeError("Health check failed")

    universe = post_json(args.base_url, "/universes", {
        "name": universe_name,
        "description": f"Ephemeral smoke-test universe. RunId={run_id}",
    })
    show_step("UNIVERSE", universe)
    universe_id = universe.get("id")
    if not universe_id:
        raise RuntimeError("Universe ID missing")

    character = post_json(args.base_url, f"/universes/{universe_id}/characters", {
        "name": "Arka",
        "description": "Anak pemberani yang suka menjelajah hutan.",
        "personality": "penasaran, pemberani, sedikit usil",
    })
    show_step("CHARACTER", character)
    character_id = character.get("id")
    if not character_id:
        raise RuntimeError("Character ID missing")

    canon = post_json(args.base_url, f"/universes/{universe_id}/canon", {
        "title": "Aturan Dunia Arunika",
        "content": "Hutan Arunika memiliki makhluk-makhluk kecil yang muncul ketika matahari terbenam.",
        "category": "world_rule",
        "importance": 5,
    })
    show_step("CANON", canon)

    context = post_json(args.base_url, f"/universes/{universe_id}/context", {
        "query": "Arka menemukan makhluk kecil di hutan pada sore hari.",
        "character_ids": [character_id],
        "max_items": 40,
    })
    show_step("CONTEXT", context)

    if args.skip_ai:
        print("\nAI step skipped (--skip-ai).")
        print("SMOKE TEST PASSED")
        return 0

    story = post_json(args.base_url, "/stories", {
        "idea": "Arka menemukan seekor anak burung yang terluka di hutan. Ia ingin menolongnya, tetapi suara aneh dari balik pepohonan membuatnya ragu untuk melanjutkan.",
        "universe_id": universe_id,
        "character_ids": [character_id],
        "target_age": "7-10",
        "genre": "fantasy adventure",
        "tone": ["warm", "funny", "adventurous"],
        "language": "Indonesian",
        "length": "short",
        "what_if_count": 3,
    })
    show_step("STORY RESULT", story)

    result_dir = Path("test-results")
    result_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "run_id": run_id,
        "universe_id": universe_id,
        "universe_name": universe_name,
        "character_id": character_id,
        "story": story,
    }
    result_path = result_dir / f"story-{run_id}.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n======================================")
    print("SMOKE TEST PASSED")
    print(f"Universe : {universe_name}")
    print(f"Universe ID: {universe_id}")
    print(f"Character: {character_id}")
    print(f"Result   : {result_path}")
    print("======================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
