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
async def bazaar(ctx):
    dat = ctx.message.content[8:].split()
    opt = dat[0]
    global data
    if len(dat) < 1 or opt not in ['tierup', 'instanttierup', 'craft', 'instantcraft', 'margin', 'sc3k', 'catalyst', 'lava_bucket', 'carrot_candy', 'exp_bottle', 'backpack', 'minion_storage']:
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
    # specific items
    elif opt == 'sc3k':
        cost = 0
        for item in data:
            if item['id'] == 'SUPER_COMPACTOR_3000':
                revenue = item['buyprice']
            elif item['id'] == 'ENCHANTED_COBBLESTONE':
                cost += item['sellprice'] * 448
            elif item['id'] == 'ENCHANTED_REDSTONE_BLOCK':
                cost += item['sellprice']
        embed = discord.Embed(title='Super Compactor 3000', description='Bazaar Statistics', type='rich', colour = discord.Colour.blurple())
        embed.add_field(name = 'Material Cost', value = '{:,} coins'.format(truncate(cost, 2)))
        embed.add_field(name = 'Sell Value', value = '{:,} coins'.format(truncate(revenue, 2)))
        embed.add_field(name = 'Profit Margins', value = '{:,}% or {:,} coins per item'.format(truncate((revenue - cost)*100/cost, 2), truncate(revenue-cost, 2)))
        await ctx.send(embed=embed)
    elif opt == 'catalyst':
        for item in data:
            if item['id'] == 'HYPER_CATALYST':
                revenue = item['buyprice'] * 8
            elif item['id'] == 'CATALYST':
                cost = item['sellprice'] * 8
        embed = discord.Embed(title='Hyper Catalyst', description='Bazaar Statistics for 8x Catalysts/Hyper Catalysts', type='rich', colour = discord.Colour.blurple())
        embed.add_field(name = 'Material Cost', value = '{:,} coins'.format(truncate(cost, 2)))
        embed.add_field(name = 'Sell Value', value = '{:,} coins'.format(truncate(revenue, 2)))
        embed.add_field(name = 'Maximum Price of Hyper Catalyst Upgrades for a guaranteed Profit', value = '{:,} coins'.format(int(revenue - cost)))
        embed.add_field(name = 'Maximum Price of Hyper Catalyst Upgrades for a 5% Profit', value = '{:,} coins'.format(int((100 * revenue) / 105 - cost)))
        embed.add_field(name = 'Maximum Price of Hyper Catalyst Upgrades for a 10% Profit', value = '{:,} coins'.format(int((100 * revenue) / 110 - cost)))
        embed.add_field(name = 'Maximum Price of Hyper Catalyst Upgrades for a 15% Profit', value = '{:,} coins'.format(int((100 * revenue) / 115 - cost)))
        embed.add_field(name = 'Maximum Price of Hyper Catalyst Upgrades for a 20% Profit', value = '{:,} coins'.format(int((100 * revenue) / 120 - cost)))
        await ctx.send(embed=embed)
    elif opt == 'lava_bucket':
        if len(dat) != 2:
            await ctx.send(embed=discord.Embed(title='Usage', description='$bazaar lava_bucket [heat core price]', type='rich', colour=discord.Colour.red()))
        for item in data:
            if item['id'] == 'ENCHANTED_LAVA_BUCKET':
                elavabuy = item['sellprice']
            elif item['id'] == 'MAGMA_BUCKET':
                magmabuy = item['sellprice']
                magmasell = item['buyprice']
            elif item['id'] == 'PLASMA_BUCKET':
                plasmasell = item['buyprice']
        heat_core = int(dat[1])
        embed = discord.Embed(title='Magma Bucket/Plasma Bucket', description='Bazaar Statistics for Enchanted Lava/Magma/Plasma Buckets', type='rich', colour = discord.Colour.blurple())
        embed.add_field(name = 'Enchanted -> Magma', value = '{:,}% or {:,} coins profit'.format(truncate((magmasell - heat_core - (2*elavabuy))*100/(heat_core + (2*elavabuy)), 2), truncate(magmasell - heat_core - (2*elavabuy), 2)))
        embed.add_field(name = 'Enchanted -> Plasma', value = '{:,}% or {:,} coins profit'.format(truncate((plasmasell - (2*heat_core) - (4*elavabuy))*100/((2*heat_core) + (4*elavabuy)), 2), truncate(plasmasell - (2*heat_core) - (4*elavabuy), 2)))
        embed.add_field(name = 'Magma -> Plasma', value = '{:,}% or {:,} coins profit'.format(truncate((plasmasell - heat_core  - (2*magmabuy))*100/(heat_core + (2*magmabuy)), 2), truncate(plasmasell - heat_core  - (2*magmabuy), 2)))
        await ctx.send(embed=embed)
    elif opt == 'carrot_candy':
        if len(dat) != 4:
            await ctx.send(embed=discord.Embed(title='Usage', description='$bazaar carrot_candy [superb carrot candy price] [ultimate carrot candy price] [ultimate carrot candy upgrade price]', type='rich', colour=discord.Colour.red()))
        else:
            revenue = 10 * int(dat(2))
            cost = 8 * int(dat[1]) + int(dat[3])
            embed = discord.Embed(title='Ultimate Carrot Candy', description='Bazaar Statistics for 8x Super Carrot Candy/10x Hyper Catalysts', type='rich', colour = discord.Colour.blurple())
            embed.add_field(name = 'Profit in Percent', value = '{:,}%'.format(truncate((revenue - cost)*100/cost, 2)))
            embed.add_field(name = 'Protit in Coins', value = '{:,} coins'.format(truncate(revenue-cost, 2)))
            await ctx.send(embed=embed)
    elif opt == 'exp_bottle':
        for item in data:
            if item['id'] == 'COLOSSAL_EXP_BOTTLE':
                revenue = item['buyprice']
            elif item['id'] == 'TITANIC_EXP_BOTTLE':
                cost = item['sellprice']
        embed = discord.Embed(title='Colossal Exp Bottles', description='Bazaar Statistics for Colossal/Titanic Exp Bottles', type='rich', colour = discord.Colour.blurple())
        embed.add_field(name = 'Material Cost', value = '{:,} coins'.format(truncate(cost, 2)))
        embed.add_field(name = 'Sell Value', value = '{:,} coins'.format(truncate(revenue, 2)))
        embed.add_field(name = 'Maximum Price of Colossal Experience Bottle Upgrades for a guaranteed Profit', value = '{:,} coins'.format(int(revenue - cost)))
        embed.add_field(name = 'Maximum Price of Colossal Experience Bottle Upgrades for a 5% Profit', value = '{:,} coins'.format(int((100 * revenue) / 105 - cost)))
        embed.add_field(name = 'Maximum Price of Colossal Experience Bottle Upgrades for a 10% Profit', value = '{:,} coins'.format(int((100 * revenue) / 110 - cost)))
        embed.add_field(name = 'Maximum Price of Colossal Experience Bottle Upgrades for a 15% Profit', value = '{:,} coins'.format(int((100 * revenue) / 115 - cost)))
        embed.add_field(name = 'Maximum Price of Colossal Experience Bottle Upgrades for a 20% Profit', value = '{:,} coins'.format(int((100 * revenue) / 120 - cost)))
        await ctx.send(embed=embed)
    elif opt == 'backpack':
        if len(dat) != 4:
            await ctx.send(embed=discord.Embed(title='Usage', description='$bazaar backpack [greater backpack price] [jumbo backpack price] [jumbo backpack upgrade price]', type='rich', colour=discord.Colour.red()))
        else:
            revenue = int(dat(2))
            cost = int(dat[1]) + int(dat[3])
            embed = discord.Embed(title='Jumbo Backpack', description='Bazaar Statistics for Greater/Jumbo Backpack', type='rich', colour = discord.Colour.blurple())
            embed.add_field(name = 'Profit in Percent', value = '{:,}%'.format(truncate((revenue - cost)*100/cost, 2)))
            embed.add_field(name = 'Protit in Coins', value = '{:,} coins'.format(truncate(revenue-cost, 2)))
            await ctx.send(embed=embed)
    elif opt == 'minion_storage':
        if len(dat) != 5:
            await ctx.send(embed=discord.Embed(title='Usage', description='$bazaar minion_storage [large storage price] [x-large storage price] [xx-large storage price] [minion storage x-pender price]', type='rich', colour=discord.Colour.red()))
        else:
            large = int(1)
            xl = int(2)
            xxl = int(3)
            upgrade = int(4)
            embed = discord.Embed(title='Large/X-Large/XX-Large Storage', description='Bazaar Statistics for Large/X-Large')
            embed.add_field(name='Large -> X-Large', value = '{:,}% or {:,} coins profit'.format(truncate((xl - large - upgrade)*100/(large + upgrade), 2), truncate((xl - large - upgrade), 2)))
            embed.add_field(name='Large -> XX-Large', value = '{:,}% or {:,} coins profit'.format(truncate((xxl - large - (2*upgrade))*100/(large + (2*upgrade)), 2), truncate((xxl - large - (2*upgrade)), 2)))
            embed.add_field(name='X-Large -> XX-Large', value = '{:,}% or {:,} coins profit'.format(truncate((xxl - xl - upgrade)*100/(xl + upgrade), 2), truncate((xxl - xl - upgrade), 2)))
            await ctx.send(embed=embed)

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
