import discord
from discord import Client, Embed, File
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from Stats_Painter import *
from HiscoreHandler import *

OS_MEMBERS_URL = './Res/os_members.txt'
IR_MEMBERS_URL = './Res/ir_members.txt'
client = commands.Bot(command_prefix='?')   # honestly no idea why i'm required to supply a command_prefix but whatever
slash = SlashCommand(client, sync_commands=True)

clan_ids = {
    872875986910314518:'IR',
    922450621720829982:'OS'
}

clan_authority_roles = {
    872875986910314518: ['leaders', 'event team', 'admin'],
    922450621720829982: ['founders', 'developers']
}

@slash.slash(
    name='update_clan',
    description='Updates the entire clan.',
    guild_ids=[872875986910314518]
)
async def update_clan(sc):
    await sc.defer()
    auth = 0
    for auth_role in clan_authority_roles[sc.guild.id]: auth += auth_role.lower() in list(map(lambda x:x.name.lower(), sc.author.roles))
    if auth < 1: await sc.send('You\'re not authorized to use this command, please use the slash command \'update <your rsn here>\' instead')
    else:
        if clan_ids[sc.guild.id] == 'IR':
            ir_members = list(map(lambda x:x.replace('\n', '').replace(',',''), open(IR_MEMBERS_URL, 'r').readlines()))
            os_members = list(map(lambda x:x.replace('\n', '').replace(',',''), open(OS_MEMBERS_URL, 'r').readlines()))

            tot_updated = 0
            if clan_ids[sc.guild.id] == 'IR':
                tot_updated += len(update_players_data(ir_members))
            else:
                tot_updated += len(update_players_data(os_members))

            ir_data = get_data(ir_members, True)
            os_data = get_data(os_members, False)

            png_lock = draw_all_categories(ir_data, os_data)

            await sc.send(str(tot_updated) + ' members from ' + ('Iron Republic ' if clan_ids[sc.guild.id] == 'IR' else 'One Shot ') + ' have been updated. These are the current standings.', files=[discord.File('./Res/snapshot.png')])
            png_lock.release()

@slash.slash(
    name='update',
    description='Updates a player.',
    options = [
        create_option(
            name='rsn',
            description='Your in game osrs name',
            option_type=SlashCommandOptionType.STRING,
            required=True
        )
    ],
    guild_ids=[872875986910314518]
)
async def update(sc, rsn):
    await sc.defer()
    ir_members = list(map(lambda x:x.replace('\n', '').replace(',',''), open(IR_MEMBERS_URL, 'r').readlines()))
    os_members = list(map(lambda x:x.replace('\n', '').replace(',',''), open(OS_MEMBERS_URL, 'r').readlines()))
    print(ir_members)
    print(os_members)
    if rsn not in (ir_members if clan_ids[sc.guild.id] == 'IR' else os_members):
        await sc.send('Player '+rsn+' is not part of your clan, did you spell it correctly?')
    elif len(update_player_data(rsn)) == 1:
        await sc.send('Player '+rsn+' has been updated, use the slash command \'standings\' to check how you\'re fairing against '+('Iron Republic' if clan_ids[sc.guild.id] == 'OS' else'One Shot')+'!')
    else:
        await sc.send('Something went wrong, try again in a few minutes.')


@slash.slash(
    name='standings',
    description='Generates an updated graph to keep track of the who\'s winning!',
    guild_ids=[872875986910314518]
)
async def standings(sc):
    await sc.defer()
    ir_members = list(open(IR_MEMBERS_URL, 'r').readlines())
    os_members = list(open(OS_MEMBERS_URL, 'r').readlines())
    ir_data = get_data(ir_members, True)
    os_data = get_data(os_members, False)
    lock = draw_all_categories(ir_data, os_data)
    await sc.send(' ',files=[discord.File('./Res/snapshot.png')])
    lock.release()


@client.event
async def on_ready():
    print('Ready')

if __name__ == '__main__':
    load_resources()
    with open('./token', 'r') as s:
        token = s.readline()
        client.run(token)