# PortalBot

A Discord bot for the Portal Speedrunning community, featuring world record tracking, time/tick conversion, community pinning, and video conversion.

## Features

| Command | Description |
|---------|-------------|
| `help++` | Display the help manual |
| `cube++` / `cube--` | Increment/decrement the cube counter (Community Contributor+) |
| `wr++` | World record archive tools |
| `wr++ search name <user>` | Search WRs by player name |
| `wr++ search category <cat>` | Search WRs by category (g, i, o, nl, nu) |
| `wr++ search year <YYYY>` | Search WRs by year |
| `time2tick++ <time>` | Convert and validate speedrun time to ticks |
| `tick2time++ <ticks>` | Convert ticks to time |
| `emergencyexit++` | Emergency shutdown (Moderator+) |

### Additional Features

- **Pinnerino** - Community-based message pinning system (📌 reaction threshold)
- **MKV to MP4** - Automatic conversion of MKV files to web-optimized MP4
- **Dox Protection** - Automatic detection and moderation of sensitive terms
- **Timeout Terms** - Auto-timeout for specific message patterns

## Installation

### Prerequisites

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) (place `ffmpeg.exe` in the project directory)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PortalBot.git
   cd PortalBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Copy `.env-example` to `.env` and fill in your values:
   ```bash
   cp .env-example .env
   ```
   
   Required variables:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   DOX_TERMS=term1,term2
   TIMEOUT_TERMS=discord.gg/,@everyone
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## Project Structure

```
PortalBot/
├── main.py              # Entry point
├── bot.py               # Main bot logic and event handlers
├── responses.py         # Response handlers and utilities
├── ticks.py             # Time/tick conversion functions
├── demoparser.py        # Demo file parsing
├── wr_archive.json      # World record database
├── cube_count.txt       # Cube counter storage
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not tracked)
├── .env-example         # Environment template
├── downloads/           # Temporary file storage
└── pinnerino/           # Pin system storage
```

## WR Categories

| Code | Full Name |
|------|-----------|
| `g` | Glitchless |
| `i` | Inbounds |
| `o` | Out of Bounds |
| `nl` | NoSLA Legacy |
| `nu` | NoSLA Unrestricted |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

- Discord: @valoix
- Website: [valoix.com](https://valoix.com/)

## License

This project is provided as-is for the Portal Speedrunning community.
