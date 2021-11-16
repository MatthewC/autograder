import src
import json
import discord
from discord.ext import commands
# async def assignment(cmd: commands.context, *, args: commands.clean_content):

# Utility functions

async def sendEmbed(cmd, title: str, desc: str):
    message = discord.Embed(title=title, description=desc)
    await cmd.send(None, embed=message)

# SEND EMAILS??
# TODO: Check due date of submission.

client = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

# Deal with creating assignments/questions/test-cases etc.
@client.group()
async def create(cmd: commands.context):
    pass

@create.command()
async def assignment(cmd: commands.context, assignment_name: str, questions: str='[]', flags: str='[]'):
    """Create a new assignment; requires an assignment name. Flags can be ommited."""
    await cmd.trigger_typing()
    print(flags)
    data = src.db()
    try:
        data.create('assignments', name=assignment_name, questions='{}', flags=f'{flags}')
        await cmd.send(content=f'Assignment `{assignment_name}` created successfully.')
        print(data.getAssignment(assignment_name))
    except json.decoder.JSONDecodeError:
        await sendEmbed(cmd, 'Error', 'Invalid JSON passed.')
    except:
        message = discord.Embed(title="Error", description=f"Assignment name ({assignment_name}) already exists.")
        await cmd.send(None, embed=message)

@create.command()
async def question(cmd: commands.context, function_name: str, points: int, test_cases:str, flags=''):
    """
    Creates a new question, requires the function name, the test cases (in JSON format), and flags.
    Sample usage: !create question recursiveUpper 10 "{'hello':'HELLO'}" 'noLoops', 'recursive'
    """
    # Flags -> OOP, Destructive/Non-Destructive, Recursive, NoLoops..
    await cmd.trigger_typing()
    data = src.db()
    try:
        # Test if proper json was passed for test_cases and flags
        json.loads(test_cases)
        json.loads(f'[{flags}]')
        
        data.create('questions', function=function_name, points=points, criteria=test_cases, flags=flags)
        await cmd.send(content=f'Assignment `{function_name}` created successfully.')
    except json.decoder.JSONDecodeError:
        message = discord.Embed(title="Error", description=f"Invalid JSON passed.")
        await cmd.send(None, embed=message)
    except:
        message = discord.Embed(title="Error", description=f"Function name ({function_name}) already exists.")
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
                await submission.run()
                # print(submission.file)
                functions = assignment['questions']
                await cmd.send(None, embed=discord.Embed(title="File submitted.", description=f"{cmd.message.attachments[0].url}"))
                # for function in functions:
                #     testCases = data.getTests(function)
            except src.exceptions.invalidPython as err:
                await cmd.send(None, embed=discord.Embed(title="invalidPython", description=f"{err}"))
            except src.exceptions.illegalImport as err:
                await cmd.send(None, embed=discord.Embed(title="illegalImport", description=f"{err}"))
            

## Error Handeling ##

@assignment.error
async def assignmentError(cmd, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.TooManyArguments):
        message = discord.Embed(title="Error", description="!create assignment requiers at least 1 argument.")
        await cmd.send(None, embed=message)

@question.error
async def questionError(cmd, error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = discord.Embed(title="Error", description="!create question requiers 3 arguments.")
        await cmd.send(None, embed=message)
    elif isinstance(error, commands.BadArgument):
        errorMsg = str(error).replace('"', '').replace('.', '').split(' ')
        message = discord.Embed(title="Error", description=f"`{errorMsg[6]}` argumented expected a type of {errorMsg[2]}.")
        await cmd.send(None, embed=message)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

client.run('OTA0MzE2NzAyMDE0MTk3Nzcw.YX5wjw.Th1vijyh0S7IxCkDGed0JtjRfmk')