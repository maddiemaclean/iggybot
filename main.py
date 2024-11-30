# imports all of the libaries used in this project
import discord
from discord.ext import commands
from datetime import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Handles setting up the Google Sheets API
script_dir = os.path.dirname(os.path.abspath(__file__))

# NOTE: The below line would need to be done if I/Pidge were to leave staff/the server, see documentation on how to set up the Google Sheets API
json_file_path = os.path.join(script_dir, "extreme-ratio-443023-e1-e5b0be894908.json")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, scope)
client = gspread.authorize(creds)

# Discord Bot Setup
intents = discord.Intents.default()
bot = discord.Bot()

#Handles the IO for Google Sheets
sheetTest = client.open("IggyBot Test").sheet1
tcPreyBackend = client.open("IggyBot Test").sheet1
scPreyBackend = client.open("IggyBot Test").sheet1
rcPreyBackend = client.open("IggyBot Test").sheet1
wcPreyBackend = client.open("IggyBot Test").sheet1

# For debuging: Prints all of the spreadsheets IggyBot has access to
print("Accessible spreadsheets:")
for spreadsheet in client.openall():
    print(spreadsheet.title)

# ---- Variables ----
herbArr = {"alder-bark", "borage", "burdock-root", "burnet", "catmint", "cobwebs", "comfrey", "curly-dock", "eyebright", "feverfew", "geranium", "lavender", "marigold", "poppy-seeds", "sea-buckthorn", "tansy", "wild-garlic", "willow-bark", "yarrrow"}
waterPreyArr = {"minnow", "bitterling", "crayfish", "guppy", "loach", "eel", "carp", "goldfish", "chub", "barbel"}
wetlandPreyArr = {"newt", "frog", "salamander", "gull", "moorhen", "mallard", "beaver", "dace", "bittern", "godwit"}
airPreyArr = {"wren", "robin", "warbler", "lark", "plover", "kingfisher", "pigeon", "starling", "dove", "sparrow"}
landPreyArr = {"hedgehog", "vole", "mole", "shrew", "rabbit", "toad", "snake", "beetles", "crickets", "rat"}
foliagePreyArr = {"woodpecker", "red-squirrel", "chipmunk", "mouse", "lizard", "grey-squirrel", "bats", "pine-marten", "snake", "stoat"}
cavePreyArr = {"bats", "vole", "mole", "worm", "rabbit", "frog", "snail", "polecat", "lizard", "mouse"}
valid_sizes = {"1", "2", "4"}

# ---- Helper Methods ----

# Iternates through the selected prey/herb array and returns true of the prey/herb is in the array and false if not.
def checkType(arrIn, typeIn):
    # arrIn: the prey array(waterPreyArr, wetlandPreyArr etc) passed into the function in checkCategoryPrey
    # ypeIn: The prey_type/herbType passed into the function
    for i in arrIn:
        if i == typeIn:
            return True
    return False

# Checks to make sure the prey being submitted is a valid prey in the category.
# Ex. Prevents a minnow being submitted as air prey, or a cat's name being submitted as prey
def checkCategoryPrey(categoryIn, preyTypeIn):
    # categoryIn: The category passed into the function
    # preyTypeIn: The prey_type passed into the function

    categoryIn = categoryIn.strip().lower() # handles case senstivities for categories. Makes Land = land for example.
    preyTypeIn = preyTypeIn.strip().lower() # handles case senstivities for prey. Makes Minnow = minnow for example.
    is_valid_type = False
    if categoryIn == "land":
        is_valid_type = checkType(landPreyArr, preyTypeIn)
    elif categoryIn == "water":
        is_valid_type = checkType(waterPreyArr, preyTypeIn)
    elif categoryIn == "wetland":
        is_valid_type = checkType(wetlandPreyArr, preyTypeIn)
    elif categoryIn == "air":
        is_valid_type = checkType(airPreyArr, preyTypeIn)
    elif categoryIn == "foliage":
        is_valid_type = checkType(foliagePreyArr, preyTypeIn)
    elif categoryIn == "cave":
        is_valid_type = checkType(cavePreyArr, preyTypeIn)
    return is_valid_type


# Proccess the prey submission and does the error handling

async def process_prey_submission(ctx, data, backend):
    try:
        parts = data.split(" ", 3)
        if len(parts) < 4:
            await ctx.respond("Please provide all four fields: cat's name, category, type of prey, size.")
            return

        name, category, prey_type, size = parts
        # name: The cat's name
        # category: Whether the prey is land, air, water, wetland, foliage or cave
        # prey_type: What species the prey is, rabbit, minnow, pigeon etc)
        # size: 1 = Normal, 2 = Nat 20 or double prey channel, 4 = Nat 20 at double prey channels or Nat 20 & Favored prey found 

        # Checks to make sure the prey being submitted is a valid prey in the category.
        is_valid = checkCategoryPrey(category, prey_type)
        if not is_valid:
            await ctx.respond(f"Whoops! `{prey_type}` isn't valid `{category}` prey! Please try again.")
            return

        # checks to make sure the prey sizes are correct
        if size not in valid_sizes:
            await ctx.respond("Size must be 1, 2, or 4.")
            return

        # gets the current time and adds to the submission
        # TO DO: Make this time server time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Adds to the backend
        backend.append_row([timestamp, name, category, prey_type, size])
        await ctx.respond(f"Successfully added {name}'s {prey_type} to the freshkill pile!")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.respond("Oh no! Something went wrong. Please try again.")
        


# --- COMMANDS ----

@bot.slash_command(name="tc-add-prey", description="Submits to TC's freshkill pile")
async def tc_add_prey(ctx, data: str):
    await process_prey_submission(ctx, data, tcPreyBackend)

@bot.slash_command(name="sc-add-prey", description="Submits to SC's freshkill pile")
async def sc_add_prey(ctx, data: str):
    await process_prey_submission(ctx, data, scPreyBackend)

@bot.slash_command(name="rc-add-prey", description="Submits to RC's freshkill pile")
async def lc_add_prey(ctx, data: str):
    await process_prey_submission(ctx, data, rcPreyBackend)

@bot.slash_command(name="wc-add-prey", description="Submits to WC's freshkill pile")
async def wc_add_prey(ctx, data: str):
    await process_prey_submission(ctx, data, wcPreyBackend)

# Run the Bot
bot.run("MTMxMTEwNzI0MzczNDg2MzkzMw.GBbqap.HzKwQDJ7xYmxnvIwlfOc5KPTiG__i0DdFtQ45Y")
