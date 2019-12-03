import sys
import pulp
import pandas as pd

# load data and LP settings

## notes: most sensitive on restaurant wait time
## it doesn't seem to matter what N to start with
## it doesn't seem to matter 

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
serviceTime = [2,4,3,4,1] # wait time per person
places = range(len(names))

preferences = dataset.loc[:, 'pref Exchange':'pref Chipotle']
travelTime = dataset.loc[:, 'travel Exchange':'travel Chipotle']
willingnessToWait = dataset.loc[:, 'wait Exchange':'wait Chipotle']

# starting number of people assigned to restaurants
# solution will iterate on this list
oldN = None
N = [0]*len(names)

iterations = 0

while (oldN != N) and iterations < 5:

    iterations += 1

    # start problem
    problem = pulp.LpProblem("cafe lunch problem", sense=pulp.LpMaximize)

    # variables
    assignments = pulp.LpVariable.dicts("A", ((person, place) for person in people for place in places), cat="Binary")
    W = pulp.LpVariable("W", lowBound = 0, cat = 'Continuous')

    # assignment constraint
    for person in people:
        problem += pulp.lpSum(assignments[person, place] for place in places) == 1

    # time limit constraint
    for person in people:
        problem += pulp.lpSum(assignments[person, place]*(N[place] * serviceTime[place] + 2*travelTime.iloc[person][place] + 15) for place in places) <= 60

    # objective
    problem += pulp.lpSum(assignments[person, place]*preferences.iloc[person][place] + (willingnessToWait.iloc[person][place] - (N[place] * serviceTime[place]))  for person in people for place in places)

    # solution
    problem.solve()

    # printing results
    
    oldN = N
    sanitycheck = 0
    N = []

    resultsPerson = []
    resultsEat = []
    resultsPref = []
    resultsTime = []
    resultsSatisfaction = []

    for place in places:
        n=0
        for person in people:
            if pulp.value(assignments[person, place]) == 1:
                n+=1
                sanitycheck+=1
                resultsPerson.append(person)
                resultsEat.append(names[place])
                resultsPref.append(preferences.iloc[person][place]) 
                resultsTime.append(oldN[place]*serviceTime[place] + 2*travelTime.iloc[person][place] + 15)
                resultsSatisfaction.append(preferences.iloc[person][place] + (willingnessToWait.iloc[person][place] - (oldN[place] * serviceTime[place])) )
        N.append(n)

    print(pulp.LpStatus[problem.status])
    print(sanitycheck==len(people))
    print()

    if N != oldN:
        resultsTime.append(N[place]*serviceTime[place] + 2*travelTime.iloc[person][place] + 15) #use newN to calculate
        resultsSatisfaction.append(preferences.iloc[person][place] + (willingnessToWait.iloc[person][place] - (N[place] * serviceTime[place])) )

        #recalcualte objective 
        obj = 0
        for place in places:
            for person in people:
                obj += pulp.value(assignments[person, place])*preferences.iloc[person][place] + (willingnessToWait.iloc[person][place] - (N[place] * serviceTime[place]))

    mapped = sorted(zip(resultsPerson,resultsEat,resultsPref,resultsTime,resultsSatisfaction), key=lambda pair: pair[0])

    for person, eat, pref, wait, sat in mapped: 
        print("Person %d goes to %s (%d), total lunch time: %d, satisfaction: %d" %(person,eat,pref,wait,sat))

    if N != oldN:
        print("Average Satisfaction :",obj/len(people))
    else:
        print("Average Satisfaction: ",pulp.value(problem.objective)/len(people))

    print()
    print("max lunch time: ", max(resultsTime))
    print()
    print("N:",N) 