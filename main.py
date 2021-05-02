# base discord
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
# data processing
import json
import hashlib
import cloudscraper
# helper functions
import math

# token
load_dotenv()
token = os.getenv('token')
bot = commands.Bot(command_prefix='$')
bot.remove_command('help')
slash = SlashCommand(bot, sync_commands=True)

def reloadAPI():
    scraper = cloudscraper.create_scraper()
    global data
    data = scraper.get('https://sky.shiiyu.moe/api/v2/bazaar').text
    data = json.loads(data)
    # process data
    clean = []
    for (key, value) in data.items():
        clean.append({'id': key, 'name': value['name'], 'buyprice': value['buyPrice'], 'sellprice': value['sellPrice'], 'buyvolume': value['buyVolume'], 'sellvolume': value['sellVolume']})
    data = clean
    # add margins
    for item in data:
            if item['sellprice'] != 0:
                item['margin'] = (item['buyprice'] - item['sellprice']) / item['sellprice']
            else:
                item['margin'] = 0
    with open('test.json', 'w') as f:
        json.dump(data, f)

# init
@bot.event
async def on_ready():
    reloadAPI()
    # ah
    # ah_data=requests.get('https://api.hypixel.net/skyblock/auctions').text
    # with open('auction.json', 'w') as file:
    # file.write(ah_data)

# helper functions
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

# bazaar
@bot.command(name='bazaar')
async def bazaar(ctx):
    global data
    opt = ctx.message.content[8:]
    if len(opt) < 1:
        await ctx.send(embed=discord.Embed(title='Usage', description='$bazaar option (tierup, instanttierup, craft, instantcraft, margin))', type='rich', colour=discord.Colour.red()))
        return
    if opt == 'tierup':
        tierup = [
            # farming
            {'base': ['WHEAT'], 't1': ['ENCHANTED_BREAD', 60], 't2': ['HAY_BLOCK', 9], 't3': ['ENCHANTED_HAY_BLOCK', 1296], 't4': ['TIGHTLY_TIED_HAY_BALE', 186624]},
            {'base': ['CARROT_ITEM'], 't1': ['ENCHANTED_CARROT', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['POTATO_ITEM'], 't1': ['ENCHANTED_POTATO', 160], 't2': ['ENCHANTED_BAKED_POTATO', 25600], 't3': None, 't4': None},
            {'base': ['PUMPKIN'], 't1': ['ENCHANTED_PUMPKIN', 160], 't2': ['POLISHED_PUMPKIN', 25600], 't3': None, 't4': None},
            {'base': ['MELON'], 't1': ['ENCHANTED_MELON', 160], 't2': ['ENCHANTED_MELON_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['SEEDS'], 't1': ['ENCHANTED_SEEDS', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RED_MUSHROOM'], 't1': ['ENCHANTED_RED_MUSHROOM', 160], 't2': ['HUGE_MUSHROOM_2', 9], 't3': ['ENCHANTED_HUGE_MUSHROOM_2', 5184], 't4': None},
            {'base': ['BROWN_MUSHROOM'], 't1': ['ENCHANTED_BROWN_MUSHROOM', 160], 't2': ['HUGE_MUSHROOM_1', 9], 't3': ['ENCHANTED_HUGE_MUSHROOM_1', 5184], 't4': None},
            {'base': ['INK_SACK:3'], 't1': ['ENCHANTED_COCOA', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ENCHANTED_CACTUS_GREEN'], 't1': ['ENCHANTED_CACTUS', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SUGAR_CANE'], 't1': ['ENCHANTED_SUGAR', 160], 't2': ['ENCHANTED_PAPER', 192], 't3': ['ENCHANTED_SUGAR_CANE', 25600], 't4': None},
            {'base': ['FEATHER'], 't1': ['ENCHANTED_FEATHER', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LEATHER'], 't1': ['ENCHANTED_LEATHER', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RAW_BEEF'], 't1': ['ENCHANTED_RAW_BEEF', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['PORK'], 't1': ['ENCAHNTED_PORK', 160], 't2': ['ENCHANTED_GRILLED_PORK', 25600], 't3': None, 't4': None},
            {'base': ['RAW_CHICKEN'], 't1': ['ENCHANTED_RAW_CHICKEN', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ENCHANTED_EGG'], 't1': ['SUPER_EGG', 144], 't2': None, 't3': None, 't4': None},
            {'base': ['MUTTON'], 't1': ['ENCHANTED_MUTTON', 160], 't2': ['ENCHANTED_COOKED_MUTTON', 25600], 't3': None, 't4': None},
            {'base': ['RABBIT'], 't1': ['ENCHANTED_RABBIT', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RABBIT_FOOT'], 't1': ['ENCHANTED_RABBIT_FOOT', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RABBIT_HIDE'], 't1': ['ENCHANTED_RABBIT_HIDE', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['NETHER_STALK'], 't1': ['ENCHANTED_NETHER_STALK', 160], 't2': ['MUTANT_NETHER_STALK', 25600], 't3': None, 't4': None},
            # mining
            {'base': ['COBBLESTONE'], 't1': ['ENCHANTED_COBBLESTONE', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['COAL'], 't1': ['ENCHANTED_COAL', 160], 't2': ['ENCHANTED_COAL_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['IRON_INGOT'], 't1': ['ENCHANTED_IRON', 160], 't2': ['ENCHANTED_IRON_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['GOLD_INGOT'], 't1': ['ENCHANTED_GOLD', 160], 't2': ['ENHANTED_GOLD_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['DIAMOND'], 't1': ['ENCHANTED_DIAMOND', 160], 't2': ['ENCHANTED_DIAMOND_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['INK_SACK:4'], 't1': ['ENCHANTED_LAPIS_LAZULI', 160], 't2': ['ENCHANTED_LAPIS_LAZULI_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['EMERALD'], 't1': ['ENCHANTED_EMERALD', 160], 't2': ['ENCHANTED_EMERALD_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['REDSTONE'], 't1': ['ENCHANTED_REDSTONE', 160], 't2': ['ENCHANTED_REDSTONE_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['QUARTZ'], 't1': ['ENCHANTED_QUARTZ', 160], 't2': ['ENCHANTED_QUARTZ_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['OBSIDIAN'], 't1': ['ENCHANTED_OBSIDIAN', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['GLOWSTONE_DUST'], 't1': ['ENCHANTED_GLOWSTONE_DUST', 160], 't2': ['ENCHANTED_GLOWSTONE', 30720], 't3': None, 't4': None},
            {'base': ['FLINT'], 't1': ['ENCHANTED_FLINT', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ICE'], 't1': ['PACKED_ICE', 9], 't2': ['ENCHANTED_ICE', 160], 't3': ['ENCHANTED_PACKED_ICE', 25600], 't4': None},
            {'base': ['NETHERRACK'], 't1': ['ENCHANTED_NETHERRACK', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SAND'], 't1': ['ENCHANTED_SAND', ], 't2': None, 't3': None, 't4': None},
            {'base': ['ENDSTONE'], 't1': ['ENCHANTED_ENDSTONE', ], 't2': None, 't3': None, 't4': None},
            {'base': ['SNOW_BALL'], 't1': ['SNOW_BLOCK', 9], 't2': ['ENCHANTED_SNOW_BLOCK', 1440], 't3': None, 't4': None},
            {'base': ['MITHRIL_ORE'], 't1': ['ENCHANTED_MITHRIL', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['TITANIUM_ORE'], 't1': ['ENCHANTED_TITANIUM', 160], 't2': None, 't3': None, 't4': None},
            # combat
            {'base': ['ROTTEN_FLESH'], 't1': ['ENCHANTED_ROTTEN_FLESH', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['BONE'], 't1': ['ENCHANTED_BONE', 160], 't2': ['ENCHANTED_BONE_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['STRING'], 't1': ['ENCHANTED_STRING', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SPIDER_EYE'], 't1': ['ENCHANTED_SPIDER_EYE', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['GUNPOWDER'], 't1': ['ENCHANTED_GUNPOWDER', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ENDER_PEARL'], 't1': ['ENCHANTED_ENDER_PEARL', 20], 't2': None, 't3': None, 't4': None},
            {'base': ['GHAST_TEAR'], 't1': ['ENCHANTED_GHAST_TEAR', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SLIME_BALL'], 't1': ['ENCHANTED_SLIME_BALL', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['BLAZE_ROD'], 't1': ['ENCHANTED_BLAZE_POWDER', 160], 't2': ['ENCHANTED_BLAZE_ROD', 25600], 't3': None, 't4': None},
            {'base': ['MAGMA_CREAM'], 't1': ['ENCHANTED_MAGMA_CREAM', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ANCIENT_CLAW'], 't1': ['ENCHANTED_ANCIENT_CLAW', 160], 't2': None, 't3': None, 't4': None},
            # woods
            {'base': ['LOG'], 't1': ['ENCHANTED_OAK_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG:2'], 't1': ['ENCHANTED_BIRCH_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG:1'], 't1': ['ENCHANTED_SPRUCE_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG_2:1'], 't1': ['ENCHANTED_DARK_OAK_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG_2'], 't1': ['ENCHANTED_ACACIA_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG:3'], 't1': ['ENCHANTED_JUNGLE_LOG', 160], 't2': None, 't3': None, 't4': None},
            # fish
            {'base': ['RAW_FISH'], 't1': ['ENCHANTED_RAW_FISH', 160], 't2': ['ENCHANTED_COOKED_FISH', 25600], 't3': None, 't4': None},
            {'base': ['RAW_FISH:1'], 't1': ['ENCHANTED_RAW_SALMON', 160], 't2': ['ENCHANTED_COOKED_SALMON', 25600], 't3': None, 't4': None},
            {'base': ['RAW_FISH:2'], 't1': ['ENCHANTED_CLOWNFISH', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RAW_FISH:3'], 't1': ['ENCHANTED_PUFFERFISH', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['PRISMARINE_SHARD'], 't1': ['ENCHANTED_PRISMARINE_SHARD', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['PRISMARINE_CRYSTAL'], 't1': ['ENCHANTED_PRISMARINE_CRYSTAL', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['CLAY_BALL'], 't1': ['ENCHANTED_CLAY_BALL', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['WATER_LILY'], 't1': ['ENCHANTED_WATER_LILY', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['INK_SACK'], 't1': ['ENCHANTED_INK_SACK', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SPONGE'], 't1': ['ENCHANTED_SPONGE', 40], 't2': ['ENCHANTED_WET_SPONGE', 1600], 't3': None, 't4': None},
            {'base': ['SHARK_FIN'], 't1': ['ENCHANTED_SHARK_FIN', 160], 't2': None, 't3': None, 't4': None},
        ]
        # index through all of them keep track of which is highest keep in 2d list and able to use sorted()
        for item in tierup:
            for otheritem in data:
                if item['base'] == otheritem['id']:
                    item['base'].extend([otheritem['sellprice'], otheritem['buyprice']])
                if item['t1'] != None:
                    if item['t1'][0] == otheritem['id']:
                        item['t1'].extend([otheritem['sellprice'], otheritem['buyprice']])
                if item['t2'] != None:
                    if item['t2'][0] == otheritem['id']:
                        item['t2'].extend([otheritem['sellprice'], otheritem['buyprice']])
                if item['t3'] != None:
                    if item['t3'][0] == otheritem['id']:
                        item['t3'].extend([otheritem['sellprice'], otheritem['buyprice']])
                if item['t4'] != None:
                    if item['t4'][0] == otheritem['id']:
                        item['t4'].extend([otheritem['sellprice'], otheritem['buyprice']])
                    
        pass
    elif opt == 'craft':
        craft = [

        ]
        pass
    #elif opt == 'volume':
        # function of (x^2-y^2)^2 to punish for a large difference between sale and buy
    #    pass
    elif opt == 'margin':
        #best = ['hi', 0]
        #for (key, value) in data.items():
            #if value['sellprice'] != 0:
                #value['margin'] = float((value['buyprice'] - value['sellprice']) / value['sellprice'])
                #if float((value['buyprice'] - value['sellprice']) / value['sellprice']) > best[1]:
                    #best[0], best[1] = value['name'], truncate(float((value['buyprice'] - value['sellprice']) / value['sellprice']), 2)
        data = sorted(data, key = lambda x: x['margin'], reverse=True)
        embed = discord.Embed(title='Best Bazaar Flips for Margin', description='List of best Margin flips.', footer=hashlib.md5(str(data).encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.green())
        for i in range(10):
            embed.add_field(name=f'{i+1}. {data[i]["name"]}', value=f'{int(data[i]["margin"]*10000)/100}% at {int((data[i]["buyprice"]-data[i]["sellprice"])*10000)/100} per item.')
        await ctx.send(embed=embed)
    # add 'misc'
    # things like refining and others

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