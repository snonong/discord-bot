import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed, ButtonStyle
from discord.ui import View, Button
import os
from keep_alive import keep_alive

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True  # 메시지 권한이 필요한 경우
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# 환경 변수에서 토큰 가져오기
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN 환경변수가 설정되지 않았습니다.")

# 봇 준비 이벤트 - 슬래시 명령어 등록
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("✅ Slash commands synced.")

# 분배 버튼 뷰
class DistributeView(View):
    def __init__(self, user_list, original_embed, original_interaction, title):
        super().__init__(timeout=None)
        self.clicked = set()
        self.total = set(user_list)
        self.original_embed = original_embed
        self.original_interaction = original_interaction
        self.title = title

        for user in user_list:
            self.add_item(DistributeButton(label=user, parent=self))

    async def update_embed(self):
        if self.clicked == self.total:
            embed = discord.Embed(
                title=f"💰 {self.title}",
                description="분배 완료! 👍",
                color=discord.Color.green()
            )
        else:
            description = f"{' '.join(self.total)} 님에게 분배금 받아 가세요 😍"
            embed = discord.Embed(
                title=f"💰 {self.title} 분배 시작!",
                description=description,
                color=discord.Color.gold()
            )
        await self.original_interaction.edit_original_response(embed=embed, view=self)

# 버튼 정의
class DistributeButton(Button):
    def __init__(self, label, parent):
        super().__init__(label=label, style=ButtonStyle.success)
        self.parent = parent
        self.clicked = False

    async def callback(self, interaction: Interaction):
        if self.clicked:
            await interaction.response.send_message("이미 수령하셨습니다!", ephemeral=True)
            return
        self.clicked = True
        self.label = f"✅ {self.label}"
        self.disabled = True
        self.parent.clicked.add(self.label.replace("✅ ", ""))
        await self.parent.update_embed()
        await interaction.response.edit_message(view=self.parent)

# 슬래시 명령어 등록
@tree.command(name="분배", description="유물 분배용 버튼 생성")
@app_commands.describe(닉네임들="띄어쓰기로 구분된 닉네임들을 입력하세요", 제목="분배 제목을 입력하세요")
async def 분배(interaction: Interaction, 닉네임들: str, 제목: str):
    user_list = 닉네임들.split()
    embed = discord.Embed(
        title=f"💰 {제목} 분배 시작!",
        description=f"{' '.join(user_list)} 님에게 분배금 받아 가세요 😍",
        color=discord.Color.gold()
    )
    view = DistributeView(user_list, embed, interaction, 제목)
    await interaction.response.send_message(embed=embed, view=view)

# 서버 유지
keep_alive()
bot.run(TOKEN)
