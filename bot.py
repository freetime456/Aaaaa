import os
import asyncio
import discord
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません")


class TestBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"ログイン成功: {self.user}")


bot = TestBot()


# =========================
# /spam
# =========================

@bot.tree.command(
    name="spam",
    description="アンチスパムBotのテスト"
)
@app_commands.describe(
    count="送信回数（1〜100）"
)
async def spam(
    interaction: discord.Interaction,
    count: app_commands.Range[int, 1, 100]
):
    await interaction.response.send_message(
        f"🧪 スパム検知テスト開始！ {count}回送信します。",
        ephemeral=True
    )

    channel = interaction.channel

    if not isinstance(channel, discord.TextChannel):
        return

    for i in range(count):
        try:
            await channel.send(
                f"【SPAM TEST】テストメッセージ {i + 1}/{count}"
            )

            # Discordへの負荷を抑える
            await asyncio.sleep(0.35)

        except discord.Forbidden:
            print("メッセージ送信権限がありません")
            break

        except discord.HTTPException as e:
            print(f"Discord APIエラー: {e}")
            break

    print(
        f"[SPAM TEST] "
        f"guild={interaction.guild.id} "
        f"channel={channel.id} "
        f"count={count}"
    )


# =========================
# /test
# チャンネル名前変更テスト
# =========================

@bot.tree.command(
    name="test",
    description="チャンネル名前変更・復元テスト"
)
async def test(interaction: discord.Interaction):

    await interaction.response.send_message(
        "🧪 チャンネル変更テストを開始します。",
        ephemeral=True
    )

    channel = interaction.channel

    if not isinstance(channel, discord.TextChannel):
        return

    old_name = channel.name
    test_name = "じいちゃん様に完全降伏w"

    try:
        # 名前変更
        await channel.edit(
            name=test_name,
            reason="アンチレイドBotのテスト"
        )

        print(
            f"[CHANNEL TEST] "
            f"{old_name} -> {test_name}"
        )

        # アンチレイドBotが検知する時間を確保
        await asyncio.sleep(8)

        # アンチレイドBotが既に元へ戻していた場合は何もしない
        current_channel = interaction.guild.get_channel(channel.id)

        if current_channel is not None:
            if current_channel.name == test_name:
                await current_channel.edit(
                    name=old_name,
                    reason="チャンネル変更テストの自動復元"
                )

                print(
                    f"[CHANNEL TEST] "
                    f"{test_name} -> {old_name}"
                )
            else:
                print(
                    "[CHANNEL TEST] "
                    "アンチレイドBotが先に復元しました"
                )

    except discord.Forbidden:
        print("チャンネル管理権限がありません")

        try:
            await interaction.followup.send(
                "❌ チャンネルを変更できません。\n"
                "Botに「チャンネルの管理」権限が必要です。",
                ephemeral=True
            )
        except discord.HTTPException:
            pass

    except discord.HTTPException as e:
        print(f"Discord APIエラー: {e}")


# =========================
# 起動
# =========================

bot.run(TOKEN)
