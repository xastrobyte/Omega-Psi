import discord, requests
from datetime import datetime
from functools import partial
from random import choice

import database
from category import errors
from category.globals import PRIMARY_EMBED_COLOR

MAX_POST_INTERVAL = 1000

REDDIT_API_URL = "https://www.reddit.com/r/{}/.json?sort=top&limit={}"

async def get_reddit_post(subreddit, allow_nsfw = True, max_posts = 1):

    # Generate post while any of the following are True
    #  the post is a video
    #  the post is an ad
    post = None
    max_posts = max_posts * MAX_POST_INTERVAL
    while True:

        # Request subreddit
        response = await database.loop.run_in_executor(None,
            partial(
                requests.get,
                REDDIT_API_URL.format(
                    subreddit,
                    max_posts
                ),
                headers = {
                    "User-agent": "Omega Psi"
                }
            )
        )
        response = response.json()

        # Choose post only if there are posts to choose from
        if len(response["data"]["children"]) == 0:
            return errors.get_error_message(
                "There are no posts in this subreddit or it doesn't exist."
            )

        post = choice(response["data"]["children"])["data"]

        # Check if is_video is true
        if post["is_video"]:
            continue

        # Check if allow_nsfw is false but the post is nsfw
        if post["over_18"] and not allow_nsfw:
            continue
        
        # Everything else is valid
        break
    
    # Get proper post
    if post["media"] != None:
        image_url = post["media"]["oembed"]["thumbnail_url"]
    
    else:
        image_url = post["url"]
    
    post_url = "https://www.reddit.com{}".format(post["permalink"])
    title = post["title"]
    timestamp = post["created"]
    upvotes = post["score"]

    return discord.Embed(
        title = "{} {}".format(
            title,
            " - (NSFW)" if post["over_18"] else ""
        ),
        description = " ",
        colour = PRIMARY_EMBED_COLOR,
        url = post_url,
        timestamp = datetime.fromtimestamp(timestamp)
    ).set_image(
        url = image_url
    ).set_footer(
        text = "⬆ {}".format(upvotes)
    )