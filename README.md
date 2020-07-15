<p align="center">
  <img sizes="(min-width: 512px) 512px, 512px" src="https://raw.githubusercontent.com/s0lst1ce/assets/master/sunflower_logo_1.png">
</p>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)]

# Botanist

This program is a Discord bot which is basically a mod to the real time messaging platform. It is built using discord.py API which offers full compatibility to the official Discord API.

​	This bot is a collection of several commands and suite of commands. They are regrouped under several extensions which can be loaded, updated and disabled on the fly, without ever having to take the bot off line. This allows one to stay use only the functions he wishes and keep them updated without any penalties.

## Development history

I ([@s0lst1ce](https://github.com/s0lst1ce)) started building this bot at the end of April 2019 using discord.py API. This bot was first made with the intent to make my discord server more powerful and alive. I had only created it a few days ago but I had realized that I would need additional tools to be able to fulfill all of the plans I had for this server. I had already started making a [bot](https://github.com/organic-bots/LazyFactorian) which serves as an interface to factorio's resources. I thus started building a bot that would enable me to easily manage a scalable server which would contain all of my future bots and would serve as a platform for all my creations.

​	After the very first version I got some help of a friend of mine. Together we made the bot evolve so that it could join the ranks of other servers. Indeed I had started to realize that the bot, however simple, may be useful to others. He built the the Todo extension. After that I kind of set back from the project.

​	After a month or two I got back to it with the idea to simplify the code base. The first thing on my list was the Config entry which was very hard to work with and hacky. So I built it in a more modular way so that it would be easier to maintain, expend, open up the way for i18n and ease expansion.

​	Once that was done I pondered a while on how to re-word the help system. Failing to find a good solution I rather got on that task of implementing more functionalities, better document commands, fix bugs and enhance the look of the commands outputs. All this made the bot a much more robust product I am now proud to share.

​	Still translations were still unsupported and the help system as unpractical. Because of this I forced myself to try both of these although I had no great idea on how to implement them. Translations were easier to introduce than I thought and I now have people working on actually writing them. As for the help system it has been enhanced already and more is on the way!

## Contribution

If you want to contribute that would be awesome ! We would love that :smile: !

So to help you out, here are some tips to get you going: [CONTRIBUTING.md](https://github.com/s0lst1ce/ForeBot/blob/master/CONTRIBUTING.md).

#### Contributors

Here's an exhaustive list of the bot's contributors:

- @adrienluitot : he has helped develop the bot since the beginning. His involvement ranges from giving opinions, shaping the future of the bot and some small snippets of code. He's also the author of the `Todo` extension, one of our biggest.
- @s0lst1ce : author and owner of the bot. He has thought out and written most of the bot. What we currently call the bot is practically entirely due to him.
- @BlueHolmesMan : author of the french translation.



Thanks to all of you who've made this project be, kept it alive and as available as possible. We owe you everything!



## Setup

There are two options to setup the game depending on the OS you intend to run the bot on. If you use windows or MacOS you should just clone the repository and run it set it up using `python`. You should change the settings in `settings.py`.

If however you choose to run the bot under Linux (recommended) you are advised to use the `deploy.sh` script. For this follow these instructions:

- Download the script (ex: `wget https://raw.githubusercontent.com/s0lst1ce/Botanist/master/deploy.sh`).
- Give it execution permissions (ex: `chmod +x deploy.sh`)
- Run the script `./deploy.sh`

To know how to use the script it is recommended to use `deploy.sh -h`. From there the process should be straightforward. This script is mean to expand as time goes.

## Commands

### Getting started

Here is an exhaustive list of all extensions and the commands they provide. This list is kept up to date with the latest updates. Some commands can only be ran in a server (ie: you can't have roles in a DM). They are also all case sensitive. To make you message a command it must start with the set `PREFIX`. By default this is set to `::`. This means that if you want to call the command `slaps`, you have to enter `::slaps`. The prefix is not mentioned in the following reference.

​	Those commands are sometimes regrouped under a **group**. This means that a command belonging to a **group** will only be recognized if the **group**'s name is appended before the command. For example the command `ls` of group `ext` needs to be called like this: `ext ls`.

​	To prevent abuse a **clearance** system is included with the bot. This allows servers to limit the use of certain commands to select group of members. One member can possess multiple roles (ie: levels of clearance). The implemented level of clearances are listed & described in the following table in order of magnitude:

| Clearance     | Description                                                  |
| ------------- | ------------------------------------------------------------ |
| *             | this represents the wildcard and means everyone can use the command. No matter their roles |
| runner        | this role is assigned to only one member: the one with the [`RUNNER_ID`](https://github.com/s0lst1ce/Botanist/blob/dev/src/settings.py#L16). This is defined in the `settings.py` file and should represent the ID of the user responsible for the bot. It is also the only cross-server role. |
| owner         | this role is automatically assigned to every server owner. It is however server-specific. It gives this member supremacy over all members in his/her server. |
| administrator | this role gives access to all server commands except the bot configuration ones |
| manager       | this role gives access to message management, warnings issues and other server moderation commands |

​	Arguments (aka: parameters) are referenced in `<` & `>` in this reference although using those symbols isn't necessary when using the commands.  Some arguments are optional. If it's the case they are preceded by a `*`. Otherwise the command's list of required arguments is to be  like this: `<arg1>` `<arg2>`.  This can also be blank when the command doesn't require any argument.

 Sometimes commands require a `*` argument. This means that the argument length is unlimited. It can range from 0 to 2000 characters (the maximum allowed by discord).

Finally arguments which are not `*` but comprises spaces need to be put in quotes like this: `"this is one argument only"`. Else each "word" will be considered a different argument. If the argument count doesn't exactly match then the command will fail. Also the arguments order matters.





### Reference

#### Defaults

A suite of commands always activated which handle extension management. This cannot be unloaded as it is part of the core of the bot and is required for live updates.

| Group | Command  |   Arguments   |                         Description                          | Clearance |
| ----- | :------: | :-----------: | :----------------------------------------------------------: | --------- |
| `ext` |  `add`   | `<extension>` | loads the  specified `extension` bot extension. If the command fails the bot will continue to run without the extension. | runner    |
| `ext` |   `rm`   | `<extension>` | removes the  specified `extension` bot extension. If the command fails the bot will continue to run with the extension. | runner    |
| `ext` | `reload` | `<extension>` | reloads the  specified `extension` bot extension. If the command fails the extension will stay unloaded | runner    |
| `ext` |   `ls`   |               |  returns an embed with all the extensions and their status   | runner    |
|       |  `help`  |   `[page]`    | initiates an interactive help session. If a `page` is supplied then it opens it only for this page and subpages. A page can be a cog, group or command. | *         |



#### Poll

This suite of commands provides automatic poll creation. A poll is an embed message sent by the bot to specified channels. Every user can react to the poll to show their opinion regarding the interrogation submitted by the poll. With each reaction, the poll's color will change to give everyone a quick visual feedback of all members' opinion. A poll is generated from a user's message. Currently it only supports messages from a `poll` channel. However it is planned to improve this to allow one to create a poll using a dedicated command. Same goes for poll editing which is yet unsupported. To palliate to this you can remove your poll if you consider it was malformed. Polls can also be deleted when reacting with the `:x:` emoji.

| Group  |  Command   |            Arguments            |                         Description                          | Clearance |
| ------ | :--------: | :-----------------------------: | :----------------------------------------------------------: | :-------: |
| `poll` |    `rm`    |           `<msg_id>`            | If the user is the author of the poll with the `msg_id` message, the bot deletes the specified poll. |     *     |
| `poll` |  `status`  |                                 | Returns stats about your active polls. This is also called when one of you poll gets deleted. |     *     |
| `poll` | `extended` | `<description...> <choices...>` | This command creates polls that can have more than the 3 standard reaction but do not support dynamic color. The way to make one is to be write the following command in a poll channel (message discarded otherwise). The message is composed of the description then a line break then, one each following line: an emoji followed by a description each of these lines are separated by a line break |     *     |



#### Embedding

This extension allows any user to send a message as an embed. The color of the embed is defined by the user's role color.

| Group | Command |   Arguments    |                         Description                          | Clearance |
| ----- | :-----: | :------------: | :----------------------------------------------------------: | --------- |
|       | `embed` | `[message...]` | converts all arguments which form the user's message into a new embed one. Markdown is supported, including named links | *         |



#### Bot Essentials

This extension contains some of the most basic managing commands and should almost always be enabled.


| Group |  Command   |           Arguments           |                         Description                          | Clearance |
| :---: | :--------: | :---------------------------: | :----------------------------------------------------------: | :-------: |
|       |   `ping`   |                               |   replies with the rounded latency of the message transfer   |     *     |
|       | `shutdown` |                               |                 shuts down the bot properly                  |  runner   |
|       |  `clear`   | `[nbr] [period] [members...]` | this command lets one delete messages from a channel. The provided arguments are filters that will be applied to the messages selection process. `nbr` specifies the maximum number of messages that should be deleted. If not given then there is no maximum, **be careful with it**. This will always be respected although less messages may get deleted if `period` doesn't contain enough messages. `period` represents a time frame. The bot will look for all messages within this time frame. It should be constructed like `remind`. All messages which were sent between *now* and `period` will get deleted unless this represents more messages than `nbr`. `members...` is a list of server members. Only messages from these users will get deleted. You do not need to pass any of the arguments to the command and can pass any combination of them to the command. However they **must** be given in order! |  manager  |
|       |  `status`  |                               | returns some statistics and info about the server and its members |     *     |



#### Slapping

Allows moderators to give quick and light warnings to disrespectful members. By slapping a member he gets notified of his misbehavior and knows who did it. Both the administrator and the user can see his/her slap count. The slap count is also cross-server.

| Group |  Command  |        Arguments        |                         Description                          | Clearance |
| ----- | :-------: | :---------------------: | :----------------------------------------------------------: | :-------: |
|       |  `slap`   | `<member> [message...]` | slaps the specified `<member>` member one time. The other arguments will form the optional reason for the slap. |  manager  |
|       | `forgive` |    `<member> [nbr]`     | forgives the specified `<member>` member `<nbr>` number of time(s). If `<nbr>` is unspecified, pardons the member of all his slaps. Member can be a mention, a user id or just the string of the name of the member. |  manager  |
|       |  `slaps`  |     `[members...]`      | returns an embed with a list of all slapped members and their slap count. If arguments are given they must represent members or their ids/name. If so detailed info will be returned only of those members. It gives access to the slapping log. |  manager  |
|       |  `mute`   |    `<member> <time>`    | mutes `member` in the current channel for `time` period. This prevents the user to send messages in the channel. |  manager  |
|       |  `abuse`  | `<member> [reason...]`  | sends a report card with `reason` description about `member` to the set moderation channel so that moderators can deal with it |     *     |
|       |  `spam`   |       `<member>`        | increases spam count of `member` by one. Once the counter reaches the the server threshold, the user is muted for 10 minutes. |     *     |



#### Role 

Allows moderators to add and remove roles to members.

| Group  | Command |        Arguments        |                         Description                          |   Clearance   |
| ------ | :-----: | :---------------------: | :----------------------------------------------------------: | :-----------: |
| `role` |  `add`  | `<member>` `<roles...>` | adds the specified `roles` roles from the `member` member (roles mustn't be empty). Member can be a mention, a user id or just the string of the name of the member | administrator |
| `role` |  `rm`   | `<member>` `<roles...>` | removes the specified `roles` roles from the `member` member (roles mustn't be empty). Member can be a mention, a user id or just the string of the name of the member | administrator |



#### Config

Allows the owner of a server to configure the behavior of the bot.

| Group |  Command  |   Arguments   |                         Description                          |   Clearance   |
| ----- | :-------: | :-----------: | :----------------------------------------------------------: | :-----------: |
|       |  `init`   |               | starts full configuration of the bot in a new, restricted, channel |     owner     |
|       |   `cfg`   | `<extension>` | starts the configuration of the `extension` extension. This is done in a new, restricted, channel | administrator |
|       | `summary` |               | Returns an exhaustive description of all settings set in the current server | administrator |



#### Development

Allows the developers to update the bot and notify all server owners of the changes. It also facilitates bug fixing by providing an easy way to retrieve the log.

| Group | Command  |   Arguments    |                         Description                          | Clearance |
| :---: | :------: | :------------: | :----------------------------------------------------------: | :-------: |
|       | `update` | `[message...]` | sends an update message to all users who own a server of which the bot is a member. `message` will be transformed into the message sent to the server owners. A default message is sent if none is provided. This can be modified in `settings.py`. |  runner   |
|       |  `log`   |                |                  returns the bot's log file                  |  runner   |
|       |  `dev`   |                | sends the development server URL to the author of the message |     *     |



#### Time

Gives several time-related commands to ease organization. For now this only includes a remind function but an event planner is in the works.

| Group |  Command  |       Arguments       |                         Description                          | Clearance |
| ----- | :-------: | :-------------------: | :----------------------------------------------------------: | :-------: |
|       | `remind`  | `<date> [message...]` | returns the specified message after the specified amount of time. To precise the delay before sending the message use the following format: `1d15h6m1s` where `d` stands for days, `h` for hours, `m` for minutes and `s` for seconds. The numbers preceding them must be integers and represent the number of units to wait for (be it days, hours, minutes or seconds). All other words given as argument will form the message's content and will be sent in PM to the user after the specified delay has elapsed. |     *     |
| event |  `new `   |       `<name>`        | creates a live event creation session in Direct Message (DM). The bot will ask the user to fill in the required and optional fields of `name`. |     *     |
| event |  `send`   |       `<name>`        |           Sends the event in the current channel.            |     *     |
| event |   `rm`    |       `<name>`        | Deletes the `name` event from the user’s selection of events |     *     |
| event |  `list`   |                       |        Returns the list of all events for this user.         |     *     |
| event |  `edit`   |   `<name> <field>`    |       lets the user only edit `field` for `name` event       |     *     |
| event | `preview` |       `<name>`        |          returns the current embed bound to `name`           |     *     |


