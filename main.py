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
    with open('data.json', 'w') as f:
        json.dump(data, f)

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
        tierup = [
            # farming
            #{'base': ['WHEAT'], 't1': ['ENCHANTED_BREAD', 60], 't2': ['HAY_BLOCK', 9], 't3': ['ENCHANTED_HAY_BLOCK', 1296], 't4': ['TIGHTLY_TIED_HAY_BALE', 186624]},
            {'base': ['WHEAT'], 'compacted': ['ENCHANTED_BREAD', 60]},
            {'base': ['WHEAT'], 'compacted': ['HAY_BLOCK', 9]},
            {'base': ['WHEAT'], 'compacted': ['ENCHANTED_HAY_BLOCK', 1296]},
            {'base': ['HAY_BLOCK'], 'compacted': ['ENCHANTED_HAY_BLOCK', 144]},
            {'base': ['WHEAT'], 'compacted': ['TIGHTLY_TIED_HAY_BALE', 186624]},
            {'base': ['HAY_BLOCK'], 'compacted': ['TIGHTLY_TIED_HAY_BALE', 20736]},
            {'base': ['ENCHANTED_HAY_BLOCK'], 'compacted': ['TIGHTLY_TIED_HAY_BALE', 144]},
            #{'base': ['CARROT_ITEM'], 't1': ['ENCHANTED_CARROT', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['CARROT_ITEM'], 'compacted': ['ENCHANTED_CARROT', 160]},
            #{'base': ['POTATO_ITEM'], 't1': ['ENCHANTED_POTATO', 160], 't2': ['ENCHANTED_BAKED_POTATO', 25600], 't3': None, 't4': None},
            {'base': ['POTATO_ITEM'], 'compacted': ['ENCHANTED_POTATO', 160]},
            {'base': ['POTATO_ITEM'], 'compacted': ['ENCHANTED_BAKED_POTATO', 25600]},
            {'base': ['ENCHANTED_POTATO'], 'compacted': ['ENCHANTED_BAKED_POTATO', 160]},
            #{'base': ['PUMPKIN'], 't1': ['ENCHANTED_PUMPKIN', 160], 't2': ['POLISHED_PUMPKIN', 25600], 't3': None, 't4': None},
            {'base': ['PUMPKIN'], 'compacted': ['ENCHANTED_PUMPKIN', 160]},
            {'base': ['PUMPKIN'], 'compacted': ['POLISHED_PUMPKIN', 25600]},
            {'base': ['ENCHANTED_PUMPKIN'], 'compacted': ['POLISHED_PUMPKIN', 160]},
            #{'base': ['MELON'], 't1': ['ENCHANTED_MELON', 160], 't2': ['ENCHANTED_MELON_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['MELON'], 'compacted': ['ENCHANTED_MELON', 160]},
            {'base': ['MELON'], 'compacted': ['ENCHANTED_MELON_BLOCK', 25600]},
            {'base': ['ENCHANTED_MELON'], 'compacted': ['ENCHANTED_MELON_BLOCK', 160]},
            #{'base': ['SEEDS'], 't1': ['ENCHANTED_SEEDS', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SEEDS'], 'compacted': ['ENCHANTED_SEEDS', 160]},
            #{'base': ['RED_MUSHROOM'], 't1': ['ENCHANTED_RED_MUSHROOM', 160], 't2': ['HUGE_MUSHROOM_2', 9], 't3': ['ENCHANTED_HUGE_MUSHROOM_2', 5184], 't4': None},
            {'base': ['RED_MUSHROOM'], 'compacted': ['ENCHANTED_RED_MUSHROOM', 160]},
            {'base': ['RED_MUSHROOM'], 'compacted': ['HUGE_MUSHROOM_2', 9]},
            {'base': ['RED_MUSHROOM'], 'compacted': ['ENCHANTED_HUGE_MUSHROOM_2', 5184]},
            {'base': ['HUGE_MUSHROOM_2'], 'compacted': ['ENCHANTED_HUGE_MUSHROOM_2', 576]},
            #{'base': ['BROWN_MUSHROOM'], 't1': ['ENCHANTED_BROWN_MUSHROOM', 160], 't2': ['HUGE_MUSHROOM_1', 9], 't3': ['ENCHANTED_HUGE_MUSHROOM_1', 5184], 't4': None},
            {'base': ['BROWN_MUSHROOM'], 'compacted': ['ENCHANTED_BROWN_MUSHROOM', 160]},
            {'base': ['BROWN_MUSHROOM'], 'compacted': ['HUGE_MUSHROOM_1', 9]},
            {'base': ['BROWN_MUSHROOM'], 'compacted': ['ENCHANTED_HUGE_MUSHROOM_1', 5184]},
            {'base': ['HUGE_MUSHROOM_1'], 'compacted': ['ENCHANTED_HUGE_MUSHROOM_1', 576]},
            #{'base': ['INK_SACK:3'], 't1': ['ENCHANTED_COCOA', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['INK_SACK:3'], 'compacted': ['ENCHANTED_COCOA', 160]},
            #{'base': ['ENCHANTED_CACTUS_GREEN'], 't1': ['ENCHANTED_CACTUS', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ENCHANTED_CACTUS_GREEN'], 'compacted': ['ENCHANTED_CACTUS', 160]},
            #{'base': ['SUGAR_CANE'], 't1': ['ENCHANTED_SUGAR', 160], 't2': ['ENCHANTED_PAPER', 192], 't3': ['ENCHANTED_SUGAR_CANE', 25600], 't4': None},
            {'base': ['SUGAR_CANE'], 'compacted': ['ENCHANTED_SUGAR', 160]},
            {'base': ['SUGAR_CANE'], 'compacted': ['ENCHANTED_PAPER', 192]},
            {'base': ['SUGAR_CANE'], 'compacted': ['ENCHANTED_SUGAR_CANE', 25600]},
            {'base': ['ENCHANTED_SUGAR'], 'compacted': ['ENCHANTED_SUGAR_CANE', 25600]},
            #{'base': ['FEATHER'], 't1': ['ENCHANTED_FEATHER', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['FEATHER'], 'compacted': ['ENCHANTED_FEATHER', 160]},
            #{'base': ['LEATHER'], 't1': ['ENCHANTED_LEATHER', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LEATHER'], 'compacted': ['ENCHANTED_LEATHER', 576]},
            #{'base': ['RAW_BEEF'], 't1': ['ENCHANTED_RAW_BEEF', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RAW_BEEF'], 'compacted': ['ENCHANTED_RAW_BEEF', 160]},
            #{'base': ['PORK'], 't1': ['ENCAHNTED_PORK', 160], 't2': ['ENCHANTED_GRILLED_PORK', 25600], 't3': None, 't4': None},
            {'base': ['PORK'], 'compacted': ['ENCHANTED_PORK', 160]},
            {'base': ['PORK'], 'compacted': ['ENCHANTED_GRILLED_PORK', 25600]},
            {'base': ['ENCHANTED_PORK'], 'compacted': ['ENCHANTED_GRILLED_PORK', 160]},
            #{'base': ['RAW_CHICKEN'], 't1': ['ENCHANTED_RAW_CHICKEN', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RAW_CHICKEN'], 'compacted': ['ENCHANTED_RAW_CHICKEN', 160]},
            #{'base': ['ENCHANTED_EGG'], 't1': ['SUPER_EGG', 144], 't2': None, 't3': None, 't4': None},
            {'base': ['ENCHANTED_EGG'], 'compacted': ['SUPER_EGG', 144]},
            #{'base': ['MUTTON'], 't1': ['ENCHANTED_MUTTON', 160], 't2': ['ENCHANTED_COOKED_MUTTON', 25600], 't3': None, 't4': None},
            {'base': ['MUTTON'], 'compacted': ['ENCHANTED_MUTTON', 160]},
            {'base': ['MUTTON'], 'compacted': ['ENCHANTED_COOKED_MUTTON', 25600]},
            {'base': ['ENCHANTED_MUTTON'], 'compacted': ['ENCHANTED_COOKED_MUTTON', 160]},
            #{'base': ['RABBIT'], 't1': ['ENCHANTED_RABBIT', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RABBIT'], 'compacted': ['ENCHANTED_RABBIT', 160]},
            #{'base': ['RABBIT_FOOT'], 't1': ['ENCHANTED_RABBIT_FOOT', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RABBIT_FOOT'], 'compacted': ['ENCHANTED_RABBIT_FOOT', 160]},
            #{'base': ['RABBIT_HIDE'], 't1': ['ENCHANTED_RABBIT_HIDE', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RABBIT_HIDE'], 'compacted': ['ENCHANTED_RABBIT_HIDE', 576]},
            #{'base': ['NETHER_STALK'], 't1': ['ENCHANTED_NETHER_STALK', 160], 't2': ['MUTANT_NETHER_STALK', 25600], 't3': None, 't4': None},
            {'base': ['NETHER_STALK'], 'compacted': ['ENCHANTED_NETHER_STALK', 160]},
            {'base': ['NETHER_STALK'], 'compacted': ['MUTANT_NETHER_STALK', 25600]},
            {'base': ['ENCHANTED_NETHER_STALK'], 'compacted': ['MUTANT_NETHER_STALK', 160]},
            # mining
            #{'base': ['COBBLESTONE'], 't1': ['ENCHANTED_COBBLESTONE', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['COBBLESTONE'], 'compacted': ['ENCHANTED_COBBLESTONE', 160]},
            #{'base': ['COAL'], 't1': ['ENCHANTED_COAL', 160], 't2': ['ENCHANTED_COAL_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['COAL'], 'compacted': ['ENCHANTED_COAL', 160]},
            {'base': ['COAL'], 'compacted': ['ENCHANTED_COAL_BLOCK', 25600]},
            {'base': ['ENCHANTED_COAL'], 'compacted': ['ENCHANTED_COAL_BLOCK', 160]},
            #{'base': ['IRON_INGOT'], 't1': ['ENCHANTED_IRON', 160], 't2': ['ENCHANTED_IRON_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['IRON_INGOT'], 'compacted': ['ENCHANTED_IRON', 160]},
            {'base': ['IRON_INGOT'], 'compacted': ['ENCHANTED_IRON_BLOCK', 25600]},
            {'base': ['ENCHANTED_IRON'], 'compacted': ['ENCHANTED_IRON_BLOCK', 160]},
            #{'base': ['GOLD_INGOT'], 't1': ['ENCHANTED_GOLD', 160], 't2': ['ENCHANTED_GOLD_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['GOLD_INGOT'], 'compacted': ['ENCHANTED_GOLD', 160]},
            {'base': ['GOLD_INGOT'], 'compacted': ['ENCHANTED_GOLD_BLOCK', 25600]},
            {'base': ['ENCHANTED_GOLD'], 'compacted': ['ENCHANTED_GOLD_BLOCK', 160]},
            #{'base': ['DIAMOND'], 't1': ['ENCHANTED_DIAMOND', 160], 't2': ['ENCHANTED_DIAMOND_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['DIAMOND'], 'compacted': ['ENCHANTED_DIAMOND', 160]},
            {'base': ['DIAMOND'], 'compacted': ['ENCHANTED_DIAMOND_BLOCK', 25600]},
            {'base': ['ENCHANTED_DIAMOND'], 'compacted': ['ENCHANTED_DIAMOND_BLOCK', 160]},
            #{'base': ['INK_SACK:4'], 't1': ['ENCHANTED_LAPIS_LAZULI', 160], 't2': ['ENCHANTED_LAPIS_LAZULI_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['INK_SACK:4'], 'compacted': ['ENCHANTED_LAPIS_LAZULI', 160]},
            {'base': ['INK_SACK:4'], 'compacted': ['ENCHANTED_LAPIS_LAZULI_BLOCK', 25600]},
            {'base': ['ENCHANTED_LAPIS_LAZULI'], 'compacted': ['ENCHANTED_LAPIS_LAZULI_BLOCK', 160]},
            #{'base': ['EMERALD'], 't1': ['ENCHANTED_EMERALD', 160], 't2': ['ENCHANTED_EMERALD_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['EMERALD'], 'compacted': ['ENCHANTED_EMERALD', 160]},
            {'base': ['EMERALD'], 'compacted': ['ENCHANTED_EMERALD_BLOCK', 25600]},
            {'base': ['ENCHANTED_EMERALD'], 'compacted': ['ENCHANTED_EMERALD_BLOCK', 160]},
            #{'base': ['REDSTONE'], 't1': ['ENCHANTED_REDSTONE', 160], 't2': ['ENCHANTED_REDSTONE_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['REDSTONE'], 'compacted': ['ENCHANTED_REDSTONE', 160]},
            {'base': ['REDSTONE'], 'compacted': ['ENCHANTED_REDSTONE_BLOCK', 25600]},
            {'base': ['ENCHANTED_REDSTONE'], 'compacted': ['ENCHANTED_REDSTONE_BLOCK', 160]},
            #{'base': ['QUARTZ'], 't1': ['ENCHANTED_QUARTZ', 160], 't2': ['ENCHANTED_QUARTZ_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['QUARTZ'], 'compacted': ['ENCHANTED_QUARTZ', 160]},
            {'base': ['QUARTZ'], 'compacted': ['ENCHANTED_QUARTZ_BLOCK', 25600]},
            {'base': ['ENCHANTED_QUARTZ'], 'compacted': ['ENCHANTED_QUARTZ_BLOCK', 160]},
            #{'base': ['OBSIDIAN'], 't1': ['ENCHANTED_OBSIDIAN', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['OBSIDIAN'], 'compacted': ['ENCHANTED_OBSIDIAN', 160]},
            #{'base': ['GLOWSTONE_DUST'], 't1': ['ENCHANTED_GLOWSTONE_DUST', 160], 't2': ['ENCHANTED_GLOWSTONE', 30720], 't3': None, 't4': None},
            {'base': ['GLOWSTONE_DUST'], 'compacted': ['ENCHANTED_GLOWSTONE_DUST', 160]},
            {'base': ['GLOWSTONE_DUST'], 'compacted': ['ENCHANTED_GLOWSTONE', 30720]},
            {'base': ['ENCHANTED_GLOWSTONE_DUST'], 'compacted': ['ENCHANTED_GLOWSTONE', 192]},
            #{'base': ['FLINT'], 't1': ['ENCHANTED_FLINT', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['FLINT'], 'compacted': ['ENCHANTED_FLINT', 160]},
            #{'base': ['ICE'], 't1': ['PACKED_ICE', 9], 't2': ['ENCHANTED_ICE', 160], 't3': ['ENCHANTED_PACKED_ICE', 25600], 't4': None},
            {'base': ['ICE'], 'compacted': ['PACKED_ICE', 9]},
            {'base': ['ICE'], 'compacted': ['ENCHANTED_ICE', 160]},
            {'base': ['ICE'], 'compacted': ['ENCHANTED_PACKED_ICE', 25600]},
            {'base': ['PACKED_ICE'], 'compacted': ['ENCHANTED_ICE', 160/9]},
            {'base': ['PACKED_ICE'], 'compacted': ['ENCHANTED_PACKED_ICE', 25600/9]},
            {'base': ['ENCHANTED_ICE'], 'compacted': ['ENCHANTED_PACKED_ICE', 160]},
            #{'base': ['NETHERRACK'], 't1': ['ENCHANTED_NETHERRACK', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['NETHERRACK'], 'compacted': ['ENCHANTED_NETHERRACK', 160]},
            #{'base': ['SAND'], 't1': ['ENCHANTED_SAND', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SAND'], 'compacted': ['ENCHANTED_SAND', 160]},
            #{'base': ['ENDSTONE'], 't1': ['ENCHANTED_ENDSTONE', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ENDER_STONE'], 'compacted': ['ENCHANTED_ENDSTONE', 160]},
            #{'base': ['SNOW_BALL'], 't1': ['SNOW_BLOCK', 4], 't2': ['ENCHANTED_SNOW_BLOCK', 640], 't3': None, 't4': None},
            {'base': ['SNOW_BALL'], 'compacted': ['SNOW_BLOCK', 4]},
            {'base': ['SNOW_BALL'], 'compacted': ['ENCHANTED_SNOW_BLOCK', 640]},
            {'base': ['SNOW_BLOCK'], 'compacted': ['ENCHANTED_SNOW_BLOCK', 160]},
            #{'base': ['MITHRIL_ORE'], 't1': ['ENCHANTED_MITHRIL', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['MITHRIL_ORE'], 'compacted': ['ENCHANTED_MITHRIL', 160]},
            #{'base': ['TITANIUM_ORE'], 't1': ['ENCHANTED_TITANIUM', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['TITANIUM_ORE'], 'compacted': ['ENCHANTED_TITANIUM', 160]},
            # combat
            #{'base': ['ROTTEN_FLESH'], 't1': ['ENCHANTED_ROTTEN_FLESH', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ROTTEN_FLESH'], 'compacted': ['ENCHANTED_ROTTEN_FLESH', 160]},
            #{'base': ['BONE'], 't1': ['ENCHANTED_BONE', 160], 't2': ['ENCHANTED_BONE_BLOCK', 25600], 't3': None, 't4': None},
            {'base': ['BONE'], 'compacted': ['ENCHANTED_BONE', 160]},
            {'base': ['BONE'], 'compacted': ['ENCHANTED_BONE_BLOCK', 25600]},
            {'base': ['ENCHANTED_BONE'], 'compacted': ['ENCHANTED_BONE_BLOCK', 160]},
            #{'base': ['STRING'], 't1': ['ENCHANTED_STRING', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['STRING'], 'compacted': ['ENCHANTED_STRING', 160]},
            #{'base': ['SPIDER_EYE'], 't1': ['ENCHANTED_SPIDER_EYE', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SPIDER_EYE'], 'compacted': ['SPIDER_EYE', 160]},
            #{'base': ['GUNPOWDER'], 't1': ['ENCHANTED_GUNPOWDER', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SULPHUR'], 'compacted': ['ENCHANTED_GUNPOWDER', 160]},
            #{'base': ['ENDER_PEARL'], 't1': ['ENCHANTED_ENDER_PEARL', 20], 't2': None, 't3': None, 't4': None},
            {'base': ['ENDER_PEARL'], 'compacted': ['ENCHANTED_ENDER_PEARL', 20]},
            #{'base': ['GHAST_TEAR'], 't1': ['ENCHANTED_GHAST_TEAR', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['GHAST_TEAR'], 'compacted': ['ENCHANTED_GHAST_TEAR', 160]},
            #{'base': ['SLIME_BALL'], 't1': ['ENCHANTED_SLIME_BALL', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SLIME_BALL'], 'compacted': ['ENCHANTED_SLIME_BALL', 160]},
            {'base': ['SLIME_BALL'], 'compacted': ['ENCHANTED_SLIME_BLOCK', 25600]},
            {'base': ['ENCHANTED_SLIME_BALL'], 'compacted': ['ENCHANTED_SLIME_BLOCK', 160]},
            #{'base': ['BLAZE_ROD'], 't1': ['ENCHANTED_BLAZE_POWDER', 160], 't2': ['ENCHANTED_BLAZE_ROD', 25600], 't3': None, 't4': None},
            {'base': ['BLAZE_ROD'], 'compacted': ['ENCHANTED_BLAZE_POWDER', 160]},
            {'base': ['BLAZE_ROD'], 'compacted': ['ENCHANTED_BLAZE_ROD', 25600]},
            {'base': ['ENCHANTED_BLAZE_POWDER'], 'compacted': ['ENCHANTED_BLAZE_ROD', 160]},
            #{'base': ['MAGMA_CREAM'], 't1': ['ENCHANTED_MAGMA_CREAM', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['MAGMA_CREAM'], 'compacted': ['ENCHANTED_MAGMA_CREAM', 160]},
            #{'base': ['ANCIENT_CLAW'], 't1': ['ENCHANTED_ANCIENT_CLAW', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['ANCIENT_CLAW'], 'compacted': ['ENCHANTED_ANCIENT_CLAW', 160]},
            # woods
            #{'base': ['LOG'], 't1': ['ENCHANTED_OAK_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG'], 'compacted': ['ENCHANTED_OAK_LOG', 160]},
            #{'base': ['LOG:2'], 't1': ['ENCHANTED_BIRCH_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG:2'], 'compacted': ['ENCHANTED_BIRCH_LOG', 160]},
            #{'base': ['LOG:1'], 't1': ['ENCHANTED_SPRUCE_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG:1'], 'compacted': ['ENCHANTED_SPRUCE_LOG', 160]},
            #{'base': ['LOG_2:1'], 't1': ['ENCHANTED_DARK_OAK_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG_2:1'], 'compacted': ['ENCHANTED_DARK_OAK_LOG', 160]},
            #{'base': ['LOG_2'], 't1': ['ENCHANTED_ACACIA_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG_2'], 'compacted': ['ENCHANTED_ACACIA_LOG', 160]},
            #{'base': ['LOG:3'], 't1': ['ENCHANTED_JUNGLE_LOG', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['LOG:3'], 'compacted': ['ENCHANTED_JUNGLE_LOG', 160]},
            # fish
            #{'base': ['RAW_FISH'], 't1': ['ENCHANTED_RAW_FISH', 160], 't2': ['ENCHANTED_COOKED_FISH', 25600], 't3': None, 't4': None},
            {'base': ['RAW_FISH'], 'compacted': ['ENCHANTED_RAW_FISH', 160]},
            {'base': ['RAW_FISH'], 'compacted': ['ENCHANTED_COOKED_FISH', 25600]},
            {'base': ['ENCHANTED_RAW_FISH'], 'compacted': ['ENCHANTED_COOKED_FISH', 160]},
            #{'base': ['RAW_FISH:1'], 't1': ['ENCHANTED_RAW_SALMON', 160], 't2': ['ENCHANTED_COOKED_SALMON', 25600], 't3': None, 't4': None},
            {'base': ['RAW_FISH:1'], 'compacted': ['ENCHANTED_RAW_SALMON', 160]},
            {'base': ['RAW_FISH:1'], 'compacted': ['ENCHANTED_COOKED_SALMON', 25600]},
            {'base': ['ENCHANTED_RAW_SALMON'], 'compacted': ['ENCHANTED_COOKED_SALMON', 160]},
            #{'base': ['RAW_FISH:2'], 't1': ['ENCHANTED_CLOWNFISH', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RAW_FISH:2'], 'compacted': ['ENCHANTED_CLOWNFISH', 160]},
            #{'base': ['RAW_FISH:3'], 't1': ['ENCHANTED_PUFFERFISH', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['RAW_FISH:3'], 'compacted': ['ENCHANTED_PUFFERFISH', 160]},
            #{'base': ['PRISMARINE_SHARD'], 't1': ['ENCHANTED_PRISMARINE_SHARD', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['PRISMARINE_SHARD'], 'compacted': ['ENCHANTED_PRISMARINE_SHARD', 160]},
            #{'base': ['PRISMARINE_CRYSTAL'], 't1': ['ENCHANTED_PRISMARINE_CRYSTAL', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['PRISMARINE_CRYSTALS'], 'compacted': ['ENCHANTED_PRISMARINE_CRYSTALS', 160]},
            #{'base': ['CLAY_BALL'], 't1': ['ENCHANTED_CLAY_BALL', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['CLAY_BALL'], 'compacted': ['ENCHANTED_CLAY_BALL', 160]},
            #{'base': ['WATER_LILY'], 't1': ['ENCHANTED_WATER_LILY', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['WATER_LILY'], 'compacted': ['ENCHANTED_WATER_LILY', 160]},
            #{'base': ['INK_SACK'], 't1': ['ENCHANTED_INK_SACK', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['INK_SACK'], 'compacted': ['ENCHANTED_INK_SACK', 160]},
            #{'base': ['SPONGE'], 't1': ['ENCHANTED_SPONGE', 40], 't2': ['ENCHANTED_WET_SPONGE', 1600], 't3': None, 't4': None},
            {'base': ['SPONGE'], 'compacted': ['ENCHANTED_SPONGE', 40]},
            {'base': ['SPONGE'], 'compacted': ['ENCHANTED_WET_SPONGE', 1600]},
            {'base': ['ENCHANTED_SPONGE'], 'compacted': ['ENCHANTED_WET_SPONGE', 40]},
            #{'base': ['SHARK_FIN'], 't1': ['ENCHANTED_SHARK_FIN', 160], 't2': None, 't3': None, 't4': None},
            {'base': ['SHARK_FIN'], 'compacted': ['ENCHANTED_SHARK_FIN', 160]},
        ]
        # index through all of them keep track of which is highest keep in 2d list and able to use sorted()
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
        craft = [
            # farming
            # golden carrot
            {'requirements': [['ENCHANTED_CARROT', 128], ['CARROT_ITEM', 32], ['GOLD_INGOT', 256/9]], 'crafted': ['ENCHANTED_GOLDEN_CARROT']},
            # enchanted cookie
            {'requirements': [['ENCHANTED_COCOA', 128], ['WHEAT', 32]], 'crafted': ['ENCHANTED_COOKIE']},
            # enchanted cake
            {'requirements': [['WHEAT', 3], ['ENCHANTED_SUGAR', 2], ['ENCHANTED_EGG', 1], ['Milk Bucket', 3, 50]], 'crafted': ['ENCHANTED_CAKE']},
            # mining
            # enchanted charcoal
            {'requirements': [['COAL', 128], ['LOG', 32]], 'crafted': ['ENCHANTED_CHARCOAL']},
            {'requirements': [['COAL', 128], ['LOG:2', 32]], 'crafted': ['ENCHANTED_CHARCOAL']},
            {'requirements': [['COAL', 128], ['LOG:1', 32]], 'crafted': ['ENCHANTED_CHARCOAL']},
            {'requirements': [['COAL', 128], ['LOG_2:1', 32]], 'crafted': ['ENCHANTED_CHARCOAL']},
            {'requirements': [['COAL', 128], ['LOG_2', 32]], 'crafted': ['ENCHANTED_CHARCOAL']},
            {'requirements': [['COAL', 128], ['LOG:3', 32]], 'crafted': ['ENCHANTED_CHARCOAL']},
            # enchanted redstone lamp
            {'requirements': [['ENCHANTED_GLOWSTONE_DUST', 128], ['ENCHANTED_REDSTONE', 32]], 'crafted': ['ENCHANTED_REDSTONE_LAMP']},
            # enchanted fermented spider eye
            {'requirements': [['ENCHANTED_SPIDER_EYE', 64], ['SUGAR_CANE', 64], ['BROWN_MUSHROOM', 64]], 'crafted': ['ENCHANTED_FERMENTED_SPIDER_EYE']},
            # enchanted firework rocket
            {'requirements': [['ENCHANTED_GUNPOWDER', 64], ['SUGAR_CANE', 16]], 'crafted': ['ENCHANTED_FIREWORK_ROCKET']},
            # enchanted eye of ender
            {'requirements': [['ENCHANTED_ENDER_PEARL', 16], ['BLAZE_ROD', 32]], 'crafted': ['ENCHANTED_EYE_OF_ENDER']},
            # slayers
            # revenant viscera
            {'requirements': [['REVENANT_FLESH', 128], ['ENCHANTED_STRING', 32]], 'crafted': ['REVENANT_VISCERA']},
            # tarantula silk
            {'requirements': [['TARANTULA_WEB', 128], ['ENCHANTED_FLINT', 32]], 'crafted': ['TARANTULA_SILK']},
            # golden wolf tooth
            {'requirements': [['WOLF_TOOTH', 128], ['ENCHANTED_GOLD', 32]], 'crafted': ['GOLDEN_TOOTH']},
            # baits
            # carrit
            # minnow
            # fish
            # light
            # dark
            # spooky
            # spiked
            # blessed
            # ice
            # whale
            # shark
            # misc
            {'requirements': [['ENCHANTED_BAKED_POTATO', 1], ['SUGAR_CANE', 3]], 'crafted': ['HOT_POTATO_BOOK']},
            {'requirements': [['ENCHANTED_COBBLESTONE', 448], ['ENCHANTED_REDSTONE_BLOCK', 1]], 'crafted': ['SUPER_COMPACTOR_3000']},
            {'requirements': [['ENCHANTED_COAL_BLOCK', 2], ['ENCHANTED_IRON', 3]], 'crafted': ['ENCHANTED_LAVA_BUCKET']},
            {'requirements': [['INK_SACK:4', 6], ['Glass Bottle', 1, 6]], 'crafted': ['EXP_BOTTLE']},
            {'requirements': [['ENCHANTED_LAPIS_LAZULI', 6], ['Glass Bottle', 1, 6]], 'crafted': ['GRAND_EXP_BOTTLE']},
            {'requirements': [['ENCHANTED_LAPIS_LAZULI_BLOCK', 6], ['Glass Bottle', 1, 6]], 'crafted': ['TITANIC_EXP_BOTTLE']},
        ]
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
            embed.add_field(name=f'{i+1}. {data[i]["name"]}', value=f'{int(data[i]["margin"]*10000)/100}% at {truncate(data[i]["buyprice"]-data[i]["sellprice"],2)} per item.')
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
