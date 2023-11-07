import discord, json, requests, asyncio, datetime, time
from discord import app_commands
from bs4 import BeautifulSoup

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

@tree.command(name="dailysearch", description="Search for new internship postings in the past 24 hours", guild=discord.Object(id=TEST_SERVER)) 
async def self(interaction: discord.Interaction):
    # Psuedocode
    # Scrape from LinkedIn
    # Send each listing with a 0.25 second break in-between
    # Scrape from Levels
    # Send each listing with a 0.25 second break in-between
    # Scrape from GitHub
    # Send each listing with a 0.25 second break in-between
    # Each listing should be an embed with the Company, Role, Location, and Link to Apply
    # Edge Cases: Site ban, Position is locked on github
        
    page_data = requests.get(links["github24"])
    
    await interaction.response.defer()
    await asyncio.sleep(10) # May need to edit

    result = BeautifulSoup(page_data.text, 'lxml')
    table_data = str(result.find("table"))

    table_data = table_data.replace("</tr>", "")
    table_data = table_data.replace("</tbody>", "")
    table_data = table_data.replace("</table>", "")
    table_data = table_data.replace("</td>", "")
    table_data = table_data.replace("\n", "")
    table_data = table_data.split("<tr>")

    for entry in table_data:
        job_data = entry.split("<td>")
        if job_data[-1] == "Nov 06":
            link_split = job_data[4].split('"')
            
            location_split = job_data[3].replace("<details><summary><strong>", "")
            location_split = location_split.replace("</details>", " ")
            location_split = location_split.replace("</strong></summary>", "/")
            location_split = location_split.replace("<br/>", "/")
            location_split = location_split.split("/")
            
            role_title = job_data[2]
            if len(location_split) == 1:
                location_title = location_split[0]
            else:
                location_string = ""
                for i in range(1, len(location_split)):
                    if i == len(location_split) - 1:
                        location_string += location_split[i]
                    else:
                        location_string += location_split[i] + ", "
                location_title = location_string
            app_link = link_split[1]
            date_posted = job_data[5]
            
            embed = discord.Embed(title=f'{role_title}', description=f"{location_title}", color=discord.Colour.green())
            embed.add_field(name=f"Apply", value=f"{app_link}")
            embed.set_footer(text=f"{date_posted}")
            await interaction.channel.send(embed=embed)
            
    await interaction.followup.send("Finished sending")

# @tree.command(name="searchweekly", description="Search for new internship postings in the past week", guild=discord.Object(id=TEST_SERVER)) 
# async def self(interaction: discord.Interaction):
#     return

@tree.command(name="help", description="Shows commands for the bot", guild=discord.Object(id=TEST_SERVER)) 
async def self(interaction: discord.Interaction):
    embed = discord.Embed(title="Commands", description="All bot commands", color=discord.Colour.gold())
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == '__main__':
    bot.run(TOKEN)