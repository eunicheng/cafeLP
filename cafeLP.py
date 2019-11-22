import sys
import pulp
import pandas as pd

# load data and LP settings

group = sys.argv[1]
path = None
if group == "a":
    path = '11-12-data.csv'
elif group == "b":
    path = '12-1-data.csv'
else:
    path = '1-2-data.csv'

dataset = pd.read_csv(path)

people = range(len(dataset))

names = ["The Exchange","Resnik Cafe","La Prima","ABP","Chipotle"]
serviceTime = [1,3,2,6,1] # wait time per person
places = range(len(names))

preferences = dataset.loc[:, 'pref Exchange':'pref Chipotle']
travelTime = dataset.loc[:, 'travel Exchange':'travel Chipotle']
willingnessToWait = dataset.loc[:, 'wait Exchange':'wait Chipotle']

minSatisfaction = 50 # will change in the future, too high and the solution is infeasible

# starting number of people assigned to restaurants
# solution will iterate on this list
oldN = None
N = [0]*len(names)

while (oldN != N):

    # start problem
    problem = pulp.LpProblem("cafe lunch problem", sense=pulp.LpMinimize)

    # variables
    assignments = pulp.LpVariable.dicts("A", ((person, place) for person in people for place in places), cat="Binary")
    W = pulp.LpVariable("W", lowBound = 0, cat = 'Continuous')

    # assignment constraint
    for person in people:
        problem += pulp.lpSum(assignments[person, place] for place in places) == 1

    # satisfaction constraint
    problem += pulp.lpSum(assignments[person, place]*preferences.iloc[person][place] - (willingnessToWait.iloc[person][place] - (N[place] * serviceTime[place]))  for person in people for place in places) >= (minSatisfaction * len(people))

    # convert min max to LP
    for person in people:
        problem += pulp.lpSum(assignments[person, place]*(N[place] * serviceTime[place] + travelTime.iloc[person][place]) for place in places) <= W

    # objective
    problem += W

    # solution
    problem.solve()

    oldN = N
    sanitycheck = 0
    N = []
    for place in places:
        n=0
        for person in people:
            if pulp.value(assignments[person, place]) == 1:
                n+=1
                sanitycheck+=1
                print(f"    {names[place]}: {person}")
        N.append(n)

    print(pulp.LpStatus[problem.status])
    print(sanitycheck==len(people))
    print()

    print("wait time:")
    print(pulp.value(problem.objective))
    print()

    print("satisfaction:")
    print(pulp.value(pulp.lpSum(assignments[person, place]*preferences.iloc[person][place] - (willingnessToWait.iloc[person][place] - (N[place] * serviceTime[place]))  for person in people for place in places)) / len(people))
    print()

    print("old N:",oldN)
    print("new N:",N)

    break # remove the break to start converging, currently does not stop :(


