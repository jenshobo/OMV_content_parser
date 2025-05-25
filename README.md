# Media Scanner with TMDb Integration and Telegram Notifications

## Overview

This Python script scans a specified folder for movies and TV series, retrieves detailed information from The Movie Database (TMDb), and sends notifications via Telegram when new items are found or processed. It supports both movies and series, including seasons for TV shows.

---

## Features

- Processes movies and TV series folders/files
- Extracts titles from filenames with cleanup
- Searches TMDb with fallback strategies
- Supports parsing season numbers from folder names for TV series
- Sends notifications to Telegram with detailed info
- Keeps track of processed items across runs

---

## Prerequisites

- Python 3.7+
- A TMDb API key (free sign-up at [TMDb API](https://www.themoviedb.org/documentation/api))
- A Telegram bot token and chat ID

---

## Setup & Installation

1. **Clone or download this repository**

2. **Install dependencies**

```bash
pip install requests
```

3. **Obtain a TMDb API key**

- Sign up at [TMDb API](https://www.themoviedb.org/documentation/api)
- Generate an API key in your account settings

4. **Create a Telegram Bot**

- Use BotFather on Telegram to create a new bot
- Save the bot token provided

5. **Get your Chat ID**

You can find your chat ID by:

- Sending a message to your bot
- Visiting this URL in your browser:

```bash
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

- Look for the `"chat":{"id":YOUR_CHAT_ID}` in the JSON response

**Alternatively**, you can use a simple, see file ``` get_chat.py ```

- Send a message to your bot first to ensure updates are received.

---

## Usage

### Command-line arguments

```bash
python your_script.py <folder_path> <seen_items_file> --type=<movie|serie>
```

- `folder_path`: Path to the folder you want to scan
- `seen_items_file`: Path to a pickle file to store processed items
- `--type`: Specify either `movie` or `serie`

### Example

```bash
python media_scanner.py /path/to/media seen.pkl --type=serie
```

---

## Configuration

At the top of the script, set your credentials:

```python
TMDB_API_KEY = 'your_tmdb_api_key_here'
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token_here'
TELEGRAM_CHAT_ID = 'your_chat_id_here'
```

---

## How it works

- Loads or creates a set of processed items
- Walks through the specified directory
- For each folder/file:
  - Checks if it has been processed
  - Cleans up the filename to extract a plausible title
  - Searches TMDb with fallbacks
  - For TV series:
    - Parses season numbers from folder names
    - Sends a message with "Seizoen {number} van {series name}"
  - For movies:
    - Sends a message about the found movie
- Saves the updated list of processed items

---

## License

This project is provided as-is. Feel free to customize and extend it.

---

## Notes

- Make sure to replace placeholder tokens and IDs with your actual credentials.
- Modify the script as needed for your specific folder structure and naming conventions.

---

## Support & Contributions

If you find bugs or want to contribute, please open an issue or a pull request.

---

**Happy media organizing!**
```
