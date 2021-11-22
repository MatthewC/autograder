# Autograder

## Usage

### To create an assignment:

`!create assignment <assignment name> <questions>`

**Example**: `!create assignment homework3 "decodeList,capitalizeWords,printUpper,nonExist,destructive,nDestructive,destructive2,nDestructive2,cantUseRecursionF,mustUseRecursionF"`

### To upload a set of questions (see tests/questions.json):

`!upload`

### To run a submission upload the file and type the command:

`!submit <assignment name>`

**There is a demo already loaded in (using the tests/sample.py file) which can be uploaded and submitted as 'homework3':** `!submit homework3`

## TODO:

- [ ] Add propper comments
- [ ] Fix minor bugs with OOP code (works, but errors can sometimes not be reported)
- [ ] Add competitions
- [ ] Keep track of submissions per user
- [ ] Allow users to view their previous submissions/results
