import json
from pathlib import Path

import fire
from loguru import logger


@logger.catch(reraise=True)
def compute_metrics(input_folder, output_metrics_file):
    data_path = Path(input_folder)
    metrics = {}
    for label_folder in data_path.iterdir():
        metrics[label_folder.name] = len(list(label_folder.iterdir()))

    for name, amount in metrics.items():
        logger.info(f"LABEL: {name}: {amount}")

    with open(output_metrics_file, "w") as f:
        json.dump(metrics, f, indent=4)


if __name__ == "__main__":
    fire.Fire(compute_metrics)