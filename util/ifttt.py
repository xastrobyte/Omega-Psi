from os import environ
from functools import partial
from requests import post

from cogs.globals import loop

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class IFTTT:

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    IFTTT_WEBHOOK_URL = "https://maker.ifttt.com/trigger/{}/with/key/{}"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @staticmethod
    def push_sync(event_name, title, subject, text, *, key = None):
        """Synchronously makes an IFTTT call to the webhook URL given the event and webhook key

        Parameters
        ----------
            event_name : str
                An event name to use to send a webhook to
            title : str
                The title of the webhook
            subject : str
                The subject of the webhook
            text : str
                The text of the webhook
        
        Keyword Parameters
        ------------------
            key : str
                A specific IFTTT webhook key to use instead of the default one
        """
        post(
            IFTTT.IFTTT_WEBHOOK_URL.format(
                event_name,
                environ["IFTTT_WEBHOOK_KEY"] if not key else key
            ),
            json = {
                "value1": title,
                "value2": subject,
                "value3": text
            }
        )
    
    @staticmethod
    async def push(event_name, title, subject, text, *, key = None):
        """Asynchronously makes an IFTTT call to the webhook URL given the event and webhook key

        Parameters
        ----------
            event_name : str
                An event name to use to send a webhook to
            title : str
                The title of the webhook
            subject : str
                The subject of the webhook
            text : str
                The text of the webhook
        
        Keyword Parameters
        ------------------
            key : str
                A specific IFTTT webhook key to use instead of the default one
        """
        await loop.run_in_executor(None, 
            partial(
                IFTTT.push_sync,
                event_name, title, subject, text,
                key = key
            )
        )