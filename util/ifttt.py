import os, requests
from functools import partial

from database import loop

def ifttt_push_sync(event_name, title, subject, text, *, key = None):
    """Synchronously makes a POST request to an IFTTT webhook URL
    given an event name, the title, subject, and text. The key should be specified
    so that the POST request will be sent to the proper user.
    """

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
    """Asynchronously makes a POST request to an IFTTT webhook URL
    given an event name, the title, subject, and text. The key should be specified
    so that the POST request will be sent to the proper user.
    """

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