#!/usr/bin/env python3
import json
import time
import random
import glob
import os

class Quiz:
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

    def listGames(self):
        self.gamesList = glob.glob("./quizzes/*.json")
        return self.gamesList

    def setGame(self, topic):
        # https://careerkarma.com/blog/python-check-if-file-exists/
        if os.path.exists(topic) and (topic in self.gamesList):
            self.topic = topic    
        elif os.path.exists("./quizzes/"+topic+".json") and ("./quizzes/"+topic+".json" in self.gamesList):
            self.topic = "./quizzes/"+topic+".json"
        else:
            raise QuizNotFound()

        game = self.readGameFile()

        for chapter in game:
            self.chapters.append(chapter)
            #print(f"Chapter: {chapter}")
            for question in game[chapter]:
                quizquestion = {}
                #print(f"Question-Nr: {question}")
                self.questionsTotal += 1
                quizquestion["chapter"] = chapter
                quizquestion["questionnr"] = question
                quizquestion["timesRightAnswered"] = 0
                quizquestion["userAnswers"] = []
                quizquestion["question"] = game[chapter][question]["question"]
                # shuffle possible answers as well
                # https://stackoverflow.com/questions/19895028/randomly-shuffling-a-dictionary-in-python
                keys = list(game[chapter][question]["answers"].keys())
                random.shuffle(keys)
                quizquestion["answers"] = [(key, game[chapter][question]["answers"][key]) for key in keys]
                # quizquestion["answers"] = game[chapter][question]["answers"]
                quizquestion["right"] = game[chapter][question]["right"]
                self.questions.append(quizquestion)
        # shuffle the questions
        random.shuffle(self.questions)

        # initially all questions are left as well
        self.questionsLeft = self.questionsTotal

        print(f"{self.questionsTotal} questions found in {self.topic}")
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
        print(f"Question: {self.question['question']}")
        print("")
        for key, answer in self.question['answers']:
            keys.append(key.upper())
            print(f"({key}) {answer}") 
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
                    print("Invalid choice. Try again")
                options = list(sorted(set(keys).difference(answers)))
            return answers    
        except KeyboardInterrupt as e:
            choice = input("\n\nDo you want to interrupt the quiz? (y/n) : ")
            if choice.lower() == "y":
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

    def printResults(self):
        questionsAnswered = self.getQuestionsTotal() - (self.getQuestionsLeft()+1) # +1 for current question
        print("")
        print("Your results:")
        print("~~~~~~~~~~~~~")
        print(f"You have answered {questionsAnswered} questions out of {self.getQuestionsTotal()} questions.")
        if questionsAnswered > 0:
            percent = int(round(len(self.questionsRightAnswered)/questionsAnswered * 100))
            print(f"And you got {len(self.questionsRightAnswered)} of {questionsAnswered} right, which is a {percent}% percentage.")
        print(f"")
        if self.questionsWrongAnswered != []:
            print("These questions should be reviewed:")
            for question in self.questionsWrongAnswered:
                print("")s
                print(f"Question:")
                print(f"{question['question']}")
                print("")
                print("possible answers:")
                for key, answer in sorted(question["answers"]):
                    print(f"({key}) {answer}")
                print("")
                print(f"Your answers: {question['useranswers']}")
                print(f"right answers: {question['right']}")
                print("--------")
            print("")


    
    def playQuiz(self, game):
        self.listGames()
        self.setGame(game)
        print("Starting the quiz now:")
        while (self.questionsLeft > 0):
            print("--------")
            print(f"progress: {self.getProgress()} % ")
            self.getQuestion()
            answer = self.askQuestion()
            if answer == False or answer == []:
                break
            else:
                self.validateAnswer(answer)
        self.printResults()
        print("Thank you for taking the quiz! Bye.")

class QuizNotFound(Exception):
    pass      




if __name__ == "__main__":
    myquiz = Quiz()
    myquiz.playQuiz("bsi")