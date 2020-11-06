# multichoice-quiz
A quiz game for multiple choice tests

## installation & usage

This python script was designed to *clone'n run*, so no installation of third party package should be required, if Python is installed > v. 3.8.5

Clone the git repo, move to the folder you cloned in and type `python3 quizgame.py -h` to get a full instruction.

All quizzes must be put in the subfolder `./quizzes` as `.json` files.

**Try playing OSISG** (see below) and have fun! :-)

## roadmap

- [x] [add] threshold in % for passing the quiz
- [ ] [add] possibility to change given answers before finishing a question
- [ ] [add] learning mode: repeat a question before it is considered as answered correctly
- [ ] [add] timer to simulate limited time in a RL test

### credits

- Diya Nag Chaudhury for inspiration of this project with her repo at https://github.com/cherryWood55/Quiz-Game/issues/

---

# OSISG - the Open Source Information Security Game
## creating a quiz with the best information security questions out there for your entertainment and learning

**Please contribute!**

### How to play

Install `multichoice-quiz` (see above) and type `python3 quizgame.py osisg`
Easy as that! 

### How to contribute

**What's your most challaging information security question?**
Please contribute it to the OSISG, to create the most challenging open source information security quiz out there!

Steps are easy:
1. Just `git clone` the repo and add you question to the file `./quizzes/osisg.json`
2. Choose the right chapter for your question or create a new one if required
3. the id of the question must be unique not necessarily numeric
4. Please do keep the structure unmodified, so it will run with multichoice-quiz
5. Add yourself to the contributors in the meta section with `your (nik)name; <email>`
6. double check the syntax of the JSON file e.g. with a linter
7. do a pull request and it will be added to this repo, if conforming to the points above

Thank you for your support and please tell also your friends about OSISG!