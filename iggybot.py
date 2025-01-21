# imports all of the libaries used in this project
import discord
from discord.ext import commands
from datetime import datetime
import pytz
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
tcPreyBackend = client.open("ThunderClan Prey").sheet1
scPreyBackend = client.open("ShadowClan Prey").sheet1
rcPreyBackend = client.open("RiverClan Prey").sheet1
wcPreyBackend = client.open("WindClan Prey").sheet1
tcHerbBackend = client.open("ThunderClan Herb Storage Backend").sheet1
scHerbBackend = client.open("ShadowClan Herb Storage Backend").sheet1
rcHerbBackend = client.open("RiverClan Herb Storage Backend").sheet1
wcHerbBackend = client.open("WindClan Herb Storage Backend").sheet1

# For debuging: Prints all of the spreadsheets IggyBot has access to
print("Accessible spreadsheets:")
for spreadsheet in client.openall():
    print(spreadsheet.title)

# ---- Variables ----
herbArr = {"alder bark", "borage", "burdock root", "burnet", "catmint", "cobwebs", "comfrey", "curly dock", "eyebright", "feverfew", "geranium", "lavender", "marigold","poppy seeds", "sea buckthorn", "tansy","wild garlic", "willow bark", "yarrow"}
waterPreyArr = {"minnow", "bitterling", "crayfish", "guppy", "loach", "eel", "carp", "goldfish", "chub", "barbel"}
wetlandPreyArr = {"newt", "frog", "salamander", "gull", "moorhen", "mallard", "beaver", "dace", "bittern", "godwit"}
airPreyArr = {"wren", "robin", "warbler", "lark", "plover", "kingfisher", "pigeon", "starling", "dove", "sparrow"}
landPreyArr = {"hedgehog", "vole", "mole", "shrew", "rabbit", "toad", "snake", "beetles", "crickets", "rat"}
foliagePreyArr = {"woodpecker", "chipmunk", "mouse", "lizard", "grey squirrel", "bats", "pine marten", "snake", "stoat", "red squirrel"}
cavePreyArr = {"bats", "vole", "mole", "worm", "rabbit", "frog", "snail", "polecat", "lizard", "mouse"}
valid_sizes = {"1", "2", "4", "8"}
categories = {"water", "wetland", "air", "land", "foliage","cave"}

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

# Ensures the formatting is correct for the Sheets Backends
def format(wordIn):
    # wordIn: The word that we want to format
    wordIn = wordIn.strip().lower()  # Handle case sensitivity

    #handles the edge cases for spelling herb/prey type (i.e makes willowbark = Willow Bark or gray-squirrel = Grey Squirrel)
    if wordIn == "alderbark" or wordIn == "alder-bark":
        formatted = "Alder Bark"
    elif wordIn == "cobweb":
        formatted = "Cobwebs"
    elif wordIn == "burdockroot" or wordIn == "burdock-root":
        formatted = "Burdock Root"
    elif wordIn == "curlydock" or wordIn == "curly-dock":
        formatted = "Curly Dock"
    elif wordIn == "poppyseeds" or wordIn == "poppyseed" or wordIn == "poppy-seeds" or wordIn == "poppy-seed":
        formatted = "Poppy Seeds"
    elif wordIn == "seabuckthorn" or wordIn == "sea-buckthorn":
        formatted = "Sea Buckthorn"
    elif wordIn == "wildgarlic" or wordIn == "wild-garlic":
        formatted = "Wild Garlic"
    elif wordIn == "willowbark" or wordIn == "willow-bark":
        formatted = "Willow Bark"
    elif wordIn == "bat":
        formatted = "Bats"
    elif wordIn == "beetle":
        formatted = "Beetles"
    elif wordIn == "cricket":
        formatted = "Crickets"
    elif wordIn == "greysquirrel" or wordIn == "graysquirrel" or wordIn == "grey-squirrel" or wordIn == "gray-squirrel":
        formatted = "Grey Squirrel"
    elif wordIn == "pinemarten" or wordIn == "pine-marten":
        formatted = "Pine Marten"
    elif wordIn == "redsquirrel" or wordIn == "red-squirrel":
        formatted = "Red Squirrel"
    else:
        formatted = wordIn.title()
    return formatted

def capitalize(input_string):
    if not input_string:
        return input_string
    return input_string[0].upper() + input_string[1:]

# For debugging, ensures we have access to the bot
@bot.event
async def on_ready():
    await bot.sync_commands()
    print(f"Logged in as {bot.user}")


# Proccess the prey submission and does the error handling
async def process_prey_submission(ctx, name, category, prey_type, size, backend):
    # ctx: Contains information about the slash command invocation, like which user issued it and in what channel.
    # name: The cat's name
    # category: Whether the prey is land, air, water, wetland, foliage, or cave
    # prey_type: What species the prey is, e.g., rabbit, minnow, pigeon
    # size: 1 = Normal, 2 = Nat 20 or double prey channel, 4 = Nat 20 at double prey channels or Nat 20 & favored prey found
    # backend: The backend where the submission will be written

    try:
        # Checks to make sure the category is valid
        category = category.strip().lower()
        if category not in categories:
            category = capitalize(category)
            await ctx.respond(f"{ctx.author.mention} :meat_on_bone:  **Freshkill Pile Submission** :meat_on_bone: ```Whoops! {category} isn't a valid category. Please try again.```")
            return
        # Checks to make sure the prey being submitted is a valid prey in the category.
        prey_type = format(prey_type)
        is_valid = checkCategoryPrey(category, prey_type)
        if not is_valid:
            prey_type = capitalize(prey_type)
            await ctx.respond(f"{ctx.author.mention} :meat_on_bone:  **Freshkill Pile Submission** :meat_on_bone: ```Whoops! {prey_type} isn't valid {category} prey! Please try again.```")
            return

        # checks to make sure the prey sizes are correct
        if size not in valid_sizes:
            await ctx.respond(f"{ctx.author.mention} :meat_on_bone:  **Freshkill Pile Submission** :meat_on_bone: ```Whoops! Size must be 1,2,4 or . Please try again.```")
            return

        # gets the current time in EST and adds to the submission
        est = pytz.timezone('US/Eastern')
        timestamp = datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")

        # handles formatting for the backend code
        name = format(name)
        size = int(size)

        # Adds to the backend
        backend.append_row([timestamp, name, category, prey_type, size])
        await ctx.respond(f"{ctx.author.mention} :meat_on_bone:  **Freshkill Pile Submission** :meat_on_bone: ```Successfully added {name}'s {prey_type} to the freshkill pile!```")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.respond(f"{ctx.author.mention} :meat_on_bone:  **Freshkill Pile Submission** :meat_on_bone: ```Oh no! Something went wrong. Please try again.```")
        
# Proccess the prey submission and does the error handling

async def process_herb_addition(ctx, name, herb_type, amount, backend):
    # ctx: Contains information about the slash command invocation, like which user issued it and in what channel.
    # name: The cat's name
    # herb_type: What herb you are submitting (catmint, alder-bark etc.)
    # amount: how much is being added or removed
    # backend: which backend the submission will be written to
    try:
        # does the error handing to make sure the herb submiited is an actual herb
        herb_type = format(herb_type).strip().lower()
        is_valid = checkType(herbArr, herb_type)

        if not is_valid:
            herb_type = capitalize(herb_type)
            await ctx.respond(f"{ctx.author.mention} :herb: **Herb Storage Submission** :herb: ```Whoops! {herb_type} isn't an herb! Please try again.```")
            return

        # gets the current time in EST and adds to the submission
        est = pytz.timezone('US/Eastern')
        timestamp = datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")

        # handles formatting for the backend code
        herb_type = format(herb_type)
        name = format(name)
        amount = int(amount)
        
        # Adds to the backend
        backend.append_row([timestamp, name, "Adding" , herb_type, amount])
        await ctx.respond(f"{ctx.author.mention} :herb: **Herb Storage Submission** :herb: ```Successfully added {name}'s {amount} {herb_type} to herb stores!```")

    # throws an exception for misc errors
    except Exception as e:
        print(f"Error: {e}")
        await ctx.respond(f"{ctx.author.mention} :herb: **Herb Storage Submission** :herb: ```Oh no! Something went wrong. Please try again.```")

async def process_herb_removal(ctx, name, herb_type, amount, backend):
    # ctx: Contains information about the slash command invocation, like which user issued it and in what channel.
    # name: The cat's name
    # herb_type: What herb you are submitting (catmint, alder-bark etc.)
    # amount: how much is being added or removed
    # backend: which backend the submission will be written to
    try:
       
        # does the error handing to make sure the herb submiited is an actual herb
        herb_type = format(herb_type).strip().lower()
        is_valid = checkType(herbArr, herb_type)

        if not is_valid:
            herb_type = capitalize(herb_type)
            await ctx.respond(f"{ctx.author.mention} :herb: **Herb Storage Submission** :herb: ```Whoops! {herb_type} isn't an herb! Please try again.```")
            return

        # gets the current time in EST and adds to the submission
        est = pytz.timezone('US/Eastern')
        timestamp = datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")

        # handles formatting for the backend code
        herb_type = format(herb_type)
        name = format(name)
        amount = int(amount)
        
        # Adds to the backend
        backend.append_row([timestamp, name, "Removing",  herb_type, amount])
        await ctx.respond(f"{ctx.author.mention} :herb: **Herb Storage Submission** :herb: ```Successfully removed {name}'s {amount} {herb_type} from herb stores!```")

    # throws an exception for misc errors
    except Exception as e:
        print(f"Error: {e}")
        await ctx.respond(f"{ctx.author.mention} :herb: **Herb Storage Submission** :herb: ```Oh no! Something went wrong. Please try again.```")

# --- COMMANDS ----

@bot.slash_command(name="tc-add-prey", description="Submits to TC's freshkill pile")
async def tc_add_prey(ctx, name: str, category: str, prey_type: str, size: str):
    await process_prey_submission(ctx, name, category, prey_type, size, tcPreyBackend)

@bot.slash_command(name="sc-add-prey", description="Submits to SC's freshkill pile")
async def sc_add_prey(ctx, name: str, category: str, prey_type: str, size: str):
    await process_prey_submission(ctx, name, category, prey_type, size, scPreyBackend)

@bot.slash_command(name="rc-add-prey", description="Submits to RC's freshkill pile")
async def rc_add_prey(ctx, name: str, category: str, prey_type: str, size: str):
    await process_prey_submission(ctx, name, category, prey_type, size, rcPreyBackend)

@bot.slash_command(name="wc-add-prey", description="Submits to WC's freshkill pile")
async def wc_add_prey(ctx, name: str, category: str, prey_type: str, size: str):
    await process_prey_submission(ctx, name, category, prey_type, size, wcPreyBackend)

@bot.slash_command(name="tc-add-herbs", description="Submits to TC's herb stores")
async def tc_herbs(ctx, name: str, herb_type: str, amount: int):
    await process_herb_addition(ctx, name, herb_type, amount, tcHerbBackend)

@bot.slash_command(name="sc-add-herbs", description="Submits to SC's herb stores")
async def sc_herbs(ctx, name: str, herb_type: str, amount: int):
    await process_herb_addition(ctx, name, herb_type, amount, scHerbBackend)

@bot.slash_command(name="rc-add-herbs", description="Submits to RC's herb stores")
async def rc_herbs(ctx, name: str, herb_type: str, amount: int):
    await process_herb_addition(ctx, name, herb_type, amount, rcHerbBackend)

@bot.slash_command(name="wc-add-herbs", description="Submits to WC's herb stores")
async def wc_herbs(ctx, name: str, herb_type: str, amount: int):
    await process_herb_addition(ctx, name, herb_type, amount, wcHerbBackend)

@bot.slash_command(name="tc-remove-herbs", description="Removes from TC's herb stores")
async def tc_herbs(ctx, name: str, herb_type: str, amount: int):
    await process_herb_removal(ctx, name, herb_type, amount, tcHerbBackend)

@bot.slash_command(name="sc-remove-herbs", description="Removes from SC's herb stores")
async def sc_herbs(ctx, name: str, herb_type: str, amount: int):
    await process_herb_removal(ctx, name, herb_type, amount, scHerbBackend)

@bot.slash_command(name="rc-remove-herbs", description="Removes from RC's herb stores")
async def rc_herbs(ctx, name: str, herb_type: str, amount: int):
    await process_herb_removal(ctx, name, herb_type, amount, rcHerbBackend)

@bot.slash_command(name="wc-remove-herbs", description="Submits from WC's herb stores")
async def wc_herbs(ctx, name: str, herb_type: str, amount: int):
    await process_herb_removal(ctx, name, herb_type, amount, wcHerbBackend)

# Run the Bot
bot.run("token")
