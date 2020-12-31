import os 
import random 
import discord
import pytz
import sqlite3
import asyncio
import time
import feedparser
import aiohttp
import json

from discord.ext import commands, tasks
from discord import File, Embed
from dotenv import load_dotenv
from time import mktime
from datetime import datetime
from pytz import timezone
from random import randint
from asyncio import TimeoutError



#loads token for discord bot
#CHANGE .env FILE TO YOUR TOKEN AND GUILD
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#opens files for links
with open(os.path.join(os.getcwd(), "media\gifs\dance_gifs.txt"), "r") as gifs:
    dance_gif_links = gifs.readlines()
with open(os.path.join(os.getcwd(), "media\gifs\\battle_gifs.txt"), "r") as gifs:
    battle_gif_links = gifs.readlines()
with open(os.path.join(os.getcwd(), "media\gifs\decline_gifs.txt"), "r") as gifs:
    decline_gif_links = gifs.readlines()
with open(os.path.join(os.getcwd(), "media\gifs\challenge_gifs.txt"), "r") as gifs:
    challenge_gif_links = gifs.readlines()
with open(os.path.join(os.getcwd(), "media\gifs\winner_gifs.txt"), "r") as gifs:
    winner_gif_links = gifs.readlines()
with open(os.path.join(os.getcwd(), "media\gifs\\laughing_gifs.txt"), "r") as gifs:
    laughing_gif_links = gifs.readlines()


#specifies intents
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True)
intents.members = True

#creates bot
bot = commands.Bot(command_prefix='<<', intents=intents)
bot.remove_command("help")

#fields 
last_update = datetime.now(timezone("UTC"))
bot.shop_items = []


"""
EVENT COMMANDS
"""
#when bot is ready, retrives approved server using env file and prints members of server 
@bot.event 
async def on_ready():
    #loopcheck.start()
    guild = discord.utils.get(bot.guilds, name=GUILD)
    await create_roles(guild)
    bot.shop_items = read_json("shop.json")
    print(f'{bot.user} is connected to {guild.name}. Members include:')
    for member in guild.members:
        print(member.name)
        print(member.id)
        print("-------")
    #ADDING MEMBERS TO DATABASE
    add_members(guild.members)

#Welcome message when user joins 
@bot.event 
async def on_member_join(member):
    add_member(member)
    await member.send(f'Hello {member.name}! Welcome to the server. We hope you have a good time!')

#Checks messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    guild = discord.utils.get(bot.guilds, name=GUILD)
    role = discord.utils.get(guild.roles, name="Muted")
    if role in message.author.roles:
        await message.delete()
    await bot.process_commands(message)

@bot.event
async def on_member_update(before, after):
    guild = discord.utils.get(bot.guilds, name=GUILD)
    role = discord.utils.get(guild.roles, name="Poor")
    entries = await guild.audit_logs(limit=1).flatten()
    last_entry = entries[0]
    if last_entry.user == bot.user:
        return
    if role not in before.roles:
        return
    if before.nick != after.nick:
        await after.edit(nick=before.nick)
        return

"""
UTILITY COMMANDS
"""
#Help command
@bot.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(
        description = "Use <<help <command> to get more information about a specific command",
        color = discord.Color.dark_gold()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="Utility Commands", value="| dance | time | timeof |", inline=False)
    embed.add_field(name="Dinz Commands", value = "| dinz | daily | bigdinz | challenge | blackjack | shop |", inline=False)
    #CHANGE TO YOUR ID
    if ctx.author.id == 1:
        embed.add_field(name="Admin Commands", value="| startmanga | price (ItemX XXXXX) | add1 (discord_ID XXXXXXX) |", inline=False)
    await ctx.send(embed=embed)
@help.command()
async def dance(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_blue()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="dance", value="Sends a gif of Kanye West dancing")
    await ctx.send(embed=embed)
@help.command()
async def timein(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_blue()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="timein", value="Tells the current time in a given timezone", inline=False)
    embed.add_field(name="Syntax", value="<<timein (timezone)", inline=False)
    embed.add_field(name="Notes", value="Timezone value is case-sensitive")
    await ctx.send(embed=embed)
@help.command()
async def timeof(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_blue()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="timeof", value="Takes the given time and timezone and tells what time it would be in EST", inline=False)
    embed.add_field(name="Syntax", value="<<timeof (MM/DD/YYYY) (HH:MM) (-timezone)", inline=False)
    embed.add_field(name="Notes", value="Timezone value is case-sensitive, format is important. Requires a '-' right before timezone")
    await ctx.send(embed=embed)
@help.command()
async def dinz(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_red()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="dinz", value="Show the current amount of dinz held", inline=False)
    embed.add_field(name="Syntax", value="<<dinz optional -> (@member)", inline=False)
    embed.add_field(name="Notes", value="Can add @'s after command to see someone elses dinz. Multiple @'s can be used")
    await ctx.send(embed=embed)
@help.command()
async def daily(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_red()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="daily", value="Collect daily dinz", inline=False)
    embed.add_field(name="Syntax", value="<<daily", inline=False)
    embed.add_field(name="Notes", value="The cooldown is based on day, rather than 24 hours.")
    await ctx.send(embed=embed)
@help.command()
async def bigdinz(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_red()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="bigdinz", value="Calculate who has the most dinz in the server", inline=False)
    embed.add_field(name="Syntax", value="<<bigdinz", inline=False)
    embed.add_field(name="Notes", value="The person with the most dinz is awarded the King Dinz role")
    await ctx.send(embed=embed)
@help.command()
async def challenge(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_red()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="challenge", value="Challenge another player to a duel", inline=False)
    embed.add_field(name="Syntax", value="<<challenge (@member) (wager amount)", inline=False)
    embed.add_field(name="Notes", value="The winner of the duel earns the wager amount and loser loses the wager amount")
    await ctx.send(embed=embed)
@help.command()
async def blackjack(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_red()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="blackjack", value="Play blackjack with the bot as a dealer", inline=False)
    embed.add_field(name="Syntax", value="<<blackjack (wager amount)", inline=False)
    embed.add_field(name="Notes", value="Wager amount is earned or lost on victor and defeat.")
    await ctx.send(embed=embed)
@help.command()
async def shop(ctx):
    embed = discord.Embed(
        color = discord.Color.dark_red()
        )
    embed.set_author(name="Help Command", icon_url="https://i.imgur.com/TYL153R.png")
    embed.add_field(name="shop", value="Opens the shop", inline=False)
    embed.add_field(name="Syntax", value="<<shop", inline=False)
    embed.add_field(name="Notes", value="Shop menus are deleted after 20s so do be quick about your selection.")
    await ctx.send(embed=embed)
#sends a message using random choice of an array of messages
@bot.command(name='dance', help='Random gif of Kanye West dancing.')
async def dance_kanye(ctx):
    await ctx.send(random.choice(dance_gif_links))

#Tells the current time in specified timezone
@bot.command(name='timein', help='Tells the current time in specified timezone')
async def global_time(ctx, timezone_=None):
    if timezone_ == None: 
        await ctx.send('Please provide a timezone')
        return
    if timezone_ not in pytz.all_timezones:
        await ctx.send('Your timezone is not a valid timezone. Refer to link: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones (Reminder that timezone is case-sens.)')
        return
    format = "%m/%d/%Y %H:%M"
    try:
        now = datetime.now(timezone(timezone_))
        await ctx.send(f'The current time in {timezone_} is: ' + now.strftime(format))
    except:
        await ctx.send('Your timezone is not a valid timezone. Refer to link: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones')

#Takes in user message and outputs given time and zone of time into EST time. uses return in if statements to halt code unlike previous time command due to extra user input required
@bot.command(name='timeof', help='Takes given time (MM/DD/YYYY HH:MM -Timezone) and outputs time in EST')
async def time_of(ctx, *, message=None):
    if message == None: 
        await ctx.send('Please enter a time and a timezone')
        return
    user_input = message.split('-')
    if len(user_input) < 2:
        await ctx.send('Your message requires a - before the timezone!')
        return
    time = user_input[0].strip()
    timezone = user_input[1]
    if timezone not in pytz.all_timezones:
        await ctx.send('Your timezone is not a valid timezone. Refer to link: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones (Reminder that timezone is case-sens.)')
        return
    format = "%m/%d/%Y %H:%M"

    try:
        timezone_ = pytz.timezone(timezone)
        localized_time = timezone_.localize(datetime.strptime(time, format))
        
        #CHANGE
        #edit this to time local to server 
        eastern_time = localized_time.astimezone(pytz.timezone('US/Eastern'))
        #edit this to time local to server 

        await ctx.send('That date would be: ' + eastern_time.strftime(format))
    except:
        await ctx.send('Enter in with correct formatting (MM/DD/YYYY HH:MM -Timezone)')

#Creates the mangadex-updates channel and starts the mangadex updates tasks 
@bot.command(name='startmanga', help='Creates the mangadex-updates channel and posts updates every 30min.')
@commands.is_owner()
async def create_mangadex(ctx):
    guild = ctx.guild
    manga_channel = discord.utils.get(guild.channels, name="mangadex-updates")
    if not manga_channel:
        manga_channel = await guild.create_text_channel('mangadex-updates')
    manga_updates.start(manga_channel)

#uses given mangadex rss feed with the mangadex api and outputs updates every 30mins
@tasks.loop(minutes=10) 
async def manga_updates(manga_channel):
    global last_update
    #CHANGE THIS TO YOUR MANGADEX RSS FEED
    manga_feed = feedparser.parse("")
    new_manga = []
    for feed in manga_feed.entries:
        date_posted = datetime.fromtimestamp(mktime(feed.published_parsed))
        date_posted = date_posted.replace(tzinfo=pytz.utc)
        if last_update < date_posted:
            new_manga.append(feed)
        elif last_update > date_posted:
            break
    if not new_manga:
        return
    last_update = datetime.now(timezone("UTC"))
    new_manga.reverse()
    for feed in new_manga:
        manga_chapter = feed.title
        manga_link = feed.link
        group_info = feed.description
        url = "https://mangadex.org/api/v2/manga/" + feed.mangalink.split("/")[4]
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    js = await r.json()
                    desc = js['data']['description'][:500] + (js['data']['description'][500:] and '...')
                    cover = js['data']['mainCover']
                    manga_name = js['data']['title']
                else:
                    return
        #embed
        embed = discord.Embed(
            title=manga_name,
            description = desc,
            color = discord.Color.light_gray()
            )
        url = cover
        embed.set_thumbnail(url=url)
        embed.set_author(name="Mangadex-Updates", icon_url="https://i.imgur.com/vuqOS7a.png")
        now = datetime.now()
        embed.set_footer(text=group_info)
        embed.add_field(name=manga_chapter, value=manga_link)
        await manga_channel.send(embed=embed)
        await asyncio.sleep(10)

"""
ECONOMY COMMANDS
"""


#command to show display user dinz
@bot.command(name='dinz', help='Displays amount of user dinz. Add @ of user to see their dinz')
async def show_dinz(ctx):
    conn = create_connection()
    cur = create_cursor(conn)
    mentions = ctx.message.mentions
    if len(mentions) == 0:
        discord_ID = ctx.author.id
        user = get_info(cur, discord_ID)
        await ctx.send(f'<@{discord_ID}>, you have {user[0][1]} Dinz!')
    for mentioned in mentions:
        discord_ID = mentioned.id 
        user = get_info(cur, discord_ID)
        await ctx.send(f'<@{discord_ID}> has {user[0][1]} Dinz.')
    conn.close()

#command for daily, CHECK IF WORKS ON OTHER PEOPLE
@bot.command(name='daily', help='Collect your daily big dinz!')
async def daily_dinz(ctx):
    conn = create_connection()
    cur = create_cursor(conn)
    user = get_info(cur, ctx.author.id)
    format = "%m/%d/%Y %H:%M"
    today = datetime.today()
    last_daily = datetime.strptime((user[0][2] + " 23:59"), format)
    if today > last_daily:
        ran_dinz = randint(50, 300)
        await add_dinz(ctx.author.id, ran_dinz)
        date = today.strftime(format)
        cur.execute("UPDATE users SET last_daily=? WHERE discord_ID=?", (date, ctx.author.id))
        conn.commit()
        await ctx.send(f'{ran_dinz} Dinz collected.')
    else:
        await ctx.send("Still too early to collect your dinz!")

#command for checking who has the most dinz, assigns roll to person with most dinz 
@bot.command(name='bigdinz', help='Displays the user with the most dinz and assigns them the King Dinz role')
async def bigdinz(ctx):
    conn = create_connection()
    cur = create_cursor(conn)
    cur.execute("SELECT * FROM users ORDER BY dinz DESC")
    users = cur.fetchall()
    top_user = users[0]
    discord_ID = top_user[0]
    dinz = top_user[1]
    #grabbing information to add role
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name='King Dinz')
    member_dinz = guild.get_member(discord_ID)
    await member_dinz.add_roles(role)
    await ctx.send(f'The King Dinz is <@{discord_ID}>!')

#Takes the user inputted mention and wager amount, allows the challenged user to accept, adds dinz to random selected winner, subtracts from loser 
@bot.command(name='challenge', help='@ someone else and add an amount of dinz you want to wager')
async def send_challenge(ctx, *, message=None):
    mentioned = ctx.message.mentions
    wager_amount = message
    if len(mentioned) != 1 or wager_amount == None:
        await ctx.send("You need to provide a single @ then a wager amount!")
        return
    if ctx.author.id == mentioned[0].id:
        await ctx.send("You can't challenge yourself!")
        return
    try:
        wager_amount = (wager_amount.split("> "))[1]
    except IndexError:
        await ctx.send("You need to enter an amount after the @!")
        return
    try:
        wager_amount = int(wager_amount)
    except ValueError as e:
        await ctx.send("Please enter a whole number after you mention who you want to challenge!")
        return

    challengee_id = ctx.author.id
    challenged_id = mentioned[0].id 
    ch_user = bot.get_user(challenged_id)
    
    chall_embed = discord.Embed(
        title=f'{ch_user.name} hit the thumbs up to accept or the thumbs down to decline!',
        description = f'{ctx.author.name} sends a challenge...',
        color = discord.Color.red()
        )
    url = random.choice(challenge_gif_links)
    chall_embed.set_image(url=url)
    chall_embed.set_author(name="Challenge sent!")

    chall_msg = await ctx.send(embed=chall_embed)

    await chall_msg.add_reaction('👍')
    await chall_msg.add_reaction('👎')

    def check(reaction, user):
        return user == ch_user and (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎')
    
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=20)
        if reaction.emoji == '👍':
            challenge_accepted = True
        elif reaction.emoji ==  '👎':
            challenge_accepted = False
    except asyncio.TimeoutError:
        challenge_accepted = False


    if challenge_accepted:
        #TODO this 
        await chall_msg.delete()
        acc_embed  = discord.Embed(
            title=f'{ch_user.name} and {ctx.author.name} are engaged in battle!!!',
            description = f'The battle continues...',
            color = discord.Color.purple()
            )
        url = random.choice(battle_gif_links)
        acc_embed.set_image(url=url)
        acc_embed.set_author(name="Challenge accepted!")
        acc_msg = await ctx.send(embed=acc_embed)
        days = randint(1, 3)
        for i in range(days):
            await asyncio.sleep(4)
            i += 1
            if i == 1:
                des_str = acc_embed.description + "\nThe battle has been going on for a day"
                acc_embed.description = des_str 
                await acc_msg.edit(embed=acc_embed)
            else:
                des_str = acc_embed.description + f'\nThe battle has been going on for {i} days'
                acc_embed.description = des_str 
                await acc_msg.edit(embed=acc_embed)
        #pick winners
        players = [ctx.author, ch_user]
        winner_user = random.choice(players)
        players.pop(players.index(winner_user))
        loser_user = players[0]
        await add_dinz(winner_user.id, wager_amount)
        await add_dinz(loser_user.id, (wager_amount * -1))

        await acc_msg.delete()
        vic_embed  = discord.Embed(
            title=f'{winner_user.name} has triumphed over {loser_user.name}',
            description = f'{wager_amount} Dinz has been added to the winners bank and taken from the losers',
            color = discord.Color.gold()
            )    
        url = random.choice(winner_gif_links)
        vic_embed.set_image(url=url)
        vic_embed.set_author(name="Victory Screen!")
        await ctx.send(embed=vic_embed)

    elif not challenge_accepted:
        await chall_msg.delete()
        dec_embed = discord.Embed(
            title=f'{ch_user.name} ran away from the challenge...',
            description = f'{ctx.author.name} cant be that intimidating..',
            color = discord.Color.purple()
            )
        url = random.choice(decline_gif_links)
        dec_embed.set_image(url=url)
        dec_embed.set_author(name="Challenge declined!")
        await ctx.send(embed=dec_embed)

#runs a game of blackjack
@bot.command(name="blackjack", help="Play a game of blackjack with the bot. Enter a value after the command to wager that amount")
async def play_blackjack(ctx, message=None):
    if message == None:
        await ctx.send("You need to included a wager amount in the command.")
        return
    try:
        wager_amount = int(message)
    except ValueError:
        await ctx.send("Please enter a number only for your bet")
        return

    deck = get_deck()
    deck_full = get_deck()

    dealer_hand_text = []
    player_hand_text = []

    dealer_hand = []
    player_hand = []

    dealer_win = False
    dealer_continue = True
    dealer_bool = True
    dealer_lose = False
    player_win = False 
    player_lose = False
    player_bool = False

    dealer_hand_total = 0
    player_hand_total = 0

    await ctx.send("Dealers hand: ")
    dealer_hand_set = await send_card(deck, dealer_hand_text, dealer_hand, dealer_hand_total, dealer_bool, ctx)
    deck = dealer_hand_set[0]
    dealer_hand_text = dealer_hand_set[1]
    dealer_hand = dealer_hand_set[2]
    dealer_hand_total = dealer_hand_set[3]
    
    #getting what first drawn card is
    first_card = " "
    #index = 0
    l = [x for x in deck_full if x not in deck]
    for card in deck_full:
        if card in l:
            first_card = card

    dealer_hand_set1 = await send_card(deck, dealer_hand_text, dealer_hand, dealer_hand_total, dealer_bool, ctx)
    deck = dealer_hand_set1[0]
    dealer_hand_text = dealer_hand_set1[1]
    dealer_hand = dealer_hand_set1[2]
    dealer_hand_total = dealer_hand_set1[3]

    await ctx.send(f'{ctx.author.name}s hand:')
    player_hand_set = await send_card(deck, player_hand_text, player_hand, player_hand_total, player_bool, ctx)
    deck = player_hand_set[0]
    player_hand_text = player_hand_set[1]
    player_hand = player_hand_set[2]
    player_hand_total = player_hand_set[3]

    player_hand_set = await send_card(deck, player_hand_text, player_hand, player_hand_total, player_bool, ctx)
    deck = player_hand_set[0]
    player_hand_text = player_hand_set[1]
    player_hand = player_hand_set[2]
    player_hand_total = player_hand_set[3]
    
    ##################

    game_check = check_game(player_hand, player_hand_total, dealer_hand, dealer_hand_total)
    #[0] = player win, [1] = dealer win, [2] = player has ace, [3] = dealer has ace
    if game_check[0]:
        await ctx.send(f'<@{ctx.author.id}> wins {wager_amount} Dinz!')
        await add_dinz(ctx.author.id, wager_amount)
        return
    elif game_check[1]:
        await ctx.send("The dealers flipped card was:")
        card = first_card
        with open(os.path.join(os.getcwd(), f'media\cards\{card}.png'), 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'card.png'))
        await ctx.send(f'<@{ctx.author.id}> loses {wager_amount} Dinz!')
        await add_dinz(ctx.author.id, (wager_amount * -1))
        return
    elif game_check[2] and not game_check[3]:
        player_hand = game_check[4]
        player_hand_total = game_check[5]
    elif game_check[3] and not game_check[2]:
        dealer_hand = game_check[6]
        dealer_hand_total = game_check[7]
    elif game_check[2] and game_check[3]:
        player_hand = game_check[4]
        player_hand_total = game_check[5]
        dealer_hand = game_check[6]
        dealer_hand_total = game_check[7]

    if dealer_hand_total >= 17:
        dealer_continue = False

    ############################

    await ctx.send("Type 'hit' to hit or 'stay' to stay")
    
    def check(m):
        return (m.content == "hit" and m.content == "stay") or  m.author.id == ctx.author.id
    try:
        acc_msg = await bot.wait_for('message', check=check, timeout=20)
    except asyncio.TimeoutError:
        await ctx.send(f'Didnt respond back fast enough! <@{ctx.author.id}> loses {wager_amount} Dinz!')
        await add_dinz(ctx.author.id, (wager_amount * -1))
        return
    #hit LOGIC
    while acc_msg.content == "hit":
        await ctx.send(f'{ctx.author.name}s new card:')
        player_hand_set = await send_card(deck, player_hand_text, player_hand, player_hand_total, player_bool, ctx)
        deck = player_hand_set[0]
        player_hand_text = player_hand_set[1]
        player_hand = player_hand_set[2]
        player_hand_total = player_hand_set[3]

        if player_hand_total == 21:
            await ctx.send(f'<@{ctx.author.id}> wins {wager_amount} Dinz!')
            await add_dinz(ctx.author.id, wager_amount)
            return
        elif player_hand_total > 21:
            check_ace = ace_check(player_hand, player_hand_total)
            if check_ace[0]:
                await ctx.send("The dealers flipped card was:")
                card = first_card
                with open(os.path.join(os.getcwd(), f'media\cards\{card}.png'), 'rb') as fp:
                    await ctx.send(file=discord.File(fp, 'card.png'))
                await ctx.send(f'<@{ctx.author.id}> loses {wager_amount} Dinz!')
                await add_dinz(ctx.author.id, (wager_amount * -1))
                return
            else:
                player_hand = check_ace[1]
                player_hand_total = check_ace[2]

        await ctx.send("Type 'hit' to hit or 'stay' to stay")
    
        def check(m):
            return (m.content == "hit" and m.content == "stay") or  m.author.id == ctx.author.id
        try:
            acc_msg = await bot.wait_for('message', check=check, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send(f'Didnt respond back fast enough! <@{ctx.author.id}> loses {wager_amount} Dinz!')
            await add_dinz(ctx.author.id, (wager_amount * -1))
            return
    # HOLD LOGIC
    if acc_msg.content == "stay":
        while dealer_continue:
            await ctx.send("Dealers newest card: ")
            dealer_hand_set = await send_card(deck, dealer_hand_text, dealer_hand, dealer_hand_total, dealer_bool, ctx)
            deck = dealer_hand_set[0]
            dealer_hand_text = dealer_hand_set[1]
            dealer_hand = dealer_hand_set[2]
            dealer_hand_total = dealer_hand_set[3]

            if dealer_hand_total > 17 and dealer_hand_total < 21:
                dealer_hand_total = False
            elif dealer_hand_total == 21:
                await ctx.send("The dealers flipped card was:")
                card = first_card
                with open(os.path.join(os.getcwd(), f'media\cards\{card}.png'), 'rb') as fp:
                    await ctx.send(file=discord.File(fp, 'card.png'))
                await ctx.send(f'<@{ctx.author.id}> loses {wager_amount} Dinz!')
                await add_dinz(ctx.author.id, (wager_amount * -1))
                return 
            elif dealer_hand_total > 21:
                check_ace = ace_check(dealer_hand, dealer_hand_total)
                if check_ace[0]:
                    await ctx.send(f'<@{ctx.author.id}> wins {wager_amount} Dinz!')
                    await add_dinz(ctx.author.id, wager_amount)
                    return
                else:
                    dealer_hand = check_ace[1]
                    dealer_hand_total = check_ace[2]
        if not dealer_continue:
            if dealer_hand_total > player_hand_total:
                await ctx.send("The dealers flipped card was:")
                card = first_card
                with open(os.path.join(os.getcwd(), f'media\cards\{card}.png'), 'rb') as fp:
                    await ctx.send(file=discord.File(fp, 'card.png'))
                await ctx.send(f'<@{ctx.author.id}> loses {wager_amount} Dinz!')
                await add_dinz(ctx.author.id, (wager_amount * -1))
                return 
            elif player_hand_total > dealer_hand_total:
                await ctx.send(f'<@{ctx.author.id}> wins {wager_amount} Dinz!')
                await add_dinz(ctx.author.id, wager_amount)
                return
            else:
                await ctx.send("The dealers flipped card was:")
                card = first_card
                with open(os.path.join(os.getcwd(), f'media\cards\{card}.png'), 'rb') as fp:
                    await ctx.send(file=discord.File(fp, 'card.png'))
                await ctx.send(f'<@{ctx.author.id}> loses {wager_amount} Dinz!')
                await add_dinz(ctx.author.id, (wager_amount * -1))
                return

#SHOP
@bot.command(name="shop", help="Enter the shop")
async def open_shop(ctx):
    shopper_id = ctx.author.id
    conn = create_connection()
    cur = create_cursor(conn)
    shopper_info = get_info(cur, shopper_id)
    shopper_dinz = shopper_info[0][1]
    shop_data = bot.shop_items
    item_data = []
    i = 0
    for item in shop_data:
        i += 1
        item_data.append(shop_data[f'Item{i}'])
    if shopper_dinz < 0:
         
        embed = discord.Embed(
            title="The Shop",
            description = f'{ctx.author.name}, you dare enter this shop without any dinz!?...',
            color = discord.Color.light_gray()
            )
        url = "https://i.imgur.com/mDIfpPO.png"
        embed.set_image(url)
        await ctx.send(embed=embed)
        return
    shop_embed = discord.Embed(
        title="The Shop",
        description = f'Welcome to the shop {ctx.author.name}! You currently have {shopper_dinz} dinz.',
        color = discord.Color.dark_magenta()
        )
    shop_embed.set_image(url="https://i.imgur.com/Fxcaw9A.png")
    shop_embed.set_footer(text="Can you handle the strongest of wares?")
    shop_embed.add_field(name="[1]. Mute someones text for 10s", value=f'{item_data[0]} Dinz', inline=False)
    shop_embed.add_field(name="[2]. Mute someones voice for 10s", value=f'{item_data[1]} Dinz', inline=False)
    shop_embed.add_field(name="[3]. Deafen someone for 10s", value=f'{item_data[2]} Dinz', inline=False)
    shop_embed.add_field(name="[4]. Change someones nickname", value=f'{item_data[3]} Dinz', inline=False)
    shop_embed.add_field(name="[5]. ????????????????", value=f'{item_data[4]} Dinz', inline=False)
    shop_embed.add_field(name="[6]. Kick someone from the server", value=f'{item_data[5]} Dinz', inline=False)
    shop_msg = await ctx.send(embed=shop_embed) 

    def check(m):
        return (m.content =="1" or m.content == "2" or m.content == "3" or m.content == "4" or m.content == "5" or m.content == "6") and m.author == ctx.author

    try:
        item_selected = await bot.wait_for("message", check=check, timeout=20)
    except asyncio.TimeoutError:
        await shop_msg.delete()
        seller_embed = discord.Embed(
            title="The Shop",
            description = f'I knew you couldnt handle my strongest wares {ctx.author.name}! Let this be a reminder...',
            color = discord.Color.dark_red()
            )
        seller_embed.set_footer(text ="And dont come back!")
        seller_embed.set_image(url="https://i.imgur.com/WLTRYyZ.png")
        await ctx.send(embed=seller_embed) 
        return
    
    await shop_msg.delete()

    #MONEY CHECK
    item_index = int(item_selected.content) - 1
    if shopper_dinz < item_data[item_index]:
        embed = discord.Embed(
            title="The Shop",
            description = f'{ctx.author.name}, you know you cannot afford such goods...',
            color = discord.Color.light_gray()
            )
        url = "https://i.imgur.com/t252pRI.png"
        embed.set_image(url=url)
        embed.set_footer(text="Buffoon...")
        await ctx.send(embed=embed)
        return
    #@ CHECK
    accept_embed = discord.Embed(
        title="The Shop",
        description = f'And daresay, what is the @ of the unfortunate soul you wish to inflict this upon?',
        color = discord.Color.orange()
        )
    accept_embed.set_footer(text="How devious...")
    accept_embed.set_image(url="https://i.imgur.com/kagjBVL.png")

    accept_msg = await ctx.send(embed=accept_embed)


    def check2(m):
        return m.author == ctx.author and len(m.mentions) == 1 and bot.user not in m.mentions
    try:
        chosen_user = await bot.wait_for("message", check=check2, timeout=10)
    except asyncio.TimeoutError:
        await accept_msg.delete()
        seller_embed = discord.Embed(
            title="The Shop",
            description = f'I knew you couldnt handle my strongest wares {ctx.author.name}! Let this be a reminder...',
            color = discord.Color.dark_red()
            )
        seller_embed.set_footer(text ="And dont come back!")
        seller_embed.set_image(url="https://i.imgur.com/WLTRYyZ.png")
        await ctx.send(embed=seller_embed)
        return


    #item logic 
    if item_selected.content == "1":
        await add_dinz(shopper_id, (item_data[0] * -1))
        await accept_msg.delete()
        guild = discord.utils.get(bot.guilds, name=GUILD)
        role = discord.utils.get(guild.roles, name="Muted")
        chosen_member = chosen_user.mentions
        total_roles = chosen_member[0].roles
        total_roles.append(role)
        await chosen_member[0].edit(roles=total_roles)
        await asyncio.sleep(10)
        await chosen_member[0].remove_roles(role)
    elif item_selected.content == "2":
        await add_dinz(shopper_id, (item_data[1] * -1))
        await accept_msg.delete()
        member = chosen_user.mentions[0]
        await member.edit(mute=True)
        await asyncio.sleep(10)
        await member.edit(mute=False)
    elif item_selected.content == "3":
        await add_dinz(shopper_id, (item_data[2] * -1))
        await accept_msg.delete()
        member = chosen_user.mentions[0]
        await member.edit(deafen=True)
        await asyncio.sleep(10)
        await member.edit(deafen=False)
    elif item_selected.content == "4":
       await add_dinz(shopper_id, (item_data[3] * -1))
       await accept_msg.delete()
       member = chosen_user.mentions[0]
       await ctx.send("What would the nickname be?")
       def check3(m):
           return m.author == ctx.author
       try:
           new_nickname = await bot.wait_for("message", check=check3, timeout=10)
       except asyncio.TimeoutError:
            await ctx.send("Timeouted. Thanks for the dinz")
            return
       await member.edit(nick=new_nickname.content)
    elif item_selected.content == "5":
        await add_dinz(shopper_id, (item_data[4] * -1))
        roll = random.randint(1,100)
        if roll == 50:
            await ctx.send("Congratz.......")
            await add_dinz(shopper_id, (item_data[4] * 2))
        else:
            await ctx.send("Hehe")
    elif item_selected.content == "6":
        await accept_msg.delete()
        await ctx.send("Hehe")
        await ctx.author.send("xP")

#edits shop prices 
@bot.command(name="price", help="<<price ItemX XXXXXXXX")
@commands.is_owner()
async def price_change(ctx, *, message=None):
    if not message:
        await ctx.send("Need message")
        return
    try:
        item = message.split(" ")[0]
        price = int(message.split(" ")[1])
    except:
        await ctx.send("Error with format")
        return
    if item == "Item1" or item == "Item2" or item == "Item3" or item == "Item4" or item == "Item5" or item == "Item6":
        edit_json(item, price, "shop.json")
        await ctx.send("Item changed")
    else:
        await ctx.send("Error with Item")
        return

#edits user dinz amount
@bot.command(name="add1", help="<<add1 discord_ID XXXXXXXXXX")
@commands.is_owner()
async def edit_dinz(ctx, *, message=None):
    if not message:
        await ctx.send("Need message")
        return
    discord_ID = message.split(" ")[0]
    
    try:
        amount = int(message.split(" ")[1])
    except ValueError:
        await ctx.send("Need int only")

    await add_dinz(discord_ID, amount)


#misc functions 
#checks if needed roles are created and adds them
async def create_roles(guild):
    poor_role = discord.utils.get(guild.roles, name='Poor')
    if not poor_role:
        poor_role = await guild.create_role(name="Poor", reason="There are poor people in the server", color=discord.Color.dark_green())
        permissions = discord.Permissions()
        permissions.update(change_nickname = False)
        await poor_role.edit(permissions=permissions)

    king_role = discord.utils.get(guild.roles, name='King Dinz')
    if not king_role:
        king_role = await guild.create_role(name="King Dinz", reason="Theres a king now...", color=discord.Color.teal())
        permissions = discord.Permissions()
        permissions.update(move_members=True)
        await king_role.edit(permissions=permissions)

    mute_role = discord.utils.get(guild.roles, name='Muted')
    if not mute_role:
        mute_role = await guild.create_role(name="Muted", reason="Shhh.")
        permissions = discord.Permissions()
        permissions.update(send_messages=False)
        await mute_role.edit(permissions=permissions)


#JSON fucntions

#Reads the JSON file and returns a dict
def read_json(filename):
    with open(os.path.join(os.getcwd(), f'{filename}')) as f:
        data = json.load(f)
    return data
#edits the json file and updates shop item
def edit_json(item, new_price, filename):
    data = bot.shop_items
    data[f'{item}'] = new_price
    with open(os.path.join(os.getcwd(), f'{filename}'), "w") as f:
        json.dump(data, f)
    bot.shop_items = read_json(filename)

#functions for database 

#creates connection to database used for game
def create_connection():
    connection = None
    try:
        connection = sqlite3.connect('game_database.db')
        return connection
    except Exception as e:
        print(e)
#creates a cursor using given connection, creates the base table 
def create_cursor(connection):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users(discord_id integer, dinz integer, last_daily text)")
        return cursor
    except Exception as e:
        print(e)
#adds given members to the database 
def add_members(members):
    conn = create_connection()
    cur = create_cursor(conn)
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    try:
        for member in members:
            member_exists = False
            for user in users:
                if member.id == user[0]:
                    member_exists = True
            if not member_exists:
                cur.execute("INSERT INTO users(discord_ID, dinz, last_daily) VALUES (?, 0, '01/01/2000')", (member.id, ))
                conn.commit()
    except Exception as e:
        print(e)
    conn.close()
#adds given member to the database 
def add_member(member):
    conn = create_connection()
    cur = create_cursor(conn)
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    member_exists = False
    try:
        for user in users:
            if member.id == user[0]:
                member_exists = True
    except Exception as e:
        print(e)
    if not member_exists: 
        cur.execute("INSERT INTO users(discord_ID, dinz, last_daily) VALUES (?, 0, '01/01/2000')", (member.id, ))
        conn.commit()
    conn.close()
#returns an array with a single tuple of given ID from database
def get_info(cursor, discord_ID):
    cursor.execute("SELECT * FROM users WHERE discord_ID=?", (discord_ID, ))
    return cursor.fetchall()
#updates given id's dinz by given amount (creates and closed its own connection to database)
async def add_dinz(discord_ID, dinz_won):
    conn = create_connection()
    cur = create_cursor(conn)
    user = get_info(cur, discord_ID)
    current_dinz = user[0][1]
    new_dinz = current_dinz + dinz_won 
    cur.execute("UPDATE users SET dinz=? WHERE discord_ID=?", ((new_dinz), discord_ID))
    #check_dinz(discord_ID, new_dinz)
    if new_dinz < 0:
        guild = discord.utils.get(bot.guilds, name=GUILD)
        role = discord.utils.get(guild.roles, name='Poor')
        member = await guild.fetch_member(discord_ID)
        await member.add_roles(role)
    elif new_dinz > 0 and current_dinz < 0:
        #REMOVE ROLE
        guild = discord.utils.get(bot.guilds, name=GUILD)
        role = discord.utils.get(guild.roles, name="Poor")
        member = await guild.fetch_member(discord_ID)
        await member.remove_roles(role)

    conn.commit()
    conn.close()


#functions for blackjack

#Draws the text version of the deck
def get_deck():
    deck = []
    for i in range(13):
        i = i+1
        if i == 1:
            deck.append("Ace of Clubs")
            deck.append("Ace of Diamonds")
            deck.append("Ace of Hearts")
            deck.append("Ace of Spades")
        elif i == 11:
            deck.append("Jack of Clubs")
            deck.append("Jack of Diamonds")
            deck.append("Jack of Hearts")
            deck.append("Jack of Spades")
        elif i == 12:
            deck.append("Queen of Clubs")
            deck.append("Queen of Diamonds")
            deck.append("Queen of Hearts")
            deck.append("Queen of Spades")
        elif i == 13:
            deck.append("King of Clubs")
            deck.append("King of Diamonds")
            deck.append("King of Hearts")
            deck.append("King of Spades")
        else:
            deck.append(f'{i} of Clubs')
            deck.append(f'{i} of Diamonds')
            deck.append(f'{i} of Hearts')
            deck.append(f'{i} of Spades')
    return deck
#Draws a card from the deck and pops out the drawn card and returns deck
def draw_card(deck):
    card = random.choice(deck)
    card_index = deck.index(card)
    deck.pop(card_index)
    return [deck, card]
#Draws a card from the deck and adds it to the text and num list for given hand
def draw_hand(deck, hand_text, hand):
    length = len(hand_text)
    draw = draw_card(deck)
    deck = draw[0]
    hand_text.append(draw[1])

    if length == 0:
        for card in hand_text:
            card_type = card.split(" ")[0]
            if card_type == "Jack" or card_type == "Queen" or card_type == "King":
                hand.append(10)
            elif card_type == "Ace":
                hand.append(11)
            else:
                hand.append(int(card_type))
    else:
        card = hand_text[length]
        card_type = card.split(" ")[0]
        if card_type == "Jack" or card_type == "Queen" or card_type == "King":
            hand.append(10)
        elif card_type == "Ace":
            hand.append(11)
        else:
            hand.append(int(card_type))
    return [deck, hand_text, hand]
#returns a list of files needed for the given hand 
def get_files(hand_text, isDealer=False):
    files = []
    if isDealer:
        hand_text[0] = "Back of Card"
        for card in hand_text:
            with open(os.path.join(os.getcwd(), f'media\cards\{card}.png'), 'rb') as fp:
                files.append(discord.File(fp, 'cardimage.png'))
    else:
        for card in hand_text:
            with open(os.path.join(os.getcwd(), f'media\cards\{card}.png'), 'rb') as fp:
                files.append(discord.File(fp, 'cardimage.png'))
    return files
#takes given info and sends the corrospoding images from hand 
async def send_card(deck, hand_text, hand, hand_total, isDealer, ctx):
    hand_set = draw_hand(deck, hand_text, hand)
    deck = hand_set[0]
    hand_text = hand_set[1]
    hand = hand_set[2]
    hand_total = get_total(hand)
    files = get_files(hand_text, isDealer)
    await ctx.send(files=files)
    return [deck, hand_text, hand, hand_total]
#returns int total of given hand 
def get_total(hand):
    hand_total = 0
    for card in hand:
        hand_total += card
    return hand_total
#checks if given hand has an ace and changes it to a 1 and returns hand 
def ace_check(hand, hand_total):
    hand_lose = False 
    ace_exist = False
    for card in hand:
        if card == 11:
            index = hand.index(card)
            hand[index] = 1
            ace_exist = True
            break
    if ace_exist:
        hand_total = 0
        for card in hand:
            hand_total += card
    if not ace_exist:
        hand_lose = True
    return [hand_lose, hand, hand_total]
#checks state of game 
def check_game(player_hand, player_hand_total, dealer_hand, dealer_hand_total):
    #returns a list with size depending on situation of game. list is always sent in same order regardless if values are needed for consistency 
    #index 0-3 must be checked in order to understand which values are needed
    player_win = False
    dealer_win = False
    player_has_ace = False
    dealer_has_ace = False
    if player_hand_total == 21:
        #player win
        player_win = True
        return [player_win, dealer_win, player_has_ace, dealer_has_ace]
    elif dealer_hand_total == 21 and player_hand_total != 21:
        #player lose
        dealer_win = True 
        return [player_win, dealer_win, player_has_ace, dealer_has_ace]
    elif player_hand_total > 21 and dealer_hand_total < 21:
        check_set = ace_check(player_hand, player_hand_total)
        if check_set[0]:
            #PLAYER LOSE
            dealer_win = True
            return [player_win, dealer_win, player_has_ace, dealer_has_ace]
        if not check_set[0]:
            player_hand = check_set[1]
            player_hand_total = check_set[2]
            player_has_ace = True
            #returns with new ace values
            return [player_win, dealer_win, player_has_ace, dealer_has_ace, player_hand, player_hand_total]
    elif dealer_hand_total > 21 and player_hand_total < 21:
        check_set = ace_check(dealer_hand, dealer_hand_total)
        if check_set[0]:
            #Player Win
            player_win = True
            return [player_win, dealer_win]
        if not check_set[0]:
            dealer_hand = check_set[1]
            dealer_hand_total = check_set[2]
            dealer_has_ace = True
            #end
            return [player_win, dealer_win, player_has_ace, dealer_has_ace, player_hand, player_hand_total, dealer_hand, dealer_hand_total]
    elif dealer_hand_total > 21 and player_hand_total > 21:
        player_check_set = ace_check(player_hand, player_hand_total)
        dealer_check_set = ace_check(dealer_hand, dealer_hand_total)
        if player_check_set[0]:
            #player lose
            dealer_win = True
            return [player_win, dealer_win, player_has_ace, dealer_has_ace]
        elif not player_check_set[0] and dealer_check_set[0]:
            #player win 
            player_win = True
            return [player_win, dealer_win, player_has_ace, dealer_has_ace]
        elif not player_check_set[0] and not dealer_check_set[0]:
            player_hand = player_check_set[1]
            player_hand_total = player_check_set[2]
            dealer_hand = dealer_check_set[1]
            dealer_hand_total = dealer_check_set[2]
            player_has_ace = True
            dealer_has_ace = True
            #end
            return [player_win, dealer_win, player_has_ace, dealer_has_ace, player_hand, player_hand_total, dealer_hand, dealer_hand_total]
    return [player_win, dealer_win, player_has_ace, dealer_has_ace]


bot.run(TOKEN)
