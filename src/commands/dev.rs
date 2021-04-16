use crate::utils::*;
use crate::ShardManagerContainer;
use serenity::model::prelude::*;
use serenity::prelude::*;
use serenity::{
    client::bridge::gateway::ShardId,
    framework::standard::{
        macros::{command, group},
        CommandError, CommandResult,
    },
};
use std::env;
use tracing::error;
#[group]
#[commands(shutdown, latency, log)]
struct Development;

#[command]
#[owners_only]
async fn shutdown(ctx: &Context, msg: &Message) -> CommandResult {
    let data = ctx.data.read().await;

    if let Some(manager) = data.get::<ShardManagerContainer>() {
        msg.reply(ctx, "Shutting down!").await?;
        manager.lock().await.shutdown_all().await;
    } else {
        //we contact the dev directly
        msg.author
            .dm(ctx, |m| {
                {
                    {
                        m.content("There was a problem getting the sard manager.")
                    }
                }
            })
            .await?;
        return Ok(());
    }
    Ok(())
}

#[command]
#[owners_only]
async fn latency(ctx: &Context, msg: &Message) -> CommandResult {
    // The shard manager is an interface for mutating, stopping, restarting, and
    // retrieving information about shards.
    let data = ctx.data.read().await;

    let shard_manager = match data.get::<ShardManagerContainer>() {
        Some(v) => v,
        None => {
            msg.reply(ctx, "There was a problem getting the shard manager")
                .await?;

            return Ok(());
        }
    };

    let manager = shard_manager.lock().await;
    let runners = manager.runners.lock().await;

    // Shards are backed by a "shard runner" responsible for processing events
    // over the shard, so we'll get the information about the shard runner for
    // the shard this command was sent over.
    let runner = match runners.get(&ShardId(ctx.shard_id)) {
        Some(runner) => runner,
        None => {
            msg.reply(ctx, "No shard found").await?;

            return Ok(());
        }
    };

    msg.reply(ctx, &format!("The shard latency is {:?}", runner.latency))
        .await?;

    Ok(())
}

#[command]
#[owners_only]
//Allows owners to send messages to all owners of the guilds the bot is in
async fn update(ctx: &Context, msg: &Message) -> CommandResult {
    for guild in ctx.cache.guilds().await {
        guild
            .to_partial_guild(ctx)
            .await?
            .owner_id
            .to_user(ctx)
            .await?
            .dm(ctx, |m| m.content(&msg.content))
            .await?;
    }
    Ok(())
}

#[command]
#[owners_only]
#[only_in(dm)]
//sends the log file over to discord
async fn log(ctx: &Context, msg: &Message) -> CommandResult {
    let path = match env::var("LOG_FILE") {
        Ok(path) => path,
        Err(err) => {
            error!("{:#}", err);
            let error = BotError::new(
                "LOG_FILE is missing",
                Some(BotErrorKind::EnvironmentError),
                Some(msg),
            );
            report_error(ctx, &msg.channel_id, &error).await;
            return Err(CommandError::from(err));
        }
    };
    match msg
        .channel_id
        .send_files(ctx, vec![path.as_str()], |m| m)
        .await
    {
        Ok(_) => (),
        //we know the only error that can occur is HttpError::UnsuccessfulRequest(ErrorResponse) (file too large)
        Err(_) => {
            msg.channel_id
                .say(ctx, "The log is too large to be sent")
                .await?;
        }
    }
    Ok(())
}
