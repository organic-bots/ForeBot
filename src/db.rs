use serenity::model::id::GuildId;
use sqlx::{query, MySqlPool, Result};

pub async fn insert_new_guild(conn: &MySqlPool, id: GuildId) -> Result<()> {
    query!("INSERT INTO guilds (id) values (?)", u64::from(id))
        .execute(conn)
        .await?;
    Ok(())
}
