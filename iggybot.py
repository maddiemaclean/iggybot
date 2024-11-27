import discord
from discord.ext import commands
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Dynamically get the file path
base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
json_file_path = os.path.join(base_dir, "extreme-ratio-443023-e1-e5b0be894908.json")

import os
from oauth2client.service_account import ServiceAccountCredentials

# Gets the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the JSON file
json_file_path = os.path.join(script_dir, "extreme-ratio-443023-e1-e5b0be894908.json")

# Define the scope for Google API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load the credentials dynamically
creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, scope)

# Google Sheets Setup
client = gspread.authorize(creds)

for spreadsheet in client.openall():
    print(spreadsheet.title)

# sheetTC = client.open("IggyBot Test").sheet1  # Open the first sheet

# Discord Bot Setup
intents = discord.Intents.default()
bot = discord.Bot()

# Variables

waterPreyArr ={"minnow", "bitterling", "crayfish", "guppy", "loach", "eel", "carp", "goldfish", "chub", "barbel"}
wetlandPreyArr = {"newt", "frog", "salamander", "gull", "moorhen", "mallard", "beaver", "dace", "bittern", "godwit"}
airPreyArr = {"wren", "robin", "warbler", "lark", "plover", "kingfisher", "pigeon", "starling", "dove", "sparrow"}
landPreyArr = {"hedgehog", "vole", "mole", "shrew", "rabbit", "toad", "snake", "beetles", "crickets", "rat"}
foliagePreyArr = {"woodpecker", "red-squrriel", "chipmunk", "mouse", "lizard", "gray-squrriel", "grey-squrriel", "bats", "pine-marten", "snake", "stoat"}
cavePreyArr = {"bats", "vole", "mole", "worm", "rabbit", "frog", "snail", "polecat", "lizard", "mouse"}

# Helper methods

def checkType(arrIn, preyIn):
    for i in arrIn:
        if i == preyIn:
            return True
    return False

# Main code

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Basic slash command for testing
@bot.slash_command(name="ping", description="Ping pong!")
async def ping(ctx):
    await ctx.respond("Pong!")

@bot.slash_command(name="add-prey", description="Add prey to the backends")
async def add_to_sheet(ctx, data: str):
    try:
        # Split the input string
        parts = data.split(" ", 3)
        if len(parts) < 4:
            await ctx.respond("Please provide all four fields: cat's name, category, type of prey, size.")
            return

        # Extract name, age, and description
        name, category, type, size = parts
        
        # Validate prey type matches category
        if category == "land":
            checkType(landPreyArr, type)
        
        elif category == "water":
            checkType(waterPreyArr, type)

        elif category == "wetland":
            checkType(wetlandPreyArr, type)

        elif category == "air":
            checkType(airPreyArr, type)

        elif category == "foliage":
            checkType(foliagePreyArr, type)
        
        elif category == "cave":
            checkType(cavePreyArr, type)

        else: 
            await ctx.respond("Whoops! {type} isn't {category} prey! Please try again")

        # Insert into Google Sheets
       # sheetTC.append_row([name, category, type, size])
        # await ctx.respond("Succesfully added {name}'s {type} to the freshkill pile!")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.respond("Oh no! Something went wrong. Please try again.")


bot.run("MTMxMTEwNzI0MzczNDg2MzkzMw.GBxBdE.dgd97l52wzMHA7krWJU50U0pskvBIH8J0Qgk7s")
