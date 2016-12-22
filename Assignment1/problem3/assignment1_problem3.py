#The program outputs an integer followed by the names
#The integer denotes the number of table needed to seat the people
#The integer is then followed by the table configuration such that each table has a person not known to each other.

#I have used BFS to take solutions out from the fringe.
#I also tried DFS but BFS gave me a configuration with lesser amount of tables.

#reference: https://www.python.org/doc/essays/graphs/

import sys

#Function to read a file of friends and read it into a list
def readfile(filename):
    try:
        text = [file.split(' ',) for file in [file.rstrip('\n') for file in open(filename)]]
        return text
    except IOError:
        print('Enter correct filename!')
        return

#creates a dictionary for every person, here a friends to b is treated as b friends to a
#a separate dictionary is created for everyone
def create_dictionary(text):
    table = {}
    for i in text:
        if i[0] not in table:
            table[i[0]] = []
        for j in range(1,len(i)):
            if i[j] not in table:
                table[i[j]] = []
            if i[j] not in table[i[0]]:
                table[i[0]].append(i[j])
            if i[0] not in table[i[j]]:
                table[i[j]].append(i[0])
    return table

#returns a dictionary which will contain the friends of each member
#if a person is already in a list, then he will not be generated another list
def generate_friends(table, friend, solution):
    flag = False
    for i in solution:
        if len(solution[i]) < table_max:
            for j in solution[i]:
                if j in table[friend]:
                    flag = True
                    break
            if flag == False:
                solution[i].append(friend)
                return table[friend]
        flag = False
    solution[len(solution)+1] = [friend]
    return table[friend]

#using BFS to find an optimal solution
def solve(table):
    sol = {}
    friend = table.keys()
    fringe = [friend[0]]
    while len(fringe) > 0:
        temp = fringe.pop()
        for s in generate_friends(table,temp,sol):
            if s not in fringe and s in friend:
                fringe.insert(0,s)
        friend.remove(temp)
    return sol

#main method to read input and call the solve function

fileName = sys.argv[1]
table_max = int(sys.argv[2])

r = readfile(fileName)
j = create_dictionary(r)
solution = solve(j)
count = 0
for i,j in solution.iteritems():
    count += 1

p=0
print count,':',
for i,j in solution.iteritems():
    for x in j:
        print x,
    p += 1
    if p == count:
        print ' ',
    else:
        print ',',
