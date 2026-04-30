# 🎓 IIIT Dharwad Parody Bot

A Discord parody bot for IIIT Dharwad, powered by [Ollama](https://ollama.com) running `llama3.1:8b` locally. The bot impersonates a professor and is completely unaware he's a bot, texts in broken Indian English, and ends every single message with *"kind of you know"*.

> ⚠️ This is a parody project made for fun within our college community. Not affiliated with IIIT Dharwad officially.


## ✨ Features

- **Responds when mentioned/tagged**
- **Responds to replies** on any of his messages
- **Keyword triggers** — reacts to any message containing his name
- **Sliding context window** — remembers up to the last 20 relevant messages per channel
- **1-hour memory expiry** — messages older than 60 minutes are dropped from context
- **Fully local** — runs on Ollama, no OpenAI or cloud API needed
- **Stays in character** — gets angry if called fake, a bot, or real name of this professor


## 🚀 Setup & Running

### Edit `.env`:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
OLLAMA_MODEL=llama3.1:8b
```


### Run

```bash
python main.py
```


## ⚙️ Configuration

All tuneable constants are at the top of `main.py`:

| Variable | Default | Description |
|---|---|---|
| `MAX_CONTEXT` | `20` | Max relevant messages kept in memory per channel |
| `MAX_AGE_MINUTES` | `60` | Messages older than this are evicted from context |
| `TRIGGER_WORDS` | `ramesh, ramoosh, athe` | Keywords that wake the bot up |


## 🤖 Bot Behaviour

| Trigger | Responds? |
|---|---|
| `@RamooshAthe` mention | ✅ Yes |
| Reply to bot's message | ✅ Yes |
| Message contains `ramoosh` / `ramesh` / `athe` | ✅ Yes |
| Random unrelated message | ❌ No |

### Character Rules

- Speaks in short, broken Indian English (WhatsApp-style)
- Uses **"kind of you know"** constantly — always ends with it
- Gets **very angry** if called "Ramesh" (wrong name)
- Gets **offended** if called a bot, fake, or parody
- Treats everyone as a student and demands respect


## 📦 Dependencies

```
discord.py>=2.3.0
ollama>=0.2.0
python-dotenv>=1.0.0
```


## 📝 TODO

- [ ] He randomly asks course questions? And insults if u don't get it right



*"this project is kind of you know, for fun only, kind of you know"*





