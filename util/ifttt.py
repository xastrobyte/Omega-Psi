import os, requests
from functools import partial

from database import loop

def ifttt_push_sync(event_name, title, subject, text, *, key = None):

    # Make a post request to IFTTT using the event specified
    requests.post(
        "https://maker.ifttt.com/trigger/{}/with/key/{}".format(
            event_name,
            os.environ["IFTTT_WEBHOOK_KEY"] if key == None else key
        ),
        json = {
            "value1": title,
            "value2": subject,
            "value3": text
        }
    )

async def ifttt_push(event_name, title, subject, text, *, key = None):

    # Make a post request to IFTTT using the event specified
    await loop.run_in_executor(None,
        partial(
            requests.post,
            "https://maker.ifttt.com/trigger/{}/with/key/{}".format(
                event_name,
                os.environ["IFTTT_WEBHOOK_KEY"] if key == None else key
            ),
            json = {
                "value1": title,
                "value2": subject,
                "value3": text
            }
        )
    )