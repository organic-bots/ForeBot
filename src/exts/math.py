import discord
import json
import logging
import asyncio
from os import path, listdir, remove
from subprocess import run
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

DEFAULT_TEX_FILE = path.join(TEX_FOLDER, "formula.tex")


class Math(commands.Cog):
    """A cog which handles mathematic functions
    WARNING: this only works on UNIX-based systems because it uses the tex bin command"""

    def __init__(self, bot):
        self.config_entry = None
        self.bot = bot
        self.tex_command = run(["whereis", "latex"], capture_output=True).stdout.decode()

    @commands.command()
    async def tex(self, ctx, *formula: str):
        if len(formula) == 0:
            await ctx.send(embed=get_embed_err(ERR_NOT_ENOUGH_ARG))
            return
        full_formula = ""
        for element in formula:
            full_formula += " " + element

        #building the formula file
        with open(DEFAULT_TEX_FILE, "r") as file:
            before = file.read()

        #for some reasons path don't seem to work with latex: path.join(TEX_FOLDER, "temp.tex")
        with open("temp.tex" , "w") as file:
            file.write("\\def\\formula{" + full_formula + "}\n" + before)

        #rendering formula
        run(["latex", "-shell-escape", "-interaction=batchmode", "temp.tex", "1>/dev/null"]) #the last param is to prevent shell from being clogged since there is no -quiet option
        await ctx.message.delete()
        await ctx.send(f"**{ctx.author.name}:**", file=discord.File("temp.png", filename="formula.png"))
        for file in listdir():
            if file.startswith("temp"):
                remove(file)



def setup(bot):
    bot.add_cog(Math(bot))
