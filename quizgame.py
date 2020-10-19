#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import random
import glob
import os
import argparse


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
        # threshold to pass the quiz; default 100% answers must be right
        self.threshold = 100

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
        self.gamesList = glob.glob("./quizzes/*.json")
        return self.gamesList

    def setGame(self, topic, limit):
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
        try:
            with open(self.topic, "r") as json_file:
                self.rawGame = json.load(json_file)
        except:
            print(f"unable to read {self.topic}")

        return self.rawGame

    def getQuestion(self):
        # take the first question of the randomized array
        self.question = self.questions.pop(0)
        # update remaining questions
        self.getQuestionsLeft()
        return self.question

    def getQuestionsTotal(self):
        return self.questionsTotal

    def getQuestionsLeft(self):
        self.questionsLeft = len(self.questions)
        return self.questionsLeft

    def getProgress(self):
        p = int(round(100-((self.getQuestionsLeft() / self.getQuestionsTotal()) * 100)))
        return p


    def askQuestion(self):
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
                    print("Any other answer you want to check?")               
                elif choice.upper() in answers:
                    print(f"you have already marked answer ({choice}) as true. Try again or press enter if no other answer is right.")
                elif choice == "" and securityQuestion == True:
                    return answers
                elif choice == "" and securityQuestion == False:
                    securityQuestion = True
                    print("Sure you have all answers marked? Press Enter again to finish this question.")
                else:
                    print(Colors.red("Invalid choice. Try again"))
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

    def validateAnswer(self, answers):
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

    def setThreshold(self, threshold):
        if threshold <= 100:
            self.threshold = threshold
        return self.threshold


    def printResults(self):
        if self.breakFlag:
            qleft = self.getQuestionsLeft()+1 # +1 for current question
        else:
            qleft = self.getQuestionsLeft()
        questionsAnswered = self.getQuestionsTotal() - qleft
        print("")
        print(Colors.green("Your results:"))
        print("~~~~~~~~~~~~~")
        print(f"You have answered {questionsAnswered} questions out of {self.getQuestionsTotal()} questions.")
        if questionsAnswered > 0:
            percent = int(round(len(self.questionsRightAnswered)/questionsAnswered * 100))
            print(f"And you got {len(self.questionsRightAnswered)} of {questionsAnswered} right, which is a {percent}% percentage (minimum {self.threshold}%).")
            if percent >= self.threshold:
                print(Colors.green(self.passedBanner))
            else:
                print(Colors.red(self.failedBanner))
        print(f"")
        if self.questionsWrongAnswered != []:
            print(Colors.yellow("These questions should be reviewed:"))
            for question in self.questionsWrongAnswered:
                print("")
                print(f"Question:")
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
        #print(f"quizname: {args.quizname} ; l: {args.l} ; t: {args.t}")
        self.listGames()
        self.setGame(args.quizname, args.l)
        if args.t:
            self.setThreshold(args.t)
        print("")
        print(Colors.green("Starting the quiz now:"))
        while (self.questionsLeft > 0):
            print("--------")
            print(f"progress: {self.getProgress()} % ")
            self.getQuestion()
            answer = self.askQuestion()
            if answer == False or answer == [] or type(answer) is not list:
                break
            else:
                self.validateAnswer(answer)
        self.printResults()
        print(Colors.green("Thank you for taking the quiz! Bye.\n"))
        exit(0)



class QuizNotFound(Exception):
    pass      


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def blue(string):
        return Colors.OKBLUE+str(string)+Colors.ENDC

    @staticmethod
    def green(string):
        return Colors.OKGREEN+str(string)+Colors.ENDC

    @staticmethod
    def yellow(string):
        return Colors.WARNING+str(string)+Colors.ENDC

    @staticmethod
    def red(string):
        return Colors.FAIL+str(string)+Colors.ENDC

    @staticmethod
    def bold(string):
        return Colors.BOLD+str(string)+Colors.ENDC
    



USAGE = f"""
-t : threshold for passing the quiz in percent. Show success or failure message at the end.
-l : limit the number of questions in a quiz. No effect if number of available question less then limit.
"""


if __name__ == "__main__":
    myquiz = Quiz()
    print(Colors.blue(myquiz.BANNER))
    print("")
    parser = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument('quizname', type=str, help='name of the quiz you want to play')
    parser.add_argument('--t', nargs='?', type=int, help='Threshold for passing the quiz in percent (rounded). Show success or failure message at the end.')
    parser.add_argument('--l', nargs='?', type=int, help='limit the number of questions in a quiz. No effect if number of available question less then limit.')
    #parser.print_help()
    args = parser.parse_args()
    myquiz.playQuiz(args)
