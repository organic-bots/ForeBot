use serenity::framework::standard::{macros::check, Args, CommandOptions, Reason};
use serenity::model::channel::Message;
use serenity::prelude::*;

#[check]
async fn is_manager(
    _: &Context,
    _msg: &Message,
    _: &mut Args,
    _: &CommandOptions,
) -> Result<(), Reason> {
    unimplemented!()
}
