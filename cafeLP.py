import pulp
import pandas as pd

# data
dataset = pd.read_csv('1-2-data.csv')

people = range(len(dataset))

names = ["The Exchange","Resnik Cafe","La Prima","ABP","Chipotle"]
wait = [10,8,4,5,3] # random estimates currently
places = range(len(names))

satisfaction = dataset.loc[:, 'pref Exchange':'pref Chipotle']
minSatisfaction = 85 # currently proposed min in paper

# problem
problem = pulp.LpProblem("cafe lunch problem", sense=pulp.LpMinimize)

# variables
assignments = pulp.LpVariable.dicts("A", ((person, place) for person in people for place in places), cat="Binary")
W = pulp.LpVariable("W", lowBound = 0, cat = 'Continuous')

# assignment constraint
for person in people:
    problem += pulp.lpSum(assignments[person, place] for place in places) == 1

# satisfaction constraint
problem += pulp.lpSum(assignments[person, place]*satisfaction.iloc[person][place] for person in people for place in places) >= (minSatisfaction * len(people))

# convert min max to LP
for person in people:
    problem += pulp.lpSum(assignments[person, place]*wait[place] for place in places) <= W

# objective
problem += W

# solution
problem.solve()

sanitycheck = 0
for place in places:
    for person in people:
        if pulp.value(assignments[person, place]) == 1:
            sanitycheck+=1
            print(f"    {names[place]}: {person}")

print(pulp.LpStatus[problem.status])
print(sanitycheck==len(people))
