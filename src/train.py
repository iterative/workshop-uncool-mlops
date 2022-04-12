import pickle
from pathlib import Path

import fire
import numpy as np
import yaml

from datasets import load_metric
from dvclive.huggingface import DvcLiveCallback
from loguru import logger
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset


metric = load_metric("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    print(labels)
    print(predictions)
    return metric.compute(predictions=predictions, references=labels)


@logger.catch(reraise=True)
def train(input_folder, output_folder):
    with open("params.yaml") as f:
        params = yaml.safe_load(f)

    raw_datasets = load_dataset("json", 
        data_files={
            "train": str(Path(input_folder) / "train.json"), 
            "val": str(Path(input_folder) / "val.json")
        },
        field="data"
    )

    tokenizer = AutoTokenizer.from_pretrained(params["train"]["pretrained_model"])

    def tokenize_function(example):
        return tokenizer(example["text"], padding=True, truncation=True, max_length=512)

    tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        params["train"]["pretrained_model"],
        num_labels=len(params["data"]["labels"]),
        id2label={n: x for n, x in enumerate(params["data"]["labels"])},
        label2id={x: n for n, x in enumerate(params["data"]["labels"])},
        ignore_mismatched_sizes=True
    )

    training_arguments = TrainingArguments(
        output_dir=output_folder,
        num_train_epochs=params["train"]["epochs"],
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        evaluation_strategy="epoch",
        lr_scheduler_type="cosine"
    )

    trainer = Trainer(
        model=model,
        args=training_arguments,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["val"],
        compute_metrics=compute_metrics,
        tokenizer=tokenizer
    )

    trainer.add_callback(DvcLiveCallback(
        path=Path(params["train"]["metrics_folder"]),
        report=None,
        model_file=params["train"]["output_folder"]))
    trainer.train()

    predictions = trainer.predict(tokenized_datasets["val"])

    with open(Path(output_folder) / "predictions.pkl", "wb") as f:
        pickle.dump(predictions, f)

if __name__ == "__main__":
    fire.Fire(train)