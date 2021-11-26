"""
competitions.py

This file deals with all the extra-competition features and exports it as a Class.
"""

import time
import json
import random
import discord
from discord.ext import commands
from main import is_admin, sendEmbed, overDeadline
from src import database, Autograder, Sandbox, exceptions

class Competitions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = database.db()
    
    @commands.group()
    async def competition(self, cmd: commands.context):
        pass

    @competition.command()
    @commands.check(is_admin)
    async def create(self, cmd: commands.context, name: str, assignment: str, time: str):
        try:
            self.data.create('competitions', name=name, assignment=assignment, deadline=time)
            await cmd.send(f'Competition **{name}** created sucesfully!\nUse `!competition start {name}` to announce the competition!')
        except:
            await self.sendEmbed(cmd, 'Error', 'Competition name must be unique.')

    @competition.command()
    async def delete(self, cmd: commands.context, name: str):
        competition = self.data.getCompetition(name)
        if competition == None: return await sendEmbed(cmd, 'Error', 'Competition not found.')
        self.data.deleteCompetition(name)
        await cmd.send('Competition deleted.')

    @competition.command()
    async def start(self, cmd: commands.context, name: str):
        competition = self.data.getCompetition(name)
        if competition == None: return await sendEmbed(cmd, 'Error', 'Competition not found.')
        if competition['status'] == 'active': return await sendEmbed(cmd, 'Error', 'Competition has already started.')

        await cmd.send(f'Starting competition **{name}**.\nSending notification to all users.')
        users = self.data.getUsers()

        for user in users:
            userID = int(user['key'])
            if userID == cmd.message.author.id: continue
            try:
                client = await self.bot.fetch_user(userID)
                await client.send(f'Competition `{name}` has now started!')
            except:
                print('[LOG] User either has DMs disabled, or has blocked the bot.')
            
            deadline = round(time.time()) + (3600 * int(competition['deadline']))
            deadline = time.strftime('%d/%m/%y %H:%M', time.localtime(deadline))
            
            self.data.setCompetitionStatus(name, 'active', deadline)
            await cmd.send('Succesfully sent out notification! ')


    @competition.command()
    async def stop(self, cmd: commands.context, name: str):
        competition = self.data.getCompetition(name)
        if competition == None: return await sendEmbed(cmd, 'Error', 'Competition not found.')
        if competition['status'] == 'inactive': return await sendEmbed(cmd, 'Error', 'Competition has not been started.')
        
        await cmd.send(f'Stopping competition **{name}**.\nSending notification to all users.')
        users = self.data.getUsers()

        for user in users:
            userID = int(user['key'])
            if userID == cmd.message.author.id: continue
            try:
                client = await self.bot.fetch_user(userID)
                await client.send(f'Competition `{name}` has been manually stopped.')
            except:
                print('[LOG] User either has DMs disabled, or has blocked the bot.')
            
            self.data.setCompetitionStatus(name, 'inactive', '')
            await cmd.send('Succesfully sent out notification! ')

    @competition.command()
    async def leaderboard(self, cmd: commands.context, name: str):
        competition = self.data.getCompetition(name)
        if competition == None: return await sendEmbed(cmd, 'Error', 'Competition not found.')

        leaderStr = '```NAME@@@@     SCORE\n'
        submissions = json.loads(competition['submissions'])

        # Get's the largest name.
        largestName = 0
        names = {}
        for submission in submissions:
            user = self.data.getUser(submission)['name']
            largestName = len(user) if len(user) > largestName else largestName
            names[user] = submissions[submission][1]

        # Adds each submission to the return list
        for name in names:
            # Fixes formatting
            spacing = ' ' * largestName
            spacing = spacing + ' ' * (largestName - len(name))

            leaderStr += f'{name}{spacing}{names[name]}\n'
            
        leaderStr += '```'
        await cmd.send(leaderStr.replace('@@@@', ' '*largestName))


    @competition.command()
    async def submit(self, cmd: commands.context, name: str):
        if cmd.message.attachments == []:
            await sendEmbed(cmd, 'Error', 'No file supplied.')
        else:
            submissionURL = cmd.message.attachments[0].url

            # Check if competition name is valid.
            submissionName = self.data.getCompetition(name)

            # Checks to see if competition name is valid and active.
            if submissionName == None: return await sendEmbed(cmd, 'Error', 'Competition name not found.')
            if submissionName['status'] == 'inactive': return await sendEmbed(cmd, 'Error', 'Competition has either finised or not been started')
            if overDeadline(submissionName['startedAt']): return await sendEmbed(cmd, 'Error', 'Competition is now over.')

            print(f'[LOG] Competition submission: {name}')
            assignment = self.data.getAssignment(submissionName['assignment'])
            if assignment == None: return await sendEmbed(cmd, 'Error', 'Submission name not found.')

            try:
                submission = Autograder(submissionURL, [])
                await submission.fetch()

                functions = json.loads(assignment['questions'])
                await cmd.send(None, embed=discord.Embed(title='Attempt submitted.', description=f'competition: {name}'))
                sandbox = Sandbox()
                overallScore = 0
                totalPoints = 0
                totalTime = 0
                finalStr = ''
                for function in functions:
                    announceTest = await cmd.send(f'Testing {function}...')

                    test = self.data.getTests(function)
                    totalPoints += test["points"]
                    
                    if function not in submission.functionNames and test['type'] != 'oop':
                        await announceTest.edit(content=f'Testing {function}: **not found, skipped**')
                        await cmd.send(f'''```{function} results:\n    Function not defined. Skipped\n    Points: 0```''')
                        continue

                    testCases = json.loads(test['criteria'])
                    fileToRun = submission.injectTestCase(testCases, function, test['type'])
                    results = sandbox.run(fileToRun)
                    counter = 0
                    
                    retString = f'```{function} results:'
                    shouldPass = False
                    passed = 0
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
                    
                    totalTime += results.get(f'{function}_time', 0)

                    score = round(passed/counter * test["points"])
                    overallScore += score
                    retString += f'\n\n    Overall Result: {passed}/{counter}\n    Points: {score}/{test["points"]}```'
                    finalStr += retString


                    await cmd.send(retString)


                # Deals with saving the submission for later refernce.
                submissionReceipt = random.getrandbits(64)
                self.data.createSubmission(f'{submissionReceipt}', finalStr.replace('``````', '\n\n'), overallScore)

                # Save python file
                userID = cmd.message.author.id
                submission.saveFile(userID, name, submissionReceipt)

                # Associate submission with user (competition)
                competition = json.loads(self.data.getCompetitionSubmissions(name)['submissions'])

                currentSubmission = competition.get(userID, [])
                currentSubmission.append(submissionReceipt)
                currentSubmission.append(overallScore)
                currentSubmission.append(totalTime)

                competition[userID] = currentSubmission
                self.data.updateCompetitionSubmissions(name, json.dumps(competition))

                await cmd.send(f'**Final Score: {overallScore}/{totalPoints}**\nSubmission Receipt: {submissionReceipt}\n\nUse `!competition leaderboard {name}` to view the stats!')


            except exceptions.invalidPython as err:
                await sendEmbed(cmd, 'invalidPython', f'{err}')
            except exceptions.illegalImport as err:
                await sendEmbed(cmd, 'illegalImport', f'{err}')
            except exceptions.missingFunction as err:
                await sendEmbed(cmd, 'missingFunction', f'{err}')

    @create.error
    async def createError(self, cmd, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await sendEmbed(cmd, 'Error', '!competition create requires 3 argument.')
        if isinstance(error, commands.TooManyArguments):
            await sendEmbed(cmd, 'Error', '!create assignment requiers at least 1 argument.')
        if isinstance(error, commands.CheckFailure):
            await sendEmbed(cmd, 'Error', 'Insufficient permissions')