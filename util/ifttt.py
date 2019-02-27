import os, requests
from functools import partial

from database import loop

def ifttt_push_sync(title, subject, text):

    # Make a post request to IFTTT using the "on_push" event
    requests.post(
        "https://maker.ifttt.com/trigger/on_push/with/key/{}".format(
            os.environ["IFTTT_WEBHOOK_KEY"]
        ),
        json = {
            "value1": title,
            "value2": subject,
            "value3": text
        }
    )

async def ifttt_push(title, subject, text):

    # Make a post request to IFTTT using the "on_push" event
    await loop.run_in_executor(None,
        partial(
            requests.post,
            "https://maker.ifttt.com/trigger/on_push/with/key/{}".format(
                os.environ["IFTTT_WEBHOOK_KEY"]
            ),
            json = {
                "value1": title,
                "value2": subject,
                "value3": text
            }
        )
    )