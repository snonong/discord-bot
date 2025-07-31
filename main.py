import os
import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive
keep_alive()

# 아래는 봇 실행
import discord
# ... your bot setup and client.run(TOKEN)

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    print(f"✅ 로그인됨: {bot.user}")
    try:
        synced = await tree.sync()
        print(f"📡 동기화된 명령어: {len(synced)}개")
    except Exception as e:
        print(f"❌ 명령어 동기화 실패: {e}")


@tree.command(name="분배", description="분배 버튼을 생성합니다.")
@app_commands.describe(분배명="분배 제목", 닉네임="띄어쓰기로 구분된 이름들 (예: 철수 영희 민수)")
async def 분배(interaction: discord.Interaction, 분배명: str, 닉네임: str):
    nicknames = [n.strip() for n in 닉네임.split() if n.strip()]

    class DistributionView(discord.ui.View):
        def __init__(self, users):
            super().__init__(timeout=None)
            self.users = users
            self.clicked = set()
            self.message = None  # 나중에 메시지 저장

            for user in users:
                self.add_item(self.DistributionButton(user))

        class DistributionButton(discord.ui.Button):
            def __init__(self, user):
                super().__init__(label=user, style=discord.ButtonStyle.primary)

            async def callback(self, interaction: discord.Interaction):
                if self.disabled:
                    await interaction.response.send_message("이미 선택된 항목입니다.", ephemeral=True)
                    return

                self.disabled = True
                self.label = f"✅ {self.label}"
                self.style = discord.ButtonStyle.success
                self.view.clicked.add(self.label)

                await interaction.response.edit_message(view=self.view)

                # 모든 버튼이 클릭되었을 때 설명 변경
                if all(button.disabled for button in self.view.children):
                    embed = self.view.message.embeds[0]
                    embed.description = "분배 완료! 👍"
                    await self.view.message.edit(embed=embed, view=self.view)

    embed = discord.Embed(
        title=f"💸 {분배명}",
        description=f"버튼을 눌러 수령하세요.",
        color=0x00ff99,
    )

    view = DistributionView(nicknames)
    await interaction.response.send_message(embed=embed, view=view)
    view.message = await interaction.original_response()

keep_alive()
bot.run(TOKEN)
