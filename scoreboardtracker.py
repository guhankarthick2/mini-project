team1 = input("Enter team 1: ")
team2 = input("Enter team 2: ")
score1 = input(f" What is {team1}'s score? ")
score2 = input(f" What is {team2}'s score? ")

if score2 > score1:
    print(f"{team2} is the winner.")
elif score1 > score2 :
    print(f"{team1} is the winner.")
elif score2 == score1:
    print(f" It is a draw")
