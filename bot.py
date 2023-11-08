import discord, json, requests, asyncio, scrapers, time
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
            #TODO: Make description be more detailed
            embed = discord.Embed(title=f'Daily Internships', description=f"Tech internships for the day", color=discord.Colour.green())
            for listing in response:
                embed.add_field(name=f"{listing[0]}", value=f"{listing[2]}", inline=False)
                
            await interaction.channel.send(embed=embed)
            
                
        await interaction.followup.send("Finished sending")
    except:
        embed = discord.Embed(title="Please try again.", color=discord.Colour.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
# @tree.command(name="subscribe", description="Subscribe a channel to get daily internship postings") 
# async def self(interaction: discord.Interaction, channel_id: int):
#     return

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

if __name__ == '__main__':
    bot.run(TOKEN)