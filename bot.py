import os
import io
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MTU1MzMzNDM5MTE5ODE5NTg0Mw.GLosFp.GU9gQiBtFL44cCByKNx9qctEBrU2dMacXY4deg") 
PREFIX = "."
MAX_SIZE_MB = 15          # Safe limit (change later if you have Nitro)
MAX_SIZE = MAX_SIZE_MB * 1024 * 1024

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------- Basic detection ----------
def detect_obfuscator(code: str) -> str:
    code_lower = code.lower()
    if "ironbrew" in code_lower or "ib2" in code_lower or "getfenv" in code_lower and "bytecode" in code_lower:
        return "IronBrew / IronBrew2"
    if "luraph" in code_lower or "lph_" in code_lower or "lph%" in code_lower:
        return "Luraph"
    if "prometheus" in code_lower or "wearedevs" in code_lower:
        return "Prometheus / WeAreDevs"
    return "Unknown / Generic"

# ---------- Very basic cleanup (placeholder for real deobfuscation) ----------
def basic_cleanup(code: str) -> str:
    # Remove some common junk comments
    code = re.sub(r"--\[\[.*?\]\]", "", code, flags=re.DOTALL)
    code = re.sub(r"--.*", "", code)
    # Normalize whitespace a bit
    code = re.sub(r"\n{3,}", "\n\n", code)
    return code.strip() + "\n"

# ---------- Main command ----------
@bot.command(name="deobf")
async def deobf(ctx: commands.Context):
    """Deobfuscate Lua code. Attach a .lua/.txt file or paste code after the command."""
    
    code = None
    filename = "input.lua"

    # 1. Check for attachment
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        if attachment.size > MAX_SIZE:
            await ctx.reply(f"❌ File too large. Max allowed: **{MAX_SIZE_MB} MB**")
            return
        if not attachment.filename.lower().endswith((".lua", ".txt", ".luau")):
            await ctx.reply("❌ Please upload a `.lua`, `.luau` or `.txt` file.")
            return
        try:
            data = await attachment.read()
            code = data.decode("utf-8", errors="ignore")
            filename = attachment.filename
        except Exception as e:
            await ctx.reply(f"❌ Failed to read attachment: `{e}`")
            return

    # 2. Check for code in message content
    else:
        content = ctx.message.content
        # Remove the command itself
        content = content[len(PREFIX + "deobf"):].strip()
        if content.startswith("```"):
            # Remove markdown code blocks
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
            content = re.sub(r"\n?```$", "", content)
        if len(content) > 10:
            code = content
            filename = "pasted.lua"
        else:
            await ctx.reply(
                "❌ Please either:\n"
                "• Attach a `.lua` / `.txt` file, **or**\n"
                "• Paste the code after `!deobf`"
            )
            return

    if not code or len(code.strip()) < 5:
        await ctx.reply("❌ Empty or invalid code.")
        return

    # Process
    await ctx.reply("🔍 Detecting obfuscator and cleaning...")

    detected = detect_obfuscator(code)
    cleaned = basic_cleanup(code)

    # Prepare result file
    result = (
        f"-- Detected: {detected}\n"
        f"-- Original size: {len(code)} bytes\n"
        f"-- Cleaned size: {len(cleaned)} bytes\n"
        f"-- Note: This is currently basic cleanup only.\n"
        f"-- Advanced IronBrew / Luraph / Prometheus support coming next.\n\n"
        f"{cleaned}"
    )

    file = discord.File(
        fp=io.BytesIO(result.encode("utf-8")),
        filename=f"deobfuscated_{filename}"
    )

    await ctx.reply(
        f"✅ Done!\n**Detected:** `{detected}`\n"
        f"Result attached below (basic cleanup for now).",
        file=file
    )

@bot.command(name="ping")
async def ping(ctx):
    await ctx.reply(f"Pong! Latency: `{round(bot.latency * 1000)}ms`")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN not set!")
    else:
        bot.run(MTU1MzMzNDM5MTE5ODE5NTg0Mw.GLosFp.GU9gQiBtFL44cCByKNx9qctEBrU2dMacXY4deg)
