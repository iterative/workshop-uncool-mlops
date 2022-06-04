# Automation

Due the nature of the dataset being used, it makes sense to automate the retraining of the model
as new data arrives to the data source.

We can use a cron schedule in a GitHub actions workflow and combine it with `dvc exp run --set-param` feature
in order to update parameters on the fly.

<details>
<summary>Create and fill `.github/workflows/daily.yml`</summary>

https://github.com/iterative/workshop-uncool-mlops-solution/blob/main/.github/workflows/daily.yaml

</details>