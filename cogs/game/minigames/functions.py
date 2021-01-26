from asyncio import wait, FIRST_COMPLETED

async def wait_for_reaction(bot, message, member, valid_reactions):
    """Waits for a user to react to a message and returns it

    :param game: The game to use in connection with message reactions
    :param member: The member to test the reaction for
    :param valid_reactions: A list of reactions to 
    """

    def check_reaction(reaction, user):
        return (
            reaction.message.id == message.id and
            user.id == member.id and
            str(reaction) in valid_reactions
        )
    
    done, pending = await wait([
        bot.wait_for("reaction_add", check = check_reaction),
        bot.wait_for("reaction_remove", check = check_reaction)
    ], return_when = FIRST_COMPLETED)
    reaction, user = done.pop().result()
    for future in pending:
        future.cancel()
    
    return str(reaction)