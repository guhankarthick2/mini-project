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

print(f" The top 3 teams: "
      f"1st place is {teams[original_indices[0]]} with {sorted_points[0]} points "
      f"2nd place is {teams[original_indices[1]]} with {sorted_points[1]} points "
      f"3rd place is {teams[original_indices[2]]} with {sorted_points[2]} points ")


