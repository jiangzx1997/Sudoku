import cplex
import sys
from cplex.exceptions import CplexError

N_digit = 9
sqrt_N_digit = 3


def sukoduReader(filename):
    sukodu = []
    with open(filename) as f:
        for line in f.readlines():
            row = [int(x) for x in line.split()]
            sukodu.append(row)
    return sukodu


def getVarName(i, j, k):
    return "x" + str(i*100 + j*10 + k)


def lpInitialization(sukodu, prob):
    prob.objective.set_sense(prob.objective.sense.maximize)
    myObj = [0] * (N_digit ** 3)
    myLowerBound = [0] * (N_digit ** 3)
    myUpperBound = [1] * (N_digit ** 3)
    myCtype = "I" * (N_digit ** 3)
    myColNames = []
    for i in range(N_digit):
        for j in range(N_digit):
            for k in range(1, N_digit+1):
                varName = getVarName(i, j, k)
                myColNames.append(varName)
    
    for i in range(N_digit):
        for j in range(N_digit):
            if sukodu[i][j] != 0:
                for k in range(1, N_digit+1):
                    pos = myColNames.index(getVarName(i, j, k))
                    if k != sukodu[i][j]:
                        myLowerBound[pos] = myUpperBound[pos] = 0
                    else:
                        myLowerBound[pos] = myUpperBound[pos] = 1

    prob.variables.add(obj=myObj, lb=myLowerBound,
                       ub=myUpperBound, types=myCtype, names=myColNames)

    rows = []
    myRhs = []
    for k in range(1, N_digit+1):
        for j in range(N_digit):
            variables = []
            coefficients = [1] * N_digit
            for i in range(N_digit):
                variables.append(getVarName(i, j, k))
            rows.append([variables, coefficients])
            myRhs.append(1)

    for k in range(1, N_digit+1):
        for i in range(N_digit):
            variables = []
            coefficients = [1] * N_digit
            for j in range(N_digit):
                variables.append(getVarName(i, j, k))
            rows.append([variables, coefficients])
            myRhs.append(1)

    for k in range(1, N_digit+1):
        for p in range(sqrt_N_digit):
            for q in range(sqrt_N_digit):
                variables = []
                coefficients = [1] * N_digit
                for n in range(sqrt_N_digit):
                    for m in range(sqrt_N_digit):
                        i = p*sqrt_N_digit + n
                        j = q*sqrt_N_digit + m
                        variables.append(getVarName(i, j, k))
                rows.append([variables, coefficients])
                myRhs.append(1)

    for i in range(N_digit):
        for j in range(N_digit):
            variables = []
            coefficients = [1] * N_digit
            for k in range(1, N_digit+1):
                variables.append(getVarName(i, j, k))
            rows.append([variables, coefficients])
            myRhs.append(1)

    mySense = "E" * len(rows)
    myRowNames = ["r"+str(num) for num in range(len(rows))]
    prob.linear_constraints.add(
        lin_expr=rows, senses=mySense, rhs=myRhs, names=myRowNames)
    return myColNames


if __name__ == '__main__':
    group = str(sys.argv[1])
    sukodu = sukoduReader("input"+group+".data")
    myProb = cplex.Cplex()
    myColNames = lpInitialization(sukodu, myProb)

    try:
        myProb.solve()
        x = myProb.solution.get_values()
        for i in range(N_digit):
            for j in range(N_digit):
                for k in range(1, N_digit+1):
                    pos = myColNames.index(getVarName(i, j, k))
                    if x[pos] == 1:
                        sukodu[i][j] = k

        with open("output"+group+".data", "w") as f:
            for line in sukodu:
                out = ""
                for var in line:
                    out += str(var) + " "
                f.write(out + "\n")

    except CplexError as exc:
        print(exc)
    
    
