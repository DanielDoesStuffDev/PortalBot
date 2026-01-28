"""
PortalBot - Discord Bot for Portal Speedrunning Community

Color Codes for Console Output:
    RED   = Error
    GREEN = Success
    BLUE  = Process/Info
"""

import discord
import responses
from discord.ext import commands
from discord.utils import get
import ticks
import os
from moviepy import *
import random
import demoparser
from zipfile import ZipFile
import datetime
import json
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# CONFIGURATION
# =============================================================================

# File paths - Set BASE_PATH in .env or defaults to script directory
BASE_PATH = os.getenv("BASE_PATH", os.path.dirname(os.path.abspath(__file__)))
PINNERINO_PATH = f"{BASE_PATH}/pinnerino"
DOWNLOADS_PATH = f"{BASE_PATH}/downloads"
WR_ARCHIVE_PATH = f"{BASE_PATH}/wr_archive.json"
CUBE_COUNT_PATH = f"{BASE_PATH}/cube_count.txt"

# Discord channel IDs
PIN_CHANNEL_ID = 1192784040634351757
WR_CHANNEL_ID = 1174320230386901023
MOD_LOG_CHANNEL_ID = 778521955435413514

# Server configuration
P1SR_SERVER_ID = "305456639530500096"
REACTION_PIN_THRESHOLD = 10

# Role permissions
PRIVILEGED_ROLES = ["Community contributor", "SRC verifier", "Moderation Team", "Admin"]

# Security terms from environment
DOX_TERMS = os.getenv("DOX_TERMS", "").split(",") if os.getenv("DOX_TERMS") else []
TIMEOUT_TERMS = os.getenv("TIMEOUT_TERMS", "").split(",") if os.getenv("TIMEOUT_TERMS") else []


def check_timeout_terms(message):
    """Check if message contains any timeout terms."""
    for term in TIMEOUT_TERMS:
        if term and term in message:
            return True, term
    return False, ""


def get_dox_terms():
    """Get list of dox terms from environment."""
    return DOX_TERMS


# Category mappings for WR archive
CATEGORY_ALIASES = {
    "glitchless": "g", "gless": "g", "g": "g",
    "noslal": "nl", "nl": "nl",
    "noslau": "nu", "nu": "nu",
    "inbounds": "i", "inb": "i", "i": "i",
    "oob": "o", "o": "o"
}

CATEGORY_FULL_NAMES = {
    "g": "Glitchless",
    "nl": "NoSLA Legacy",
    "nu": "NoSLA Unrestricted",
    "i": "Inbounds",
    "o": "Out of Bounds"
}


# =============================================================================
# WR ARCHIVE FUNCTIONS (JSON-based)
# =============================================================================

def load_wr_archive():
    """Load the WR archive from JSON file."""
    try:
        with open(WR_ARCHIVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(responses.print_colour("R", f"JSON parse error: {e}"))
        return []


def save_wr_archive(records):
    """Save the WR archive to JSON file."""
    with open(WR_ARCHIVE_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)


def add_wr_record(name, category, time, date, link):
    """Add a new WR record to the archive."""
    normalized_category = CATEGORY_ALIASES.get(category.lower(), category.lower())
    
    records = load_wr_archive()
    records.append({
        "name": name,
        "category": normalized_category,
        "time": time,
        "date": date,
        "link": link
    })
    save_wr_archive(records)
    print(responses.print_colour("G", "WR record added successfully"))


def search_wr_by_name(name):
    """Search WR archive by player name."""
    records = load_wr_archive()
    return [r for r in records if r["name"].lower() == name.lower()]


def search_wr_by_category(category):
    """Search WR archive by category."""
    normalized = CATEGORY_ALIASES.get(category.lower(), category.lower())
    records = load_wr_archive()
    return [r for r in records if r["category"].lower() == normalized]


def search_wr_by_year(year):
    """Search WR archive by year."""
    records = load_wr_archive()
    return [r for r in records if r["date"].endswith(year) or r["date"][-4:] == year[-4:]]


def format_wr_record(record):
    """Format a single WR record for display."""
    category_name = CATEGORY_FULL_NAMES.get(record["category"], record["category"])
    return f"[{record['date']}] {record['name'].capitalize()} {category_name} {record['time']} {record['link']}"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def has_privileged_role(member):
    """Check if a member has any privileged role."""
    return any(str(role) in PRIVILEGED_ROLES for role in member.roles)


def sanitize_mentions(content):
    """Replace @ mentions with safe versions."""
    return content.replace("@", "@ ") if "@" in content else content


def contains_ping(text):
    """Check if text contains a ping attempt."""
    return "@" in text


async def send_message(message, user_message):
    """Send a response if one is generated."""
    try:
        response = responses.handle_response(message, user_message)
        if response:
            await message.channel.send(response)
    except Exception as e:
        print(responses.print_colour("R", f"Error sending message: {e}"))


# =============================================================================
# PINNERINO HANDLER
# =============================================================================

async def handle_pin_reaction(client, payload):
    """Handle the pin reaction workflow."""
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    reaction = get(message.reactions, emoji=payload.emoji.name)
    
    if not reaction or reaction.count != REACTION_PIN_THRESHOLD:
        return
    
    # Check if already pinned
    pinned_ids_path = f"{PINNERINO_PATH}/pinnerino_message_ids.txt"
    try:
        with open(pinned_ids_path, "r") as f:
            if any(str(message.id) == line.strip() for line in f):
                return
    except FileNotFoundError:
        pass
    
    # Record the message ID
    with open(pinned_ids_path, "a") as f:
        f.write(f"{message.id}\n")
    
    # Prepare and send the pin
    pin_channel = client.get_channel(PIN_CHANNEL_ID)
    content = sanitize_mentions(str(message.content))
    pin_embed = discord.Embed(
        title=str(message.author).capitalize(),
        description=content,
        color=0xFF0000
    )
    message_link = responses.generate_message_link(message.guild.id, message.channel.id, message.id)
    
    # Handle different attachment types
    if message.attachments:
        attachment = message.attachments[0]
        filename = attachment.filename
        
        if filename.endswith(".mp4"):
            save_path = f"{PINNERINO_PATH}/pinnerino.mp4"
        else:
            save_path = f"{PINNERINO_PATH}/pinnerino.jpg"
        
        await attachment.save(save_path)
        await pin_channel.send(embed=pin_embed)
        await pin_channel.send(file=discord.File(save_path))
        await pin_channel.send(message_link)
    
    elif "https://tenor.com/view/" in message.content or ".gif" in message.content:
        pin_embed.description = "SENT GIF"
        await pin_channel.send(embed=pin_embed)
        await pin_channel.send(message.content)
        await pin_channel.send(message_link)
    
    else:
        await pin_channel.send(embed=pin_embed)
        await pin_channel.send(message_link)


# =============================================================================
# VIDEO CONVERSION HANDLER
# =============================================================================

async def handle_mkv_conversion(message, filename):
    """Convert MKV files to MP4 format."""
    try:
        await message.channel.send("Converting to MP4...")
        
        input_path = f"{DOWNLOADS_PATH}/input_video.mkv"
        output_path = f"{DOWNLOADS_PATH}/output_video.mp4"
        resized_path = f"{DOWNLOADS_PATH}/resized_output_video.mp4"
        
        # Download the file
        print(responses.print_colour("B", "Downloading Video..."))
        await message.attachments[0].save(input_path)
        print(responses.print_colour("G", "Downloaded"))
        
        # Rename to MP4 (container change)
        print(responses.print_colour("B", "Converting to MP4..."))
        os.rename(input_path, output_path)
        
        # Determine resolution based on file size
        clip = VideoFileClip(output_path)
        file_size = os.path.getsize(output_path)
        print(responses.print_colour("B", f"{file_size} bytes"))
        
        if file_size > 30000000:
            print(responses.print_colour("B", "Converting to 240p"))
            resized_clip = clip.resized(width=427, height=240)
        elif file_size > 20000000:
            print(responses.print_colour("B", "Converting to 480p"))
            resized_clip = clip.resized(width=854, height=480)
        else:
            print(responses.print_colour("B", "Converting to 720p"))
            resized_clip = clip.resized(width=1280, height=720)
        
        resized_clip.write_videofile(resized_path)
        clip.close()
        print(responses.print_colour("G", "Converted Successfully"))
        
        await message.channel.send("Converted Successfully!", file=discord.File(resized_path))
        
        # Cleanup
        os.remove(output_path)
        os.remove(resized_path)
        
    except Exception as e:
        print(responses.print_colour("R", str(e)))
        await message.channel.send("Something went wrong!!! :((")
        # Cleanup on error
        for path in [f"{DOWNLOADS_PATH}/input_video.mkv", 
                     f"{DOWNLOADS_PATH}/output_video.mp4",
                     f"{DOWNLOADS_PATH}/resized_output_video.mp4"]:
            try:
                os.remove(path)
            except:
                pass


# =============================================================================
# WR COMMAND HANDLERS
# =============================================================================

async def handle_wr_help(message):
    """Display WR command help."""
    await message.channel.send("""
**wr++ Help Manual**

**Usage:**
`wr++ search name <username>` - Search WR archive for runs by a certain user.
`wr++ search category <inb, noslal, noslau, oob, gless>` - Search WR archive for all WRs in a category.
`wr++ search year <YYYY>` - Search WR archive for runs done in that year.

**Examples:**                                                 
`wr++ search name Msushi` - Retreives all of Msushi's WRs
`wr++ search category inb` - Retreives all Inbounds WRs
`wr++ search year 2022` - Get WRs done in 2022

**Notes:**
- Each category have their respective short hands to make the command easier to type. (i, nl, nu, o, g)
- Contact Valoix for wr++ moderation commands
- Results include WR name, category, time, date and message link
""")


async def handle_wr_search(message, args):
    """Handle WR search commands."""
    if len(args) < 4:
        await message.channel.send("Invalid search format. Use `wr++ help` for usage.")
        return
    
    search_type = args[2].lower()
    search_term = args[3]
    
    # Perform search based on type
    if search_type == "name":
        await message.channel.send(f"Searching for name {search_term}...")
        results = search_wr_by_name(search_term)
    elif search_type == "category":
        await message.channel.send(f"Searching for category {search_term}...")
        results = search_wr_by_category(search_term)
    elif search_type == "year":
        await message.channel.send(f"Searching for year {search_term}...")
        results = search_wr_by_year(search_term)
    else:
        await message.channel.send("Invalid search type. Use `wr++ help` for usage.")
        return
    
    if not results:
        await message.channel.send("No results found. Use `wr++ help` for more information :)")
        return
    
    # Format results (split into chunks to avoid Discord message limits)
    output_1 = ""
    output_2 = ""
    
    for record in results:
        formatted = format_wr_record(record) + "\n"
        if len(output_1) < 1700:
            output_1 += formatted
        else:
            output_2 += formatted
    
    await message.author.send(f"**WR ARCHIVE SEARCH FOR '{search_term}'**\n{output_1}")
    if output_2:
        await message.author.send(output_2)
    await message.channel.send("Finished! Found WRs will be sent to your DMs :)")


async def handle_wr_post(client, message, args):
    """Handle posting a new WR (privileged users only)."""
    if not has_privileged_role(message.author):
        return
    
    if len(args) < 6:
        await message.channel.send("Invalid format. Expected: wr++ <name> <category> <time> <date> <link>")
        return
    
    try:
        # Parse arguments
        wr_name = args[1]
        wr_category = args[2].lower()
        wr_time = args[3]
        wr_date = args[4]
        wr_link = args[5]
        
        # Validate category
        if wr_category not in CATEGORY_ALIASES:
            await message.channel.send(f"Invalid category. Valid options: {', '.join(CATEGORY_ALIASES.keys())}")
            return
        
        # Try to download the attached image
        wr_image_path = f"{DOWNLOADS_PATH}/wr.jpg"
        try:
            await message.attachments[0].save(wr_image_path)
        except:
            responses.print_colour("R", "No Image Attached")
            await message.channel.send("Please attach an image with the WR!")
            return
        
        # Get full category name for the announcement
        normalized_category = CATEGORY_ALIASES[wr_category]
        category_name = CATEGORY_FULL_NAMES[normalized_category]
        
        # Post to WR channel
        wr_channel = client.get_channel(WR_CHANNEL_ID)
        announcement = (
            f"[{wr_date}] {wr_name.capitalize()} just got a World Record "
            f"{category_name} run in {wr_time}! Congratulations :tada: {wr_link}"
        )
        await wr_channel.send(announcement, file=discord.File(wr_image_path))
        
        # Add to archive
        add_wr_record(wr_name, wr_category, wr_time, wr_date, wr_link)
        
    except Exception as e:
        print(responses.print_colour("R", str(e)))
        await message.channel.send("Oops! Something went wrong :(. Please contact developer for more information!")


async def handle_wr_command(client, message, user_message):
    """Main WR command router."""
    if contains_ping(user_message):
        print(responses.print_error("304"))
        return
    
    args = user_message.split()
    
    if len(args) < 2:
        await message.channel.send("Use `wr++ help` for usage information.")
        return
    
    subcommand = args[1].lower()
    
    if subcommand == "help":
        await handle_wr_help(message)
    elif subcommand == "search":
        await handle_wr_search(message, args)
    else:
        # Assume it's a WR post command: wr++ <name> <category> <time> <date> <link>
        await handle_wr_post(client, message, args)


# =============================================================================
# MAIN BOT
# =============================================================================

def run_discord_bot():
    """Initialize and run the Discord bot."""
    
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        """Called when the bot successfully connects."""
        activity = discord.Game(name="Get started with help++!")
        await client.change_presence(status=discord.Status.online, activity=activity)
        print(f"{client.user} is now running!")

    @client.event
    async def on_raw_reaction_add(payload):
        """Handle reactions for pin functionality."""
        if payload.emoji.name == "📌":
            await handle_pin_reaction(client, payload)

    @client.event
    async def on_message(message):
        """Handle incoming messages."""
        # Ignore self
        if message.author == client.user:
            return
        
        # Ignore ANSI escape sequences (ESC character is \x1b)
        if "\x1b" in message.content:
            print(responses.print_error("201"))
            return
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        try:
            message_server_id = str(message.guild.id)
        except:
            message_server_id = "0"
        
        # =================================================================
        # SECURITY CHECKS
        # =================================================================
        
        # Check for dox in message
        if responses.text_dox_blox(user_message):
            print(responses.print_error("301"))
            await message.author.ban(reason="Potential Dox Detected")
            await message.delete()
            return
        
        # Check for dox in username
        if responses.name_dox_blox(username):
            print(responses.print_error("302"))
            await message.author.ban(reason="Potential Dox Detected")
            await message.delete()
            return
        
        # Check for timeout terms
        has_timeout, timeout_term = check_timeout_terms(user_message)
        if has_timeout:
            try:
                print(responses.print_error("305"))
                print(message.author)
                timeout_until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
                await message.author.timeout(timeout_until, reason="Timeout Term Detected in message")
                await message.delete()
                mod_channel = client.get_channel(MOD_LOG_CHANNEL_ID)
                await mod_channel.send(f"Timed out {message.author.mention} for `{timeout_term}`")
            except:
                print(responses.print_colour("R", "Timeout Failed (Likely missing permissions)"))
        
        # =================================================================
        # COMMANDS
        # =================================================================
        
        lower_message = user_message.lower()
        
        # Emergency Exit (P1SR server only, privileged users)
        if user_message == "emergencyexit++" and message_server_id == P1SR_SERVER_ID:
            if has_privileged_role(message.author):
                await message.channel.send("Shutting Down...")
                exit()
        
        # Help Manual
        if lower_message.startswith("help++"):
            await message.channel.send("""
**Help Manual**

`help++` - Displays this help manual
`cube++` - Increments cube count (Community Contributor+ Only)
`cube--` - Decrements cube count (Community Contributor+ Only)
`wr++` - Tools for the WR archive *[WIP]*
`time2tick++ <time>` - Converts + Validates time to ticks
`tick2time++ <ticks>` - Converts ticks to time
`emergencyexit++` - Shuts down the bot (Moderator Only)
""")
        
        # Easter egg: 4104 reaction
        if "4104" in user_message:
            if random.randint(1, 10) == 1:
                print(responses.print_colour("B", "4104 easter egg triggered!"))
                await message.add_reaction("<:no4104:1180929144977117364>")
        
        # DM Command (Valoix only)
        if lower_message.startswith("dm++") and str(message.author) == "valoix":
            try:
                parts = user_message.split()
                user_id = int(parts[1])
                content = " ".join(parts[2:])
                target_user = await client.fetch_user(user_id)
                
                print(responses.print_colour("B", f"DM to {target_user} ({user_id}): {content}"))
                await target_user.send(content)
                print(responses.print_colour("G", "DM Sent!"))
            except Exception as e:
                print(responses.print_error("000"))
                print(responses.print_colour("R", str(e)))
        
        # Tick to Time Conversion
        if lower_message.startswith(("tick2time++", "ticks2time++", "tk2tm++")):
            parts = user_message.split()
            print(responses.print_colour("B", str(parts)))
            
            if len(parts) < 2:
                await message.reply("Please provide a tick count!")
                return
            
            if contains_ping(parts[1]):
                print(responses.print_error("304"))
                return
            
            try:
                result = ticks.tick_to_time(parts[1])
                await message.reply(result)
            except:
                await message.reply(f'Your ticks "{parts[1]}" was not a valid tick count, please try again!')
        
        # Time to Tick Conversion
        if lower_message.startswith(("time2tick++", "time2ticks++", "tm2tk++")):
            parts = user_message.split()
            print(responses.print_colour("B", str(parts)))
            
            if len(parts) < 2:
                await message.reply("Please provide a time!")
                return
            
            if contains_ping(parts[1]):
                print(responses.print_error("304"))
                return
            
            try:
                result = ticks.time_to_tick(parts[1])
                await message.reply(result)
            except:
                await message.reply(f'Your time "{parts[1]}" was not a valid time, please try again!')
        
        # =================================================================
        # ATTACHMENT HANDLING
        # =================================================================
        
        try:
            if message.attachments:
                filename = message.attachments[0].filename
                
                # MKV to MP4 conversion
                if filename.endswith(".mkv"):
                    await handle_mkv_conversion(message, filename)
                
                print(f"{username}: '{user_message}' [{channel}] with ({message.attachments})")
        except:
            pass
        
        # =================================================================
        # WR COMMAND
        # =================================================================
        
        if user_message.startswith("wr++"):
            try:
                await handle_wr_command(client, message, user_message)
            except Exception as e:
                print(responses.print_colour("R", str(e)))
                await message.channel.send("i no no wanna :(")
        
        # Log message
        if not message.attachments:
            print(f"{username}: '{user_message}' [{channel}]")
        
        # Handle other responses
        await send_message(message, user_message)

    client.run(os.getenv("DISCORD_TOKEN"))
