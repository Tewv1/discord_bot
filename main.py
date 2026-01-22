import discord
import os
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import json, os, random, string

from myserver import server_on

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ---------- UTIL ----------
def load_keys():
    with open("keys.json", "r") as f:
        return json.load(f)

def save_keys(data):
    with open("keys.json", "w") as f:
        json.dump(data, f, indent=4)

def generate_key():
    return "RANK-" + "-".join(
        "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        for _ in range(2)
    )

# ---------- MODAL ----------
class RedeemModal(Modal):
    def __init__(self, program):
        super().__init__(title=f"Redeem Key - {program}")
        self.program = program
        self.key = TextInput(label="Redeem Key", placeholder="RANK-XXXX-XXXX")
        self.add_item(self.key)

    async def on_submit(self, interaction: discord.Interaction):
        keys = load_keys()
        key = self.key.value

        if key not in keys[self.program]:
            await interaction.response.send_message("❌ Key ไม่ถูกต้อง", ephemeral=True)
            return

        if keys[self.program][key]:
            await interaction.response.send_message("⚠️ Key ถูกใช้ไปแล้ว", ephemeral=True)
            return

        keys[self.program][key] = True
        save_keys(keys)

        await interaction.response.send_message(
            f"✅ Redeem สำเร็จสำหรับ **{self.program}**",
            ephemeral=True
        )

# ---------- SELECT ----------
class ProgramSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="SUPERRANK1", description="Key สำหรับ SuperRank1"),
            discord.SelectOption(label="HYBRID", description="Key สำหรับ Hybrid"),
            discord.SelectOption(label="NOVA", description="Key สำหรับ Nova"),
            discord.SelectOption(label="SPECIAL", description="Key สำหรับ Special CMD"),
            discord.SelectOption(label="CLEANER", description="Key สำหรับ Cleaner")
        ]
        super().__init__(placeholder="เลือกโปรแกรมที่ต้องการกรอกคีย์", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RedeemModal(self.values[0]))

class RedeemView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProgramSelect())

# ---------- GEN KEY ----------
class GenSelect(Select):
    def __init__(self):
        options = [discord.SelectOption(label=p) for p in load_keys().keys()]
        super().__init__(placeholder="เลือกโปรแกรมที่จะสร้าง Key", options=options)

    async def callback(self, interaction: discord.Interaction):
        keys = load_keys()
        program = self.values[0]
        new_key = generate_key()
        keys[program][new_key] = False
        save_keys(keys)

        await interaction.response.send_message(
            f"🔑 Key ใหม่ ({program})\n`{new_key}`",
            ephemeral=True
        )

class GenView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(GenSelect())

# ---------- SLASH COMMAND ----------
@bot.tree.command(name="redeem", description="Redeem Key")
async def redeem(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔐 ระบบ Redeem Key รวม",
        description=(
            "📌 เลือกโปรแกรมจากเมนูด้านล่าง\n"
            "📌 กรอก Redeem Key\n"
            "📌 ระบบ Redeem ให้อัตโนมัติ"
        ),
        color=0xff0000
    )
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/XXXXXXXX/banner.png"
    )

    await interaction.response.send_message(
        embed=embed,
        view=RedeemView()
    )

@bot.tree.command(name="genkey", description="สร้าง Redeem Key (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def genkey(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔑 Generate Redeem Key",
        description="เลือกโปรแกรมด้านล่าง",
        color=0xff0000
    )
    await interaction.response.send_message(
        embed=embed,
        view=GenView(),
        ephemeral=True
    )

# ---------- READY ----------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online: {bot.user}")

server_on()


bot.run(os.getenv('TOKEN'))