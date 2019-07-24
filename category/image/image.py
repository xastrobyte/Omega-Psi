import asyncio, discord, os, requests
from discord.ext import commands
from functools import partial
from random import choice, randint

from category import errors
from category.globals import FIELD_THRESHOLD
from category.globals import SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE
from category.globals import get_embed_color
from category.predicates import is_nsfw_or_private
from database import loop
from database import database
from util.string import generate_random_string
from util.discord import get_reddit_post

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

AVATAR_LIST = "https://api.adorable.io/avatars/list"
AVATAR_API = "https://api.adorable.io/avatars/face/{}/{}/{}/{}"

IMGUR_ALBUM_API = "https://api.imgur.com/3/album"
IMGUR_ALBUM_GET_API = "https://api.imgur.com/3/album/{}"
IMGUR_IMAGE_API = "https://api.imgur.com/3/image"
IMGUR_REMOVE_IMAGE_API = "https://api.imgur.com/3/album/{}/remove_images"

IMGUR_ALBUM_URL = "https://imgur.com/a/{}"
IMGUR_IMAGE_URL = "https://i.imgur.com/{}"

ROBOHASH_API = "https://robohash.org/{}"

MEME_SUBREDDITS = [
    "meme",
    "blackpeopletwitter",
    "me_irl",
    "coaxedintoasnafu",
    "dankmemes"
]

class Image(commands.Cog, name = "image"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "meme",
        description = "Sends you a random meme from reddit.",
        cog_name = "image"
    )
    @commands.check(is_nsfw_or_private)
    async def meme(self, ctx):

        await ctx.send(
            embed = await get_reddit_post("+".join(MEME_SUBREDDITS), max_posts = len(MEME_SUBREDDITS))
        )

    @commands.command(
        name = "imgur",
        description = "Allows you to upload an image to an anonymous imgur album.",
        cog_name = "image"
    )
    async def imgur(self, ctx, *params):
        
        attachments = ctx.message.attachments

        # Get album for user
        album = await database.users.get_imgur(ctx.author)
        album_hash = album["hash"]
        album_id = album["id"]

        # Check if there are no parameters and no attachments
        if not (len(params) == 0 and len(attachments) == 0):

            # Check if user does not have an album attached to them
            field_value = ""
            fields = []
            if not album_id:
                result = await loop.run_in_executor(None,
                    partial(
                        requests.post,
                        IMGUR_ALBUM_API,
                        data = {
                            "title": ctx.author,
                            "description": "An anonymous imgur album made for the above Discord User"
                        },
                        headers = {
                            "Authorization": "Client-ID {}".format(
                                os.environ["IMGUR_API_KEY"]
                            )
                        }
                    )
                )
                result = result.json()

                # See if album creation failed
                if result["status"] != 200:
                    error = result["data"]["error"] + "\n"

                    # Add error to the result field
                    if len(field_value) + len(error) > FIELD_THRESHOLD:
                        fields.append(field_value)
                        field_value = ""
                    
                    field_value += error
                
                # ALbum creation did not fail
                else:
                    success = "Anonymous Album Create at [this link]({}).\n".format(
                        IMGUR_ALBUM_URL.format(result["data"]["id"])
                    )

                    # Add the success message to the result field
                    if len(field_value) + len(success) > FIELD_THRESHOLD:
                        fields.append(field_value)
                        field_value = ""
                    
                    field_value += success

                    # Set the user's imgur album
                    album_hash = result["data"]["deletehash"]
                    album_id = result["data"]["id"]
                    await database.users.set_imgur(ctx.author, {"hash": album_hash, "id": album_id})
            
            # Not getting their album and images; Adding one
            else:

                # Get url for each attachment
                for attachment in range(len(attachments)):
                    attachments[attachment] = attachments[attachment].url
                
                attachments += params

                # Iterate through attachments
                for attachment in attachments:

                    # Upload image
                    result = await loop.run_in_executor(None,
                        partial(
                            requests.post,
                            IMGUR_IMAGE_API,
                            data = {
                                "image": attachment,
                                "album": album_hash
                            },
                            headers = {
                                "Authorization": "Client-ID {}".format(
                                    os.environ["IMGUR_API_KEY"]
                                )
                            }
                        )
                    )
                    result = result.json()

                    # See if image upload failed
                    if result["status"] != 200:
                        error = result["data"]["error"] + "\n"

                        # Add the error to the result field
                        if len(field_value) + len(error) > FIELD_THRESHOLD:
                            fields.append(field_value)
                            field_value = ""
                        
                        field_value += error
                    
                    # Image upload did not fail
                    else:
                        success = "Anonymous Image uploaded and Added to your album. [Here]({}) is the direct link to the image.\n".format(
                            IMGUR_IMAGE_URL.format(
                                result["data"]["id"]
                            )
                        )

                        # Add the success message to the result field
                        if len(field_value) + len(success) > FIELD_THRESHOLD:
                            fields.append(field_value)
                            field_value = ""
                        
                        field_value += success
                
                # Add the trailing result field
                if len(field_value) > 0:
                    fields.append(field_value)
                
                # Create embed
                embed = discord.Embed(
                    title = "Results {}".format(
                        "({} / {})".format(
                            1, len(fields)
                        ) if len(fields) > 1 else ""
                    ),
                    description = fields[0],
                    colour = await get_embed_color(ctx.author)
                )

                # Add all the fields to the embed
                count = 1
                for field in fields[1:]:
                    count += 1
                    embed.add_field(
                        name = "Results {}".format(
                            "({} / {})".format(
                                count, len(fields)
                            ) if len(fields) > 1 else ""
                        ),
                        value = field,
                        inline = False
                    )
                
                await ctx.send(
                    embed = embed
                )
            
        # Getting author's images
        else:

            # Get the list of images
            album = await loop.run_in_executor(None,
                partial(
                    requests.get,
                    IMGUR_ALBUM_GET_API.format(
                        album_id
                    ),
                    headers = {
                        "Authorization": "Client-ID {}".format(
                            os.environ["IMGUR_API_KEY"]
                        )
                    }
                )
            )
            album = album.json()

            # Create the scrolling embed
            count = 0
            embed = discord.Embed(
                title = "Image {}".format(
                    "({} / {})".format(
                        count + 1, len(album["data"]["images"])
                    ) if len(album["data"]["images"]) > 1 else ""
                ),
                description = album["data"]["description"] if len(album["data"]["images"]) > 0 else "You do not have any images in your album.",
                colour = await get_embed_color(ctx.author),
                url = album["data"]["link"]
            ).set_author(
                name = album["data"]["title"],
                icon_url = ctx.author.avatar_url
            )

            if len(album["data"]["images"]) > 0:
                embed.set_image(
                    url = album["data"]["images"][count]["link"]
                )

            msg = await ctx.send(
                embed = embed
            )

            # Add reactions
            if len(album["data"]["images"]) > 1:

                if len(album["data"]["images"]) > 2:
                    await msg.add_reaction(FIRST_PAGE)

                await msg.add_reaction(PREVIOUS_PAGE)
                await msg.add_reaction(NEXT_PAGE)

                if len(album["data"]["images"]) > 2:
                    await msg.add_reaction(LAST_PAGE)

            await msg.add_reaction(LEAVE)

            while True:

                # Wait for next reaction from user
                def check(reaction, user):
                    return str(reaction) in SCROLL_REACTIONS and reaction.message.id == msg.id and user == ctx.author

                done, pending = await asyncio.wait([
                    self.bot.wait_for("reaction_add", check = check),
                    self.bot.wait_for("reaction_remove", check = check)
                ], return_when = asyncio.FIRST_COMPLETED)

                reaction, user = done.pop().result()

                # Cancel any futures
                for future in pending:
                    future.cancel()

                # Reaction is first page; Go to first image
                if str(reaction) == FIRST_PAGE:
                    count = 0
                
                # Reaction is last page; Go to last image
                elif str(reaction) == LAST_PAGE:
                    count = len(album["data"]["images"]) - 1
                
                # Reaction is previous page; Go to previous page
                # If current page goes below 0, set current page to 0
                elif str(reaction) == PREVIOUS_PAGE:
                    count -= 1
                    if count < 0:
                        count = 0
                
                # Reaction is next page; Go to next page
                # If current page goes above max page, set current page to max page
                elif str(reaction) == NEXT_PAGE:
                    count += 1
                    if count > len(album["data"]["images"]) - 1:
                        count = len(album["data"]["images"]) - 1
                
                # Reaction is leave; Delete the message that this is wrapped around and break from the loop
                elif str(reaction) == LEAVE:
                    await msg.delete()
                    break
                
                # Update the embed
                await msg.edit(
                    embed = discord.Embed(
                        title = "Image {}".format(
                            "({} / {})".format(
                                count + 1, len(album["data"]["images"])
                            ) if len(album["data"]["images"]) > 1 else ""
                        ),
                        description = album["data"]["description"],
                        colour = await get_embed_color(ctx.author),
                        url = album["data"]["link"]
                    ).set_image(
                        url = None if len(album["data"]["images"]) == 0 else album["data"]["images"][count]["link"]
                    ).set_author(
                        name = album["data"]["title"],
                        icon_url = ctx.author.avatar_url if album["data"]["cover"] == None else IMGUR_IMAGE_URL.format(album["data"]["cover"])
                    )
                )
    
    @commands.command(
        name = "avatar",
        description = "Sends a random cute avatar.",
        cog_name = "image"
    )
    async def avatar(self, ctx):
        
        # Get list of face features
        face_values = await loop.run_in_executor(None,
            requests.get,
            AVATAR_LIST
        )
        face_values = face_values.json()["face"]

        # Choose random eyes, nose, mouth, and color
        eyes = choice(face_values["eyes"])
        nose = choice(face_values["nose"])
        mouth = choice(face_values["mouth"])
        color = hex(randint(0, 16777215))[2:].rjust(6, "0")

        # Send image in embed
        await ctx.send(
            embed = discord.Embed(
                title = "Avatar!",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = AVATAR_API.format(eyes, nose, mouth, color)
            )
        )
    
    @commands.command(
        name = "robohash",
        aliases = ["robo"],
        description = "Sends a robohash avatar based off the text you enter.",
        cog_name = "image"
    )
    async def robohash(self, ctx, *, text = None):
        
        # Generate personal robohash if content is empty
        if text == None:
            text = str(ctx.author.id)
        
        elif text == "random":
            text = generate_random_string()
        
        # Send image in embed
        await ctx.send(
            embed = discord.Embed(
                title = "Robohash!",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = ROBOHASH_API.format(text.replace(" ", "+"))
            )
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @meme.error
    async def nsfw_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                embed = errors.get_error_message(
                    "You can only run this command in NSFW channels."
                )
            )

def setup(bot):
    bot.add_cog(Image(bot))