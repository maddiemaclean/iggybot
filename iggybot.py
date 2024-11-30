import discord
from discord.ext import commands
from datetime import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
script_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(script_dir, "extreme-ratio-443023-e1-e5b0be894908.json")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, scope)
client = gspread.authorize(creds)
sheetTC = client.open("IggyBot Test").sheet1

print("Accessible spreadsheets:")
for spreadsheet in client.openall():
    print(spreadsheet.title)


# Discord Bot Setup
intents = discord.Intents.default()
bot = discord.Bot()

# Variables
waterPreyArr = {"minnow", "bitterling", "crayfish", "guppy", "loach", "eel", "carp", "goldfish", "chub", "barbel"}
wetlandPreyArr = {"newt", "frog", "salamander", "gull", "moorhen", "mallard", "beaver", "dace", "bittern", "godwit"}
airPreyArr = {"wren", "robin", "warbler", "lark", "plover", "kingfisher", "pigeon", "starling", "dove", "sparrow"}
landPreyArr = {"hedgehog", "vole", "mole", "shrew", "rabbit", "toad", "snake", "beetles", "crickets", "rat"}
foliagePreyArr = {"woodpecker", "red-squirrel", "chipmunk", "mouse", "lizard", "grey-squirrel", "bats", "pine-marten", "snake", "stoat"}
cavePreyArr = {"bats", "vole", "mole", "worm", "rabbit", "frog", "snail", "polecat", "lizard", "mouse"}
valid_sizes = {"1", "2", "4"}

# Helper Methods
def checkType(arrIn, preyIn):
    preyIn = preyIn.strip().lower()
    for i in arrIn:
        if i == preyIn:
            return True
    return False

# Event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Commands

@bot.slash_command(name="add-prey", description="Add prey to the backends")
async def add_to_sheet(ctx, data: str):
    try:
        parts = data.split(" ", 3)
        if len(parts) < 4:
            await ctx.respond("Please provide all four fields: cat's name, category, type of prey, size.")
            return

        #Error handling for prey category and type (can't submit a fish as air prey, can't submit a fox as water prey)
        name, category, prey_type, size = parts
        is_valid_type = False
        if category == "land":
            is_valid_type = checkType(landPreyArr, prey_type)
        elif category == "water":
            is_valid_type = checkType(waterPreyArr, prey_type)
        elif category == "wetland":
            is_valid_type = checkType(wetlandPreyArr, prey_type)
        elif category == "air":
            is_valid_type = checkType(airPreyArr, prey_type)
        elif category == "foliage":
            is_valid_type = checkType(foliagePreyArr, prey_type)
        elif category == "cave":
            is_valid_type = checkType(cavePreyArr, prey_type)

        if not is_valid_type:
            await ctx.respond(f"Whoops! `{prey_type}` isn't valid `{category}` prey! Please try again.")
            return

        #Error handing for prey sizes
        if size not in valid_sizes:
            await ctx.respond("Size must be 1, 2, or 4.")
            return

        # Gets the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Puts data into google sheets
        sheetTC.append_row([timestamp ,name, category, prey_type, size])

        #returns success to the user in discord
        await ctx.respond(f"Successfully added {name}'s {prey_type} to the freshkill pile!")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.respond("Oh no! Something went wrong. Please try again.")

# Run the Bot
