import discord
import json
import logging
import asyncio
from time import time as sec_time
from time import gmtime, asctime
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


class Event(object):
    """This is a data strcuture representing a discord user event.
    WARN: construction may need to be followed by the resolve coroutine"""

    empty_event = {"partial": {}, "sent": {}}

    def __init__(
        self,
        bot,
        user_id: int,
        name: str,
        start: int,
        reminder: int = 0,
        description: str = None,
        guild: int = None,
        channel: int = None,
        role: int = None,
        color: discord.Color = 7506394,
        subscribers: list = [],
        message=None,
    ):
        self._user = None
        self.bot = bot
        self.user_id = user_id
        self.name = name
        self.start = start
        self.reminder = reminder
        self.description = description
        self.color = color
        self.subscribers = subscribers
        self.message = message
        self.guild = guild
        self.role = role
        self.channel = channel

    async def resolve(self):
        if type(self.guild) == int:
            self.guild = self.bot.get_guild(self.guild)
            if type(self.role) == int:
                self.role = self.guild.get_role(self.role)
            else:
                self.role = self.role

            if type(self.channel) == int:
                self.channel = self.guild.get_channel(self.channel)
            else:
                self.channel = self.channel

            if type(self.message) == int:
                self.message = await self.guild.fetch_message(self.message)

    def __repr__(self):
        return f"<exts.time.Event name={self.name}, time={self.start}, reminder={self.reminder}, role={self.role}, channel={self.channel}, guild={self.guild}>"

    @classmethod
    def from_dict(cls, bot, user_id: int, name: str, params: dict):
        start = params.pop("start")
        return cls(bot, user_id, name, start, **params)

    @classmethod
    def load(cls, bot, user_id: int, name: str, **params):
        if not get_event_view(user_id):
            raise ValueError(f"Event {name} from user {user_id} doesn't exist.")

        with ConfigFile(
            str(user_id), folder=EVENT_FOLDER, default=Event.empty_event
        ) as file:
            for status in file:
                if name in file[status]:
                    event = file[status][name].copy()
                    for key, value in params.items():
                        event[key] = value
                    return Event.from_dict(bot, user_id, name, event)

    @property
    def user(self):
        if not self._user:
            self._user = self.bot.get_user(self.user_id)

        return self._user

    def to_dict(self):
        if isinstance(self.channel, discord.TextChannel):
            channel = self.channel.id
        else:
            channel = self.channel

        if isinstance(self.guild, discord.Guild):
            guild = self.guild.id
        else:
            guild = self.guild

        if isinstance(self.role, discord.Role):
            role = self.role.id
        else:
            role = self.role

        subscribers = []
        for subscriber in self.subscribers:
            if isinstance(subscriber, discord.User):
                subscribers.append(subscriber.id)
            else:
                subscribers.append(subscriber)

        return {
            "start": self.start,
            "reminder": self.reminder,
            "description": self.description,
            "channel": channel,
            "guild": guild,
            "role": role,
            "color": self.color,
            "subscribers": subscribers,
        }

    def embed(self):
        dates = f"""This message is set to start at **{asctime(gmtime(self.start))}** and participants will be reminded **{asctime(gmtime(self.reminder))}** before the event."""
        preview = discord.Embed(title=self.name, description=dates, color=self.color)
        preview.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        preview.add_field(name="Description", value=self.description, inline=False)
        if self.guild:
            # the message was sent
            guild_spec = ""
            if type(self.role) not in (bool, None):
                guild_spec += (
                    f"The associated role for this event is {self.role.mention}.\n"
                )
            if type(self.channel) not in (bool, None):
                guild_spec += f"Discussion takes place in {self.channel.mention}"
            if len(guild_spec):
                preview.add_field(name="Information", value=guild_spec, inline=False)
        return preview

    def save(self, status="partial"):
        tmp_dict = self.to_dict()
        if type(tmp_dict["color"]) == discord.Color:
            tmp_dict["color"] = self.color.value
        with ConfigFile(
            self.user_id, folder=EVENT_FOLDER, default=Event.empty_event
        ) as file:
            file[status][self.name] = tmp_dict

    def delete(self):
        delete_event(self.user_id, self.name)

    def mark_sent(self):
        self.save(status="sent")
        self.delete()

    async def open(self):
        await self.message.add_reaction(EMOJIS["white_check_mark"])

    async def subscribe(self, user):
        self.subscribers.append(user)
        await self.resolve()
        if self.role:
            await self.subscribers[-1].add_roles(
                self.role, reason=f"Subscribed to {self.name} event."
            )

    async def countdown(self):
        pass


def get_event_view(user_id):
    with ConfigFile(
        str(user_id), folder=EVENT_FOLDER, default=Event.empty_event
    ) as file:
        return list(file["partial"].keys()) + list(file["sent"].keys())


def get_events(user_id, bot):
    with ConfigFile(
        str(user_id), folder=EVENT_FOLDER, default=Event.empty_event
    ) as file:
        partial = []
        for name, event in file["partial"].items():
            partial.append(Event.from_dict(bot, user_id, name, event.copy()))

        sent = []
        for name, event in file["sent"].items():
            sent.append(Event.from_dict(bot, user_id, name, event.copy()))

        return partial, sent


def delete_event(user_id, name: str, lenient=False):
    with ConfigFile(
        str(user_id), folder=EVENT_FOLDER, default=Event.empty_event
    ) as file:
        if name in file["partial"]:
            file["partial"].pop(name)
            return True
        elif name in file["sent"]:
            file["sent"].pop(name)
            return True
        elif lenient:
            return False
        else:
            raise ValueError(f"User {user_id} has no event {name}")


class Time(commands.Cog):
    """A cog which handles reminder events and commands"""

    def __init__(self, bot):
        self.config_entry = None
        self.bot = bot

    @commands.command()
    async def remind(self, ctx, *args):
        """for more information on how argument parsing is done see to_datetime"""
        args = list(args)
        args.append("null")  # so that a missing message is detected in the while loop
        delay = 0
        time_factor = to_datetime(args[0], sub=False, lenient=True)

        while time_factor:
            delay += time_factor.total_seconds()
            args.pop(0)
            time_factor = to_datetime(args[0], sub=False, lenient=True)

        # making sure the reminder is not set to current time
        if delay == 0 or len(args) == 1:
            await ctx.send(embed=get_embed_err(ERR_NOT_ENOUGH_ARG))
            return

        # making the text
        text = ""
        for word in args:
            text += f" {word}"

        await asyncio.sleep(delay)
        await ctx.author.send(text)

    @commands.group()
    async def event(self, ctx):
        """event interface with the user.
        Handles creation, tracking and publishing"""
        pass

    @event.command(alias=["draft", "compose", "create"])
    @discord.ext.commands.dm_only()
    async def new(self, ctx, name: str):
        """creates a new event and starts the creation interface
        TODO: make sure the rest of the "conversation" tales place exclusively in DM

        this command should be sent in a guild so that the bot can get its ID. The creation process will then take place in the DM."""
        # making sure an event with the same name isn't already registered for this user

        interface = ConfigEntry(self.bot, ctx.channel)

        evts_names = get_event_view(ctx.author.id)
        if name in evts_names:
            await ctx.send(
                "An event with the same name is already registered. Type `::event list` to get a list of registered events or `::help event` to learn how events work."
            )
            return

        await ctx.send(
            f"Starting creation of {name} event. You will need to enter details about the event you have in mind. You can always come back on these by using `::event edit <name>`."
        )

        # description
        description = await interface.get_answer(
            ctx, "Please enter the description of your event."
        )  # no need to check for char count since the user can't send more than 2k chars in a single message
        description = description.content
        await ctx.send(
            "Added the following text as description:\n--- **START** ---\n"
            + description
            + "\n--- **STOP** ---"
        )

        # start date
        # TODO: add support for fixed GMT time input instead?
        start_date = await interface.get_datetime(
            ctx,
            "In how much time should the event start? To learn more on the time format type `::help remind`.",
            later=60,
            seconds=True,
        )
        start_date += sec_time()
        await ctx.send(f"The event is set to start at {asctime(gmtime(start_date))}.")

        # remind date
        remind = await interface.get_datetime(
            ctx,
            "How much time before the event starts should the user be reminded?",
            seconds=True,
        )
        await ctx.send(
            f"The reminder will go off at {asctime(gmtime(start_date - remind))}."
        )

        # attributed role
        role = await interface.get_yn(
            ctx,
            "Should a role be made for this event? You will be able to modify its name and permissions directly from your guild once you send the event.",
        )

        # attributed channel
        chan = await interface.get_yn(
            ctx, "Should there be a new channel attributed and dedicated to the event?"
        )

        # color
        color = await interface.get_color(
            ctx,
            "What color should your event be? This should be either an integer or hexadecimal HTML color value (have it start with a `#`).",
        )

        draft = Event(
            self.bot,
            ctx.author.id,
            name,
            start_date,
            reminder=remind,
            description=description,
            color=color,
            role=role,
            channel=chan,
        )
        draft.save()
        await ctx.send("This is a preview of your event", embed=draft.embed())

    @event.command(alias=["list", "list_events", "events"])
    @discord.ext.commands.dm_only()
    async def ls(self, ctx):
        partial, sent = get_events(ctx.author.id, ctx.bot)
        events = discord.Embed(
            title="Your events",
            description="This is an exhaustive list of all of your events.",
            color=7506394,
        )

        # partial
        if len(partial) == 0:
            partial_list = "You have no draft events."
        else:
            partial_list = ""
            for event in partial:
                partial_list += f"**{event.name}** starting in **{asctime(gmtime(event.start - sec_time()))}**\n"
        events.add_field(name="Partial", value=partial_list)

        # sent
        if len(sent) == 0:
            sent_list = "You have no ongoing events"
        else:
            sent_list = ""
            for event in sent:
                sent_list += (
                    f"**{event.name}** started **{asctime(gmtime(event.start))}**\n"
                )
        events.add_field(name="Sent", value=sent_list)

        await ctx.send(embed=events)

    @event.command()
    async def preview(self, ctx, name: str):
        try:
            event = Event.load(ctx.bot, ctx.author.id, name)
        except ValueError:
            await ctx.send(embed=get_embed_err(ERR_MISFORMED))
        await ctx.send(embed=event.embed())

    @event.command(alias=["remove", "delete", "del"])
    @discord.ext.commands.dm_only()
    async def rm(self, ctx, *names: str):
        for name in names:
            if delete_event(ctx.author.id, name, lenient=True):
                await ctx.send(f"Event {name} was deleted.")
            else:
                await ctx.send(f"You have no event named: {name}")

    @event.command()
    @has_auth("planner")
    async def send(self, ctx, name: str):
        if name not in get_event_view(ctx.author.id):
            await ctx.author.send(
                f"I couldn't send event {name} because it doesn't exist! Please type `::event ls` to get a list of your events."
            )

        event = Event.load(ctx.bot, ctx.author.id, name, guild=ctx.guild)
        await event.resolve()

        if event.role == True:
            event.role = await ctx.guild.create_role(
                name=f"event-{name}",
                color=discord.Color(event.color),
                reason=f"Making event {name} role.",
                mentionable=True,
            )

        if event.channel == True:
            event.channel = await ctx.guild.create_text_channel(
                name=f"event-{event.name}",
                reason=f"Making event {name} channel.",
                topic=f"{event.name} event.",
            )
            if event.role:
                await event.channel.set_permissions(
                    event.guild.default_role,
                    overwrite=discord.PermissionOverwrite(read_messages=False),
                )
                await event.channel.set_permissions(
                    event.role,
                    overwrite=discord.PermissionOverwrite(read_messages=True),
                )

            await event.channel.send(
                "This channel has been set as an event channel!", embed=event.embed()
            )

        event.message = await ctx.send(
            "An event has been announced!", embed=event.embed()
        )
        event.mark_sent()
        await event.open()
        await event.countdown()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """used to have the members subscribe to an event"""
        # fetching concerned message and the user who added the reaction
        message = await self.bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id
        )
        # checking that user isn't the bot
        if (payload.user_id != self.bot.user.id) and len(message.embeds):
            if message.embeds[0].title in get_event_view(payload.user_id):
                # this is an event (really should anyways)
                event = Event.load(self.bot, payload.user_id, message.embeds[0].title)
                if payload.emoji.name == EMOJIS["white_check_mark"]:
                    print("adding subscriber")
                    await event.subscribe(payload.user_id)
                    event.save()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # fetching concerned message and the user who added the reaction
        message = await self.bot.get_channel(payload.channel_id).fetch_message(
            payload.message_id
        )
        # checking that user isn't the bot
        if (payload.user_id != self.bot.user.id) and len(message.embeds):
            if message.embeds[0].title in get_event_view(payload.user_id):
                # this is an event (really should anyways)
                event = Event.load(self.bot, payload.user_id, message.embeds[0].title)
                if payload.emoji.name == EMOJIS["white_check_mark"]:
                    await event.resolve()
                    user = self.bot.get_user(payload.user_id)
                    if user in event.subscribers:
                        event.subscribers.pop(user)
                        local_logger.info(f"Unsubscribed {user} from event: {event}")
                        event.save()


def setup(bot):
    bot.add_cog(Time(bot))
