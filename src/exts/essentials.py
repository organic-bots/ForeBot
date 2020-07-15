"""Essential features all bot built with this template should have.
Do note that disabling it will cause issues to the config extension."""
import datetime
from os import listdir
import logging
import discord
from settings import *
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
#               BotEssentials           #
#                                       #
#                                       #
#########################################
"""This cog contains all the basemost functions that all bots should contain.
See https://github.com/s0lst1ce/Botanist for more information"""

name = __name__.split(".")[-1]


class EssentialsConfigEntry(ConfigEntry):
    """docstring for EssentialsConfigEntry"""

    def __init__(self, bot, cfg_chan_id):
        super().__init__(bot, cfg_chan_id)

    async def run(self, ctx):
        # welcome & goodbye messages
        tr = Translator(name, get_lang(ctx.guild.id))
        msgs = {
            "welcome": [tr["welcome1"], tr["welcome2"]],
            "goodbye": [tr["goodbye1"], tr["goodbye2"]],
        }
        try:
            for wg in msgs:
                await self.config_channel.send(tr["start_conf"].format(wg))
                retry = await self.get_yn(ctx, msgs[wg][0])
                message = False

                while retry:

                    message = await self.get_answer(ctx, msgs[wg][1])

                    await self.config_channel.send(tr["send_check"])
                    await self.config_channel.send(
                        message.content.format(ctx.guild.owner.mention)
                    )
                    response = await self.get_yn(ctx, tr["response"].format(wg))
                    # the user has made a mistake
                    if response == False:
                        response = await self.get_yn(ctx, tr["retry"])
                        if response == False:
                            message = False
                            retry = False
                        # otherwise retry
                        continue

                    else:
                        retry = False

                if message == False:
                    return
                with ConfigFile(ctx.guild.id) as conf:
                    conf["messages"][wg] = message.content

        except Exception as e:
            local_logger.exception(e)
            raise e


class Essentials(commands.Cog):
    """All of the essential methods all of our bots should have"""

    def __init__(self, bot):
        self.bot = bot
        self.config_entry = EssentialsConfigEntry

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """handles command errors"""
        raise error
        local_logger.error(error)
        if type(error) in ERRS_MAPPING.keys():
            msg = get_embed_err(ERRS_MAPPING[type(error)])
            if ERRS_MAPPING[error][2] is False:
                await ctx.send(embed=msg)
            else:
                await ctx.author.send(embed=msg)
                await ctx.message.delete()
        else:
            await ctx.send(embed=get_embed_err(ERR_UNEXCPECTED))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        ConfigFile(guild.id, default=DEFAULT_SERVER_FILE)
        await guild.owner.send(
            f"I was just added to your server. For me to work correctly (or at all) on your server you should send `::init` in any channel of your {guild.name} server."
        )
        local_logger.info(f"Joined server {guild.name}")

    @commands.Cog.listener()
    async def on_guild_leave(self, guild):
        remove(os.path.join(CONFIG_FOLDER, str(guild.id) + ".json"))

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logged in as {0.user}".format(self.bot))
        local_logger.info("Logged in as {0.user}".format(self.bot))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        local_logger.info(
            "User {0.name}[{0.id}] joined {1.name}[{1.id}]".format(member, member.guild)
        )
        with ConfigFile(member.guild.id) as conf:
            welcome_msg = conf["messages"]["welcome"]
        if welcome_msg != False:
            await member.guild.system_channel.send(welcome_msg.format(member.mention))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        local_logger.info(
            "User {0.name}[{0.id}] left {1.name}[{1.id}]".format(member, member.guild)
        )
        with ConfigFile(member.guild.id) as conf:
            goodbye_msg = conf["messages"]["goodbye"]
        if goodbye_msg != False:
            await member.guild.system_channel.send(goodbye_msg.format(member.mention))

    @commands.command()
    async def ping(self, ctx):
        """This command responds with the current latency."""
        tr = Translator(name, get_lang(ctx.guild.id))
        latency = self.bot.latency
        await ctx.send(EMOJIS["ping_pong"] + tr["latency"].format(latency))

    # Command that shuts down the bot
    @commands.command(aliases=["poweroff"])
    @is_runner()
    async def shutdown(self, ctx):
        print("Goodbye")
        local_logger.info("Switching to invisible mode")
        await self.bot.change_presence(status=discord.Status.offline)
        await ctx.send(f"""Going to sleep {EMOJIS["sleeping"]}""")
        local_logger.info("Closing connection to discord")
        await self.bot.close()
        local_logger.info("Quitting python")
        await quit()

    @commands.command()
    @has_auth("manager")
    async def clear(self, ctx, *filters):
        """deletes specified <nbr> number of messages in the current channel."""
        # building arguments
        filters = list(filters)
        nbr = None
        period = None
        members = []
        try:
            nbr = int(filters[0])
            filters.pop(0)
        except:
            pass

        if filters:
            period = to_datetime(filters[0])
            if period:
                filters.pop(0)

            for m in filters:
                try:
                    members.append(
                        await discord.ext.commands.MemberConverter().convert(ctx, m)
                    )
                except:
                    raise discord.ext.commands.ArgumentParsingError(
                        f"Unrecognized filter {m}"
                    )

        hist_args = {}
        if period:
            hist_args["after"] = period
        if nbr and not members:
            nbr += 1
            hist_args["limit"] = nbr
        if members:
            await ctx.message.delete()

        if not (period or nbr):
            raise discord.ext.commands.ArgumentParsingError(
                "Can't delete all messages of a user!"
            )

        to_del = []
        now = datetime.datetime.now()
        async for msg in ctx.channel.history(**hist_args):
            if not members or msg.author in members:
                local_logger.debug(
                    f"Deleting message {msg.jump_url} from guild {msg.guild.name}."
                )
                if (msg.created_at - now).days <= -14:
                    await msg.delete()
                else:
                    to_del.append(msg)

                if nbr != None:
                    nbr -= 1
                    if nbr <= 0:
                        break

        try:
            await ctx.channel.delete_messages(to_del)

        except discord.HTTPException as e:
            raise e

        except Exception as e:
            local_logger.exception("Couldn't delete at least on of{}".format(to_del))
            raise e

    @commands.command()
    async def status(self, ctx):
        """returns some statistics about the server and their members"""
        tr = Translator(name, get_lang(ctx.guild.id))
        stats = discord.Embed(
            name=tr["stats_name"],
            description=tr["stats_description"].format(
                ctx.guild.name,
                str(ctx.guild.created_at)[:10],
                ctx.guild.owner.mention,
                ctx.guild.member_count - 1,
            ),
            color=7506394,
        )
        stats.set_thumbnail(url=ctx.guild.icon_url)

        # member stats
        mstatus = {"online": 0, "idle": 0, "dnd": 0, "offline": 0}
        for member in ctx.guild.members:
            mstatus[str(member.status)] += 1
        # -> change to make use of custom emojis
        status_str = tr["status_str"].format(**mstatus)
        stats.add_field(name=tr["mstats_name"], value=status_str, inline=False)

        # structure info
        rs = ctx.guild.roles
        rs.reverse()
        rs_str = ""
        for r in rs:
            rs_str += f"{r.mention}"
        stats.add_field(name=tr["sstats_name"], value=rs_str, inline=False)
        await ctx.send(embed=stats)


def setup(bot):
    bot.add_cog(Essentials(bot))
