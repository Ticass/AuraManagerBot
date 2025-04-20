import discord
import os
from discord.ext import commands
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# Application Default credentials are automatically created.
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()



# Replace this with the actual ID of the channel you want to send "hello" to
CAUGHT_IN_4K = 1362179931018362980
AURA_CHANNEL = 1362158658380894469
LEADERBOARD_CHANNEL = 1362926205355167844
leaderboard_message_id = 1363608546364621060

# Setup bot with proper intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#Utilities


async def RegisterDB(member):
    Player_ref = db.collection(u'Players').document(u''+f'{member.id}')
    _Player = Player_ref.get()
    if not _Player.exists:
        print("Player doesn't exist")
        data = {
            u'Name': f'{member.name}',
            u'Aura': 500000
        }
        db.collection(u'Players').document(u''+f'{member.id}').set(data)
        channel2 = await member.create_dm()
        content2 = f"Your aura is mine, **{member.name}**!"
        await channel2.send(content2)
    else:
        pass

async def GetPlayer(member):
    Player_ref = db.collection(u'Players').document(u''+f'{member.id}')
    _Player = Player_ref.get()
    if not _Player.exists:
        print("Player doesn't exist")
        return
    return _Player.to_dict()

async def GetTopAuras():
    Player_ref = db.collection("Players").order_by("Aura", direction=firestore.Query.ASCENDING).limit(10)
    results = Player_ref.stream()
    return leaderBoardEmbed(results)


async def remove_aura(member, amount):
    # Your custom logic here
    print(f"Doing something with user: {member.name}")
    # e.g., give a role, send DM, log, etc.
    Player_ref = db.collection(u'Players').document(u''+f'{member.id}')
    _Player = Player_ref.get()
    if not _Player.exists:
        print("Player doesn't exist")
        return
    player = await GetPlayer(member)
    aura = player["Aura"]
    calculated_aura = aura - amount
    Player_ref.update({"Aura": calculated_aura})

async def add_aura(member, amount):
    # Your custom logic here
    print(f"Doing something with user: {member.name}")
    # e.g., give a role, send DM, log, etc.
    Player_ref = db.collection(u'Players').document(u''+f'{member.id}')
    _Player = Player_ref.get()
    if not _Player.exists:
        print("Player doesn't exist")
        return
    player = await GetPlayer(member)
    aura = player["Aura"]
    calculated_aura = aura - amount
    Player_ref.update({"Aura": calculated_aura})

def auraEmbed(member, aura):
    AuraEmbed = discord.Embed(title="Aura Counter", color=discord.Color.red())
    AuraEmbed.add_field(name="Member", value=f"```{member.name}```")
    AuraEmbed.add_field(name="Aura", value=f"``` {aura} ```")
    AuraEmbed.set_author(name="Aura Bot", url="https://github.com/Ticass")
    AuraEmbed.set_footer(text=f"Aura Bot")
    return AuraEmbed

def leaderBoardEmbed(documents):
    LeaderEmbed = discord.Embed(title="Aura Leaderbord", color=discord.Color.red())
    for doc in documents:
        player = doc.to_dict()
        name = player["Name"]
        aura = player["Aura"]
        LeaderEmbed.add_field(name="Member", value=f"```{name}```", inline=True)
        LeaderEmbed.add_field(name="Aura", value=f"```{aura}```", inline=True)
        LeaderEmbed.add_field(name="\u200b", value="\u200b", inline=False)  # zero-width space forces line break
        LeaderEmbed.set_author(name="Aura Bot", url="https://github.com/Ticass")
        LeaderEmbed.set_footer(text=f"Aura Bot")
    return LeaderEmbed
    

@bot.command()
async def aura(ctx, member : discord.Member):
    user = await GetPlayer(member)
    userAura = user["Aura"]
    embed = auraEmbed(member, userAura)
    await ctx.channel.send(embed=embed)
    
@bot.command()
async def leaderboard(ctx):
    leaderboard = await GetTopAuras()
    await ctx.channel.send(embed=leaderboard)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.event
async def on_voice_state_update(member, before, after):
    global leaderboard_message_id
    # User joins a voice channel
    leaderboard = bot.get_channel(LEADERBOARD_CHANNEL)
    if before.channel != after.channel:
        if after.channel and after.channel.id == AURA_CHANNEL:
            channel = bot.get_channel(CAUGHT_IN_4K)
            if channel:
                await RegisterDB(member)
                await channel.send(f"**{member.name}** lost **10,000** aura")
            else:
                print("Channel not found. Make sure the bot has access to it.")
            print(f"{member.name} joined the target channel!")
            # You can now "do stuff" with their user ID
            await remove_aura(member, 10000)
            player = await GetPlayer(member)
            aura = player["Aura"]
            embed = auraEmbed(member, aura)
            topAuras = await GetTopAuras()
            await channel.send(embed=embed)
            if leaderboard_message_id:
                try:
                    message = await leaderboard.fetch_message(leaderboard_message_id)
                    await message.edit(embed=topAuras)
                except discord.NotFound:
                    msg = await leaderboard.send(embed=topAuras)
                    leaderboard_message_id = msg.id
            else:
                msg = await leaderboard.send(embed=topAuras)
                leaderboard_message_id = msg.id



# Start the bot
bot.run(os.getenv("BOT_KEY"))