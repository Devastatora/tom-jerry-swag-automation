from __future__ import annotations

import argparse
import json

from .config import load_settings
from .db import QueueDB
from .service import run_once, seed_queue


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrogram Instagram queue")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed", help="Import assets/queue/manifest.json")
    sub.add_parser("status", help="Show queue counts")
    sub.add_parser("post-now", help="Publish the next item, or preview in DRY_RUN")
    args = parser.parse_args()

    settings = load_settings()
    db = QueueDB(settings.database_path)
    if args.command == "seed":
        print(json.dumps({"added": seed_queue(db, settings.queue_dir), **db.counts()}, ensure_ascii=False))
    elif args.command == "status":
        print(json.dumps(db.counts(), ensure_ascii=False))
    elif args.command == "post-now":
        print(run_once(settings))


if __name__ == "__main__":
    main()

