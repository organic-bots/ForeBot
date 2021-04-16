use serenity::{builder::CreateEmbed, model::prelude::*, prelude::*};
use std::fmt::Display;
use std::time::Duration;
use tracing::{debug, error, info};

///Two weeks in seconds
pub const TWO_WEEKS: i64 = 1209600;
//Error handler
//Logs the error and sends an embed error report on discord
pub async fn report_error<'a, 'b>(
    ctx: &Context,
    channel: &ChannelId,
    error: &BotError<'a, 'b>,
) -> () {
    debug!("The error report {:?} was sent in {:?}", error, channel);
    let mut embed = CreateEmbed::default();
    embed
        .color(16720951)
        .description(error.description)
        .title(match &error.kind {
            None => "UnexpectedError",
            Some(kind) => "An error occured",
        });

    let cause_user: Option<&User> = None;
    if let Some(msg) = error.origin {
        embed.timestamp(&msg.timestamp);
        //embed.url(msg.link()); currently removed because it doesn't link correctly
        let cause_user = Some(&msg.author);
        embed.footer(|f| {
            f.text(format!("caused by {:#}", cause_user.unwrap().name))
                .icon_url(
                    cause_user
                        .unwrap()
                        .avatar_url()
                        .unwrap_or(cause_user.unwrap().default_avatar_url()),
                )
        });
    };

    if let Some(kind) = &error.kind {
        embed.field("❓ How to fix this", format!("{:#}", kind), false);
    };

    embed.field("🐛 Bug report", String::from("[GitHub](https://github.com/Botanism/Botanist/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BREPORTED+BUG%5D) | [Official Server](https://discord.gg/mpGM5cg)"), false);
    //we send the created embed in the channel where the error occured, if possible
    match channel
        .send_message(ctx, |m| m.set_embed(embed.clone()))
        .await
    {
        Ok(_) => (),
        Err(SerenityError::Http(_)) => {
            info!(
                "couldn't report error in {:?} because of missing permissions",
                channel
            );
            error_report_fallback(ctx, channel, cause_user, embed).await;
        }
        Err(SerenityError::Model(ModelError::MessageTooLong(excess))) => {
            error!("CRITICAL: error embed was too long by {:?}", excess)
        }
        _ => unimplemented!(),
    }
}

//used if the bot couldn't report an error through the channel of origin
//since it's a fallback it mustn't fail, however acttuall delivery may for network error reasons
//or if the user has blocked DMs
//may one day be merged with error_report if BotError gains a dm:bool attribute
async fn error_report_fallback(
    ctx: &Context,
    chan: &ChannelId,
    culprit: Option<&User>,
    embed: CreateEmbed,
) {
    match culprit {
        None => info!("Could not determine a user that caused the issue, can't fallback to DM error reporting"),
        //since we couldn't send the error in the channel we try to do so in DM
        Some(user) => match user.dm(ctx, |m| m.set_embed(embed).content(format!("We couldn't report the error in {:#} so we're doing it here!", chan.mention()))).await {
            Err(_) => error!("Fallback error reporting failed because the DM couldn't be sent"),
            Ok(_) => (),
        }
    }
}

//used to describe an error to the user, meant to be supplied to `report_error`
#[derive(Debug)]
pub struct BotError<'a, 'b> {
    description: &'a str,
    //optionally provide additional information on this kind of error
    kind: Option<BotErrorKind>,
    //sometimes the error doesn't originate from a specific message or command -> None
    origin: Option<&'b Message>,
}
impl<'a, 'b> BotError<'a, 'b> {
    pub fn new(
        description: &'a str,
        kind: Option<BotErrorKind>,
        origin: Option<&'b Message>,
    ) -> BotError<'a, 'b> {
        BotError {
            description,
            kind,
            origin,
        }
    }
}

//when applicable, used to provide additional information on the error to the user
#[derive(Debug)]
pub enum BotErrorKind {
    EnvironmentError,
    IncorrectNumberOfArgs,
    UnexpectedError,
    DurationSyntaxError,
    ModelParsingError,
    MissingPermissions,
}

impl Display for BotErrorKind {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> Result<(), core::fmt::Error> {
        write!(f, "{}", match self {
            BotErrorKind::EnvironmentError => "The bot was incorrectly configured by its owner. Please contact a bot administrator so that they can fix this ASAP!",
            BotErrorKind::IncorrectNumberOfArgs => "You called a command but provided an incorrect number of arguments. Consult the online documentation or type `::help <command>` to know which arguments are expected. If you think you've provided the right number of arguments make sure they are separated by a valid delimiter. For arguments containing space(s), surround them with quotes: `:: <command> \"arg with spaces\"`",
            BotErrorKind::UnexpectedError => "This error is not covered. It is either undocumented or comes from an unforseen series of events. Either way this is a bug. **Please report it!**",
            BotErrorKind::DurationSyntaxError => "A duration was expected as an argument but what you provided was invalid. The correct syntax for duations is `00d00h00m00s` where `00` stands for any valid number. As for the letters they're shorts for `day`, `hour`, `minute` and `second` respectively. They can be both lowercase and uppercase.",
            BotErrorKind::ModelParsingError => "This error occurs when a command expects a role/member/channel but something that could not be understood as such was provided. The bot uses multiple methods to interpolate the channel/role/member. You can use it's ID, mention directly, or use the name. The latter may fail if the name is ambiguous.",
            BotErrorKind::MissingPermissions => "The bot lacks the required permissions for this command in this channel. Please contact a server admin so that they can fix this. ",
        })
    }
}

//Top-level error enum for the bot (which name is Botanist).
//allows us to use custom errors alongside serenity's ones
#[derive(Debug)]
pub enum BotanistError {
    DurationParseError(DurationParseError),
    Serenity(SerenityError),
    SerenityUserIdParseError(serenity::model::misc::UserIdParseError),
}

impl Display for BotanistError {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> Result<(), core::fmt::Error> {
        write!(f, "BotanistError: {:#}", self)
    }
}

impl std::error::Error for BotanistError {}

impl From<SerenityError> for BotanistError {
    fn from(err: SerenityError) -> Self {
        BotanistError::Serenity(err)
    }
}

impl From<serenity::model::misc::UserIdParseError> for BotanistError {
    fn from(err: serenity::model::misc::UserIdParseError) -> Self {
        BotanistError::SerenityUserIdParseError(err)
    }
}

//occurs only with `parse_duration` when the given string cannot be parsed
#[derive(Debug)]
pub struct DurationParseError {
    pub source: String,
}
impl Display for DurationParseError {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> Result<(), core::fmt::Error> {
        write!(f, "Could not parse {:#} as a duration.", self.source)
    }
}
impl std::error::Error for DurationParseError {}

pub fn parse_duration<S: AsRef<str>>(string: S) -> Result<Duration, DurationParseError> {
    const TIME_IDENTIFIERS: [char; 4] = ['d', 'h', 'm', 's'];
    const TIME_VALUES: [u64; 4] = [86400, 3600, 60, 1];

    let mut total: u64 = 0;

    let (mut start, mut stop): (usize, usize) = (0, 0);
    let mut value: String;
    let mut ident = 0;

    for character in string.as_ref().chars() {
        if character.is_ascii_digit() {
            stop += 1;
        } else {
            value = string.as_ref()[start..stop].to_string();
            if value.is_empty() {
                return Err(DurationParseError {
                    source: string.as_ref().to_string(),
                });
            } else {
                start = stop + 1;
                stop = start;
                total += value.parse::<u64>().unwrap() * TIME_VALUES[ident];
                value.clear();
                ident = match TIME_IDENTIFIERS
                    .iter()
                    //we currently use the char 'Z' to denote a missing lowercase version of a char.
                    //indeed if this happends it means the char is not an ASCII letter and 'Z' will fail to match
                    .position(|short| short == &character.to_lowercase().next().unwrap_or('Z'))
                {
                    Some(index) => index,
                    None => {
                        return Err(DurationParseError {
                            source: string.as_ref().to_string(),
                        })
                    }
                };
            }
        }
    }

    Ok(Duration::from_secs(total))
}
