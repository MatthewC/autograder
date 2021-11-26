"""
main.py

This is the main file which handles most of the autograder-discord interface.
"""



import src
import json
import time
import random
import discord
import aiohttp
import asyncio

from discord.ext import commands
if __name__ == '__main__': from cogs.competitions import Competitions

botOwners = [472521286807977994]

# Sets up discord client.
client = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

# Utility functions

# Sends a message back to the user as an embed
async def sendEmbed(cmd, title: str, desc: str):
    message = discord.Embed(title=title, description=desc)
    await cmd.send(None, embed=message)

# Fixes the formatting of flags when passed in as a discord argument
def flagParser(arguments: str):
    if arguments == '':
        return ''
    args = arguments.replace(' ', '').split(',')
    ret = ''
    for arg in args:
        ret += f'"{arg}",'
    return ret[:-1]

# Fixes the formatting of arguments passed.
def cleanDict(argument: str):
    if argument == '':
        return '{}'

    argument = argument.replace('\'', '~')
    argument = argument.replace('"', '\'')
    argument = argument.replace('~', '"')
    return argument

# Periodically checks if competitions are about to finish, 
# and warns users.
# Refernced how to create periodic tasks from: https://www.youtube.com/watch?v=rWAnKvI2ePI
async def check_competition(client):
    await client.wait_until_ready()

    data = src.db()

    while not client.is_closed:
        comps = data.getCompetitions()
        for competition in comps:

            # Checks and calcualtes the deadline
            deadline = competition['startedAt']
            realDeadline = time.mktime(time.strptime(deadline, '%d/%m/%y %H:%M'))
            fDeadline = round(realDeadline) - (60 * 5)
            fDeadline = time.strftime('%d/%m/%y %H:%M', time.localtime(fDeadline))

            # For each competition, check if will be over soon.
            if overDeadline(deadline) or overDeadline(fDeadline):
                name = competition['name']
                users = data.getUsers()

                # Calculates difference between time and deadline.
                remainingTime = (realDeadline - time.time())//60

                for user in users:
                    userID = int(user['key'])

                    try:
                        client = await client.fetch_user(userID)
                        msg = f'Competition `{name}` is now over!' if overDeadline(deadline) else f'Competition `{name}` will finish in {remainingTime} minutes!'
                        await client.send(msg)
                    except:
                        print('[LOG] User either has DMs disabled, or has blocked the bot.')
                    
                if overDeadline(deadline): data.setCompetitionStatus(name, 'inactive', '')
        await asyncio.sleep(60)

# Checks the type of user who is invoking the command.
async def is_admin(cmd: commands.context):
    id = cmd.message.author.id
    if id in botOwners:
        return True
    else:
        return False
    
# Returns True or False depending 
def overDeadline(date):
    deadlineDate = time.strptime(date, '%d/%m/%y %H:%M')
    deadlineTime = time.mktime(deadlineDate)

    if time.time() - deadlineTime < 0:
        return False
    else:
        return True

# Groups up commands that deal with creating assignments/questions 
@client.group()
async def create(cmd: commands.context):
    pass


### SECTION THAT DEALS WITH CREATING ASSIGNMENTS ###

# Creates an assignment based on the passed arguments
# Sample usage: !create assignment homework1 "recursiveUpper, recursiveOddNumbersOnly" "noLoops, recursive"
@create.command()
@commands.check(is_admin)
async def assignment(cmd: commands.context, assignment_name: str, questions: flagParser='', deadline: str = '', flags: flagParser=''):
    """
    Create a new assignment; requires an assignment name. Flags and questions can be ommited.
    Sample usage: !create assignment homework1 "recursiveUpper, recursiveOddNumbersOnly" "noLoops, recursive"
    """
    await cmd.trigger_typing()
    data = src.db()
    try:
        json.loads(f'[{questions}]')
        json.loads(f'[{flags}]')

        data.create('assignments', name=assignment_name, questions=f'[{questions}]', flags=f'[{flags}]', deadline=deadline)
        await cmd.send(content=f'Assignment `{assignment_name}` created successfully.')
    except json.decoder.JSONDecodeError as err:
        await sendEmbed(cmd, 'Error', f'Invalid JSON passed.\n{err}')
    except:
        await sendEmbed(cmd, 'Error', f'Assignment name ({assignment_name}) already exists.')


# Creates a question based on the passed arguments.
# Sample usage: !create question recursiveUpper 10 "{'hello':'HELLO'}" "return" "noLoops, recursive"
@create.command()
@commands.check(is_admin)
async def question(cmd: commands.context, function_name: str, points: int, test_cases: cleanDict, type: str='return', flags: flagParser=''):
    """
    Creates a new question, requires the function name, the test cases (in JSON format), and flags.
    Sample usage: !create question recursiveUpper 10 "{'hello':'HELLO'}" "return" "noLoops, recursive"

    recursive: Function must be recursive
    recursion: Function cannot use recursion
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


# Deletes either a question or assignment
@client.command()
async def delete(cmd: commands.context, table: str, name: str):
    try:
        data = src.db()
        if table == 'assignment':
            data.deleteAssignment(name)
            await cmd.send(f'`{name}` succesfully deleted.')
    
        elif table == 'questions':
            data.deleteQuestion(name)
            await cmd.send(f'`{name}` succesfully deleted.')
    
    except Exception as err:
        await sendEmbed(cmd, 'Error', f'No such {table} ({name}) was found.')


# Deals with importing questions as a file.
@client.command()
async def upload(cmd: commands.context):
    if cmd.message.attachments == []:
        await sendEmbed(cmd, 'Error', 'No file supplied.')
    else:
        importURL = cmd.message.attachments[0].url

        async with aiohttp.ClientSession() as session:
            async with session.get(importURL) as response:
                file = await response.text()
                try:
                    importFile = json.loads(file)
                except SyntaxError:
                    await sendEmbed(cmd, 'Error', 'Invalid JSON file passed.')
        data = src.db()
        try: 
            for func in importFile:
                flag = str(importFile[func].pop('FLAGS'))
                point = importFile[func].pop('POINTS')
                fType = importFile[func].pop('TYPE')
                testCases = json.dumps(importFile[func])

                data.create('questions', function=func, flags=flag, points=point, type=fType, criteria=testCases)
                await cmd.send(f'`{func}` succesfully imported.')
        except json.decoder.JSONDecodeError:
            await sendEmbed(cmd, 'JSON Error', 'There was an issue reading your JSON file.')
        except Exception as err:
            await sendEmbed(cmd, str(type(err)), f'{err}')

### SECTION THAT DEALS WITH SUBMISSIONS ###

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
            if overDeadline(assignment['deadline']):
                await sendEmbed(cmd, 'Time expired', 'No more submissions are being accepted.')
                return


            try:
                submission = src.Autograder(submissionURL, assignment['flags'])
                await submission.fetch()

                functions = json.loads(assignment['questions'])
                await cmd.send(None, embed=discord.Embed(title='File submitted.', description=f'Assignment: {submissionName}'))
                sandbox = src.Sandbox()
                overallScore = 0
                totalPoints = 0
                finalStr = ''
                for function in functions:
                    announceTest = await cmd.send(f'Testing {function}...')

                    test = data.getTests(function)
                    totalPoints += test["points"]
                    
                    if function not in submission.functionNames and test['type'] != 'oop':
                        await announceTest.edit(content=f'Testing {function}: **not found, skipped**')
                        await cmd.send(f'''```{function} results:\n    Function not defined. Skipped\n    Points: 0```''')
                        continue

                    flagsMet = submission.checkFlags(function, test['flags'])

                    if flagsMet[0] == None:
                        await announceTest.edit(content=f'Testing {function}: **Skipped** - Function not recursive. (0 POINTS)')
                        finalStr += f'```{function} results: SKIPPED - Function not recursive. (0 POINTS)```'
                        continue
                    elif not flagsMet[0]:
                        failedFlags = ', '.join(flagsMet[1:])
                        await announceTest.edit(content=f'Testing {function}: **Skipped** - Use of {failedFlags} not allowed. (0 POINTS)')
                        finalStr += f'```{function} results: SKIPPED - Use of {failedFlags} not allowed. (0 POINTS)```'
                        continue

                    testCases = json.loads(test['criteria'])
                    fileToRun = submission.injectTestCase(testCases, function, test['type'])
                    results = sandbox.run(fileToRun)
                    counter = 0
                    
                    retString = f'```{function} results:'
                    shouldPass = False
                    passed = 0

                    if results[function] == None: return await announceTest.edit(content=f'Testing {function}: **Skipped** - TIMEOUT.')

                    for result in results[function]:

                        counter += 1
                        if result[1] == True:
                            retString += f'\n    Test #{counter}: Passed'
                            passed += 1
                        elif result[1] == None:
                            await announceTest.edit(content=f'Testing {function}: **Skipped** - Function must be {test["type"]}.')
                            finalStr += f'```{function} results: SKIPPED - Function must be {test["type"]}. (0 POINTS)```'
                            shouldPass = True
                            break
                        else:
                            retString += f'\n    Test #{counter}: Failed\n        Expected: {result[2]}\n        Received: {result[3]}'
                    if shouldPass: continue
                    await announceTest.edit(content=f'Testing {function}: **Finished**')

                    score = round(passed/counter * test["points"])
                    overallScore += score
                    retString += f'\n\n    Overall Result: {passed}/{counter}\n    Points: {score}/{test["points"]}```'
                    finalStr += retString

                    await cmd.send(retString)


                # Deals with saving the submission for later refernce.
                submissionReceipt = random.getrandbits(64)
                data.createSubmission(f'{submissionReceipt}', finalStr.replace('``````', '\n\n'), overallScore)

                # Save python file
                submission.saveFile(cmd.message.author.id, submissionName, submissionReceipt)

                # Associate submission with user
                user = json.loads(data.getUserSubmissions(cmd.message.author.id, cmd.message.author.name)['submissions'])
                currentSubmission = user.get(submissionName, [])
                currentSubmission.append(submissionReceipt)
                user[submissionName] = currentSubmission
                data.newUserSubmission(cmd.message.author.id, json.dumps(user))

                await cmd.send(f'**Final Score: {overallScore}/{totalPoints}**\nSubmission Receipt: {submissionReceipt}\n\nUse `!submissions {submissionName} {submissionReceipt}` to revisit the assignment')


            except src.exceptions.invalidPython as err:
                await sendEmbed(cmd, 'invalidPython', f'{err}')
            except src.exceptions.illegalImport as err:
                await sendEmbed(cmd, 'illegalImport', f'{err}')
            except src.exceptions.missingFunction as err:
                await sendEmbed(cmd, 'missingFunction', f'{err}')


# Sends back user statistics.
@client.command()
async def stats(cmd: commands.context, userID = None):
    if not await is_admin(cmd): (userID, username) = (cmd.message.author.id, cmd.message.author.name)
    else: (userID, username) = (userID, cmd.message.author.name)

    data = src.db()

    tableStr = '```ASSIGNMENT@@@@KEPT SCORE             TIME\n'
    assignments = json.loads(data.getUserSubmissions(userID, username)['submissions'])
    
    # Get largest assignment name (for formatting reasons)
    largestAssignment = 0
    for assignment in assignments:
        largestAssignment = len(assignment) if len(assignment) > largestAssignment else largestAssignment

    for assignment in assignments:
        activeSubmission = assignments[assignment][-1]

        assignmentExp = data.getAssignment(assignment)['deadline']

        assignmentExp = 'CLOSED' if overDeadline(assignmentExp) else assignmentExp

        submission = data.getSubmission(f'{activeSubmission}')

        # Fixes formatting
        spacing = ' ' * largestAssignment
        spacing = spacing + ' ' * (largestAssignment - len(assignment))

        tableStr += f'{assignment}{spacing}     {submission["score"]}                {assignmentExp}\n'
    tableStr = tableStr.replace('@@@@', ' ' * largestAssignment)
    await cmd.send(f'{tableStr}```')




@client.command()
@commands.check(is_admin)
async def users(cmd: commands.context):
    data = src.db()
    users = data.getUsers()
    largestName = ''
    tableString = '```NAME@@@@               ID              SUBMISSIONS\n'

    # Finds the largest name
    for user in users:
        if len(user['name']) > len(largestName):
            largestName = user['name']
    
    # Loops through each user and appends it to the table
    # Also takes into account large usernames, to fix formatting
    for user in users:
        name = user['name']
        id = user['key']
        submissions = json.loads(user['submissions'])
        submissionNames = ', '.join(submissions.keys())

        # Fixes formatting
        spacing = ' ' * len(largestName)
        spacing = spacing + ' ' * (len(largestName) - len(name))

        tableString += f'{name}{spacing}{id}        {submissionNames}\n'
    
    # Send the formatted string back.
    tableString = tableString.replace('@@@@', ' '*len(largestName))
    await cmd.send(f'{tableString}```')


# I can't send the file as text due to discord limitations
@client.command()
async def submissions(cmd: commands.context, *, args):
    data = src.db()
    args = args.split(' ')
    userID = cmd.message.author.id

    if await is_admin(cmd):
        userID = args.pop(0)
        if data.getUser(userID) == None: return await sendEmbed(cmd, 'User not found', f'Could not find the user with id {userID}')
        if len(args) == 0: return await stats(cmd, userID)

    if len(args) > 3:
        await sendEmbed(cmd, 'Invalid Usage', '!submissions <assignment name> [submission id] [file/results]')
        return
    assignmentName = args[0]

    userSubmissions = json.loads(data.getUserSubmissions(userID, cmd.message.author.name)['submissions'])
    activeSubmission = userSubmissions.get(assignmentName, None)

    if activeSubmission == None: return await sendEmbed(cmd, 'Not found.', 'Assignment name not found')

    # sqlite3 doesn't support 64bit integers, so we convert it to a string
    receipt = activeSubmission[-1] if args[1:2] == [] else args[1]
    receipt = f'{receipt}'

    fileType = 'results' if args[2:] == [] else args[2]

    if fileType == 'results':
        submissionResult = data.getSubmission(receipt)['results']
        await cmd.send(submissionResult)
    else:
        pythonFile = discord.File(f'./submissions/{userID}/{assignmentName}_{receipt}.py')
        await cmd.send(file=pythonFile, content=f'Submission for {assignmentName}.')

### ERROR HANDELING FOR COMMANDS ###

@assignment.error
async def assignmentError(cmd, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await sendEmbed(cmd, 'Error', '!create assignment requires at least 1 argument.')
    if isinstance(error, commands.TooManyArguments):
        await sendEmbed(cmd, 'Error', '!create assignment requires at least 1 argument.')
    if isinstance(error, commands.MissingPermissions):
        await sendEmbed(cmd, 'Error', 'Insufficient permissions')
    if isinstance(error, commands.CheckFailure):
        await sendEmbed(cmd, 'Error', 'Insufficient permissions')

@question.error
async def questionError(cmd, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await sendEmbed(cmd, 'Error', '!create question requires 3 arguments.')
    if isinstance(error, commands.BadArgument):
        errorMsg = str(error).replace('"', '').replace('.', '').split(' ')
        await sendEmbed(cmd, 'Error', f'`{errorMsg[6]}` argumented expected a type of {errorMsg[2]}.')
    if isinstance(error, commands.CheckFailure):
        await sendEmbed(cmd, 'Error', 'Insufficient permissions')

@submissions.error
async def submissionsError(cmd, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await sendEmbed(cmd, 'Error', '!submissions requires at least 1 argument.')
    if isinstance(error, commands.CheckFailure):
        await sendEmbed(cmd, 'Error', 'Insufficient permissions')
    else:
        print(error)

@users.error
async def userError(cmd, error):
    if isinstance(error, commands.CheckFailure):
        await sendEmbed(cmd, 'Error', 'Insufficient permissions')

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

if __name__ == '__main__':
    client.loop.create_task(check_competition(client))
    client.add_cog(Competitions(client))
    client.run('OTA0MzE2NzAyMDE0MTk3Nzcw.YX5wjw.Th1vijyh0S7IxCkDGed0JtjRfmk')