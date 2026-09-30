import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"ログイン成功: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"スラッシュコマンド同期: {len(synced)}個")
    except Exception as e:
        print(f"同期エラー: {e}")


@bot.tree.command(
    name="spam",
    description="自分のサーバーでスパム検知をテストします"
)
@app_commands.describe(
    count="送信する回数"
)
async def spam(
    interaction: discord.Interaction,
    count: app_commands.Range[int, 1, 100]
):
    # 管理者限定
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 管理者のみ使用できます。",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"🧪 スパム検知テスト開始！ {count}回送信します。",
        ephemeral=True
    )

    channel = interaction.channel

    if channel is None:
        return

    test_message = "【SPAM TEST】じいちゃん様に完全降伏w"

    for i in range(count):
        try:
            await channel.send(test_message)

            # 連投しすぎないよう少し待つ
            await asyncio.sleep(0.3)

        except discord.Forbidden:
            print("メッセージ送信権限がありません")
            break

        except discord.HTTPException as e:
            print(f"Discord APIエラー: {e}")
            break

    try:
        await channel.send(
            f"🧪 スパム検知テスト終了！ {count}回送信しました。",
            delete_after=5
        )
    except Exception:
        pass


bot.run(TOKEN)import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"ログイン成功: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"スラッシュコマンド同期: {len(synced)}個")
    except Exception as e:
        print(f"同期エラー: {e}")


@bot.tree.command(
    name="spam",
    description="自分のサーバーでスパム検知をテストします"
)
@app_commands.describe(
    count="送信する回数"
)
async def spam(
    interaction: discord.Interaction,
    count: app_commands.Range[int, 1, 100]
):
    # 管理者限定
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ 管理者のみ使用できます。",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"🧪 スパム検知テスト開始！ {count}回送信します。",
        ephemeral=True
    )

    channel = interaction.channel

    if channel is None:
        return

    test_message = "【SPAM TEST】じいちゃん様に完全降伏w"

    for i in range(count):
        try:
            await channel.send(test_message)

            # 連投しすぎないよう少し待つ
            await asyncio.sleep(0.3)

        except discord.Forbidden:
            print("メッセージ送信権限がありません")
            break

        except discord.HTTPException as e:
            print(f"Discord APIエラー: {e}")
            break

    try:
        await channel.send(
            f"🧪 スパム検知テスト終了！ {count}回送信しました。",
            delete_after=5
        )
    except Exception:
        pass


bot.run(TOKEN)
