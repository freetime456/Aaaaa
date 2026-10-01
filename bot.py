import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN が設定されていません")


intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True  # !nuke 用

bot = commands.Bot(command_prefix="!", intents=intents)


async def rename_target(target, new_name: str, reason: str):
    try:
        await target.edit(name=new_name, reason=reason)
        return True
    except Exception as e:
        print(f"[RENAME] {getattr(target, 'id', '?')} 失敗: {e}")
        return False


async def spam_target(target, count: int):
    for i in range(count):
        try:
            await target.send(f"【SPAM TEST】{i + 1}/{count}")
            await asyncio.sleep(0.12)
        except Exception as e:
            print(f"[SPAM] {getattr(target, 'id', '?')}: {e}")
            break


@bot.event
async def on_ready():
    print(f"ログイン成功: {bot.user}")


@bot.command(name="nuke")
async def nuke(ctx: commands.Context, count: int = 5):
    """全テキストチャンネル + スレッドに名前変更＆同時スパム"""
    if ctx.guild is None:
        await ctx.send("❌ サーバー内でのみ使用できます。")
        return

    if count < 1 or count > 50:
        await ctx.send("❌ 回数は 1〜50 で指定してください。")
        return

    guild = ctx.guild

    if guild.me is None:
        await ctx.send("❌ Botがこのサーバーに参加していません。")
        return

    # テキストチャンネル収集
    targets = []
    for ch in guild.text_channels:
        try:
            perms = ch.permissions_for(guild.me)
            if perms.send_messages and perms.manage_channels:
                targets.append(ch)
        except Exception:
            pass

    # アクティブスレッド収集
    for thread in guild.threads:
        try:
            perms = thread.permissions_for(guild.me)
            if perms.send_messages and perms.manage_channels:
                targets.append(thread)
        except Exception:
            pass

    if not targets:
        me_perms = guild.me.guild_permissions
        await ctx.send(
            "❌ 操作可能なチャンネル/スレッドがありません。\n"
            f"・メッセージ送信: {'✅' if me_perms.send_messages else '❌'}\n"
            f"・チャンネルの管理: {'✅' if me_perms.manage_channels else '❌'}\n"
            f"・管理者: {'✅' if me_perms.administrator else '❌'}"
        )
        return

    await ctx.send(
        f"🧪 高速テスト開始！\n"
        f"対象: テキストチャンネル + スレッド ({len(targets)}個)\n"
        f"・名前変更（復元なし）\n"
        f"・各所に {count} 回同時スパム"
    )

    test_name = "じいちゃん様に完全降伏w"

    # 1. 名前変更（並列・復元なし）
    print(f"[NUKE] 名前変更開始: {len(targets)} 個")
    await asyncio.gather(*[
        rename_target(t, test_name, "アンチレイドBotのテスト")
        for t in targets
    ])

    await asyncio.sleep(2)

    # 2. 同時スパム
    print(f"[NUKE] 同時スパム開始: {len(targets)} × {count}")
    spam_tasks = []
    for t in targets:
        obj = guild.get_channel(t.id) or guild.get_thread(t.id)
        if obj is not None:
            spam_tasks.append(spam_target(obj, count))
    await asyncio.gather(*spam_tasks)

    print(f"[NUKE 完了] guild={guild.id} targets={len(targets)} count={count}")
    await ctx.send(f"✅ 完了\n対象数: {len(targets)}\nスパム回数: {count}")


bot.run(TOKEN)
