import random
questionsCount = input("How many questions? ")
questionsAnswered = 0
correctAnswered = 0
difficulty = input("Chooose a difficulty (easy, medium, hard, or extreme)  ")
while questionsAnswered < int(questionsCount):
    if difficulty == "easy":
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
    elif difficulty == "medium":
        num1 = random.randint(5, 20)
        num2 = random.randint(5, 20)
    elif difficulty == "hard":
        num1 = random.randint(100,1000 )
        num2 = random.randint(100,1000)
    elif difficulty == "extreme":
        num1 = random.randint(1000, 10000)
        num2 = random.randint(1000, 10000)
    else:
        print("Invalid difficulty, easy has automatically been chosen")
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
    answer = input(f"{num1} * {num2}  ")
    if float(answer) == (num1 * num2):
        print("Correct!")
        correctAnswered += 1
    else:
        print("Incorrect!")

    questionsAnswered += 1
    print(f'{correctAnswered} out of {questionsAnswered} correct!')

if correctAnswered == questionsAnswered:
    print("Great Job, everything is correct!")
