Welcome to the documentation for Forum-Bot-Tg!
This bot is designed to create a kind of forum from a Tg channel. Participants send a post through the bot, the bot checks the content for family friendly (the check is quite weak, so I do not recommend relying on it), after which it puts the post on the queue in the channel and posts it to the channel.

Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Commands](#commands)

Installation

1. Clone the repository:
```bash
git clone https://github.com/Goldingeng/Forum-Bot-Tg.git
```

2. Go to the project directory:
```bash
cd Forum-Bot-Tg
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Configuration
1. Configure the parameters in the `config.py` file.
2. Specify the channel link in `help_markup.py`. The bot works with 2 admin chats
1) The first chat receives all posts that the bot did not miss by automatic checking, with the ability to ban the user, or skip the post to the channel
2) The second chat is a summary of posts that were posted thanks to the bot, with the ability to ban the one who posted a post bypassing the protection (the system did not detect existing violations)

Usage
Run the bot with the following command:
```bash
python main.py
```
The bot will start working and will be ready to interact via Telegram.

### Commands
- `/start` - Start the bot and a welcome message.
- `/help` - A short explanation and a link to the channel
- `/menu` - Sending a post

For all questions, contact @goldingeng in Telegram
