import fire
from loguru import logger
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline


def _get_pipeline(model_folder):
    model = AutoModelForSequenceClassification.from_pretrained(model_folder)
    tokenizer = AutoTokenizer.from_pretrained(model_folder)

    pipeline = TextClassificationPipeline(model=model, tokenizer=tokenizer)
    return pipeline


@logger.catch(reraise=True)
def inference(model_folder, text):
    pipeline = _get_pipeline(model_folder)

    return pipeline([f"{text}"])


if __name__ == "__main__":
    fire.Fire(inference)