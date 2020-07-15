import logging
import discord
import asyncio
import os
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
#           Making commands             #
#                                       #
#                                       #
#########################################


class MendatoryConfigEntries(ConfigEntry):
    """docstring for ClearanceConfigEntry"""

    def __init__(self, bot, cfg_chan_id):
        super().__init__(bot, cfg_chan_id)

    def is_valid(self, lang):
        if lang in ALLOWED_LANGS:
            return True
        else:
            return False

    async def run(self, ctx):
        try:
            # LANGUAGE CONFIG
            good = False
            while not good:
                lang = await self.get_answer(
                    ctx,
                    f"I'm an international robot and tend to operate in many places. This also means that I speak many language! The list of supported languages can be found on my website {WEBSITE}. So which do you want to speak with? Languages are expressed in their 2 letter code.",
                )
                if not self.is_valid(lang.content):
                    continue
                good = True
            await ctx.send(
                f"You have selected {lang.content}. Glad you could find a language that suits you! If you think the translation is incomplete or could be improved, feel free to improve it. The translations are open to everyone on our {WEBSITE}."
            )

            with ConfigFile(ctx.guild.id) as conf:
                conf["lang"] = lang.content

            # ROLE CONFIG
            await self.config_channel.send(
                "Role setup is **mandatory** for the bot to work correctly. Otherwise no one will be able to use administration commands."
            )
            await self.config_channel.send(
                "**\nStarting role configuration**\nThis bot uses two hierachical level of clearance plus an independant one for its commands.\nThe first level of clearance is **admin**. Anyone who has a role with this level of clearance can use all commands but the ones related to the bot configuration. This is reserved to the server owner. All roles with this level of clearance inherit **manager** clearance as well.\nThe second one is the **manager** level of clearance. Everyone with a role with this clearance can use commands related to server management. This includes but is not limited to message management and issuing warnings.\nThe last is **planner** and allows its bearers to post events in the server."
            )

            new_roles = []
            for role_lvl in ROLES_LEVEL:
                retry = True
                while retry:
                    new_role = []
                    # asking the owner which roles he wants to give clearance to
                    pre_roles = await self.get_answer(
                        ctx,
                        f"List all the roles you want to be given the **{role_lvl}** level of clearance.",
                    )

                    # converting to Role obj
                    roles = []
                    for role in pre_roles.content.split(" "):
                        try:
                            roles.append(
                                await discord.ext.commands.RoleConverter().convert(
                                    ctx, role
                                )
                            )
                        except:
                            continue

                    # making sure at least a role was selected
                    if len(roles) == 0:
                        await self.config_channel.send(
                            f"You need to set at least one role for the {role_lvl} clearance."
                        )
                        continue

                    # building role string
                    roles_str = ""
                    for role in roles:
                        roles_str += f" {role.name}"

                    # asking for confirmation
                    confirmed = await self.get_yn(
                        ctx,
                        f"You are about to give{roles_str} roles the **{role_lvl}** level of clearance. Do you confirm this ?",
                    )
                    if not confirmed:
                        again = await self.get_yn(
                            ctx,
                            f"Aborting configuration of {role_lvl}. Do you want to retry?",
                        )
                        if not again:
                            local_logger.info(
                                f"The configuration for the {role_lvl} clearance has been cancelled for server {ctx.guild.name}"
                            )
                            retry = False

                    else:
                        retry = False

                local_logger.info(
                    f"Server {ctx.guild.name} configured its {role_lvl} roles"
                )
                for role in roles:
                    new_role.append(role.id)

                # adding to master role list
                new_roles.append(new_role)

            # giving admin roles the manager clearance
            for m_role in new_roles[1]:
                new_roles[0].append(m_role)

            with ConfigFile(ctx.guild.id) as conf:
                conf["roles"]["manager"] = new_roles[0]
                conf["roles"]["admin"] = new_roles[1]
                conf["roles"]["planner"] = new_roles[2]

            await self.config_channel.send("Successfully updated role configuration")

        except Exception as e:
            raise e


class Config(commands.Cog, ConfigEntry):
    """a suite of commands meant ot give server admins/owners and easy way to setup the bot's
    preferences directly from discord."""

    def __init__(self, bot):
        self.config_entry = MendatoryConfigEntries
        self.config_channels = {}
        self.bot = bot
        self.allowed_answers = {1: ["yes", "y"], 0: ["no", "n"]}

    @commands.Cog.listener()
    async def on_guild_join(guild):
        await self.make_cfg_chan(guild)

    async def make_cfg_chan(self, ctx_or_guild):
        if type(ctx_or_guild) == discord.Guild:
            g = ctx_or_guild
        else:
            g = ctx_or_guild.guild
        overwrite = {
            g.default_role: discord.PermissionOverwrite(read_messages=False),
            g.owner: discord.PermissionOverwrite(read_messages=True),
        }
        self.config_channels[g.id] = await g.create_text_channel(
            "cli-bot-config", overwrites=overwrite
        )
        if f"{g.id}.json" not in os.listdir(CONFIG_FOLDER):
            # making sure there's a file to write on but don't overwrite if there's already one.
            with open(os.path.join(CONFIG_FOLDER, str(g.id) + ".json"), "w") as file:
                json.dump(DEFAULT_SERVER_FILE, file)

            with open(os.path.join(SLAPPING_FOLDER, str(g.id) + ".json"), "w") as file:
                json.dump(DEFAULT_SLAPPED_FILE, file)

        return self.config_channels[g.id]

    @commands.command()
    @has_auth("admin")
    async def cfg(self, ctx, cog_name: str):
        cog = self.bot.get_cog(cog_name.title())
        if not cog:
            local_logger.debug(
                f"{ctx.author} tried to configure {cog_name} which doesn't exist."
            )
            raise discord.ext.commands.errors.ArgumentParsingError(
                message=f"{cog_name} cog doesn't exist."
            )
            return

        if cog.config_entry:
            try:
                self.config_channel = await self.make_cfg_chan(ctx)
                ctx.channel = self.config_channel
                await cog.config_entry(self.bot, self.config_channel).run(ctx)

            finally:
                await self.config_channels[ctx.guild.id].send(
                    f"You Successfully configured {cog.qualified_name}.\nThis channel will be deleted in 10 seconds..."
                )
                await asyncio.sleep(10)
                await self.config_channels[ctx.guild.id].delete(
                    reason="Configuration completed"
                )

        else:
            await ctx.send("{cog.qualified_name} doesn't have any configuration entry!")

    @commands.command()
    @is_server_owner()
    async def init(self, ctx):
        # creating new hidden channel only the owner/admins can see
        self.config_channel = await self.make_cfg_chan(ctx)
        ctx.channel = self.config_channel

        try:
            # starting all configurations
            await self.config_channels[ctx.guild.id].send(
                f"""You are about to start the configuration of {ctx.me.mention}. If you are unfamiliar with CLI (Command Line Interface) you may want to check the documentation on github ({WEBSITE}). The same goes if you don't know the bot's functionnalities"""
            )

            await self.config_channels[ctx.guild.id].send(
                "**Starting full bot configuration...**"
            )

            for cog in self.bot.cogs:
                if self.bot.cogs[cog].config_entry:
                    await self.bot.cogs[cog].config_entry(
                        self.bot, self.config_channel
                    ).run(ctx)

            # asking for permisison to advertise
            await self.config_channels[ctx.guild.id].send(
                "You're almost done ! Just one more thing..."
            )
            allowed = await self.get_yn(
                ctx,
                "Do you allow me to send a message in a channel of your choice? This message would give out a link to my development server. It would allow me to get more feedback. This would really help me pursue the development of the bot. If you like it please think about it.",
            )
            ad_msg = discord.Embed(
                description="I ({}) have recently been added to this server! I hope I'll be useful to you. Hopefully you won't find me too many bugs. However if you do I would appreciate it if you could report them to the [server]({}) where my developers are ~~partying~~ working hard to make me better. This is also the place to share your thoughts on how to improve me. Have a nice day and hopefully, see you there {}".format(
                    ctx.me.mention, DEV_SRV_URL, EMOJIS["wave"]
                )
            )
            if not allowed:
                return False

            chan = await self.get_answer(
                ctx,
                "Thank you very much ! In which channel do you want me to post this message?",
                filters=["channels"],
            )

            with ConfigFile(ctx.guild.id) as conf:
                conf["advertisement"] = chan[0].id

            await chan[0].send(embed=ad_msg)

            local_logger.info(
                f"Setup for server {ctx.guild.name}({ctx.guild.id}) is done"
            )

        except Exception as e:
            raise e
            await ctx.send(embed=get_embed_err(ERR_UNEXCPECTED.format(str(e))))
            await ctx.send(
                "Dropping configuration and rolling back unconfirmed changes."
            )
            local_logger.exception(e)

        finally:
            await self.config_channels[ctx.guild.id].send(
                "Thank you for inviting our bot and taking the patience to configure it.\nThis channel will be deleted in 10 seconds..."
            )
            await asyncio.sleep(10)
            await self.config_channels[ctx.guild.id].delete(
                reason="Configuration completed"
            )

    @commands.command()
    @has_auth("admin")
    async def summary(self, ctx):
        config = ConfigFile(ctx.guild.id).read()

        config_sum = discord.Embed(
            title="Server settings",
            description=f"""This server uses `{config["lang"]}` language and have set advertisement policy to **{config["advertisement"]}**.""",
            color=7506394,
        )

        # messages
        messages = ""
        for msg_type in config["messages"]:
            if config["messages"][msg_type]:
                messages += (
                    f"""**{msg_type.title()}:**\n{config["messages"][msg_type]}\n"""
                )

        if len(messages) == 0:
            messages = (
                "No **welcome** or **goodbye** messages were set for this server."
            )
        config_sum.add_field(name="Messages", value=messages, inline=False)

        # community moderation
        if config["commode"]["reports_chan"]:
            try:
                value = await discord.ext.commands.TextChannelConverter().convert(
                    ctx, str(config["commode"]["reports_chan"])
                )
                value = "The channel for reports is:" + value.mention + "\n"
            except Exception as e:
                local_logger.exception(
                    f"The report channel for guild {ctx.guild.id} was deleted.", e
                )
                # the channel was deleted
                value = "The set report channel was deleted. You are advised to set a new one using `::cfg slapping`.\n"
        else:
            value = "No report channel has been set. You are advised to set one using `::cfg slapping`.\n"

        value += f"""A user is automatically muted in a channel for 10 minutes after **{config["commode"]["spam"]["mute"]}** `spam` reports."""
        config_sum.add_field(name="Community moderation", value=value, inline=True)

        # polls
        if len(config["poll_channels"]) > 0:
            chans = "The **poll channels** are:"
            for chan in config["poll_channels"]:
                try:
                    crt_chan = await discord.ext.commands.TextChannelConverter().convert(
                        ctx, str(chan)
                    )
                except Exception as e:
                    # the channel was deleted
                    local_logger.exception(
                        f"A poll channel of guild {ctx.guild.id} was deleted."
                    )
                    continue

                chans += crt_chan.mention
        else:
            chans = "There are no **poll channels** for this server."
        config_sum.add_field(name="Poll Channels", value=chans, inline=True)

        # clearance/roles
        clearance = ""
        for level in config["roles"]:
            clearance += f"**{level.title()}:**\n"
            for role_id in config["roles"][level]:
                try:
                    crt_role = await discord.ext.commands.RoleConverter().convert(
                        ctx, str(role_id)
                    )
                except Exception as e:
                    # the role doesn't exist anymore
                    local_logger.exception(
                        f"The role associated with {level} clearance doesn't exist anymiore",
                        e,
                    )
                    continue
                clearance += " " + crt_role.mention
            clearance += "\n"

        if config["free_roles"]:
            clearance += "**Free roles:**\n"
            for role_id in config["free_roles"]:
                try:
                    crt_role = await discord.ext.commands.RoleConverter().convert(
                        ctx, str(role_id)
                    )
                except Exception as e:
                    # the role doesn't exist anymore
                    local_logger.exception(f"The free role doesn't exist anymiore", e)
                    continue
                clearance += " " + crt_role.mention

        else:
            clearance += "There are no **free roles** in this server."

        config_sum.add_field(name="Clearance", value=clearance, inline=True)

        await ctx.send(embed=config_sum)


def setup(bot):
    bot.add_cog(Config(bot))
