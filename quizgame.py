#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import random
import glob
import os
import argparse
# import call method from subprocess module 
from subprocess import call 


class Quiz:
    BANNER = r'''
                  _ _   _      _           _                            _     
  _ __ ___  _   _| | |_(_) ___| |__   ___ (_) ___ ___        __ _ _   _(_)____
 | '_ ` _ \| | | | | __| |/ __| '_ \ / _ \| |/ __/ _ \_____ / _` | | | | |_  /
 | | | | | | |_| | | |_| | (__| | | | (_) | | (_|  __/_____| (_| | |_| | |/ / 
 |_| |_| |_|\__,_|_|\__|_|\___|_| |_|\___/|_|\___\___|      \__, |\__,_|_/___|
                                                               |_|            
A quiz game for multiple choice tests
@author: butterflyx <info@butterflyx.com>
'''

    def __init__(self):
        # list available json files with quiz data
        self.gamesList = []
        # chosen game from gameslist
        self.topic = ""
        # the content of the loaded json file
        self.rawGame = None
        # list of chapters in game
        self.chapters = []

        # number of questions available (to calc eg pass limit)
        self.questionsTotal = 0
        # number of questions left in stack
        self.questionsLeft = 0        
        # list of shuffeled questions for the quiz itself
        self.questions = []
        # the actually asked question
        self.question = []
        # list of right answered questions
        # while learning depend on times answered right before pushed here
        # while simulating a test, instantly pushed here if correct
        self.questionsRightAnswered = []
        # list of wrong answered questions
        # if simulating a test to show a list of questions that should be repeated
        self.questionsWrongAnswered = []

        # limit of questions to ask
        self.limit = 0
        # threshold to pass the quiz; show banners only if set
        self.threshold = None

        # set to true if Strg+C to stop quiz
        self.breakFlag = False

        self.failedBanner = """
                                                                   
            @@@@@@@@   @@@@@@   @@@  @@@       @@@@@@@@  @@@@@@@   
            @@@@@@@@  @@@@@@@@  @@@  @@@       @@@@@@@@  @@@@@@@@  
            @@!       @@!  @@@  @@!  @@!       @@!       @@!  @@@  
            !@!       !@!  @!@  !@!  !@!       !@!       !@!  @!@  
            @!!!:!    @!@!@!@!  !!@  @!!       @!!!:!    @!@  !@!  
            !!!!!:    !!!@!!!!  !!!  !!!       !!!!!:    !@!  !!!  
            !!:       !!:  !!!  !!:  !!:       !!:       !!:  !!!  
            :!:       :!:  !:!  :!:   :!:      :!:       :!:  !:!  
             ::       ::   :::   ::   :: ::::   :: ::::   :::: ::  
             :         :   : :  :    : :: : :  : :: ::   :: :  :   
                                                                   
        """

        self.passedBanner = """
         :::::::::    :::     ::::::::  :::::::: :::::::::::::::::::  
         :+:    :+: :+: :+:  :+:    :+::+:    :+::+:       :+:    :+: 
         +:+    +:++:+   +:+ +:+       +:+       +:+       +:+    +:+ 
         +#++:++#++#++:++#++:+#++:++#+++#++:++#+++#++:++#  +#+    +:+ 
         +#+      +#+     +#+       +#+       +#++#+       +#+    +#+ 
         #+#      #+#     #+##+#    #+##+#    #+##+#       #+#    #+# 
         ###      ###     ### ########  ######## ###################  
        """

    def listGames(self):
        """ list all available quizzes in subfolder 'quizzes' """
        self.gamesList = glob.glob("./quizzes/*.json")
        return self.gamesList

    def setGame(self, topic, limit):
        """ load the raw quiz data into memory and prepare quiz to play """
        # https://careerkarma.com/blog/python-check-if-file-exists/
        if os.path.exists(topic) and (topic in self.gamesList):
            self.topic = topic    
        elif os.path.exists("./quizzes/"+topic+".json") and ("./quizzes/"+topic+".json" in self.gamesList):
            self.topic = "./quizzes/"+topic+".json"
        else:
            raise QuizNotFound()

        game = self.readGameFile()

        for chapter in game["quiz"]:
            self.chapters.append(chapter)
            #print(f"Chapter: {chapter}")
            for question in game["quiz"][chapter]:
                quizquestion = {}
                #print(f"Question-Nr: {question}")
                self.questionsTotal += 1
                quizquestion["chapter"] = chapter
                quizquestion["questionnr"] = question
                quizquestion["timesRightAnswered"] = 0
                quizquestion["userAnswers"] = []
                quizquestion["question"] = game["quiz"][chapter][question]["question"]
                # shuffle possible answers as well
                # https://stackoverflow.com/questions/19895028/randomly-shuffling-a-dictionary-in-python
                keys = list(game["quiz"][chapter][question]["answers"].keys())
                random.shuffle(keys)
                quizquestion["answers"] = [(key, game["quiz"][chapter][question]["answers"][key]) for key in keys]
                # quizquestion["answers"] = game[chapter][question]["answers"]
                quizquestion["right"] = game["quiz"][chapter][question]["right"]
                self.questions.append(quizquestion)
        # shuffle the questions
        random.shuffle(self.questions)
        print(Colors.blue(f"{self.questionsTotal} questions found in {self.topic}"))

        # pop questions above limit after shuffling
        if limit:
            self.limit = limit
            while self.limit > 0 and len(self.questions) > self.limit:
                self.questions.pop(0)
            self.questionsTotal = len(self.questions)
            print(Colors.blue(f"This quiz is limited to {self.questionsTotal} random questions."))

        # initially all questions are left as well
        self.questionsLeft = self.questionsTotal

        return True

    def readGameFile(self):
        """ open and read the file with the quiz """
        try:
            with open(self.topic, "r") as json_file:
                self.rawGame = json.load(json_file)
        except:
            print(f"unable to read {self.topic}")

        return self.rawGame

    def getQuestion(self):
        """ get one question out of the heap """
        # take the first question of the randomized array
        self.question = self.questions.pop(0)
        # update remaining questions
        self.getQuestionsLeft()
        return self.question

    def getQuestionsTotal(self):
        """ get total number of questions in quiz """
        return self.questionsTotal

    def getQuestionsLeft(self):
        """ get number of questions in quiz not yet asked """
        self.questionsLeft = len(self.questions)
        return self.questionsLeft

    def getProgress(self):
        """ calculates the percentage of answered questions """
        p = int(round(100-((self.getQuestionsLeft() / self.getQuestionsTotal()) * 100)))
        return p

    def printProgressbar(self, prog=None):
        """ visualize the percentage of answered questions """
        progress =  prog if prog != None else self.getProgress()
        barlevel = int(str(progress*0.1)[:1]) # get first digit
        blanks = (10-barlevel)
        if barlevel < 5:
            print("[ "+Colors.highlight_lightgreen(("##"*barlevel))+Colors.highlight_gray(("  "*blanks))+" ]")
        else:
            print("[ "+Colors.highlight_green(("##"*barlevel))+Colors.highlight_gray(("  "*blanks))+" ]")

    # define clear function ; from https://www.geeksforgeeks.org/clear-screen-python/
    def clear(self): 
        """ clears screen """
        # check and make call for specific operating system 
        _ = call('clear' if os.name =='posix' else 'cls') 


    def askQuestion(self):
        """ prints the questions as well as possible answers and awaits input(s) """
        answers = []
        keys = []
        securityQuestion = False

        print("")
        print(f"Category: {self.question['chapter']}")
        print("")
        print(Colors.blue("Question:")+f" {self.question['question']}")
        print("")
        for key, answer in self.question['answers']:
            keys.append(key.upper())
            print(Colors.blue(f"({key}) ")+f"{answer}") 
        print("")
        print(f">> ")
        options = list(sorted(set(keys).difference(answers)))
        try:
            while(options != []):
                choice = input(f"Enter choice {options} or hit Enter to finish question: ")
                if choice.upper() in options:
                    answers.append(choice.upper())
                    print(Colors.blue("Any other answer you want to check?"))
                    securityQuestion = False          
                elif choice.upper() in answers:
                    print(Colors.yellow(f"you have already marked answer ({choice}) as true. Try again or press enter if no other answer is right."))
                    securityQuestion = False
                elif choice == "" and securityQuestion == True:
                    return answers
                elif choice == "" and securityQuestion == False:
                    securityQuestion = True
                    print(Colors.blue("Sure you have all answers marked? Press Enter again to finish this question."))
                else:
                    print(Colors.red("Invalid choice. Try again"))
                    securityQuestion = False
                options = list(sorted(set(keys).difference(answers)))
            return answers    
        except KeyboardInterrupt:
            choice = input(Colors.yellow("\n\nDo you want to interrupt the quiz? (y/n) : "))
            if choice.lower() == "y":
                self.breakFlag = True
                return False
            else:
                print("OK, then try again.")
                self.askQuestion()

    def validateAnswer(self, answers) -> bool:
        """ check if answer given was right """
        if sorted(answers) == sorted(self.question['right']):
            #print(f"Right! {answers} == {self.question['right']}")
            self.questionsRightAnswered.append(self.question)
            self.question = []
            return True
        #print(f"Question not correctly answered! {answers} != {self.question['right']}")
        self.question["useranswers"] = answers
        self.questionsWrongAnswered.append(self.question)
        self.question = []
        return False

    def setThreshold(self, threshold) -> int:
        """ set the minimum amount of right answers to pass the quiz """
        self.threshold = threshold if threshold <= 100 else 100
        return self.threshold


    def printResults(self):
        """ print the results of the quiz """
        qleft = self.getQuestionsLeft()+1 if self.breakFlag else self.getQuestionsLeft() # +1 for current question
        questionsAnswered = self.getQuestionsTotal() - qleft
        print("")
        print(Colors.green("Your results:"))
        print("~~~~~~~~~~~~~")
        print(f"You have answered {questionsAnswered} questions out of {self.getQuestionsTotal()} questions.")
        if questionsAnswered > 0:
            percent = int(round(len(self.questionsRightAnswered)/questionsAnswered * 100))
            print(f"And you got {len(self.questionsRightAnswered)} of {questionsAnswered} right, which is a {percent}% percentage (minimum %: {self.threshold}).")
            if percent >= self.threshold and self.threshold != None:
                print(Colors.green(self.passedBanner))
            else:
                print(Colors.red(self.failedBanner))
        print(f"")
        if self.questionsWrongAnswered != []:
            print(Colors.yellow("These questions should be reviewed:"))
            for question in self.questionsWrongAnswered:
                print("")
                print(f"{question['chapter']} - question {question['questionnr']} :")
                print(Colors.blue(question['question']))
                print("")
                print("possible answers:")
                for key, answer in sorted(question["answers"]):
                    print("("+Colors.blue(key)+f") {answer}")
                print("")
                print(f"Your answers: "+Colors.red(question['useranswers'])+"")
                print(f"right answers: "+Colors.green(question['right'])+"")
                print("--------")
            print("")

        

        
    
    def playQuiz(self, args):
        """ take the quiz """
        #print(f"quizname: {args.quizname} ; l: {args.l} ; t: {args.t}")
        self.listGames()
        self.setGame(args.quizname, args.l)
        if args.t:
            self.setThreshold(args.t)
        print("")
        print(Colors.green("Starting the quiz in a moment..."))
        time.sleep(2)
        while (self.questionsLeft > 0):
            self.clear()
            print("--------")
            print(f"progress: {self.getProgress()} % ")
            self.printProgressbar()
            self.getQuestion()
            answer = self.askQuestion()
            if answer == False or answer == [] or type(answer) is not list:
                break
            else:
                self.validateAnswer(answer)
            self.clear()
        self.printResults()
        print(Colors.green("Thank you for taking the quiz!"))
        print("")
        print("~~~~~~~~~~")
        print(f"{self.rawGame['meta']['title']}")
        print("~~~~~~~~~~")
        print(f"brought to you by: {self.rawGame['meta']['author']}")
        print("")
        if self.rawGame["meta"]["contributors"] != []:
            print("with contributions by:")
            for supporter in self.rawGame["meta"]["contributors"]:
                print(f"{supporter}")
        print("")
        print(f"licence: {self.rawGame['meta']['licence']}")
        print("")
        print(f"please visit {self.rawGame['meta']['homepage']} for more information.")
        print("")
        print("Bye.\n")
        exit(0)



class QuizNotFound(Exception):
    pass      


class Colors:

    # https://godoc.org/github.com/whitedevops/colors
    Reset = "\033[0m"

    Bold       = "\033[1m"
    Dim        = "\033[2m"
    Underlined = "\033[4m"
    Blink      = "\033[5m"
    Reverse    = "\033[7m"
    Hidden     = "\033[8m"

    ResetBold       = "\033[21m"
    ResetDim        = "\033[22m"
    ResetUnderlined = "\033[24m"
    ResetBlink      = "\033[25m"
    ResetReverse    = "\033[27m"
    ResetHidden     = "\033[28m"

    Default      = "\033[39m"
    Black        = "\033[30m"
    Red          = "\033[31m"
    Green        = "\033[32m"
    Yellow       = "\033[33m"
    Blue         = "\033[34m"
    Magenta      = "\033[35m"
    Cyan         = "\033[36m"
    LightGray    = "\033[37m"
    DarkGray     = "\033[90m"
    LightRed     = "\033[91m"
    LightGreen   = "\033[92m"
    LightYellow  = "\033[93m"
    LightBlue    = "\033[94m"
    LightMagenta = "\033[95m"
    LightCyan    = "\033[96m"
    White        = "\033[97m"

    BackgroundDefault      = "\033[49m"
    BackgroundBlack        = "\033[40m"
    BackgroundRed          = "\033[41m"
    BackgroundGreen        = "\033[42m"
    BackgroundYellow       = "\033[43m"
    BackgroundBlue         = "\033[44m"
    BackgroundMagenta      = "\033[45m"
    BackgroundCyan         = "\033[46m"
    BackgroundLightGray    = "\033[47m"
    BackgroundDarkGray     = "\033[100m"
    BackgroundLightRed     = "\033[101m"
    BackgroundLightGreen   = "\033[102m"
    BackgroundLightYellow  = "\033[103m"
    BackgroundLightBlue    = "\033[104m"
    BackgroundLightMagenta = "\033[105m"
    BackgroundLightCyan    = "\033[106m"
    BackgroundWhite        = "\033[107m"

    @staticmethod
    def blue(string):
        return Colors.Blue+str(string)+Colors.Reset

    @staticmethod
    def green(string):
        return Colors.Green+str(string)+Colors.Reset

    @staticmethod
    def yellow(string):
        return Colors.Yellow+str(string)+Colors.Reset

    @staticmethod
    def red(string):
        return Colors.Red+str(string)+Colors.Reset

    @staticmethod
    def bold(string):
        return Colors.Bold+str(string)+Colors.Reset
    
    @staticmethod
    def highlight_green(string):
        return Colors.BackgroundGreen+str(string)+Colors.Reset

    @staticmethod
    def highlight_lightgreen(string):
        return Colors.BackgroundLightGreen+str(string)+Colors.Reset

    @staticmethod
    def highlight_gray(string):
        return Colors.BackgroundDarkGray+str(string)+Colors.Reset



if __name__ == "__main__":
    myquiz = Quiz()
    myquiz.clear()
    print(Colors.blue(myquiz.BANNER))
    print("")
    parser = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('quizname', type=str, help='name of the quiz you want to play')
    parser.add_argument('--t', nargs='?', type=int, help='THRESHOLD for passing the quiz in percent (rounded). Show success or failure message at the end.')
    parser.add_argument('--l', nargs='?', type=int, help='LIMIT the number of questions in a quiz. No effect if number of available question less then limit.')
    #parser.print_help()
    args = parser.parse_args()
    myquiz.playQuiz(args)
