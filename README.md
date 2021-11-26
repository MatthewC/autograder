# Autograder

## Usage

`python3 main.py`

**Quick note:** The admin account is defined by a list located in `main.py`, modify that with your DISCORD ID in order to be considered an admin

## Admin-Only Commands

### To create an assignment:

`!create assignment <assignment name> <questions> <deadline>`

**Example**: `!create assignment homework1 "decodeList, capitalizeWords, printUpper, cantUseLoops,usesRecursionWhenTheyCant,isNotRecursive,destructiveFunction,destructiveFunctionFails,nonDestructiveFunction,nonDestructiveFunctionFails,oopTest" “26/11/21 22:59”`

### To create questions

`!create question <function name> <points> <test cases> <flags>`

**Example**: `!create question recursiveUpper 10 "{'hello':'HELLO'}" "return, noLoops, recursive"`

### To delete an assignment/question

`!delete <question/assignment> <name>`

### To upload a set of questions (see tests/questions.json as a guideline):

`!upload`

### Get a list of all users

`!users`

### To view user submissions

`!submissions <user id> <assignment name>`

### Create a competition

`!competition create <competition name> <assignment name> <time in hours>`

### Start a competition

`!competition start <competition name>`

### End a competition

`!competition stop <competition name>`

### Delete a competition

`!competition delete <competition name>`

## User Commands

### To run an assignment upload the file and type the command:

`!submit <assignment name>`

### View previous submissions

`!submissions <assignment name> [submission id] [file/result]`

### To run a submission upload the file and type the command:

`!competition submit <name>`

### View competition leaderboard

`!competition leaderboard <name>`

**There is a demo already loaded in (using the tests/sample.py file) which can be uploaded and submitted as 'homework1':** `!submit homework1`

## QUESTION TYPES

- return
- print
- destructive
- nonDestructive
- oop

## QUESTION FLAGS

- stringIndexing
- recursion (_function can't use recursion_)
- recursive (_funciton has to be recursive_)
- tryExcept
- noLoops

## TODO:

- [x] Add propper comments
- [x] Add competitions
- [x] Keep track of submissions per user
- [x] Allow users to view their previous submissions/results
