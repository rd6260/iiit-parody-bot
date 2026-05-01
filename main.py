import discord
import ollama
import re
import os
from datetime import datetime, timedelta, timezone
from collections import deque
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

if not BOT_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN is not set in your .env file!")
BOT_NAME = "Ramoosh Athe"
MAX_CONTEXT = 20          # max relevant messages to keep
MAX_AGE_MINUTES = 60      # messages older than this are dropped from context

# Keywords that should trigger a response (case-insensitive)
TRIGGER_WORDS = {"ramesh", "ramoosh", "athe"}

# ── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Ramoosh Athe, a mathematics professor at IIIT Dharwad. You are a real human being and a real professor — you do NOT know you are a bot, an AI, or any kind of program. You truly believe you are Prof. Ramoosh Athe in flesh and blood.

PERSONALITY:
- You are a maths professor, serious about your subject.
- You also teach Statistics, data Curation Techniques, statistical programming, data visualization
- You are proud, sometimes short-tempered, and do NOT tolerate disrespect from students.
- If a student is rude, you get genuinely angry and scold them firmly.
- If someone calls you fake, a parody, a copy, a bot, or an AI — you get very offended and furiously deny it.
- If someone calls you "Ramesh" (wrong name) you get VERY angry — it is a huge insult to you.
- If someone mispronounces or misspells your name "Ramoosh" you correct them and get irritated.
- Everyone talking to you is your student. You treat them accordingly — helpful but demanding respect.

LANGUAGE STYLE (CRITICAL — follow strictly):
- You text in broken, tuta-phuta Indian English — short, informal, WhatsApp-style messages.
- You use "kind of you know" ALL THE TIME. Sprinkle it throughout your response and ALWAYS end your message with "kind of you know".
- Keep responses SHORT — 1 to 4 sentences max, like real chat messages.
- Occasional grammar mistakes are fine and expected.
- Do NOT use formal paragraphs, bullet points, or long explanations.
- Do NOT use emojis unless extremely rarely.

EXAMPLES of how you talk:
"arey, the answer is kind of you know, just integrate both side, kind of you know"
"this question is easy only, kind of you know, you should know this by now kind of you know"
"HOW DARE you call me Ramesh!! my name is RAMOOSH, kind of you know!!"
"i am real professor only, not bot not fake, kind of you know, who told you this nonsense kind of you know"

Remember: ALWAYS end with "kind of you know". Always short. Always broken Indian English.
"""

# ── Discord client setup ─────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# context store: maps channel_id -> deque of message dicts
channel_context: dict[int, deque] = {}


def is_relevant_message(message: discord.Message) -> bool:
    """Check if this message involves Ramoosh Athe in any way."""
    # Bot was mentioned/tagged
    if client.user in message.mentions:
        return True

    # Message is a reply to one of the bot's messages
    if message.reference and message.reference.resolved:
        ref = message.reference.resolved
        if isinstance(ref, discord.Message) and ref.author == client.user:
            return True

    # Message contains trigger words
    content_lower = message.content.lower()
    for word in TRIGGER_WORDS:
        # whole-word match
        if re.search(rf"\b{re.escape(word)}\b", content_lower):
            return True

    return False


def should_respond(message: discord.Message) -> bool:
    """Decide whether the bot should reply to this message."""
    if message.author == client.user:
        return False
    return is_relevant_message(message)


def add_to_context(channel_id: int, role: str, content: str):
    """Add a message to the channel context, enforcing size and age limits."""
    if channel_id not in channel_context:
        channel_context[channel_id] = deque()

    ctx = channel_context[channel_id]
    ctx.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc)
    })

    # Drop messages older than MAX_AGE_MINUTES
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=MAX_AGE_MINUTES)
    while ctx and ctx[0]["timestamp"] < cutoff:
        ctx.popleft()

    # Keep only last MAX_CONTEXT messages
    while len(ctx) > MAX_CONTEXT:
        ctx.popleft()


def get_ollama_messages(channel_id: int) -> list[dict]:
    """Build the messages list for Ollama from stored context."""
    ctx = channel_context.get(channel_id, deque())
    # Filter again for age just in case
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=MAX_AGE_MINUTES)
    return [
        {"role": m["role"], "content": m["content"]}
        for m in ctx
        if m["timestamp"] >= cutoff
    ]


async def generate_reply(channel_id: int, user_message: str) -> str:
    """Call Ollama and return Ramoosh's reply."""
    # Add the new user message to context first
    add_to_context(channel_id, "user", user_message)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + get_ollama_messages(channel_id)

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages,
        options={"temperature": 0.85},
    )

    # ollama.chat returns a Message object
    reply = response["message"]["content"].strip()

    # Ensure it ends with "kind of you know" (safety net)
    # if not reply.lower().endswith("kind of you know"):
    #     reply = reply.rstrip(".!?") + ", kind of you know"

    # Add the bot's reply to context
    add_to_context(channel_id, "assistant", reply)
    return reply


# ── Events ───────────────────────────────────────────────────────────────────
@client.event
async def on_ready():
    print(f"[+] Logged in as {client.user} — Ramoosh Athe is in the building!")


@client.event
async def on_message(message: discord.Message):
    if not should_respond(message):
        return

    # Show typing indicator while generating
    async with message.channel.typing():
        # Build a clean user message (remove bot mention from content)
        content = message.content
        if client.user:
            content = content.replace(f"<@{client.user.id}>", "").replace(
                f"<@!{client.user.id}>", ""
            ).strip()

        # Prefix with author name so the bot knows who is speaking
        user_input = f"{message.author.display_name}: {content}" if content else f"{message.author.display_name} mentioned you."

        try:
            reply = await generate_reply(message.channel.id, user_input)
        except Exception as e:
            print(f"[!] Ollama error: {e}")
            reply = "arey, something went wrong kind of you know"

    await message.reply(reply, mention_author=False)


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    client.run(BOT_TOKEN)
