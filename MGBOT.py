import os
import discord
import time
import requests
import yt_dlp
import asyncio
from datetime import timedelta
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.ui import View, Button
from myserver import server_on

# ตั้งค่า Intents เพื่อเปิดใช้งานฟีเจอร์ที่เกี่ยวข้องกับสมาชิก
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # เปิดการตรวจสอบการเข้า-ออกของสมาชิก

# สร้าง Bot สำหรับบอท (ใช้ commands.Bot แทน discord.Client)
bot = commands.Bot(command_prefix="!", intents=intents)
queues = {}  # เก็บคิวของแต่ละเซิร์ฟเวอร์
looping = {}  # ✅ เพิ่ม dictionary สำหรับเก็บสถานะ loop ของแต่ละเซิร์ฟเวอร์
current_song = {}  # เก็บ URL เพลงปัจจุบันของแต่ละเซิร์ฟเวอร์

# Event เมื่อบอทพร้อมทำงาน
@bot.event
async def on_ready():
    channel = bot.get_channel(1355095121095430244)
    await channel.send("✅✅    บอทออนไลน์แล้วไอสัสเลิกกดรันสักที      ✅✅")
    bot.add_view(TicketView())  # 🔥 ป้องกันปุ่มหมดอายุหลังรีสตาร์ทบอท
    print(f'✅✅    บอทออนไลน์แล้วไอสัสเลิกกดรันสักที     ✅✅     {bot.user}')

# Event เมื่อมีสมาชิกใหม่เข้าร่วมเซิร์ฟเวอร์
@bot.event
async def on_member_join(member):
    guild_name = member.guild.name

    # หา ID ของช่องที่ใช้ในการต้อนรับสมาชิก (ปรับเปลี่ยนชื่อช่องตามที่คุณต้องการ)
    channel = bot.get_channel(1355099514482065418) # ใช้ชื่อช่องที่คุณต้องการ
    await channel.send("ยินดีต้อนรับสู่เซิฟเวอร์ ทุกคนต้อนรับสมาชิกใหม่หน่อยสิ \n @everyone ! ! !")
    if channel:
        # ส่งข้อความต้อนรับและ GIF
        gif_url = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ3g3YXdxcXQybTM5ZHRhajM2aHEwbjFzNmptYTJ5Ym1jbzRydHl1dSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/P63emfqbLi37u6w105/giphy.gif"
        
        embed = discord.Embed(title="ยินดีต้อนรับสู่เซิฟเวอร์ของเรา", description=f"สวัสดีครับ {member.mention}! ยินดีต้อนรับสู่เซิร์ฟเวอร์ {guild_name} 🎊\n\n 📸ถ่ายรูปกด Ticket ได้เลย📸", color=0x00ff00)
        embed.set_image(url=gif_url)
        await channel.send(embed=embed)
        print(f'ส่งข้อความต้อนรับให้กับ {member.name}')

# Event เมื่อสมาชิกออกจากเซิร์ฟเวอร์
@bot.event
async def on_member_remove(member):
    # หา ID ของช่องที่ใช้ในการบอกลาสมาชิก
    channel = bot.get_channel(1355137703468863661)  # ใช้ชื่อช่องที่คุณต้องการ
    await channel.send("ลาก่อน ไว้เจอกันใหม่นะ ! ! !")
    gif_url = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGQ0azJ2dGV6enAyaWluMmxsa3A1Y2RvbmpmODJvNWFzM2F3dnI1diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UUhnOExaUB8BkDUaJn/giphy.gif"
    if channel:
        embed = discord.Embed(title="😢 ขอให้โชคดีนะ!", description=f"{member.name} ได้ออกจากเซิร์ฟเวอร์แล้ว", color=0xff0000)
        embed.set_image(url=gif_url)
        await channel.send(embed=embed)
        print(f'ส่งข้อความบอกลาให้กับ {member.name}')

@bot.command()
async def on(ctx):
    channel = bot.get_channel(1355110818240532520)
    await channel.send("ร้ า น เ ปิ ด แ ล้ ว ! ! ! นะทุกคน @everyone")
    gif_url = "https://media.giphy.com/media/l0HlS1sQnf2Do0osU/giphy.gif?cid=ecf05e470velsuqylmmaqzqev5319vf3vmaczkiii4svjjiw&ep=v1_gifs_search&rid=giphy.gif&ct=g"  # ลิงก์ GIF ที่ต้องการส่ง
    if channel:
        embed = discord.Embed(title="📸 ร้ า น เ ปิ ด แ ล้ ว ! ! ! นะทุกคน ", description="ถ่ายรูปเปิด Tickets มาได้เลย 🎟️ ! ! !", color=0x00ff00)
        embed.set_image(url=gif_url)
        await channel.send(embed=embed)
        
    else:
        await ctx.send("❌ ไม่พบห้องที่กำหนด!")

@bot.command()
async def off(ctx):
    channel = bot.get_channel(1355110818240532520)
    await channel.send("ร้ า น ปิ ด แ ล้ ว ! ! ! นะทุกคน @everyone")
    gif_url = "https://media.giphy.com/media/kDwIbnBqKe3D7BSqrt/giphy.gif?cid=790b76111lpgzrmxsr6ubsxe0pzgtm5md15ri5unyhgatw3h&ep=v1_gifs_search&rid=giphy.gif&ct=g"  # ลิงก์ GIF ที่ต้องการส่ง
    if channel:
        embed = discord.Embed(title="📸 ร้ า น ปิ ด แ ล้ ว ! ! ! นะทุกคน \n", description="ไว้มาถ่ายรูปด้วยกันใหม่นะจ๊ะ ! ! !", color=0x00ff00)
        embed.set_image(url=gif_url)
        await channel.send(embed=embed)
    else:
        await ctx.send("❌ ไม่พบห้องที่กำหนด!")

@bot.command()
async def rate(ctx):
    channel = bot.get_channel(1355176066993356960)
    await channel.send("เ ร ท ร า ค า ถ่ า ย รู ป 2.0 ! ! ! @everyone")
    gif_url = "https://media.discordapp.net/attachments/1340644576129716326/1340647114296004702/72ae51242d2070fb.gif?ex=67e731ac&is=67e5e02c&hm=a5942a2948de1bb8ddb7ff0d341aae0f642e9cde93ab422e380346562c034b17&=&width=978&height=550"  # ลิงก์ GIF ที่ต้องการส่ง
    if channel:
        embed = discord.Embed(title="📸 เรทราคาถ่ายรูป 2.0 ! ! ! \n", description="รับถ่ายทุกรูปแบบ\n\n1.ถ่ายแบบเดี่ยว📸\n\n2.ถ่ายแบบคู่📸\n\n3.ถ่ายแบบกลุ่ม📸\n\n\n📸📸สนใจถ่ายรูปกด Ticket ได้เลย ! ! ! 🎟️📸", color=0x00ff00)
        embed.set_image(url=gif_url)
        await channel.send(embed=embed)
    else:
        await ctx.send("❌ ไม่พบห้องที่กำหนด!")

@bot.command()
async def all(ctx):
    channel = bot.get_channel(1355110818240532520)
    await channel.send("ร้ า น เ ปิ ด แ ล้ ว ! ! ! นะทุกคน @everyone")
    gif_url = "https://media.giphy.com/media/l0HlS1sQnf2Do0osU/giphy.gif?cid=ecf05e470velsuqylmmaqzqev5319vf3vmaczkiii4svjjiw&ep=v1_gifs_search&rid=giphy.gif&ct=g"  # ลิงก์ GIF ที่ต้องการส่ง
    if channel:
        embed = discord.Embed(title="📸 ร้ า น เ ปิ ด แ ล้ ว ! ! ! นะทุกคน ", description="📸📸ถ่ายรูปเปิด Tickets มาได้เลย 🎟️📸 ! ! !", color=0x00ff00)
        embed.set_image(url=gif_url)
        await channel.send(embed=embed)
        
    else:
        await ctx.send("❌ ไม่พบห้องที่กำหนด!")
    channel = bot.get_channel(1355176066993356960)
    await channel.send("เ ร ท ร า ค า ถ่ า ย รู ป 2.0 ! ! ! @everyone")
    gif_url = "https://media.discordapp.net/attachments/1340644576129716326/1340647114296004702/72ae51242d2070fb.gif?ex=67e731ac&is=67e5e02c&hm=a5942a2948de1bb8ddb7ff0d341aae0f642e9cde93ab422e380346562c034b17&=&width=978&height=550"  # ลิงก์ GIF ที่ต้องการส่ง
    if channel:
        embed = discord.Embed(title="📸 เรทราคาถ่ายรูป 2.0 ! ! ! \n", description="รับถ่ายทุกรูปแบบ\n\n1.ถ่ายแบบเดี่ยว📸\n\n2.ถ่ายแบบคู่📸\n\n3.ถ่ายแบบกลุ่ม📸\n\n\n📸📸สนใจถ่ายรูปกด Ticket ได้เลย ! ! ! 🎟️📸", color=0x00ff00)
        embed.set_image(url=gif_url)
        await channel.send(embed=embed)
    else:
        await ctx.send("❌ ไม่พบห้องที่กำหนด!")

@bot.command()
async def menu(ctx): #เรียกใช้เมนูร้าน
    gif_url = "https://media.discordapp.net/attachments/1340644576129716326/1340647114296004702/72ae51242d2070fb.gif?ex=67e731ac&is=67e5e02c&hm=a5942a2948de1bb8ddb7ff0d341aae0f642e9cde93ab422e380346562c034b17&=&width=978&height=550"  # ใส่ URL ของ GIF
    # ✅ สร้าง Embed ก่อนใช้งาน
    embed = discord.Embed(title="📌 เมนูร้านค้า", description="รับถ่ายทุกรูปแบบ\n\n1.ถ่ายแบบเดี่ยว📸\n\n2.ถ่ายแบบคู่📸\n\n3.ถ่ายแบบกลุ่ม📸\n\n\n📸📸สนใจถ่ายรูปกด Ticket ได้เลย ! ! ! 🎟️📸", color=0x00ff00)
    embed.set_image(url=gif_url)  # ✅ ใส่ภาพ GIF
    await ctx.send(embed=embed)
    await ctx.send("📌 **ถ่ายรูปกด Ticket แล้วรอสักครู่นะคับ 📌\n 📌กดเล่นแบนทันที ! ! !📌**", view=TicketView())

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # 🔥 ป้องกันปุ่มหมดอายุ

    @discord.ui.button(label="📩 ติดต่อถ่ายรูปกด Ticket ได้เลย ! ! !", style=discord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # 🔍 เช็คว่าผู้ใช้มี Ticket อยู่แล้วหรือไม่
        existing_channel = discord.utils.get(guild.channels, name=f"ticket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"คุณมี Ticket อยู่แล้ว: {existing_channel.mention}", ephemeral=True)
            return

        # ✅ สร้างห้อง Ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(name=f"ticket-{user.name.lower()}", overwrites=overwrites)

        # 📩 ส่งข้อความพร้อมปุ่มปิด
        embed = discord.Embed(title="📩 Ticket ถูกสร้างแล้ว", description=f"สวัสดี {user.mention}!\nโปรดรอสักครู่จะมาตอบกลับให้เร็วที่สุด ! ! !", color=discord.Color.green())
        await ticket_channel.send(content=user.mention, embed=embed, view=CloseTicketView())

        await interaction.response.send_message(f"✅ สร้าง Ticket เรียบร้อย! ไปที่ {ticket_channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # 🔥 ป้องกันปุ่มหมดอายุ

    @discord.ui.button(label="🔒 ปิด Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="⚠ ยืนยันการปิด Ticket", description="คุณแน่ใจหรือไม่ว่าต้องการปิด Ticket นี้?", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, view=ConfirmCloseView(), ephemeral=True)

class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # 🔥 ป้องกันปุ่มหมดอายุ

    @discord.ui.button(label="✅ ใช่, ปิดเลย", style=discord.ButtonStyle.success, custom_id="confirm_close")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        await interaction.response.send_message("🔒 กำลังปิด Ticket...", ephemeral=True)
        await channel.delete()  # ลบห้อง Ticket

    @discord.ui.button(label="❌ ยกเลิก", style=discord.ButtonStyle.secondary, custom_id="cancel_close")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ การปิด Ticket ถูกยกเลิก", ephemeral=True)

# คำสั่งลบข้อความ
@bot.command()
async def ลบ(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ ลบข้อความ {amount} ข้อความเรียบร้อย', delete_after=3,ephemeral=True)

@bot.command()
@commands.has_permissions(moderate_members=True)  # ต้องมีสิทธิ์ "Timeout Members"
async def timeout(ctx, member: discord.Member, time: int, *, reason="ไม่ได้ระบุเหตุผล"):
    """ กำหนด Timeout ให้กับผู้ใช้ (ไม่สามารถพิมพ์/ส่งข้อความได้) """
    try:
        duration = timedelta(minutes=time)  # กำหนดเวลาที่จะ Timeout
        await member.timeout(duration, reason=reason)
        await ctx.send(f"✅ `{member.display_name}` ถูก Timeout เป็นเวลา `{time}` นาที ด้วยเหตุผล: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ บอทไม่มีสิทธิ์ Timeout ผู้ใช้นี้!")
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {e}")

@bot.command()
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    """ ยกเลิก Timeout ให้กับผู้ใช้ """
    try:
        await member.timeout(None)  # กำหนดเวลาเป็น None เพื่อยกเลิก Timeout
        await ctx.send(f"✅ `{member.display_name}` ถูกยกเลิก Timeout แล้ว!")
    except discord.Forbidden:
        await ctx.send("❌ บอทไม่มีสิทธิ์ยกเลิก Timeout!")
    except Exception as e:
        await ctx.send(f"❌ เกิดข้อผิดพลาด: {e}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def เตะ(ctx, member: discord.Member, *, reason="ไม่ได้ระบุ"):
    await member.kick(reason=reason)
    await ctx.send(f":✅: {member.mention} ถูกเตะออกจากเซิร์ฟเวอร์ ด้วยเหตุผล: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def แบน(ctx, member: discord.Member, *, reason="ไม่ได้ระบุ"):
    await member.ban(reason=reason)
    await ctx.send(f"🚫 {member.mention} ถูกแบนจากเซิร์ฟเวอร์ ด้วยเหตุผล: {reason}")

def check_queue(ctx):
    """ ตรวจสอบว่ามีเพลงในคิวหรือไม่ หรือให้เล่นซ้ำถ้าเปิด Loop """
    guild_id = ctx.guild.id
    vc = ctx.voice_client

    if not vc or not vc.is_connected():
        return

    if looping.get(guild_id, False) and current_song.get(guild_id):
        # ถ้าเปิด Loop เล่นเพลงเดิมซ้ำ
        new_source = FFmpegPCMAudio(current_song[guild_id], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
        vc.play(new_source, after=lambda e: check_queue(ctx))
    elif queues.get(guild_id):
        # ถ้ามีเพลงในคิว เล่นเพลงถัดไป
        next_url = queues[guild_id].pop(0)
        current_song[guild_id] = next_url  # อัปเดตเพลงปัจจุบัน
        new_source = FFmpegPCMAudio(next_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
        vc.play(new_source, after=lambda e: check_queue(ctx))
    else:
        # ถ้าไม่มีเพลงในคิว บอทยังอยู่แต่ไม่เล่นอะไร
        pass

@bot.command()
async def join(ctx):
    """ ให้บอทเข้าห้องเสียง """
    if not ctx.author.voice:
        return await ctx.send("❌ คุณต้องอยู่ในช่องเสียงก่อน!")
    channel = ctx.author.voice.channel
    await channel.connect(reconnect=True)
    await ctx.send(f"✅ บอทเข้าห้อง {channel.name} แล้ว!")

@bot.command()
async def play(ctx, *, url):
    """ เล่นเพลงจาก YouTube และใช้คิวเพื่อให้เล่นต่อเนื่อง """
    guild_id = ctx.guild.id
    vc = ctx.voice_client

    if not vc:
        await ctx.invoke(join)
        vc = ctx.voice_client

    await ctx.send(f"🎵 กำลังค้นหาเพลง...")

    # ตั้งค่า yt-dlp
    ydl_opts = {"format": "bestaudio/best", "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]

    # ถ้าเพลงกำลังเล่นอยู่ให้เพิ่มไปที่คิว
    if vc.is_playing():
        if guild_id not in queues:
            queues[guild_id] = []
        queues[guild_id].append(audio_url)
        return await ctx.send(f"➕ เพิ่ม `{info['title']}` ลงคิว!")

    # เล่นเพลง
    current_song[guild_id] = audio_url  # บันทึก URL เพลงปัจจุบัน
    new_source = FFmpegPCMAudio(audio_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
    vc.play(new_source, after=lambda e: check_queue(ctx))
    await ctx.send(f"🎶 กำลังเล่น: {info['title']}")

@bot.command()
async def stop(ctx):
    """ หยุดเล่นเพลง, ล้างคิว, ปิด Loop """
    guild_id = ctx.guild.id
    vc = ctx.voice_client

    if vc and vc.is_playing():
        vc.stop()  # หยุดเพลง
        queues[guild_id] = []  # ล้างคิว
        looping[guild_id] = False  # ปิด Loop
        current_song.pop(guild_id, None)  # ล้างเพลงปัจจุบัน
        await ctx.send("⏹️ หยุดเล่นเพลงและล้างคิวทั้งหมด!")
    else:
        await ctx.send("❌ ไม่มีเพลงที่กำลังเล่น!")

@bot.command()
async def leave(ctx):
    """ ออกจากช่องเสียงและล้างคิวเพลง """
    guild_id = ctx.guild.id
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        queues.pop(guild_id, None)  # ล้างคิว
        looping[guild_id] = False  # ปิด Loop
        current_song.pop(guild_id, None)  # ล้างเพลงปัจจุบัน
        await ctx.send("🚪 บอทออกจากช่องเสียงแล้ว!")
    else:
        await ctx.send("❌ บอทไม่ได้อยู่ในช่องเสียง!")

@bot.command()
async def loop(ctx):
    """ เปิด/ปิด Loop เล่นเพลงซ้ำ """
    guild_id = ctx.guild.id
    looping[guild_id] = not looping.get(guild_id, False)
    status = "✅ เปิด Loop แล้วฟังวนไปนะไอสัส ! ! !" if looping[guild_id] else "❌ ปิด Loop แล้วเลิกฟังวนแล้วดิไอสัส ! ! !"
    await ctx.send(status)

server_on()
# เริ่มการทำงานของบอท
bot.run(os.getenv('TOKEN'))