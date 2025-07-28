import os
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")

# Intents 설정
intents = discord.Intents.default()
intents.message_content = True

# Bot 및 Tree 초기화
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# 봇 실행 시 동기화
@bot.event
async def on_ready():
    print(f"✅ {bot.user} 로 로그인됨.")
    try:
        synced = await tree.sync()
        print(f"🌐 {len(synced)}개의 명령어가 동기화됨.")
    except Exception as e:
        print(f"❌ 명령어 동기화 실패: {e}")


# /분배 명령어 정의
@tree.command(name="분배", description="분배 버튼을 생성합니다.")
@app_commands.describe(분배명="예: 성수, 헤일로 등", 닉네임="쉼표(,)로 구분된 이름들 (예: 철수,영희,민수)")
async def 분배(interaction: discord.Interaction, 분배명: str, 닉네임: str):
    user_list = [name.strip() for name in 닉네임.split(",") if name.strip()]

    class DistributionView(discord.ui.View):
        def __init__(self, users):
            super().__init__(timeout=300)  # 5분 타임아웃
            for user in users:
                self.add_item(self.DistributionButton(user))

        class DistributionButton(discord.ui.Button):
            def __init__(self, user):
                super().__init__(label=user, style=discord.ButtonStyle.primary, custom_id=f"btn_{user}")

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    await interaction.response.send_message("⚠ 이미 클릭된 버튼입니다.", ephemeral=True)
                    return

                self.disabled = True
                self.label += " ✔"
                self.style = discord.ButtonStyle.secondary

                try:
                    await interaction.response.edit_message(view=self.view)
                except discord.NotFound:
                    return  # 메시지가 삭제되었거나 응답 타이밍 문제

                if all(item.disabled for item in self.view.children):
                    await interaction.followup.send("✅ **분배 완료**", ephemeral=False)

    embed = discord.Embed(
        title=f"💸 {분배명} 분배",
        description="버튼을 눌러 분배금을 수령하세요!",
        color=0x00ff99
    )

    await interaction.response.send_message(embed=embed, view=DistributionView(user_list))


# 웹서버 유지용 함수 실행
keep_alive()

# 봇 실행
bot.run(TOKEN)
