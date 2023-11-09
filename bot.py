import discord, json, requests, asyncio, scrapers, time, pytz
from discord import app_commands
from datetime import datetime, timedelta
from discord.ext import tasks

with open('vars/config.json', 'r') as f:
    data = json.load(f)
with open('vars/links.json', 'r') as f2:
    links = json.load(f2)
with open('storage/channels.json', 'r') as f3:
    channels = json.load(f3)
    
TOKEN = data['TOKEN']
TEST_SERVER = data['SERVER']
pst_timezone = pytz.timezone('America/Los_Angeles')

class pre_bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await tree.sync() 
        self.synced = True
        print("Bot Online")
        
bot = pre_bot()
tree = app_commands.CommandTree(bot)

@tree.command(name="dailysearch", description="Search for new internship postings in the past 24 hours") 
@app_commands.describe(style="Choose a method for displaying the roles")
@app_commands.choices(style=[
    discord.app_commands.Choice(name="Compact", value=1),
    discord.app_commands.Choice(name="Singular", value=2),
])
async def self(interaction: discord.Interaction, style: discord.app_commands.Choice[int]):   
    try:
        page_data = requests.get(links["GITHUB_24"])
        
        await interaction.response.defer()
        await asyncio.sleep(10) # ? Needs adjusting

        response = scrapers.githubData(page_data)
        
        if style.value == 2:
            for listing in response:
                embed = discord.Embed(title=f'{listing[0]}', description=f"{listing[1]}", color=discord.Colour.green())
                embed.add_field(name=f"Apply", value=f"{listing[2]}")
                embed.set_footer(text=f"{listing[3]}")
                
                time.sleep(0.25)
                await interaction.channel.send(embed=embed)
        elif style.value == 1:
            current_time_pst = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pst_timezone)
            formatted_date = current_time_pst.strftime('%m/%d/%y')
            
            embed = discord.Embed(title=f'Daily Internships', description=f"{formatted_date}", color=discord.Colour.green())
            for listing in response:
                embed.add_field(name=f"{listing[0]}", value=f"{listing[2]}", inline=False)
            
            #TODO: Implement pagination for embed
            await interaction.channel.send(embed=embed)
                
        await interaction.followup.send("Finished.")
    except:
        embed = discord.Embed(title="Please try again.", color=discord.Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
@tree.command(name="subscribe", description="Subscribe a channel to get daily internship postings") 
async def self(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    server_id = interaction.guild_id
    
    channels[server_id] = channel_id
    with open("storage/channels.json", "w") as outfile:
        json.dump(channels, outfile)
    
    embed = discord.Embed(title="Subscribed!", color=discord.Colour.dark_green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

# @tree.command(name="searchweekly", description="Search for new internship postings in the past week") 
# async def self(interaction: discord.Interaction):
#     return

@tree.command(name="invite", description="Invite the bot to your server!") 
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(f"Click here to [Invite]({links['BOT_INVITE']}) Internship Bot")

@tree.command(name="help", description="Shows commands for the bot") 
async def self(interaction: discord.Interaction):
    embed = discord.Embed(title="Commands", description="All bot commands", color=discord.Colour.gold())
    embed.add_field(name=f"/dailysearch", value=f"Shows today's internship postings according to Pitts GitHub repo")
    embed.add_field(name=f"/invite", value=f"Sends invite link for the bot")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tasks.loop(hours=24)
async def daily_update():
    for channel_id in channels.values():
        channel = bot.get_channel(channel_id) 
        if channel:  
            await channel.send("Test")

@daily_update.before_loop
async def before_daily_message():
    hour = 8  
    now = datetime.utcnow()
    future = datetime(now.year, now.month, now.day, hour, 0)
    if now.hour >= hour:  
        future += timedelta(days=1)
    await discord.utils.sleep_until(future)

if __name__ == '__main__':
    bot.run(TOKEN)
    daily_update.start()