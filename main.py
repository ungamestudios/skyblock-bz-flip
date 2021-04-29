from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
import json
import requests
import hashlib
import os
import cloudscraper

# token
load_dotenv()
token = os.getenv('token')
bot = commands.Bot(command_prefix='$')
bot.remove_command('help')
slash = SlashCommand(bot, sync_commands=True)

# reload api
@bot.command(name='reload')
async def reload(ctx):
    scraper = cloudscraper.create_scraper()
    data=scraper.get('https://sky.shiiyu.moe/api/v2/bazaar').text
    with open('bazaar.json', 'w') as file:
        file.write(data)
    # ah
    # ah_data=requests.get('https://api.hypixel.net/skyblock/auctions').text
    # with open('auction.json', 'w') as file:
    # file.write(ah_data)
    await ctx.send(embed=discord.Embed(title='Successfully Reloaded API', description=hashlib.md5(data.encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.red()))

# debug command
@bot.command(name='debug')
async def debug(ctx):
    if ctx.author.id == 750055850889969725:
        # reload()
        bz_data='temp'
        ah_data='temp'
        data=bz_data+ah_data
        await ctx.send(embed=discord.Embed(title='Debug Info', description=hashlib.md5(data.encode('utf-8')).hexdigest(), type='rich', colour=discord.Colour.red()))
        await ctx.send(file=discord.File('data.json'))

# help command
@bot.command(name='help')
async def help(ctx):
    embed=discord.Embed(title='Command List', description='Commands Available to You', type='rich', colour=discord.Colour.blue())
    embed.add_field(name='$bazaar', value='Queries the bazaar for the best flips', inline=False)
    embed.add_field(name='$auction', value='Queries the auction house for the best flips **COMING SOON!!**', inline=False)
    if ctx.author.id == 750055850889969725:
        embed.add_field(name='$reload', value='Reloads the Hypixel API', inline=False)
        embed.add_field(name='$debug', value='Shows current Internal State', inline=False)
    await ctx.send(embed=embed)


bot.run(token)