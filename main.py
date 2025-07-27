import os
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive  # 웹 서버 실행

# 디스코드 봇 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

# View 클래스: 버튼 묶음
class MultiSelectButton(discord.ui.View):
    def __init__(self, labels: list[str], author_id: int):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.selected = []
        self.total = len(labels)

        for label in labels:
            self.add_item(NameButton(label=label, author_id=author_id, parent=self))

# 버튼 하나의 동작
class NameButton(discord.ui.Button):
    def __init__(self, label: str, author_id: int, parent: MultiSelectButton):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.author_id = author_id
        self.parent = parent

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ 이 버튼은 명령어 작성자만 클릭할 수 있어요.", ephemeral=True)
            return

        self.disabled = True
        self.style = discord.ButtonStyle.success
        self.label = f"✅ {self.label}"
        self.parent.selected.append(self.label)

        # 모든 버튼을 눌렀을 때 메시지 수정
        if len(self.parent.selected) == self.parent.total:
            embed = discord.Embed(
                title="💰 분배 완료!",
                description="모든 분배가 완료되었습니다! 👍",
                color=0x00ff00
            )
            await interaction.message.edit(embed=embed, view=self.parent)
        else:
            await interaction.message.edit(view=self.parent)

# 슬래시 명령어 정의
@tree.command(name="분배", description="분배명과 닉네임들을 입력하면 버튼이 생성됩니다.")
@app_commands.describe(분배명="예: 성수, 헤일로 등", 닉네임="띄어쓰기로 구분된 이름들 (예: 철수 영희 민수)")
async def 분배(interaction: discord.Interaction, 분배명: str, 닉네임: str):
    labels = 닉네임.strip().split()
    if not labels:
        await interaction.response.send_message("❗ 이름을 하나 이상 입력해주세요.", ephemeral=True)
        return

    if len(labels) > 25:
        await interaction.response.send_message("❗ 최대 25개까지 입력할 수 있습니다.", ephemeral=True)
        return

    view = MultiSelectButton(labels, interaction.user.id)
    embed = discord.Embed(
        title=f"💰 **{분배명}** 분배 시작!",
        description=f"**{interaction.user.display_name}** 님에게 분배금 받아 가세요 😍",
        color=0xfcd34d
    )
    await interaction.response.send_message(embed=embed, view=view)

# 봇 실행 시 슬래시 명령어 등록
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ 봇 실행됨: {bot.user}")

# 🔽 Flask 웹서버 실행 (repl.dev 주소 대응용)
keep_alive()

# 🔽 디스코드 토큰으로 봇 실행
bot.run(os.getenv("DISCORD_TOKEN"))
