import logging
import os
import discord.ext.commands.errors as ce

#########################################
#                                       #
#                                       #
#           Global Variables            #
#                                       #
#                                       #
#########################################


PREFIX = "::"
TOKEN = os.getenv("DISCORD_TOKEN", default=None)
RUNNER_ID = 289426079544901633

# server with all of the bot's devs. Where all bug reports should be made.
DEV_SRV = 564213369834307600

# github website URL
WEBSITE = "https://github.com/s0lst1ce/Botanist"

# invite to dev server URL
DEV_SRV_URL = "https://discord.gg/mpGM5cg"

# update message
DEFAULT_UPDATE_MESSAGE = (
    "The bot has been updated. Look at the development server for more information"
)

# emojis dict. May be possible to change incomprehensible unicode to other strings recognized by discord
EMOJIS = {
    "thumbsup": "\U0001f44d",
    "thumbsdown": "\U0001f44e",
    "shrug": "\U0001f937",
    "wastebasket": "\U0001F5D1",
    "check": "\U00002705",
    "hourglass": "\U000023F3",
    "wave": "\U0001F44B",
    "no_entry_sign": "\U0001F6AB",
    "red_circle": "\U0001F534",
    "large_blue_circle": "\U0001F535",
    "tada": "\U0001F389",
    "hammer": "\U0001F528",
    "x": "\U0000274C",
    "X": "\U00002716",
    "warning": "\U000026a0",
    "ping_pong": "\U0001f3d3",
    "sleeping": "\U0001F634",
    "free": "\U0001f193",
    "soon": "\U0001f51c",
    "zip": "\U0001f910",
    "arrow_backward": "\U000025c0",
    "arrow_forward": "\U000025b6",
    "information_source": "\U00002139",
    "track_previous": "\U000023ee",
    "track_next": "\U000023ed",
}

# NotImplemented
COMING_SOON = f"""Sorry this is not yet implemented. Coming Soon{EMOJIS["soon"]}"""

HELP_TAB = "  "
ALLOWED_LANGS = ["en"]
HELP_TIME = 180  # maximum time to wait for a reaction on a help message


#########################################
#                                       #
#                                       #
#                 Files                 #
#                                       #
#                                       #
#########################################

# Files
EXT_FOLDER = "exts"
EXTENSIONS_FILE = "enabled_exts.json"
SLAPPING_FOLDER = "slapping"
CONFIG_FOLDER = "servers"
TODO_FOLDER = "todo"
TIMES_FOLDER = "countdowns"
LANG_FOLDER = "lang"
TEX_FOLDER = "tex"

# roles
ROLES_LEVEL = ["manager", "admin"]

# default JSON files
DEFAULT_EXTENSIONS_JSON = {
    "slapping": False,
    "essentials": True,
    "development": False,
    "embedding": False,
    "role": False,
    "poll": False,
    "time": False,
    "todo": False,
    "math": False,
}

DEFAULT_SLAPPED_FILE = {"463665420054953995": 0}

DEFAULT_SERVER_FILE = {
    "lang": "en",
    "commode": {"reports_chan": False, "spam": {"mute": 3,},},
    "poll_channels": [],
    "todo_channel": False,
    "roles": {"manager": [], "admin": []},
    "free_roles": [],
    "messages": {"welcome": False, "goodbye": False},
    "advertisement": False,
}

DEFAULT_TODO_FILE = {"groups": {"default": []}, "types": {"default": "000000"}}

#########################################
#                                       #
#                                       #
#               Logging                 #
#                                       #
#                                       #
#########################################

LOG_FILE = "botanist.log"
LOGGING_HANDLER = logging.FileHandler(LOG_FILE, "a")
LOGGING_FORMATTER = logging.Formatter("\n[%(asctime)s][%(name)s]:%(message)s")
LOGGING_LEVEL = logging.INFO
LOGGING_HANDLER.setFormatter(LOGGING_FORMATTER)

#########################################
#                                       #
#                                       #
#                Errors                 #
#                                       #
#                                       #
#########################################


ERR_NO_SUBCOMMAND = (
    "No subcommand",
    "You didn't provide any subcommand. See `::help <command>` for more info on command usage.",
    False,
)
ERR_UNEXCPECTED = (
    "Unexcpected error",
    "An unexcpected error occured. Please report a bug in {} or contact an admin of your server.",
    False,
)
ERR_NOT_ENOUGH_ARG = (
    "Not enough arguments",
    "This command requires additional arguments. See `::help <command>` to get more information on the command's usage",
    False,
)
ERR_UNSUFFICIENT_PRIVILEGE = (
    "Unsufficient privileges",
    "You don't have the permissions to do this...",
    False,
)
ERR_NOT_SETUP = (
    "Server not setup",
    "This server hasn't been configured. If you're the owner of the server you can initialize the bot by doing `::init` in any channel. You won't be able to use the bot before that.",
    False,
)
ERR_CANT_SAVE = (
    "Couldn't save configuration",
    "Couldn't save settings to JSON configuration file.",
    False,
)
ERR_MISFORMED = (
    "Misformed command",
    "The command was malformed. See `::help <command>` to get more information on the command's usage",
    False,
)
ERR_TOO_MANY_ARGS = (
    "Too many arguments",
    "This command requires less arguments. See `::help <command>` to get more information on the command's usage.",
    False,
)
ERR_COMMAND_NOT_FOUND = (
    "Command not found",
    "This command doesn't exist. Type `::help` to get a list of commands.",
    False,
)
ERR_UNSUFFICIENT_PERMS = (
    "Missing bot privileges",
    "I do not have the required privileges to do this. This is probably due to a bad setup. Please report it to the server owner.",
    True,
)
ERR_CONVERSION = (
    "Conversion error", """One of your arguments couldn't be converted into. This is either a `member`, `role` or `channel`. Do note that the arguments are **case-sensitive** and that they must be surrounded by quotes (`"`) if they contain spaces. If you can't get it to work, try mentionning the role/member/channel. If even this fails then whatever you tried to mention isn't part of this server anymore and there's nothing we can do about it!""",
    False,
)

ERR_MAX_CONCURRENCY = ("Concurrency Error.", "You can only use this command one at a time. Wait for the previous one to expire before you call another one.", True)


ERRS_MAPPING = {
    ce.MissingRequiredArgument: ERR_NOT_ENOUGH_ARG,
    ce.ArgumentParsingError: ERR_MISFORMED,
    ce.TooManyArguments: ERR_TOO_MANY_ARGS,
    ce.CommandNotFound: ERR_COMMAND_NOT_FOUND,
    ce.BotMissingPermissions: ERR_UNSUFFICIENT_PERMS,
    ce.BadArgument: ERR_MISFORMED,
    ce.CheckFailure: ERR_UNSUFFICIENT_PRIVILEGE,
    ce.ConversionError: ERR_CONVERSION,
    ce.MaxConcurrencyReached: ERR_MAX_CONCURRENCY
}
