from functools import partial
from os import environ
from requests import get, post

from cogs.globals import loop

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Imgur:
    """A static class to process Imgur album API methods."""

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    IMGUR_ALBUM_API = "https://api.imgur.com/3/album"
    IMGUR_ALBUM_GET_API = "https://api.imgur.com/3/album/{}"
    IMGUR_IMAGE_API = "https://api.imgur.com/3/image"

    IMGUR_ALBUM_URL = "https://imgur.com/a/{}"
    IMGUR_IMAGE_URL = "https://i.imgur.com/{}.png"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @staticmethod
    async def create_imgur_album(data = None):
        """Creates an anonymous Imgur album and returns the album hash and album ID

        Parameters
        ----------
            data : dict or None
                The default data to create the Imgur album with
        
        Returns
        -------
            dict
                A dict object containing the created album hash and the created album ID
        """

        # Make a POST request to create the anonymous Imgur album
        result = await loop.run_in_executor(None,
            partial(
                post, Imgur.IMGUR_ALBUM_API,
                data = data,
                headers = {
                    "Authorization": "Client-ID {}".format(
                        environ["IMGUR_API_KEY"]
                    )
                }
            )
        )
        result = result.json()

        # Check if the creation failed
        if result["status"] != 200:
            return None
        
        # The album creation did not fail
        else:
            return {
                "hash": result["data"]["deletehash"], 
                "id": result["data"]["id"]
            }
    
    @staticmethod
    async def add_to_imgur_album(url, album_hash):
        """Adds an image at the specified URL to the specified album given the album hash

        Parameters
        ----------
            url : str
                The URL of an image to add
            album_hash : str
                The anonymous album to add the image to

        Returns
        -------
            bool
                Whether or not the image was added to specified album.
        """
        
        # Make a POST request to add upload the image to the specified Imgur album hash
        result = await loop.run_in_executor(None,
            partial(
                post, Imgur.IMGUR_IMAGE_API,
                data = {
                    "image": url,
                    "album": album_hash
                },
                headers = {
                    "Authorization": "Client-ID {}".format(
                        environ["IMGUR_API_KEY"]
                    )
                }
            )
        )
        result = result.json()

        # Check if image upload failed
        if result["status"] != 200:
            return {"success": False, "reason": result["data"]["error"]}

        # Image upload did not fail, return the ID of the uploaded image
        return {"success": True, "result": result["data"]["id"]}
    
    @staticmethod
    async def get_imgur_album(album_id):
        """Gets a list of images from the specified album

        Parameters
        ----------
            album_id : str
                The ID of the album to get images from

        Returns
        -------
            list
                A list of images from the specified album
        """
        
        # Make a GET request to access the images from the specified album
        result = await loop.run_in_executor(None,
            partial(
                get, Imgur.IMGUR_ALBUM_GET_API.format(album_id),
                headers = {
                    "Authorization": "Client-ID {}".format(
                        environ["IMGUR_API_KEY"]
                    )
                }
            )
        )
        result = result.json()
        return result["data"]["images"]