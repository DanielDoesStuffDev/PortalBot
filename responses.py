"""
PortalBot Response Handlers

This module contains helper functions for:
- Cube count management
- Dox detection
- Message formatting and utilities
- Console colored output
"""

import os
from dotenv import load_dotenv

load_dotenv()

DOX_TERMS = os.getenv("DOX_TERMS", "").split(",") if os.getenv("DOX_TERMS") else []

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_PATH = os.getenv("BASE_PATH", os.path.dirname(os.path.abspath(__file__)))
CUBE_COUNT_PATH = f"{BASE_PATH}/cube_count.txt"
P1SR_SERVER_ID = "305456639530500096"
PRIVILEGED_ROLES = ["Community contributor", "SRC verifier", "Moderation Team", "Admin"]

# Category display names
CATEGORY_NAMES = {
    "g": "Glitchless",
    "nl": "NoSLA Legacy",
    "nu": "NoSLA Unrestricted",
    "i": "Inbounds",
    "o": "Out of Bounds"
}


# =============================================================================
# CUBE COUNT HANDLERS
# =============================================================================

def get_cube_count():
    """Read current cube count from file."""
    with open(CUBE_COUNT_PATH, "r") as f:
        return int(f.read().strip())


def set_cube_count(count):
    """Write cube count to file."""
    with open(CUBE_COUNT_PATH, "w") as f:
        f.write(str(count))


def handle_response(user_data, message):
    """
    Process cube++ and cube-- commands.
    
    Args:
        user_data: Discord message object containing author and guild info
        message: The message content string
    
    Returns:
        Response string if command was handled, False otherwise
    """
    try:
        message_server_id = str(user_data.guild.id)
    except:
        return False
    
    if message_server_id != P1SR_SERVER_ID:
        return False
    
    # Check for privileged role
    has_permission = any(str(role) in PRIVILEGED_ROLES for role in user_data.author.roles)
    if not has_permission:
        return False
    
    if message == "cube++":
        count = get_cube_count() + 1
        set_cube_count(count)
        return f"So many cubes! I've now seen {count} cubes!"
    
    if message == "cube--":
        count = get_cube_count() - 1
        set_cube_count(count)
        return f"I was mistaken, cube rescinded. I've now seen only {count} cubes!"
    
    return False


# =============================================================================
# DOX DETECTION
# =============================================================================

def text_dox_blox(message):
    """
    Check if message contains any dox terms.
    
    Args:
        message: String to check
    
    Returns:
        True if dox term found, False otherwise
    """
    for term in DOX_TERMS:
        if term and term in message:
            return True
    return False


def name_dox_blox(username):
    """
    Check if username contains any dox terms.
    
    Args:
        username: Username string to check
    
    Returns:
        True if dox term found, False otherwise
    """
    for term in DOX_TERMS:
        if term and term in username:
            return True
    return False


# =============================================================================
# WR FORMATTING UTILITIES
# =============================================================================

def process_wr_category(category):
    """
    Convert category code to full name.
    
    Args:
        category: Short category code (g, nl, nu, i, o)
    
    Returns:
        Full category name string
    """
    return CATEGORY_NAMES.get(category.lower(), category)


def process_wr_output(raw_wr_search):
    """
    Format a raw WR search line for display.
    
    Args:
        raw_wr_search: Space-separated string: "name category time date link"
    
    Returns:
        Formatted string for display
    """
    parts = raw_wr_search.strip().split()
    
    if len(parts) < 5:
        return raw_wr_search
    
    wr_name = parts[0]
    wr_category = process_wr_category(parts[1])
    wr_time = parts[2]
    wr_date = parts[3]
    wr_link = parts[4]
    
    return f"[{wr_date}] {wr_name.capitalize()} {wr_category} {wr_time} {wr_link}"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def generate_message_link(server_id, channel_id, message_id):
    """
    Generate a Discord message URL.
    
    Args:
        server_id: Discord server/guild ID
        channel_id: Discord channel ID
        message_id: Discord message ID
    
    Returns:
        Full Discord message URL
    """
    return f"https://discord.com/channels/{server_id}/{channel_id}/{message_id}"


# =============================================================================
# CONSOLE OUTPUT
# =============================================================================

def print_colour(colour, text):
    """
    Format text with ANSI color codes for console output.
    
    Args:
        colour: Color code - "R" (red), "G" (green), "B" (blue)
        text: Text to colorize
    
    Returns:
        ANSI-formatted string
    """
    colours = {
        "R": "\033[31m",  # Red
        "G": "\033[32m",  # Green
        "B": "\033[34m",  # Blue
    }
    reset = "\033[0m"
    
    colour_code = colours.get(colour.upper(), "")
    return f"{colour_code}{text}{reset}"


def print_error(code):
    """
    Get formatted error message by code.
    
    Args:
        code: Error code string (e.g., "301")
    
    Returns:
        Red-colored error message
    """
    error_codes = {
        "000": "Error 000: Unclassified Error",
        "201": "Error 201: ESC sequence found in message.",
        "301": "Error 301: Dox Detected in message.",
        "302": "Error 302: Dox Detected in name.",
        "303": "Error 303: Dox Detected in image.",
        "304": "Error 304: Ping Detected in message.",
        "305": "Error 305: Timeout Term in message.",
    }
    
    message = error_codes.get(code, f"Error {code}: Unknown error")
    return print_colour("R", message)
