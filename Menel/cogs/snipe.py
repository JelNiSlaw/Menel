import datetime

import discord
from discord.ext import commands

from ..utils import embeds
from ..utils.context import Context
from ..utils.text_tools import clean_content, human_size, plural


class SnipeMessage:
    def __init__(self, text: str, author: discord.Member, time: datetime):
        self.text = text
        self.author = author
        self.time = time


_SNIPES_TYPE = dict[int, discord.Message]


class SnipeNotFound(commands.CommandError):
    pass


class Snipe(commands.Cog):
    def __init__(self):
        self.delete_snipes: _SNIPES_TYPE = {}
        self.edit_snipes: _SNIPES_TYPE = {}
        self.bot_delete_snipes: _SNIPES_TYPE = {}
        self.bot_edit_snipes: _SNIPES_TYPE = {}

    def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage()
        return True

    async def cog_command_error(self, ctx, error):
        if isinstance(error, SnipeNotFound):
            await ctx.error('Nie wykryłem żadnej wiadomości')

    @staticmethod
    def create_snipe_embed(ctx: Context, snipes: _SNIPES_TYPE) -> discord.Embed:
        if ctx.channel.id not in snipes:
            raise SnipeNotFound()

        message = snipes[ctx.channel.id]
        time = message.edited_at or message.created_at
        color = message.author.color

        if ctx.command_time - time > datetime.timedelta(hours=2):
            raise SnipeNotFound()

        embed = embeds.with_author(
            message.author,
            description=message.content,
            color=color if color != discord.Color.default() else discord.Color.green(),
            timestamp=time
        )
        embed.set_footer(text=str(message.id))

        if message.reference:
            embed.add_field(name='Odpowiedź na', value=f'[link]({message.reference.jump_url})', inline=False)

        if message.attachments:
            attachment_count = len(message.attachments)
            embed.add_field(
                name=f"{plural(attachment_count, 'plik', 'pliki', 'plików')}",
                value='\n'.join(
                    f'[{clean_content(a.filename)}]({a.url}) {human_size(a.size)}' for a in message.attachments
                ),
                inline=False
            )

        return embed

    @commands.command()
    async def snipe(self, ctx: Context):
        """Pokazuje ostatnią usuniętą wiadomość"""
        await ctx.send(embed=self.create_snipe_embed(ctx, self.delete_snipes))

    @commands.command('edit-snipe', aliases=['editsnipe'])
    async def edit_snipe(self, ctx: Context):
        """Pokazuje ostatnią edytowaną wiadomość"""
        await ctx.send(embed=self.create_snipe_embed(ctx, self.edit_snipes))

    @commands.command('bot-snipe', aliases=['botsnipe'])
    async def _bot_snipe(self, ctx: Context):
        """Pokazuje ostatnią usuniętą wiadomość bota lub webhooka"""
        await ctx.send(embed=self.create_snipe_embed(ctx, self.bot_delete_snipes))

    @commands.command('bot-edit-snipe', aliases=['boteditsnipe'])
    async def _bot_edit_snipe(self, ctx: Context):
        """Pokazuje ostatnią edytowaną wiadomość bota lub webhooka"""
        await ctx.send(embed=self.create_snipe_embed(ctx, self.bot_edit_snipes))

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not after.guild:
            return

        if before.content == after.content and len(before.attachments) == len(after.attachments):
            return

        snipes = self.edit_snipes if not after.author.bot else self.bot_edit_snipes

        snipes[after.channel.id] = before

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild:
            return

        if not (message.content or message.attachments):
            return

        snipes = self.delete_snipes if not message.author.bot else self.bot_delete_snipes

        snipes[message.channel.id] = message


def setup(bot):
    bot.add_cog(Snipe())