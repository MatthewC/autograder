import discord
from discord.ext import commands
# async def assignment(cmd: commands.context, *, args: commands.clean_content):

client = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

@client.group()
async def create(cmd: commands.context):
    pass

@create.command()
async def assignment(cmd: commands.context, assignment_name, flags=""):
    """Create a new assignment; requires an assignment name. Flags can be ommited."""
    await cmd.trigger_typing()
    message = discord.Embed(title="Error", description="Hello, World")
    await cmd.send(content=None, embed=message)

## Error Handeling ##

@assignment.error
async def assignmentError(cmd, error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = discord.Embed(title="Error", description="!create assignment requiers at least 1 argument.")
        await cmd.send(None, embed=message)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

client.run('OTA0MzE2NzAyMDE0MTk3Nzcw.YX5wjw.Th1vijyh0S7IxCkDGed0JtjRfmk')