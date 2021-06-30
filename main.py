# base discord
import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
# data processing
import json
import hashlib
import requests
# helper functions
import math

# token
load_dotenv()
token = os.getenv('token')
bot = commands.Bot(command_prefix='$')
bot.remove_command('help')
slash = SlashCommand(bot, sync_commands=True)

def reloadAPI():
    global data
    data = requests.get('https://api.hypixel.net/skyblock/bazaar?key=', os.getenv('apikey')).text
    data = json.loads(data)
    # process data
    clean = []
    with open('clean_names.json', 'r') as f:
        clean_names = json.load(f)
    for value in data['products'].values():
        clean.append({'id': value['product_id'], 'name': clean_names[value['product_id']], 'buyprice': value['quick_status']['buyPrice'], 'sellprice': value['quick_status']['sellPrice'], 'buyvolume': value['quick_status']['buyVolume'], 'sellvolume': value['quick_status']['sellVolume']})
    data = clean
    for item in data:
            if item['sellprice'] != 0:
                item['margin'] = (item['buyprice'] - item['sellprice']) / item['sellprice']
            else:
                item['margin'] = 0
    with open('tierup.json', 'r') as f:
        global tierup
        tierup = json.load(f)
    with open('craft.json', 'r') as f:
        global craft
        craft = json.load(f)
# init
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="$help"))
    bot.loop.create_task(reloadAPIdiscord())
    # ah
    # ah_data=requests.get('https://api.hypixel.net/skyblock/auctions').text
    # with open('auction.json', 'w') as file:
    # file.write(ah_data)

async def reloadAPIdiscord():
    while True:
        reloadAPI()
        await asyncio.sleep(5)

# helper functions
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

# bazaar
@bot.command(name='bazaar')
async def bazaar(ctx, opt):
    global data
    if len(opt) < 1 or opt not in ['tierup', 'instanttierup', 'craft', 'instantcraft', 'margin']:
        await ctx.send(embed=discord.Embed(title='Usage', description='$bazaar option (tierup, instanttierup, craft, instantcraft, margin)', type='rich', colour=discord.Colour.red()))
        return
    if opt == 'tierup' or opt == 'instanttierup':
        # index through all of them keep track of which is highest keep in 2d list and able to use sorted()
        global tierup
        for item in tierup:
            for otheritem in data:
                if item['base'][0] == otheritem['id']:
                    item['base'].extend([otheritem['sellprice'], otheritem['buyprice'], otheritem['name']])
                if item['compacted'][0] == otheritem['id']:
                    item['compacted'].extend([otheritem['sellprice'], otheritem['buyprice'], otheritem['name']])
            item['margin'] = (float(item['compacted'][3]) - (item['compacted'][1] * item['base'][1]))
            item['marginpercent'] = (float(item['compacted'][3]) - (item['compacted'][1] * item['base'][1])) / (item['compacted'][1] * item['base'][1])
            item['instantmargin'] = (float(item['compacted'][2]) - (item['compacted'][1] * item['base'][2]))
            item['instantmarginpercent'] = (float(item['compacted'][2]) - (item['compacted'][1] * item['base'][2])) / (item['compacted'][1] * item['base'][2])
        if opt == 'tierup':
            tierup = sorted(tierup, key = lambda x: x['marginpercent'], reverse=True)
            embed = discord.Embed(title='Best Bazaar Tier-up Flips', description='Buy order at +0.1, personal compact, and sell order at -0.1', footer=hashlib.md5(str(data).encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.green())
            for i in range(16):
                embed.add_field(name=f'{i+1}. {tierup[i]["compacted"][4]}', value=f'Buy {tierup[i]["compacted"][1]}x {tierup[i]["base"][3]} at {truncate(tierup[i]["marginpercent"]*100,2)}% or {truncate(tierup[i]["margin"],2)} coins profit per item.')
        elif opt == 'instanttierup':
            tierup = sorted(tierup, key = lambda x: x['instantmarginpercent'], reverse=True)
            embed = discord.Embed(title='Best Bazaar Tier-up Flips', description='Instant-buy, personal compact, and instant-sell', footer=hashlib.md5(str(data).encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.green())
            for i in range(16):
                embed.add_field(name=f'{i+1}. {tierup[i]["compacted"][4]}', value=f'Instant-buy {tierup[i]["compacted"][1]}x {tierup[i]["base"][3]} at {truncate(tierup[i]["instantmarginpercent"]*100,2)}% or {truncate(tierup[i]["instantmargin"],2)} coins profit per item.')
        await ctx.send(embed=embed)
    elif opt == 'craft' or opt == 'instantcraft':
        global craft
        for item in craft:
            for requirement in item['requirements']:
                # prevent npc items
                if len(item) == 2:
                    for dat in data:
                        if dat['id'] == requirement[0]:
                            if opt == 'craft':
                                requirement.append(dat['sellprice'])
                                requirement.append(requirement[1] * dat['sellprice'])
                            if opt == 'instantcraft':
                                requirement.append(dat['buyprice'])
                                requirement.append(requirement[1] * dat['buyprice'])
            x = 0
            for requirement in item['requirements']:
                x += requirement[2]
            item['requirements'].append(x)
            for dat in data:
                if dat['id'] == item['crafted'][0]:
                    if opt == 'craft':
                        item['crafted'].append(dat['buyprice'])
                    if opt == 'instantcraft':
                        item['crafted'].append(dat['sellprice'])
                    item['name'] = dat['name']
                for req in item['requirements']:
                    if isinstance(req, float) or isinstance(req, int):
                        continue
                    if dat['id'] == req[0]:
                        req.append(dat['name'])
        craft = sorted(craft, key = (lambda x: x['crafted'][-1] / x['requirements'][-1]), reverse=True)
        embed = discord.Embed(title='Best Bazaar Craft Flips', description='Buy order at +0.1, craft/quick-craft, and sell order at -0.1', footer=hashlib.md5(str(data).encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.green())
        for i in range(16):
            x = ''
            for a in range(len(craft[i]['requirements'])-1):
                x += f'{craft[i]["requirements"][a][1]}x {craft[i]["requirements"][a][-1]} '
            embed.add_field(name=f'{i+1}. {craft[i]["name"]}', value=f'Buy {x}for {truncate(((craft[i]["crafted"][-1] / craft[i]["requirements"][-1])*10000)/10000, 2)}% or {truncate(craft[i]["crafted"][-1] - craft[i]["requirements"][-1], 2)} coins profit per item.')
        await ctx.send(embed=embed)
    #elif opt == 'volume':
        # function of (x^2-y^2)^2 to punish for a large difference between sale and buy
    #    pass
    elif opt == 'margin':
        data = sorted(data, key = lambda x: x['margin'], reverse=True)
        embed = discord.Embed(title='Best Bazaar Flips for Margin', description='Buy order at +0.1 and sell order at -0.1', footer=hashlib.md5(str(data).encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.green())
        for i in range(16):
            embed.add_field(name=f'{i+1}. {data[i]["name"]}', value=f'{int(data[i]["margin"]*100)/100}% at {truncate(data[i]["buyprice"]-data[i]["sellprice"],2)} per item.')
        await ctx.send(embed=embed)
    # add 'misc'
    # things like refining and others

# dragons profit calculator
@bot.command(name='dragons')
async def dragons(ctx):
    dragons = {'SUMMONING_EYE': [], 'FRAGMENTS': {}, 'ARMORS': {}, 'RARE_DROPS': {}}
    global data
    for item in data:
        if item['id'] == 'SUMMONING_EYE':
            eye.extend([item['sellprice'], item['buyprice']])

# reload api
@bot.command(name='reload')
async def reload(ctx):
    reloadAPI()
    global data
    # ah
    # ah_data=requests.get('https://api.hypixel.net/skyblock/auctions').text
    # with open('auction.json', 'w') as file:
    # file.write(ah_data)
    await ctx.send(embed=discord.Embed(title='Successfully Reloaded API', description=hashlib.md5(str(data).encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.green()))

# debug command
@bot.command(name='debug')
async def debug(ctx):
    if ctx.author.id == 750055850889969725:
        global data
        bz_data = data
        await ctx.send(embed=discord.Embed(title='Debug Info', description=hashlib.md5(str(bz_data).encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.red()))
        await ctx.send(file=discord.File('data.json'))

# help command
@bot.command(name='help')
async def help(ctx):
    embed=discord.Embed(title='Command List', description='Commands Available to You', type='rich', colour=discord.Colour.blue())
    embed.add_field(name='$bazaar [options]', value='Queries the bazaar for the best flips', inline=False)
    embed.add_field(name='$bazaar **CONTINUED**', value='tierup: personal compactable, instanttierup: instant buy and instant selling, craftable: non-personal compactable, instantcraft: instant buy and instant sell, margin: high margin flips')
    embed.add_field(name='$auction', value='Queries the auction house for the best flips **COMING SOON!!**', inline=False)
    if ctx.author.id == 750055850889969725:
        embed.add_field(name='$reload', value='Reloads the Hypixel API', inline=False)
        embed.add_field(name='$debug', value='Shows current Internal State', inline=False)
    await ctx.send(embed=embed)


bot.run(token)
