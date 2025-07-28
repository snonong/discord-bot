import os
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

# 환경 변수에서 토큰 불러오기
TOKEN = os.getenv("DISCORD_TOKEN")

# 봇 intents 설정
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 슬래시 명령어 등록용 tree
tree = bot.tree

# 봇 준비 완료 시 출력
@bot.event
async def on_ready():
    print(f"{bot.user} 로 로그인됨.")
    try:
        synced = await tree.sync()
        print(f"{len(synced)}개의 명령어가 등록됨.")
    except Exception as e:
        print(f"명령어 동기화 실패: {e}")

# /분배 명령어
@tree.command(name="분배", description="분배 버튼을 생성합니다.")
@app_commands.describe(분배명="예: 성수, 헤일로 등", 닉네임="띄어쓰기로 구분된 이름들 (예: 철수 영희 민수)")
async def 분배(interaction: discord.Interaction, 분배명: str, 닉네임: str):
    user_list = [name.strip() for name in 닉네임.split(",")]

    # 버튼 뷰 생성
    class DistributionView(discord.ui.View):
        def __init__(self, users):
            super().__init__(timeout=None)
            self.clicked_users = set()
            for user in users:
                self.add_item(self.DistributionButton(user))

        class DistributionButton(discord.ui.Button):
            def __init__(self, user):
                super().__init__(label=user, style=discord.ButtonStyle.primary, custom_id=f"btn_{user}")

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    await interaction.response.send_message("이미 분배 완료된 버튼입니다.", ephemeral=True)
                    return

                self.disabled = True
                self.label += " ✔"
                self.style = discord.ButtonStyle.secondary
                await interaction.response.edit_message(view=self.view)

                # 모든 버튼이 비활성화되었는지 확인
                if all(item.disabled for item in self.view.children):
                    await interaction.followup.send("✅ **분배 완료!**", ephemeral=False)

    embed = discord.Embed(
        title=f"💸 {분배명} 분배",
        description="아래 버튼을 눌러 분배금을 수령하세요!",
        color=0x00ff99
    )
    await interaction.response.send_message(embed=embed, view=DistributionView(user_list))

# 웹서버 유지용
keep_alive()

# 봇 실행
bot.run(TOKEN)
