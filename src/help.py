import logging
import asyncio
from time import time
import discord
from settings import EMOJIS, HELP_TIME
from utilities import *

#########################################
#                                       #
#                                       #
#           Setting up logging          #
#                                       #
#                                       #
#########################################
local_logger = logging.getLogger(__name__)
local_logger.setLevel(LOGGING_LEVEL)
local_logger.addHandler(LOGGING_HANDLER)
local_logger.info("Innitalized {} logger".format(__name__))

#########################################
#                                       #
#                                       #
#           Making commands             #
#                                       #
#                                       #
#########################################


class InteractiveHelp(discord.ext.commands.DefaultHelpCommand):
    """This Help class offers interaction support through embeds and reactions."""

    def __init__(self, react_time: int = HELP_TIME, **options):
        super().__init__(**options, verify_checks=False)
        self.react_time = react_time

    def help_reaction(self, reaction, user):
        if reaction.emoji not in (
            EMOJIS["arrow_backward"],
            EMOJIS["arrow_forward"],
            EMOJIS["information_source"],
            EMOJIS["track_previous"],
            EMOJIS["track_next"],
        ):
            return False

        # making sure the author of the help command is indeed the one reacting
        if user == reaction.message.author:
            return False

        return True

    def get_help_lang(self):
        if isinstance(self.get_destination(), discord.Guild):
            with ConfigFile(self.get_destination().guild.id) as conf:
                lang = conf["lang"]
        else:
            lang = "en"
        return lang

    async def set_reactions(self, msg: discord.Message, pages: int):
        # adding approriate interactions
        if pages > 1:
            if pages > 2:
                await msg.add_reaction(EMOJIS["track_previous"])
            await msg.add_reaction(EMOJIS["arrow_backward"])
            await msg.add_reaction(EMOJIS["information_source"])
            await msg.add_reaction(EMOJIS["arrow_forward"])
            if pages > 2:
                await msg.add_reaction(EMOJIS["track_next"])

        else:
            await msg.add_reaction(EMOJIS["information_source"])

    async def start_interaction(self, pages: list, msg: discord.Message):
        current_page = 0
        start_time = time()
        elapsed_time = 0
        try:
            while elapsed_time < self.react_time:
                reaction, user = await self.context.bot.wait_for(
                    "reaction_add",
                    timeout=self.react_time - elapsed_time,
                    check=self.help_reaction,
                )

                # interpret reactions
                if reaction.emoji == EMOJIS["arrow_forward"]:
                    # making sure you're not on the last page
                    local_logger.debug("Going forward in paging")
                    if current_page != len(pages) - 1:
                        current_page += 1

                elif reaction.emoji == EMOJIS["arrow_backward"]:
                    local_logger.debug("Going backward in paging")
                    # making sure you're not on the first page
                    if current_page != 0:
                        current_page -= 1

                elif reaction.emoji == EMOJIS["track_next"]:
                    local_logger.debug("Going to last page.")
                    current_page = len(pages) - 1

                elif reaction.emoji == EMOJIS["track_previous"]:
                    local_logger.debug("Going to first page")
                    current_page = 0

                else:
                    # the only other allowed reaction is information_source
                    local_logger.debug(
                        "Deleting help embed and sending help interface manual."
                    )
                    await self.send_bot_help(self.get_bot_mapping())
                    await msg.delete()
                    return

                await msg.remove_reaction(reaction, user)
                await msg.edit(suppress=False, embed=pages[current_page])
                elapsed_time = time() - start_time
        except asyncio.exceptions.TimeoutError:
            await msg.delete()

    async def send_bot_help(self, mapping):
        pages = get_bot_pages(self.context.bot.cogs, self.get_help_lang())
        msg = await self.get_destination().send(embed=pages[0])

        await self.set_reactions(msg, len(pages))
        await self.start_interaction(pages, msg)

    async def send_cog_help(self, cog):
        pages = get_cog_pages(cog, self.get_help_lang())
        msg = await self.get_destination().send(embed=pages[0])

        await self.set_reactions(msg, len(pages))
        await self.start_interaction(pages, msg)

    async def send_group_help(self, group):
        pages = get_group_pages(group, self.get_help_lang())
        msg = await self.get_destination().send(embed=pages[0])

        await self.set_reactions(msg, len(pages))
        await self.start_interaction(pages, msg)

    async def send_command_help(self, command):
        pages = get_command_pages(command, self.get_help_lang())
        msg = await self.get_destination().send(embed=pages[0])

        await self.set_reactions(msg, len(pages))
        await self.start_interaction(pages, msg)


def get_help(command, lang: str):
    """this needs heavy refactoring"""
    if command.cog:
        text = Translator(
            command.cog.__module__.split(".")[-1], lang, help_type=True
        )._dict
        if not command.parents:
            if isinstance(command, discord.ext.commands.Group):
                return text[command.name][0]  # returns the description of the group
            elif isinstance(command, discord.ext.commands.Command):
                return text[command.name]

        else:
            if isinstance(command, discord.ext.commands.Command):
                for parent in command.parents:
                    text = text[parent.name][1]
                return text[command.name]
            elif isinstance(command, discord.ext.commands.Group):
                for parent in command.parents[:-1]:
                    text = text[parent.name][1]
                return text[0]  # returns the description of the group

    else:
        # the only commands not in a cog are in main.py -> ext group
        return Translator("default", lang, help_type=True)[command.name]


def get_bot_pages(cog_mapping, lang: str):
    """currently doesn't support commands outside of cogs"""
    cogs = cog_mapping.values()
    cog_names = cog_mapping.keys()

    pages = []
    for cog in cogs:
        pages += get_cog_pages(cog, lang, paginate=False)

    # explaining how help works
    tr = Translator("help", lang, help_type=True)._dict
    description = tr["description"]
    header = discord.Embed(title="Help", description=description, color=7506394)

    # listing all available cogs
    chars_per_cog = int(5000 / len(cog_names))
    index = discord.Embed(
        title="Index",
        description="Here's an index of all cogs (sometimes also refered to as extensions) this bot contains. To get more information on a specific one type `::help <cog>`. Otherwise you can also browse through the pages.",
        color=7506394,
    )
    for cog in cog_names:
        index.add_field(name=cog, value=tr[cog.lower()][:chars_per_cog], inline=True)

    pages_number = len(pages)
    header.set_footer(text=f"Page (1/{pages_number+2})")
    index.set_footer(text=f"Page (2/{pages_number+2})")
    for embed, crt in zip(pages, range(pages_number)):
        embed.set_footer(text=f"Page ({crt+3}/{pages_number+2})")

    pages.insert(0, header)
    pages.insert(1, index)
    return pages


def get_cog_pages(
    cog: discord.ext.commands.Cog, lang: str, paginate: bool = True
) -> list:
    pages = []
    for command in cog.get_commands():
        if isinstance(command, discord.ext.commands.Group):
            pages += get_group_pages(command, lang, paginate=False)
        else:
            pages += get_command_pages(command, lang, paginate=False)

    description = Translator("help", lang, help_type=True)._dict[
        cog.qualified_name.lower()
    ]
    header = discord.Embed(
        title=cog.qualified_name, description=description, color=7506394
    )

    # paginating
    if paginate:
        pages_number = len(pages)
        header.set_footer(text=f"Page (1/{pages_number+1})")
        for embed, crt in zip(pages, range(pages_number)):
            embed.set_footer(text=f"Page ({crt+2}/{pages_number+1})")

    pages.insert(0, header)
    return pages


def get_group_pages(
    group: discord.ext.commands.Group, lang: str, paginate: bool = True
) -> list:
    pages = []
    for command in group.commands:
        pages += get_command_pages(command, lang, paginate=False)

    description = get_help(group, lang)
    header = discord.Embed(title=group.name, description=description, color=7506394)

    # paginating
    if paginate:
        pages_number = len(pages)
        header.set_footer(text=f"Page (1/{pages_number+1})")
        for embed, crt in zip(pages, range(pages_number)):
            embed.set_footer(text=f"Page ({crt+2}/{pages_number+1})")

    pages.insert(0, header)
    return pages


def get_command_pages(
    command: discord.ext.commands.command,
    lang: str,
    threshold: int = 150,
    paginate: bool = True,
) -> list:
    """this returns a list of Embeds that represent help pages
    cmd_type is an int that must be 0 (command), 1 (cog), 2 (group)
    maybe return a generator instead?"""
    name = ""
    if command.parents:
        for parent in command.parents:
            name += f"{parent.name} / "
    name += command.name

    description, usage = get_help(command, lang)

    # split command in multiple pages
    if (
        count_chars(description, usage, name) > 2048 - threshold
    ):  # maximum embed description size is 2048 chars
        pages = []
        # splitting by line breaks
        paragraphs = description.split("\n")

        # splitting by "."
        for paragraph in paragraphs:
            if count_chars(paragraph) > 2048 - threshold:
                sentences = paragraph.split(".")
                assert len(sentences) > 0, ValueError(
                    "No known parsing method for this help string. Should contain at least one dot."
                )
                while sentences:
                    page = ""  # the page we're starting to build
                    crt_count = 2048  # how many chars are left before we need to make a new page
                    while (crt_count > threshold) and len(sentences) != 0:
                        # print(sentences)
                        sentence = sentences.pop(0)
                        crt_count -= count_chars(sentence)
                        # /!\ currently not handling the case of sentences larger than 2048 chars
                        assert crt_count > 0, ValueError(
                            "This sentence is over 2048 characters long!"
                        )  # > and not >= because we need to add the dot again
                        page += sentence + "."
                    pages.append(page)

            else:
                pages.append(paragraph)
    else:
        pages = [description]

    # building the embeds from the paged descriptions
    embeds = []
    pages_number = len(pages)
    for page, crt in zip(pages, range(len(pages))):
        embed = discord.Embed(title=name, description=page, color=7506394,)
        if paginate:
            embed.set_footer(text=f"Page ({crt+1}/{pages_number})")
        embed.add_field(name="Usage", value=f"`{command.name} {usage}", inline=False)
        embeds.append(embed)

    return embeds


def count_chars(*args: str) -> int:
    count = 0
    for string in args:
        assert type(string) == str, TypeError(
            f"args should be of type str not {type(string)}"
        )
        count += len(string)
    return count
