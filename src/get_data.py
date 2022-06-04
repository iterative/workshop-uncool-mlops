import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

import fire
import yaml
from github import Github
from loguru import logger


def clean_labels(labels):
    return [
        x.name.replace("A: ", "")
        for x in labels
    ]


@logger.catch(reraise=True)
def get_data(output_folder):
    with open("params.yaml") as f:
        params = yaml.safe_load(f)["data"]

    output_folder = Path(output_folder)
    for label in params["labels"]:
        (output_folder / label).mkdir(parents=True, exist_ok=True)

    since = datetime(*map(int, params["since"].split("/")))
    until = datetime(*map(int, params["until"].split("/")))
    logger.info(f"Getting issue labels since {since} until {until}")

    logger.info("Initializing Github")
    if os.environ.get("GITHUB_TOKEN"):
        g = Github(os.environ["GITHUB_TOKEN"])
    else:
        g = Github()

    logger.info(f"Querying repo: {params['repo']}")
    repo = g.get_repo(params["repo"])

    metrics = Counter()
    for issue in repo.get_issues(since=since):
        issue_labels = [
            label 
            for label in clean_labels(issue.labels) 
            if label in params["labels"]
        ]
    
        if (
            issue.pull_request 
            or issue.created_at > until
            or len(issue_labels) != 1
        ):
            logger.debug(f"Skipping issue: {issue.title}")
            logger.debug(f"Created at: {issue.created_at}")
            logger.debug(f"Labels: {issue.labels}")
            continue
    
        label = str(issue_labels[0])
        logger.info(f"\nTITLE: {issue.title}\nLABEL: {label}")

        output_file = output_folder / label / f"{issue.number}.txt"
        output_file.write_text(f"{issue.title}")
        metrics[label] += 1

    Path(params["metrics_file"]).write_text(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    fire.Fire(get_data)