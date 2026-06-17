teams_count = int(input("How many teams do you want to analyze  "))

teams = []
points = []

for i in range(teams_count):
    team_name = input(f"Enter team {i+1}: ")
    teams.append(team_name)
    points.append(0)

for i in range(len(teams)):
    for j in range(i + 1, len(teams)):
        score1 = int(input(f"How many goals did {teams[i]} score vs {teams[j]}?  "))
        score2 = int(input(f"Now how many goals did {teams[j]} score vs {teams[i]}?  "))

        if score1 == score2:
            points[i] += 1
            points[j] += 1
        elif score1 > score2:
            points[i] += 3
        elif score1 < score2:
            points[j] += 3

index_points = enumerate(points)
sorted_points_indices = sorted(index_points, key=lambda x: x[1], reverse=True)

sorted_points = [value for index, value in sorted_points_indices]
original_indices = [index for index, value in sorted_points_indices]


print("Teams   Points   Place")
for i in range(teams_count):
    print(f" {teams[original_indices[i]]}    {sorted_points[i]}    #{i+1} ")
# need to make it so teams with same number of points should have same place by tomorrow




