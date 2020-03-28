#!/usr/bin/env python3.7

import discord
import math
import time
import random
import logging
import json
import os

from settings import *
from utilities import *
from help import InteractiveHelp
import config as cfg


# INITS THE BOT
bot = commands.Bot(command_prefix=PREFIX, help_command=None)

bot.help_command = InteractiveHelp(
    command_attrs={
        "max_concurrency": discord.ext.commands.MaxConcurrency(
            1, per=commands.BucketType.user, wait=False
        )
    }
)

#########################################
#                                       #
#                                       #
#           Setting up logging          #
#                                       #
#                                       #
#########################################

# Creating main logger
main_logger = logging.getLogger(__name__)
main_logger.setLevel(LOGGING_LEVEL)
main_logger.addHandler(LOGGING_HANDLER)
main_logger.info(f"Initalized {__name__} logger")


# Creating discord.py's logger
discord_logger = logging.getLogger("discord")
discord_logger.setLevel(LOGGING_LEVEL)
discord_logger.addHandler(LOGGING_HANDLER)
discord_logger.info("Initalized discord's logger")


#########################################
#                                       #
#                                       #
#           Extension Manipulation      #
#                                       #
#                                       #
#########################################


# commands that lets admin update the bot without shutting it down
@bot.group(aliases=["extension"])
@is_runner()
async def ext(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(ERR_NOT_ENOUGH_ARG)


@ext.command()
async def reload(ctx, extension: str):
    try:
        bot.reload_extension(os.path.join(EXT_FOLDER, extension))
        await ctx.send("Successfully reloaded {}".format(extension))
    except Exception as e:
        await ctx.send(
            "Couldn't reload extension {} because:```python\n{}```".format(extension, e)
        )
        raise e


@ext.command()
async def add(ctx, *extensions: str):
    for extension in extensions:
        # trying to load the extension. Should only fail if the extension is not installed
        try:
            bot.load_extension(str(EXT_FOLDER + "." + extension))

        except Exception as e:
            main_logger.exception(e)
            await ctx.send("UnexpectedError:\tReport issue to an admin\n{}".format(e))
            raise e

        # if the extension was correctly loaded, adding it to the enabled file
        try:
            with open(EXTENSIONS_FILE, "r") as file:
                enabled_exts = json.load(file)

            enabled_exts[extension] = True

            with open(EXTENSIONS_FILE, "w") as file:
                json.dump(enabled_exts, file)

        except FileNotFoundError as e:
            # if the file didn't yet exist a new one will be created. This should not happen, only here as a failsafe
            main_logger.warning("{} doesn't exist.".format(EXTENSIONS_FILE))
            with open(EXTENSIONS_FILE, "w") as file:
                file.write(DEFAULT_EXTENSIONS_JSON)

        except Exception as e:
            # logging any other possible issue
            await ctx.send("UnexpectedError:\tReport issue to an admin")
            raise e

        await ctx.send(f"Successfully added and loadded {extension}")


@ext.command()
async def rm(ctx, extension: str):
    try:
        bot.unload_extension(str(EXT_FOLDER + "." + extension))

    except Exception as e:
        main_logger.exception(e)
        await ctx.send(f"UnexpectedError:\tReport issue to an admin\n{e}")
        raise e

    # if the extension was correctly unloaded, removing it from the enblaed extension file
    try:
        with open(EXTENSIONS_FILE, "r") as file:
            enabled_exts = json.load(file)

        enabled_exts[extension] = False

        with open(EXTENSIONS_FILE, "w") as file:
            json.dump(enabled_exts, file)

    except Exception as e:
        main_logger.exception(e)
        await ctx.send(f"UnexpectedError:\tReport issue to an admin\n{e}")
        raise e

    await ctx.send(f"Successfully removed and unloaded {extension}")
    local_logger.info(f"Disabled and removed {extension}")


@ext.command()
@is_runner()
async def ls(ctx):
    try:
        enabled = []
        running = []
        disabled = []
        # fetching list of enbaled and disabled extensions
        with ConfigFile(EXTENSIONS_FILE[:-5], folder=".") as exts:
            for e in exts:
                if exts[e] == True:
                    enabled.append(e)
                else:
                    disabled.append(e)

        # checking whether all enabled extensions are running
        for e in bot.extensions.keys():
            running.append(e)

        # building strings
        disabled_str = ""
        for e in disabled:
            disabled_str += EMOJIS["X"] + e + "\n"

        enabled_str = ""
        for e in enabled:
            if EXT_FOLDER + "." + e in running:
                enabled_str += EMOJIS["check"] + e + "\n"
            else:
                enabled_str += EMOJIS["x"] + e + "\n"

        # building embed
        ext_embed = discord.Embed(
            title="Extensions",
            description="The list of all extensions and their status",
            colour=7506394,
            url=None,
        )

        # ext_embed.set_thumbnail(url=bot.avatar_url)
        ext_embed.add_field(name="Enabled", value=enabled_str, inline=False)
        if len(disabled_str) != 0:
            ext_embed.add_field(name="Disabled", value=disabled_str, inline=False)

        await ctx.send(embed=ext_embed)

    except Exception as e:
        raise e
        LOCAL_LOGGER.exception(e)


#########################################
#                                       #
#                                       #
#           Setup & Execution           #
#                                       #
#                                       #
#########################################
# loading enabled extensions and starting
# bot

# trying to load all enabled extensions
try:
    assert_struct(bot.guilds)
    bot.add_cog(cfg.Config(bot))
    with open(EXTENSIONS_FILE, "r") as file:
        extensions = json.load(file)

    for ext in extensions:
        if extensions[ext] == True:
            bot.load_extension(str(EXT_FOLDER + "." + ext))


# if no extension is enabled
except FileNotFoundError as e:
    main_logger.warning(
        "No extension enabled, none loaded. You probably want to configure the bot or add some extensions"
    )
    raise e

# unexpected error handling
except Exception as e:
    main_logger.exception(e)
    raise e

# running the bot, no matter what
finally:
    if TOKEN != None and assert_struct(bot.guilds):
        print("Running bot")
        bot.run(TOKEN)
    elif TOKEN == None:
        main_logger.error(
            """Invalid TOKEN. Make sure you set up the "DISCORD_TOKEN" environement variable."""
        )
    else:
        main_logger.error("""Directory structure is invalid.""")
