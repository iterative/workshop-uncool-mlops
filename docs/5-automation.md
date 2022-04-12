# Automation

Due the nature of the dataset being used, it makes sense to automate the retraining of the model
as new data arrives to the data source.

We can use a cron schedule in a GitHub actions workflow and combine it with `dvc exp run --set-param` feature
in order to update parameters on the fly.

<details>
<summary>Create and fill `.github/workflows/daily.yml`</summary>

```yaml
name: Daily DVC & CML Workflow

on:
  schedule:
    - cron: "0 0 * * *"

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    container: docker://ghcr.io/iterative/cml:latest

    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0

      - name: Setup
        run: |
          pip install -r requirements.txt

      - name: Run DVC pipeline
        env:
          GITHUB_TOKEN: ${{ secrets.PERSONAL_GITHUB_TOKEN }}
          GDRIVE_CREDENTIALS_DATA: ${{ secrets.GDRIVE_CREDENTIALS_DATA }}
        run: |
          dvc exp run --set-param data.until=$(date +'%Y/%m/%d') --pull

      - name: Share changes
        env:
          GDRIVE_CREDENTIALS_DATA: ${{ secrets.GDRIVE_CREDENTIALS_DATA }}
        run: |
          dvc push

      - name: Create a P.R. with CML 
        env:
          REPO_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          cml pr "dvc.lock" "outs/*.json" "outs/eval"  "outs/train_metrics" "params.yaml"
```
</details>