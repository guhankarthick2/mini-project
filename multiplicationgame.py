import random

questionsCount = input("How many questions? ")
questionsAnswered = 0
correctAnswered = 0
correctStreak = 0
compliment = ["You're on fire!", "Great Job!", "Excellent!","Too easy?","Genius level!"]
difficulty = input("Chooose a difficulty (easy, medium, hard, or extreme)  ")
while questionsAnswered < int(questionsCount):
    if difficulty.lower() == "easy":
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
    elif difficulty.lower() == "medium":
        num1 = random.randint(5, 20)
        num2 = random.randint(5, 20)
    elif difficulty.lower() == "hard":
        num1 = random.randint(100,1000 )
        num2 = random.randint(100,1000)
    elif difficulty.lower() == "extreme":
        num1 = random.randint(1000, 10000)
        num2 = random.randint(1000, 10000)
    else:
        print("Invalid difficulty, easy has automatically been chosen")
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
    answer = input(f"Question {questionsAnswered + 1}: {num1} * {num2}  ")
    if float(answer) == (num1 * num2):
        print("Correct!")
        correctAnswered += 1
        correctStreak += 1
    else:
        print("Incorrect!")
        correctStreak = 0

    if correctStreak >= 3:
        print(f"{correctStreak} in a row, {compliment[random.randint(0,4)]}")

    questionsAnswered += 1
    print(f'{correctAnswered} out of {questionsAnswered} correct!')

percentage = correctAnswered / questionsAnswered * 100
print(f"{percentage}% correct")
if percentage == 100:
    print("Great Job, everything is correct!")


