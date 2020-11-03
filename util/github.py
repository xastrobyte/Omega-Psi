from os import environ
from functools import partial

from requests import get, post, patch

from cogs.globals import loop

create_issue_url = "https://api.github.com/repos/FellowHashbrown/Omega-Psi/issues"
update_issue_url = create_issue_url + "/{}"
GITHUB_ISSUE_URL = "https://github.com/FellowHashbrown/Omega-Psi/issues/{}"

def create_issue_sync(title: str, body: str, *, is_bug: bool=True) -> dict:
    """Synchronously creates an issue on GitHub for a bug or suggestion made
    towards Omega Psi

    :param title: The title of the issue
    :param body: The description of the issue
    :param is_bug: Whether or not the issue pertains to a bug
        (Default: False)
    """

    response = post(
        create_issue_url,
        json = {
            "title": title,
            "body": body,
            "labels": [
                "bug" if is_bug else "enhancement"
            ]
        },
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {environ['GITHUB_TOKEN']}"
        }
    )
    return response.json()

async def create_issue(title: str, body: str, *, is_bug: bool=True) -> dict:
    """Asynchronously creates an issue on GitHub for a bug or suggestion made
    towards Omega Psi

    :param title: The title of the issue
    :param body: The description of the issue
    :param is_bug: Whether or not the issue pertains to a bug
        (Default: False)
    """
    return await loop.run_in_executor(
        None, 
        partial(
            create_issue_sync, 
            title, body, is_bug = is_bug))

def fix_issue_sync(number: int, *, reason: str=None) -> dict:
    """Synchronously labels the specified issue as fixed, or closed.

    :param number: The issue number on GitHub to fix or consider, if a suggestion
    :param reason: The reason the issue was not considered.
        Note: this parameter only applies to suggestions
    """

    # Get the issue from GitHub to get the body and
    #   update it, if needed
    response = get(
        update_issue_url.format(number),
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {environ['GITHUB_TOKEN']}"
        }
    )
    body = response.json()["body"]
    if reason is True:
        body += "\n# Considered\n"
    elif reason is not None:
        body += "\n# Not Considered\n{}".format(reason)

    # Update the issue in GitHub
    response = patch(
        update_issue_url.format(number),
        json = {
            "body": body,
            "state": "closed"
        },
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {environ['GITHUB_TOKEN']}"
        }
    )
    return response.json()

async def fix_issue(number: int, *, reason: str=None) -> dict:
    """Synchronously labels the specified issue as fixed, or closed.

    :param number: The issue number on GitHub to fix or consider, if a suggestion
    :param reason: The reason the issue was not considered.
        Note: this parameter only applies to suggestions
    """
    return await loop.run_in_executor(
        None, 
        partial(
            fix_issue_sync, number,
            reason = reason))
