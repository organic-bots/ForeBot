import logging
from settings import *
import discord
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

name = __name__.split(".")[-1]


class RoleConfigEntry(ConfigEntry):
    """user can choose which roles are "free" """

    def __init__(self, bot, config_chan_id):
        super().__init__(bot, config_chan_id)

    async def run(self, ctx):
        tr = Translator(name, get_lang(ctx.guild.id))
        try:
            await ctx.send(tr["start_conf"])
            free_roles = []
            pursue = await self.get_yn(ctx, tr["pursue"])
            while pursue:
                proles = await self.get_answer(ctx, tr["proles"])
                roles = []
                for role in proles.content.split(" "):
                    try:
                        roles.append(
                            await discord.ext.commands.RoleConverter().convert(
                                ctx, role
                            )
                        )
                    except:
                        pass
                        # raise discord.ext.commands.ArgumentParsingError(f"Couldn't find role {role}")

                roles_str = ""
                for role in roles:
                    roles_str += f" {role.name}"
                agrees = await self.get_yn(ctx, tr["agrees"].format(roles_str))

                if not agrees:
                    retry = await self.get_yn(ctx, tr["retry"])
                    if retry:
                        continue
                    else:
                        pursue = False

                else:
                    pursue = False
                    with ConfigFile(ctx.guild.id) as conf:
                        conf["free_roles"] = [role.id for role in roles]
        except:
            raise


class Role(commands.Cog):
    """role management utility. Requires a Gestion role"""

    def __init__(self, bot):
        self.bot = bot
        self.config_entry = RoleConfigEntry

    @commands.group()
    async def role(self, ctx):
        """role management utility. Requires a Gestion role"""
        pass

    @role.command()
    async def add(self, ctx, member: discord.Member, *roles: discord.Role):
        """Gives <member> listed <roles> roles"""
        tr = Translator(name, get_lang(ctx.guild.id))
        # checking if member can self-assing role(s)
        if not has_auth("admin")(ctx):
            allowed_roles = []
            with ConfigFile(ctx.guild.id) as conf:
                for role in roles:
                    if str(role.id) in conf["free_roles"]:
                        allowed_roles.append(role)
                    else:
                        await ctx.send(tr["not_free_role"].format(role.name))

        else:
            allowed_roles = roles

        if len(allowed_roles) == 0:
            local_logger.warning("User didn't provide a role")
            raise discord.ext.commands.MissingRequiredArgument(
                "You must provide at least one role."
            )

        else:
            try:
                await member.add_roles(*allowed_roles)
                roles_str = ""
                for role in allowed_roles:
                    roles_str += f" {role}"

                await ctx.send(tr["gave"].format(member.name, roles_str))
            except Exception as e:
                local_logger.exception(
                    "Couldn't add {} to {}".format(allowed_roles, member)
                )
                raise e

    @role.command()
    async def rm(self, ctx, member: discord.Member, *roles: discord.Role):
        """Removes <member>'s <roles> roles"""
        if len(roles) == 0:
            local_logger.warning("User didn't provide a role")
            raise discord.ext.commands.MissingRequiredArgument(
                "You must provide at least one role."
            )

        else:
            try:
                await member.remove_roles(*roles)
            except Exception as e:
                local_logger.exception("Couldn't remove roles ")
                raise e

    @role.command()
    async def free(self, ctx):
        """return a list of free role"""
        free_roles = ""
        with ConfigFile(ctx.guild.id) as conf:
            for role in conf["free_roles"]:
                try:
                    resolved = ctx.guild.get_role(role)
                    free_roles += f"{resolved.mention}\n"

                except discord.ext.commands.ConversionError as e:
                    raise e
                    local_logger.error(
                        "A free role couldn't be found, maybe it was deleted?"
                    )
                    local_logger.exception(e)

            # if no role was added -> report it to the user
            if not free_roles:
                await ctx.send("There is no free role on this server.")
                return

        listing = discord.Embed(
            title="Free roles",
            description="The list of free roles of this server. Free roles are roles anyone can get, by themselves. They can be obtained using `role add <member> [roles...]`.",
            color=7506394,
        )
        listing.add_field(name="Listing", value=free_roles)
        await ctx.send(embed=listing)


def setup(bot):
    bot.add_cog(Role(bot))
