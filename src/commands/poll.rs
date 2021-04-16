use crate::ShardManagerContainer;
use serenity::model::prelude::*;
use serenity::prelude::*;
use serenity::{
    async_trait,
    client::bridge::gateway::ShardId,
    framework::standard::{
        macros::{command, group},
        CommandResult,
    },
};

struct PollHandler;

#[async_trait]
impl EventHandler for PollHandler {
    async fn message(&self, ctx: Context, msg: Message) {}
}
