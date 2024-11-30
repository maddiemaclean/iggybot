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
tcHerbBackend = client.open("IggyBot Test").sheet1
scHerbBackend = client.open("IggyBot Test").sheet1
rcHerbBackend = client.open("IggyBot Test").sheet1
wcHerbBackend = client.open("IggyBot Test").sheet1

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
    # typeIn: The prey_type/herbType passed into the function
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

# Checks if we are adding or removing herbs
def checkAddRemove(add_remove_in):
    add_remove_in = add_remove_in.strip().lower()  # Handle case sensitivity
    if add_remove_in == "add" or add_remove_in == "adding":
        return "Adding"
    elif add_remove_in == "remove" or add_remove_in == "removing":
        return "Removing"
    else:
        return "fail"

@bot.event
async def on_ready():
    await bot.sync_commands()
    print(f"Logged in as {bot.user}")


# Proccess the prey submission and does the error handling
async def process_prey_submission(ctx, data, backend):
    try:
        parts = data.split(" ", 3)
        if len(parts) != 4:
            await ctx.respond("Please provide all four fields: cat's name, category, type of prey, size. Remember two word prey need to have a dash in the middle ex. owlscreech foliage red-squirrel")
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
        
# Proccess the prey submission and does the error handling

async def process_herb_submission(ctx, data, backend):
    try:
        parts = data.split(" ", 3)
        if len(parts) != 4:
            await ctx.respond("Please provide all four fields: cat's name, adding or removing, herb, amount. Remember two word herbs need to have a dash in the middle ex. lunarlynx add willow-bark 8")
            return

        name, add_remove, herb_type, amount = parts
        # name: The cat's name
        # add_remove: Whether you are adding or removing herbs
        # herb_type: What herb you are submitting (catmint, alder-bark etc.)
        # amount: how much is being added or removed

        add_remove_flag = checkAddRemove(add_remove)
        if add_remove_flag == "fail":
            await ctx.respond(f"Whoops! Make sure to use add/adding or remove/removing as the second input of your command. Please try again.")
            return

        is_valid = checkType(herbArr, herb_type)
        if not is_valid:
            await ctx.respond(f"Whoops! `{herb_type}` isn't an herb! Please try again.")
            return

        # gets the current time and adds to the submission
        # TO DO: Make this time server time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Adds to the backend
        backend.append_row([timestamp, name, add_remove_flag, herb_type, amount])
        if add_remove_flag == "Adding":
            await ctx.respond(f"Successfully added {name}'s {amount} {herb_type} to the herb stores!")
        else:
            await ctx.respond(f"Successfully removed {amount} {herb_type} to from herb stores!")

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
async def rc_add_prey(ctx, data: str):
    await process_prey_submission(ctx, data, rcPreyBackend)

@bot.slash_command(name="wc-add-prey", description="Submits to WC's freshkill pile")
async def wc_add_prey(ctx, data: str):
    await process_prey_submission(ctx, data, wcPreyBackend)

@bot.slash_command(name="tc-herbs", description="Submits to TC's herb stores")
async def tc_herbs(ctx, data: str):
    await process_herb_submission(ctx, data, tcHerbBackend)

@bot.slash_command(name="sc-herbs", description="Submits to SC's herb stores")
async def sc_herbs(ctx, data: str):
    await process_herb_submission(ctx, data, scHerbBackend)

@bot.slash_command(name="rc-herbs", description="Submits to RC's herb stores")
async def rc_herbs(ctx, data: str):
    await process_herb_submission(ctx, data, rcHerbBackend)

@bot.slash_command(name="wc-herbs", description="Submits to WC's herb stores")
async def wc_herbs(ctx, data: str):
    await process_herb_submission(ctx, data, wcHerbBackend)

# Run the Bot
bot.run("MTMxMTEwNzI0MzczNDg2MzkzMw.GBIXMn.UcNHuXE2rzOa57L34tyR5CXXz8xgA_ImJYhwog")
