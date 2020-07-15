from collections import OrderedDict
import logging
import os
import json
from time import time
import datetime
import discord
from settings import *
from discord.ext import commands
from collections import UserDict

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
local_logger.info(f"Innitalized {__name__} logger")


#########################################
#                                       #
#                                       #
#               Checks                  #
#                                       #
#                                       #
#########################################


def is_runner():  # to be deleted sine it does the same as is_owner()
    def check_condition(ctx):
        return ctx.message.author.id == RUNNER_ID

    result = commands.check(check_condition)
    if result == False:
        pass
        # ctx.send(ERR_UNSUFFICIENT_PRIVILEGE)
    return result


def is_init():
    """checks whether the server has been initialized. Meant as a fail-safe for commands requiring configuration."""

    def check_condition(ctx):
        conf_files = os.listdir(CONFIG_FOLDER)
        file_name = f"{ctx.guild.id}.json"
        # ctx.send(ERR_NOT_SETUP)
        return file_name in conf_files

    return commands.check(check_condition)


def was_init(ctx):
    """same as the previous function except this one isn't a decorator. Mainly used for listenners"""
    if ctx.guild:
        return f"{ctx.guild.id}.json" in os.listdir(CONFIG_FOLDER)
    else:
        # so that we make sure the check doesn't fail in a DM
        return True


def has_auth(clearance, *args):
    """checks whether the user invoking the command has the specified clearance level of clearance for the server the command is being ran on"""

    def predicate(ctx):
        with ConfigFile(ctx.guild.id, folder=CONFIG_FOLDER) as c:
            allowed_roles = c["roles"][clearance]
            for role in ctx.author.roles:
                if role.id in allowed_roles:
                    return True
            # await ctx.send(embed=get_embed_err(ERR_UNSUFFICIENT_PRIVILEGE)) -> not async
            local_logger.warning(ERR_UNSUFFICIENT_PRIVILEGE[1])
            return False

    return commands.check(predicate)


def is_server_owner():
    """check meant to verify whether its author os the owner of the server where the command is being ran"""

    def predicate(ctx):
        if ctx.author == ctx.guild.owner:
            return True
        # ctx.send(ERR_UNSUFFICIENT_PRIVILEGE)
        return False

    return commands.check(predicate)


#########################################
#                                       #
#                                       #
#           Utilities                   #
#                                       #
#                                       #
#########################################


def get_embed_err(error):
    err_embed = discord.Embed(
        title=f"""{EMOJIS["warning"]} **Command Error:** """ + error[0],
        description=error[1],
        color=16729127,
    )
    return err_embed


def assert_struct(guilds):
    try:
        # making sure all folder are built
        files = os.listdir()
        to_make = [
            SLAPPING_FOLDER,
            TODO_FOLDER,
            CONFIG_FOLDER,
            LANG_FOLDER,
            EVENT_FOLDER,
            TIME_FOLDER,
            EVENT_FOLDER,
            REMINDERS_FOLDER,
            POLL_FOLDER,
        ]
        for folder in to_make:
            if folder not in files:
                os.mkdir(folder)

        # making sure all config files are here, with their at least their default content
        for folder in [CONFIG_FOLDER, SLAPPING_FOLDER]:
            g_folder = os.listdir(folder)
            for g in guilds:
                if (str(g.id) + ".json" not in g_folder) or (
                    os.path.getsize(folder + str(g.id) + ".json") == 0
                ):
                    local_logger.warning(f"Missing config file for {g}!")
                    with open(
                        os.path.join(CONFIG_FOLDER, str(g.id) + ".json"), "w"
                    ) as file:
                        json.dump(DEFAULT_SERVER_FILE)

        # TODO: making sure the lang folder is complete

        # making sure ext file is there and valid
        if EXTENSIONS_FILE not in files or os.path.getsize(EXTENSIONS_FILE) == 0:
            with open(EXTENSIONS_FILE, "w") as file:
                json.dump(
                    DEFAULT_EXTENSIONS_JSON, file
                )  # write data to the newly created file

        return True

    except Exception as e:
        local_logger.exception(e)
        raise e
        return False


time_seps = ["d", "h", "m", "s"]
DIGITS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")


def to_datetime(argument, sub=True, lenient=False):
    """the date format is as such:
    d => days
    h => hours
    m => minutes
    s => seconds
    """

    times = OrderedDict([("y", 0), ("M", 0), ("d", 0), ("h", 0), ("m", 0), ("s", 0)])

    last = 0
    for char, i in zip(argument, range(len(argument))):
        if char not in DIGITS:
            if char in time_seps:
                if lenient:
                    if len(argument[last:i]) == 0:
                        return False
                times[char] = int(argument[last:i])
                last = i + 1
            else:
                return False
        else:
            continue

    diff = datetime.timedelta(
        days=times["d"], hours=times["h"], minutes=times["m"], seconds=times["s"]
    )
    if sub:
        return datetime.datetime.now() - diff
    else:
        return diff


class Singleton(type):
    """a metaclass that makes your class a a singleton"""

    _instances = {}  # dict so that different classes can inherit from the metaclass

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigFile(UserDict):
    """A class representing a json config file. Used to handle configuration information.
            
            file:   the file name without the extension. This is usually the ID of the guild it represents
            folder: the folder to read the file from. This represents the kind of data handled
            fext:   the file extension. Only supports "json" for now
            force:  creates the file if not found
            default:default dict to write in-place
            """
    folder_mapping = {
    CONFIG_FOLDER: DEFAULT_SERVER_FILE,
    TIME_FOLDER: DEFAULT_MUTE_FILE,
    SLAPPING_FOLDER: DEFAULT_SLAPPED_FILE,
    REMINDERS_FOLDER: {},
    EVENT_FOLDER: {"partial": {}, "sent": {}},
    }

    def __init__(
        self, file, folder=CONFIG_FOLDER, fext="json", force=True, default=None
    ):
        super(ConfigFile, self).__init__()
        # since the ID is an int -> making sure it is considered as a string
        self.file = str(file)

        self.folder = folder
        self.fext = fext
        self.force = force

        if not default:
            assert folder in ConfigFile.folder_mapping, local_logger.critical("Couldn't find a default for folder "+ folder)
            self.default = self.data = ConfigFile.folder_mapping[folder]

        # currently only supports "json" files
        self.file += "." + self.fext
        # making path
        self.path = os.path.join(self.folder, self.file)
        # self.last_m_time = os.path.getmtime(self.path)

    def __enter__(self):
        if not self.make_file():
            return self.default
        self.read()
        return self

    def __exit__(self, *args):
        self.save()

    def make_file(self):
        files = os.listdir(self.folder)
        # print(self.file not in files)
        if self.file not in files:
            if not self.force:
                return False
            with open(
                os.path.join(self.folder, self.file), "w", encoding="utf-8"
            ) as file:
                json.dump(self.default, file)  # creating empty file
        else:
            with open(os.path.join(self.folder, self.file), "r") as file:
                try:
                    json.load(file)
                except Exception as e:
                    if self.force:
                        json.dump(self.default, file)
                    else:
                        return False
        return True

    def is_json(self, file):
        try:
            out = json.loads(file)
        except:
            return False
        return True

    def save(self):
        """makes the file from the dict
        can we really do anything if it fails to write? Save the original contents are write them again?"""
        if not self.is_json(self.data):
            raise ValueError(f"Incorrect JSON for updated {self.file}")
            local_logger.critical(f"Discarding changes to {self.file} because they invalidated the JSON file.")

        try:
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(self.data, file)

        except Exception as e:
            local_logger.error(f"An exception occured while saving {self.file}.")
            local_logger.exception(e)
            raise e

    def read(self):
        """builds the dict from the file """
        try:
            with open(os.path.join(self.folder, self.file), "r") as file:
                self.data = json.load(file)

            return self.data

        except Exception as e:
            local_logger.error(f"An exception occured while reading {self.file}.")
            local_logger.exception(e)
            raise e
            return self.default



class Translator(object):
    """docstring for Translator
    lang can either be a 2-chars long string or a Context object"""

    def __init__(self, ext, lang, help_type=False):
        self.ext = ext
        self.lang = self.get_lang(lang)

        if help_type:
            name = "help"
        else:
            name = "strings"

        self.file = os.path.join("lang", ext, name + "." + self.lang)
        self._dict = self.load_strings()

    def __repr__(self):
        return f"<Translator> {self._dict}"

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, item):
        if type(item) == str:
            self._dict[key] = item
        else:
            raise TypeError("Translations must be strings!")

    @classmethod
    def guess_lang(cls, ctx, ext, **kwargs):
        with ConfigFile(ctx.guild.id) as conf:
            return cls(ext, conf["lang"], **kwargs)

    def load_strings(self):
        try:
            with open(self.file, "r", encoding="utf-8") as translation:
                return json.load(translation)
        except json.decoder.JSONDecodeError as e:
            local_logger.error(f"Couldn't read translation for file {self.file}")
            raise e

    def get_lang(self, lang):
        if isinstance(lang, str):
            return lang

        elif isinstance(lang, discord.ext.commands.Context):
            with ConfigFile(lang.guild.id, force=False) as conf:
                return conf["lang"]

        else:
            raise TypeError(
                "lang must be <str> or <discord.ext.commands.Context> not {}".format(
                    type(lang)
                )
            )


def get_lang(guild_id):
    with ConfigFile(guild_id) as conf:
        return conf["lang"]


class ConfigEntry(object):
    """A generic configuration class that must subclasses to be used correctly in each extension."""

    def __init__(self, bot, config_channel):
        self.bot = bot
        # only a single config channel because the class can have several instances, each for a different server
        self.config_channel = config_channel
        self.allowed_answers = {1: ["yes", "y"], 0: ["no", "n"]}

        if isinstance(config_channel, discord.TextChannel):
            self.owner = config_channel.guild.owner
        else:
            # in a DM
            self.owner = config_channel.recipient

    def is_answer(self, message):
        if message.channel == self.config_channel and message.author == self.owner:
            return True
        return False

    def list_allowed_answers(self) -> list:
        correct_answers = []
        for ans in self.allowed_answers.values():
            correct_answers += ans
        return correct_answers

    def is_react_yn_answer(self, reaction, user):
        if reaction.message.channel == self.config_channel and user == self.owner:
            if reaction.emoji in [
                EMOJIS["negative_squared_cross_mark"],
                EMOJIS["white_check_mark"],
            ]:
                return True
        return False

    async def get_yn(self, ctx, question):
        msg = await ctx.send(question)
        await msg.add_reaction(EMOJIS["white_check_mark"])
        await msg.add_reaction(EMOJIS["negative_squared_cross_mark"])
        reaction, user = await self.bot.wait_for(
            "reaction_add", check=self.is_react_yn_answer
        )

        if reaction.emoji == EMOJIS["white_check_mark"]:
            return True
        else:
            return False

    async def get_answer(self, ctx, question, filters=[]):
        await ctx.send(question)
        answered = False
        while not answered:
            response = await self.bot.wait_for("message", check=self.is_answer)

            if filters:
                cat = self.filter_msg(response)
                complete = True
                for filt in filters:
                    if not cat[filt]:
                        cat.pop(filt)
                        complete = False  # -> remove bc sometimes you need to accept no mention?

                if complete:
                    if len(filters) == 1:
                        return cat[filters[0]]
                    else:
                        return cat

            else:
                return response

            await ctx.send(question)

    async def get_datetime(
        self, ctx, question, later: int = False, seconds: bool = False
    ):
        """"this returns a datetime object from a user message.
        question: the question to ask the user
        later: if true will refuse any datetime that is already in the past. Can either be an int for a treshold or bool for simple comparison.
        seconds: if true returns a int representing seconds instead of a datetime"""

        await ctx.send(question)
        true_time = False
        while not true_time:
            response = await self.bot.wait_for("message", check=self.is_answer)
            true_time = to_datetime(response.content, sub=False, lenient=True)

            if not true_time:
                await ctx.send("The time you entered is incorrect, please try again.")
                continue
            else:
                if later:
                    if type(later) == int:
                        if true_time.total_seconds() <= later:
                            continue
                    else:
                        if true_time.total_seconds() <= 0:
                            continue

                if seconds:
                    return true_time.total_seconds()
                return true_time

    async def get_color(self, ctx, question: str):
        await ctx.send(question)
        color = None
        while not color:
            response = await self.bot.wait_for("message", check=self.is_answer)
            if response.content.startswith("#"):
                base = 16
            else:
                base = 10

            try:
                color = discord.Color(int(response.content, base=base))
                return color
            except Exception as e:
                continue

    def filter_msg(self, msg):
        # assert filters != None, TypeError("You must set filters to filter a message.")

        results = {
            "roles": msg.role_mentions,
            "mentions": msg.mentions,
            "channels": msg.channel_mentions,
        }

        return results

    async def run(self, ctx):
        """this functions serves as placeholder for the instances which should override it"""
        pass


async def audit(guild, *args, **kwargs):
    """audits the provided message to the moderation channel of the guild if set"""
    try:
        with ConfigFile(guild.id) as config:
            audit_chan = config["commode"]["reports_chan"]
            if audit_chan:
                audit_chan = guild.get_channel(audit_chan)
                await audit_chan.send(*args, **kwargs)

    except Exception as e:
        local_logger.error(
            f"Couldn't record audit log in the moderation channel of {guild}."
        )
        local_logger.exception(e)
        raise e
