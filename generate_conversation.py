import argparse
import csv
import json
import random
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic MMORPG chats")
    parser.add_argument("--dataset", default="data/train.csv")
    parser.add_argument("--text-column", default="message")
    parser.add_argument("--conversations", type=int, default=100)
    parser.add_argument("--players", type=int, default=50)
    parser.add_argument("--output", default="conversations.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.conversations <= 0 or args.players < 2:
        parser.error("--conversations must be positive and --players must be at least 2")

    with open(args.dataset, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if args.text_column not in (reader.fieldnames or []):
            parser.error(f"Missing CSV column: {args.text_column}")

        statements = [
            row[args.text_column].strip()
            for row in reader
            if row[args.text_column] and row[args.text_column].strip()
        ]

    if len(statements) < 5:
        parser.error("Dataset must contain at least 5 nonempty statements")

    rng = random.Random(args.seed)
    conversations = []

    for i in range(args.conversations):
        first, second = rng.sample(range(1, args.players + 1), 2)
        count = rng.randint(3, 5)
        selected = rng.sample(statements, count)
        messages = []

        for j, statement in enumerate(selected):
            sender, recipient = (
                (first, second) if j % 2 == 0 else (second, first)
            )

            messages.append({
                "from-user": f"player_{sender:03d}",
                "to-user": f"player_{recipient:03d}",
                "times-stamp": datetime.now(timezone.utc)
                    .isoformat(timespec="milliseconds")
                    .replace("+00:00", "Z"),
                "message": statement,
            })

        conversations.append({
            "conversation_id": f"conv_{i + 1:05d}",
            "messages": messages
        })

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(conversations, file, indent=2, ensure_ascii=False)

    print(
        f"Generated {len(conversations)} conversations, "
        f"{sum(len(c['messages']) for c in conversations)} messages "
        f"-> {args.output}"
    )


if __name__ == "__main__":
    main()
