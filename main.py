import src
import json
import discord
from discord.ext import commands
# async def assignment(cmd: commands.context, *, args: commands.clean_content):

# Utility functions

async def sendEmbed(cmd, title: str, desc: str):
    message = discord.Embed(title=title, description=desc)
    await cmd.send(None, embed=message)

def flagParser(arguments: str):
    if arguments == '':
        return ''
    args = arguments.replace(' ', '').split(',')
    ret = ''
    for arg in args:
        ret += f'"{arg}",'
    return ret[:-1]

def cleanDict(argument: str):
    if argument == '':
        return '{}'
    return argument.replace('\'', '"')

# SEND EMAILS??
# TODO: Check due date of submission.

client = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

#TODO: Deal with authentication.
# Deal with creating assignments/questions/test-cases etc.
@client.group()
async def create(cmd: commands.context):
    pass

@client.group()
async def delete(cmd: commands.context):
    pass

@create.command()
async def assignment(cmd: commands.context, assignment_name: str, questions: flagParser='', flags: flagParser=''):
    """
    Create a new assignment; requires an assignment name. Flags and questions can be ommited.
    Sample usage: !create assignment homework1 "recursiveUpper, recursiveOddNumbersOnly" "noLoops, recursive"
    """
    await cmd.trigger_typing()
    data = src.db()
    try:
        json.loads(f'[{questions}]')
        #TODO: Check if proper flags are being passed.
        json.loads(f'[{flags}]')

        data.create('assignments', name=assignment_name, questions='{}', flags=f'{flags}')
        await cmd.send(content=f'Assignment `{assignment_name}` created successfully.')
    except json.decoder.JSONDecodeError as err:
        await sendEmbed(cmd, 'Error', f'Invalid JSON passed.\n{err}')
    except:
        await sendEmbed(cmd, 'Error', f'Assignment name ({assignment_name}) already exists.')

@create.command()
async def question(cmd: commands.context, function_name: str, points: int, test_cases: cleanDict, type: str='return', flags: flagParser=''):
    """
    Creates a new question, requires the function name, the test cases (in JSON format), and flags.
    Sample usage: !create question recursiveUpper 10 "{'hello':'HELLO'}" "return" "noLoops, recursive"
    """
    # Flags -> OOP, Destructive/Non-Destructive, Recursive, NoLoops..
    await cmd.trigger_typing()
    data = src.db()
    try:
        # Test if proper json was passed for test_cases and flags
        if isinstance(json.loads(test_cases), int):
            raise json.decoder.JSONDecodeError('Expecting valid JSON', '', 0)
        #TODO: Check if proper flags are being passed.
        json.loads(f'[{flags}]')
        
        data.create('questions', function=function_name, points=points, type=type, criteria=test_cases, flags=f'[{flags}]')
        await cmd.send(content=f'Function `{function_name}` created successfully.')
    except json.decoder.JSONDecodeError:
        await sendEmbed(cmd, 'Error', 'Invalid JSON passed.')
    except:
        await sendEmbed(cmd, 'Error', f'Function name ({function_name}) already exists.')


@delete.command()
async def assignment(cmd: commands.context, assignment_name: str):
    try:
        data = src.db()
        data.deleteAssignment(assignment_name)
        await cmd.send(f'`{assignment_name}` succesfully deleted.')
    except Exception as err:
        print(err)
        await sendEmbed(cmd, 'Error', f'No such assignment ({assignment_name}) was found.')

# Deal with submissions

@client.command()
async def submit(cmd: commands.context, submissionName):
    if cmd.message.attachments == []:
        await sendEmbed(cmd, 'Error', 'No file supplied.')
    else:
        submissionURL = cmd.message.attachments[0].url

        # Check if submission name provided is valid.
        data = src.db()
        assignment = data.getAssignment(submissionName)
        if assignment == None:
            await sendEmbed(cmd, 'Error', 'Submission name not found.')
        else:
            try:
                submission = src.Autograder(submissionURL)
                await submission.fetch()
                # print(submission.file)
                functions = json.loads(assignment['questions'])
                await cmd.send(None, embed=discord.Embed(title="File submitted.", description=f"{cmd.message.attachments[0].url}"))
                for function in functions:
                    # testCases = data.getTests(function)
                    print('a', function)
            except src.exceptions.invalidPython as err:
                await sendEmbed(cmd, 'invalidPython', f'{err}')
            except src.exceptions.illegalImport as err:
                await sendEmbed(cmd, 'illegalImport', f'{err}')
            

## Error Handeling ##

@assignment.error
async def assignmentError(cmd, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.TooManyArguments):
        mySand = src.Sandbox(5)
        x = mySand.run()
        print(x)
        await sendEmbed(cmd, 'Error', '!create assignment requiers at least 1 argument.')

@question.error
async def questionError(cmd, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await sendEmbed(cmd, 'Error', '!create question requiers 3 arguments.')
    elif isinstance(error, commands.BadArgument):
        errorMsg = str(error).replace('"', '').replace('.', '').split(' ')
        await sendEmbed(cmd, 'Error', f'`{errorMsg[6]}` argumented expected a type of {errorMsg[2]}.')

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

if __name__ == "__main__":
    client.run('OTA0MzE2NzAyMDE0MTk3Nzcw.YX5wjw.Th1vijyh0S7IxCkDGed0JtjRfmk')