import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()


# @logger.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> dict[str]:
    try:
        logger.info("start")
        logger.debug("debug...")
        logger.info(f"event:{json.dumps(event)}...")
        logger.info(f"context:{context}...")
        logger.info("end")
        if event["test"] > 100:
            raise ValueError(f"value test {event['test']} too high!")
        return {"test": event["test"]}
    except Exception as e:
        logger.error(f"exception:{e}.")
        return {"msg": "internal server error"}
