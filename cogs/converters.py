from discord.ext.commands import Converter

class CommandConverter(Converter):
    async def convert(self, ctx, cmd):
        """A converter function to get a command

        :param ctx: The context of where the converter acts upon
        :param cmd: The command to convert, if possible
        :return: The command object or just the given cmd parameter
        """
        command = ctx.bot.get_command(cmd)
        if command is not None:
            return command
        return cmd