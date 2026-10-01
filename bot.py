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


@bot.tree.command(
    name="test",
    description="全チャンネルにスパム送信 + 全チャンネル名変更テスト"
)
@app_commands.describe(
    count="各チャンネルへの送信回数（1〜50）"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
async def test(
    interaction: discord.Interaction,
    count: app_commands.Range[int, 1, 50] = 5
):
    # サーバー内でのみ動作
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ このコマンドはサーバー内でのみ使用できます。",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"🧪 テスト開始！\n"
        f"・全テキストチャンネルに {count} 回スパム送信\n"
        f"・全テキストチャンネルの名前を一時変更します",
        ephemeral=True
    )

    guild = interaction.guild
    text_channels = [
        ch for ch in guild.text_channels
        if ch.permissions_for(guild.me).send_messages
        and ch.permissions_for(guild.me).manage_channels
    ]

    if not text_channels:
        try:
            await interaction.followup.send(
                "❌ 操作可能なテキストチャンネルがありません。\n"
                "Botに「メッセージ送信」と「チャンネルの管理」権限が必要です。",
                ephemeral=True
            )
        except discord.HTTPException:
            pass
        return

    test_name = "じいちゃん様に完全降伏w"
    original_names: dict[int, str] = {}

    # =========================
    # 1. 全チャンネル名を変更
    # =========================
    print(f"[TEST] チャンネル名変更開始: {len(text_channels)} チャンネル")

    for channel in text_channels:
        try:
            original_names[channel.id] = channel.name
            await channel.edit(
                name=test_name,
                reason="アンチレイドBotのテスト"
            )
            print(f"[CHANNEL] {channel.id}: {original_names[channel.id]} -> {test_name}")
            await asyncio.sleep(0.4)  # rate limit対策
        except discord.Forbidden:
            print(f"[CHANNEL] {channel.id}: 権限不足で変更不可")
        except discord.HTTPException as e:
            print(f"[CHANNEL] {channel.id}: APIエラー {e}")

    # アンチレイドBotが検知する時間を確保
    await asyncio.sleep(8)

    # =========================
    # 2. 名前を元に戻す（まだ変更されたままなら）
    # =========================
    for channel_id, old_name in original_names.items():
        channel = guild.get_channel(channel_id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            continue

        try:
            if channel.name == test_name:
                await channel.edit(
                    name=old_name,
                    reason="チャンネル変更テストの自動復元"
                )
                print(f"[CHANNEL] {channel_id}: {test_name} -> {old_name}")
            else:
                print(f"[CHANNEL] {channel_id}: 既に復元済み or 変更なし")
            await asyncio.sleep(0.4)
        except discord.Forbidden:
            print(f"[CHANNEL] {channel_id}: 復元権限不足")
        except discord.HTTPException as e:
            print(f"[CHANNEL] {channel_id}: 復元APIエラー {e}")

    # =========================
    # 3. 全チャンネルにスパム送信
    # =========================
    print(f"[TEST] スパム送信開始: {len(text_channels)} チャンネル × {count} 回")

    for channel in text_channels:
        # 最新のチャンネルオブジェクトを再取得
        channel = guild.get_channel(channel.id)
        if channel is None or not isinstance(channel, discord.TextChannel):
            continue

        for i in range(count):
            try:
                await channel.send(
                    f"【SPAM TEST】テストメッセージ {i + 1}/{count} (ch: {channel.name})"
                )
                await asyncio.sleep(0.35)
            except discord.Forbidden:
                print(f"[SPAM] {channel.id}: 送信権限なし")
                break
            except discord.HTTPException as e:
                print(f"[SPAM] {channel.id}: APIエラー {e}")
                break

    print(
        f"[TEST 完了] "
        f"guild={guild.id} "
        f"channels={len(text_channels)} "
        f"count={count}"
    )

    try:
        await interaction.followup.send(
            f"✅ テスト完了\n"
            f"対象チャンネル数: {len(text_channels)}\n"
            f"各チャンネル送信回数: {count}",
            ephemeral=True
        )
    except discord.HTTPException:
        pass


bot.run(TOKEN)
