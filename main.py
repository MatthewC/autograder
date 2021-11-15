import src
import discord
from discord.ext import commands
# async def assignment(cmd: commands.context, *, args: commands.clean_content):

client = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

# Deal with creating assignments/questions/test-cases etc.
@client.group()
async def create(cmd: commands.context):
    pass

@create.command()
async def assignment(cmd: commands.context, assignment_name, flags='[]'):
    """Create a new assignment; requires an assignment name. Flags can be ommited."""
    await cmd.trigger_typing()
    print(flags)
    data = src.db()
    try:
        data.create('assignments', name=assignment_name, questions='{}', flags=f'{flags}')
        await cmd.send(content=f'Assignment `{assignment_name}` created successfully.')
        print(data.getAssignment(assignment_name))
    except:
        message = discord.Embed(title="Error", description=f"Assignment name ({assignment_name}) already exists.")
        await cmd.send(None, embed=message)


# Deal with submissions

@client.command()
async def submit(cmd: commands.context, submissionName):
    if cmd.message.attachments == []:
        message = discord.Embed(title="Error", description="No file supplied.")
        await cmd.send(None, embed=message)
    else:
        submissionURL = cmd.message.attachments[0].url

        # Check if submission name provided is valid.
        data = src.db()
        assignment = data.getAssignment(submissionName)
        if assignment == []:
            message = discord.Embed(title="Error", description="Submission not found.")
            await cmd.send(None, embed=message)
        else:
            try:
                submission = src.Autograder(submissionURL)
                functions = assignment['questions']
                for function in functions:
                    testCases = data.getTests(function)
            except src.exceptions.invalidPython as err:
                await cmd.send(None, embed=discord.Embed(title="invalidPython", description=f"{err}"))
            except src.exceptions.illegalImport as err:
                await cmd.send(None, embed=discord.Embed(title="illegalImport", description=f"{err}"))
            

        

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