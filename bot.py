import discord, json, requests, asyncio, scrapers
from discord import app_commands

with open('vars/config.json', 'r') as f:
    data = json.load(f)
with open('vars/links.json', 'r') as f2:
    links = json.load(f2)
    
TOKEN = data['TOKEN']
TEST_SERVER = data['SERVER']

class pre_bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await tree.sync(guild=discord.Object(id=TEST_SERVER)) 
        self.synced = True
        print("Bot Online")
        
bot = pre_bot()
tree = app_commands.CommandTree(bot)

@tree.command(name="dailysearch", description="Search for new internship postings in the past 24 hours", guild=discord.Object(id=TEST_SERVER)) # Change to support all servers
async def self(interaction: discord.Interaction):   
    page_data = requests.get(links["GITHUB_24"])
    
    await interaction.response.defer()
    await asyncio.sleep(10) # ? Needs adjusting

    response = scrapers.githubData(page_data)
    
    for listing in response:
        embed = discord.Embed(title=f'{listing[0]}', description=f"{listing[1]}", color=discord.Colour.green())
        embed.add_field(name=f"Apply", value=f"{listing[2]}")
        embed.set_footer(text=f"{listing[3]}")
        await interaction.channel.send(embed=embed)
            
    await interaction.followup.send("Finished sending")

# @tree.command(name="searchweekly", description="Search for new internship postings in the past week", guild=discord.Object(id=TEST_SERVER)) 
# async def self(interaction: discord.Interaction):
#     return

@tree.command(name="invite", description="Invite the bot to your server!", guild=discord.Object(id=TEST_SERVER)) 
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(links['BOT_INVITE'])

@tree.command(name="help", description="Shows commands for the bot", guild=discord.Object(id=TEST_SERVER)) 
async def self(interaction: discord.Interaction):
    embed = discord.Embed(title="Commands", description="All bot commands", color=discord.Colour.gold())
    embed.add_field(name=f"/dailysearch", value=f"Shows today's internship postings according to Pitts GitHub repo")
    embed.add_field(name=f"/invite", value=f"Sends invite link for the bot")
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == '__main__':
    bot.run(TOKEN)