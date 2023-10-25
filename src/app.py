import json
import logging


def lambda_handler(event, context):
    logging.debug(f"event:{event}...")
    logging.debug(f"context:{context}...")
    return {"msg": f"ciao{json.dumps(event)}."}
