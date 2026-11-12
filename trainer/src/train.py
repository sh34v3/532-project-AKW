import argparse
import os

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

LABELS = [
    "Non-Toxic",
    "Insults and Flaming",
    "Other Offensive Texts",
    "Hate and Harassment",
    "Threats",
    "Extremism",
]
ID2LABEL = {i: name for i, name in enumerate(LABELS)}
LABEL2ID = {name: i for i, name in ID2LABEL.items()}


def prepare(df, text_col, label_col):
    for col in (text_col, label_col):
        if col not in df.columns:
            raise SystemExit(
                f"Column '{col}' not found. "
                "Columns in file: {list(df.columns)}. "
                "Pass the right names with --text-col / --label-col."
            )
    df = df[[text_col, label_col]].dropna().copy()
    df[text_col] = df[text_col].astype(str)

    # Accept either integer ids (0-5) or the class names from the README.
    lowered = {name.lower(): i for name, i in LABEL2ID.items()}
    try:
        df[label_col] = df[label_col].astype(int)
    except (ValueError, TypeError):
        df[label_col] = df[label_col].\
            astype(str).\
            str.strip().\
            str.lower().\
            map(lowered)
        if df[label_col].isna().any():
            raise SystemExit(
                f"Unrecognised label values. Expected 0-5 or one of {LABELS}."
            )
    df[label_col] = df[label_col].astype(int)

    bad = ~df[label_col].between(0, len(LABELS) - 1)
    if bad.any():
        raise SystemExit(
            f"{int(bad.sum())} rows have labels outside 0-{len(LABELS) - 1}."
        )
    return df.reset_index(drop=True)


class TextDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = int(self.labels[idx])
        return item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--train",
        required=True,
        help="training file (csv/tsv/json/jsonl)"
    )
    ap.add_argument(
        "--val",
        help="optional validation file; otherwise 10%% of train is held out"
    )
    ap.add_argument("--text-col", default="text")
    ap.add_argument("--label-col", default="label")
    ap.add_argument(
        "--output",
        default=os.getenv("MODEL_DIR", "/models/gametox-distilbert")
    )
    ap.add_argument("--base-model", default="distilbert-base-uncased")
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--max-length", type=int, default=128)
    ap.add_argument("--max-train-examples", type=int, default=None)
    args = ap.parse_args()

    train_df = prepare(pd.read_csv(args.train), args.text_col, args.label_col)
    if args.val:
        val_df = prepare(pd.read_csv(args.val), args.text_col, args.label_col)
    else:
        train_df, val_df = train_test_split(
            train_df,
            test_size=0.1,
            random_state=42,
            stratify=train_df[args.label_col]
        )
    if args.max_train_examples and len(train_df) > args.max_train_examples:
        train_df, _ = train_test_split(
            train_df,
            train_size=args.max_train_examples,
            random_state=42,
            stratify=train_df[args.label_col],
        )
        train_df = train_df.reset_index(drop=True)
    print(f"train rows: {len(train_df)}, val rows: {len(val_df)}", flush=True)
    print(
        train_df[args.label_col].map(ID2LABEL).value_counts().to_string(),
        flush=True
    )

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)

    def encode(df):
        enc = tokenizer(
            df[args.text_col].tolist(),
            truncation=True,
            max_length=args.max_length
        )
        return TextDataset(enc, df[args.label_col].tolist())

    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=len(LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    training_args = TrainingArguments(
        output_dir=os.path.join(args.output, "checkpoints"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size * 2,
        learning_rate=args.lr,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        save_total_limit=1,
        logging_steps=50,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=encode(train_df),
        eval_dataset=encode(val_df),
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
    )
    trainer.train()
    print("final eval:", trainer.evaluate(), flush=True)

    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)
    print(f"model saved to {args.output}", flush=True)


if __name__ == "__main__":
    main()
