import discord
from discord.ext import commands, tasks
from discord import app_commands
import requests
import mysql.connector
import os

DISCORD_TOKEN = "TON_DISCORD_TOKEN"
TWITCH_CLIENT_ID = "TON_TWITCH_CLIENT_ID"
TWITCH_CLIENT_SECRET = "TON_TWITCH_CLIENT_SECRET"
DISCORD_CHANNEL_ID = 1234567890
CHECK_INTERVAL = 60

DB_HOST = "TON_DB_HOST"
DB_USER = "TON_DB_USER"
DB_PASSWORD = "TON_DB_PASSWORD"
DB_NAME = "TON_DB_NAME"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
is_live_states = {}


def db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def init_db():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS streamers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()


def load_streamers():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, description FROM streamers")
    streamers = {username: {"description": description} for username, description in cursor.fetchall()}
    conn.close()
    return streamers


def save_streamer(username, description):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO streamers (username, description) VALUES (%s, %s) ON DUPLICATE KEY UPDATE description = %s",
                   (username.lower(), description, description))
    conn.commit()
    conn.close()


def get_twitch_token():
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, data=payload)
    return response.json().get("access_token")


@tasks.loop(seconds=CHECK_INTERVAL)
async def check_streams():
    global is_live_states
    streamers = load_streamers()
    token = get_twitch_token()
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }

    for username, info in streamers.items():
        if username not in is_live_states:
            is_live_states[username] = False

        stream_url = f"https://api.twitch.tv/helix/streams?user_login={username}"
        response = requests.get(stream_url, headers=headers)
        
        if response.status_code != 200:
            continue

        try:
            data = response.json()
        except ValueError:
            continue

        if data.get('data'):
            if not is_live_states[username]:
                is_live_states[username] = True
                channel = bot.get_channel(DISCORD_CHANNEL_ID)
                if channel:
                    embed = discord.Embed(
                        title=f"{username} est en live sur Twitch",
                        description=f"🎮 {info['description']}\n🔴 Regardez ici : [Twitch](https://www.twitch.tv/{username})",
                        color=discord.Color.green()
                    )
                    await channel.send(content="@everyone", embed=embed)
        else:
            is_live_states[username] = False


@bot.tree.command(name="addstreamer", description="Ajoute un streamer à la liste de surveillance.")
async def add_streamer(interaction: discord.Interaction, username: str, description: str = "Pas de description fournie."):
    streamers = load_streamers()
    if username.lower() in streamers:
        await interaction.response.send_message(f"⚠️ {username} est déjà surveillé.")
        return

    save_streamer(username, description)
    await interaction.response.send_message(f"✅ {username} ajouté avec la description : \"{description}\"")


@bot.tree.command(name="liststreamers", description="Affiche la liste des streamers surveillés.")
async def list_streamers(interaction: discord.Interaction):
    streamers = load_streamers()
    if not streamers:
        await interaction.response.send_message("❌ Aucun streamer surveillé.")
        return

    embed = discord.Embed(title="📢 Liste des streamers surveillés", color=discord.Color.blue())
    for username, info in streamers.items():
        embed.add_field(name=username, value=info['description'], inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="removestreamer", description="Supprime un streamer de la liste de surveillance.")
async def remove_streamer(interaction: discord.Interaction, username: str):
    streamers = load_streamers()
    if username.lower() not in streamers:
        await interaction.response.send_message(f"⚠️ {username} n'est pas surveillé.")
        return

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM streamers WHERE username = %s", (username.lower(),))
    conn.commit()
    conn.close()
    await interaction.response.send_message(f"✅ {username} a été retiré de la liste.")


@bot.tree.command(name="editstreamer", description="Modifie la description d'un streamer.")
async def edit_streamer(interaction: discord.Interaction, username: str, new_description: str):
    streamers = load_streamers()
    if username.lower() not in streamers:
        await interaction.response.send_message(f"⚠️ {username} n'est pas surveillé.")
        return

    save_streamer(username, new_description)
    await interaction.response.send_message(f"✅ Description de {username} mise à jour : \"{new_description}\"")


GUILD_ID = 1234567890
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et surveille les streams !")
    check_streams.start()
    guild = bot.get_guild(GUILD_ID)

    await bot.tree.sync()

    for command in bot.tree.get_commands():
        print(f"- {command.name}")

    if guild:
        try:
            await bot.tree.sync(guild=guild)
        except Exception as e:
            print(f"Erreur lors de la synchronisation des commandes slash : {e}")


init_db()
bot.run(DISCORD_TOKEN)
