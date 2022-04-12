import json
from collections import Counter
from pathlib import Path

import fire
import yaml
from loguru import logger
from sklearn.model_selection import train_test_split


def load_texts_labels(input_folder):
    texts = []
    labels = []
    logger.info(f"Loading texts and labels from {input_folder} ...")
    for text_file in Path(input_folder).rglob("*.txt"):
        texts.append(Path(text_file).read_text())
        labels.append(text_file.parent.name)
    logger.success("Done!")
    logger.info(f"texts: {len(texts)}")
    logger.info(f"labels: {len(labels)}")
    return texts, labels


@logger.catch(reraise=True)
def split(input_folder, output_folder, test_size, metrics_file):
    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    label_names = params["data"]["labels"]

    texts, labels = load_texts_labels(input_folder)
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=test_size, stratify=labels)
    
    Path(output_folder).mkdir(exist_ok=True, parents=True)
    
    train_json = [
        {"text": text, "label": label_names.index(label)} 
        for text, label in zip(train_texts, train_labels)
    ]
    val_json = [
        {"text": text, "label": label_names.index(label)} 
        for text, label in zip(val_texts, val_labels)
    ]

    logger.info(f"Writing outputs to {output_folder} ...")
    with open(f"{Path(output_folder) / 'train.json'}", "w") as f:
        json.dump({"data": train_json}, f, ensure_ascii=False)

    with open(f"{Path(output_folder) / 'val.json'}", "w") as f:
        json.dump({"data": val_json}, f, ensure_ascii=False)

    logger.success("Done!")

    logger.info("Computing metrics ...")
    metrics = {
        "train_texts": len(train_texts),
        "val_texts": len(val_texts),
        "train_labels": Counter(train_labels),
        "val_labels": Counter(val_labels)
    }
    logger.success("Done!")
    logger.info(json.dumps(metrics, indent=4))

    logger.info("Writing metrics ...")
    with open(metrics_file, "w") as f:
        json.dump(metrics, f)
    logger.success("Done!")


if __name__ == "__main__":
    fire.Fire(split)