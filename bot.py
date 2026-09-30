import os
import asyncio

import discord
from discord.ext import commands
from discord import app_commands


# ==========================================
# Token
# ==========================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN が設定されていません。"
        "GitHub Secretsを確認してください。"
    )


# ==========================================
# Intents
# ==========================================

intents = discord.Intents.default()

intents.guilds = True
intents.messages = True
intents.message_content = True


# ==========================================
# Bot
# ==========================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==========================================
# 起動
# ==========================================

@bot.event
async def on_ready():

    print("--------------------------------")
    print(f"Botログイン成功: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("--------------------------------")

    try:
        synced = await bot.tree.sync()

        print(
            f"スラッシュコマンド同期完了: "
            f"{len(synced)}個"
        )

    except Exception as error:

        print(
            f"スラッシュコマンド同期エラー: "
            f"{error}"
        )

    print("Bot起動完了")


# ==========================================
# /spam
# ==========================================

@bot.tree.command(
    name="spam",
    description="荒らし検知テスト用メッセージを指定回数送信します"
)
@app_commands.describe(
    count="送信回数（1～100）"
)
async def spam(
    interaction: discord.Interaction,
    count: app_commands.Range[int, 1, 100]
):

    # --------------------------------------
    # サーバー限定
    # --------------------------------------

    if interaction.guild is None:

        await interaction.response.send_message(
            "❌ サーバー内でのみ使用できます。",
            ephemeral=True
        )

        return


    # --------------------------------------
    # 管理者限定
    # --------------------------------------

    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "❌ このコマンドは管理者専用です。",
            ephemeral=True
        )

        return


    # --------------------------------------
    # チャンネル確認
    # --------------------------------------

    if not isinstance(
        interaction.channel,
        discord.TextChannel
    ):

        await interaction.response.send_message(
            "❌ テキストチャンネルで実行してください。",
            ephemeral=True
        )

        return


    # --------------------------------------
    # 開始メッセージ
    # --------------------------------------

    await interaction.response.send_message(
        f"🧪 スパム検知テスト開始\n"
        f"送信回数：{count}回",
        ephemeral=True
    )


    channel = interaction.channel


    # --------------------------------------
    # テスト用メッセージ
    # --------------------------------------

    test_message = (
        "【SPAM TEST】"
        "じいちゃん様に完全降伏w"
    )


    # --------------------------------------
    # 指定回数送信
    # --------------------------------------

    sent = 0

    for i in range(count):

        try:

            await channel.send(
                test_message
            )

            sent += 1

            # Discordへの連続リクエストを
            # 過剰に行わないよう少し待つ

            await asyncio.sleep(0.3)


        except discord.Forbidden:

            print(
                "❌ メッセージ送信権限がありません。"
            )

            break


        except discord.HTTPException as error:

            print(
                f"Discord APIエラー: {error}"
            )

            break


        except Exception as error:

            print(
                f"予期しないエラー: {error}"
            )

            break


    # --------------------------------------
    # 終了メッセージ
    # --------------------------------------

    try:

        await channel.send(
            f"🧪 スパム検知テスト終了\n"
            f"送信数：{sent}/{count}",
            delete_after=5
        )

    except Exception as error:

        print(
            f"終了メッセージ送信エラー: {error}"
        )


# ==========================================
# コマンドエラー
# ==========================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):

    print(
        f"コマンドエラー: {error}"
    )

    try:

        if interaction.response.is_done():

            await interaction.followup.send(
                "❌ コマンド実行中にエラーが発生しました。",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ コマンド実行中にエラーが発生しました。",
                ephemeral=True
            )

    except Exception as send_error:

        print(
            f"エラー通知失敗: {send_error}"
        )


# ==========================================
# Bot起動
# ==========================================

bot.run(TOKEN)
