import random
import numpy as np
import math
from copy import deepcopy
import pickle
import sys
import time

global boardsize 
boardsize = 4

class Node:
    def __init__(self,state,turn,parent = None):
        self.state = state
        self.w = 0
        self.N = 0

        self.parent = parent
        self.childs = []    
        self.turn = turn
        
        self.UCT = 0
    
    def addchild(self,state):
        child = Node(state,1-self.turn,self)
        self.childs.append(child)
        return child

    def CalUct(self, n):
        #n : 부모의 N
        if self.N == 0:
            self.UCT = math.inf
        else:
            self.UCT = (self.w/self.N)+math.sqrt(2)*math.sqrt(math.log(n)/(self.N))
    
    def __str__(self):
        pr = ""
        for i in range(boardsize):
            for j in range(boardsize):
                if self.state[i][j] == -1 * boardsize:
                    pr += str("O") + " "
                elif self.state[i][j] == 0:
                    pr += str("@") + " "
                elif self.state[i][j] == 1:
                    pr += str("X") + " "
            pr += "\n"
        pr += "w : " + str(self.w) + " N : " +str(self.N) + " UCT : " + str(self.UCT)
        return pr

class Tree:
    def __init__(self,state,turn):
        self.root = Node(state,turn,None)
        self.now = self.root
        
    def selection(self):
        self.now = self.root
        
        while len(self.now.childs) != 0: 

            for i in range(len(self.now.childs)):
                self.now.childs[i].CalUct(self.now.N)
                
            self.now = max(self.now.childs,key = lambda x : x.UCT)
            
        return self.now.state

    def expansion(self):
        arr = statetoarr(self.now.state)
        
        for n in arr:
            states = checkboard(deepcopy(self.now.state),self.now.turn,n)
            self.now.addchild(states)
        
        if len(self.now.childs)!=0:
            self.now = random.choice(self.now.childs)
            return 1 # 1일때는 게임이 안 끝난, 연장하고 랜덤으로 들어감

        return -1 # -1일때는 게임이 끝난, leaf node 일때
    
    def backpropagation(self,w, k):

        if self.now.turn == 0: # 사람차례
            w *= -1

        while True:
            self.now.w += w
            self.now.N += k
            w *= -1
            if self.now == self.root:
                return
            self.now = self.now.parent    
        
def initial():
    state = [[-1*boardsize for _ in range(boardsize)] for _ in range(boardsize)]
    # -3 : 아무것도 없음
    # 0 : 컴퓨터
    # 1 : 사람
    return state

def statetoarr(state): # 빈칸만 저장
    arr = []
    for i in range(boardsize**2):
        if state[int(i//boardsize)][int(i%boardsize)] == -1*boardsize:
            arr.append(i)
    return arr

def randomchoice(state,t,arr):
    n = arr.pop(0)
    
    if t == 0:
        state[int(n//boardsize)][int(n%boardsize)] = 0
    elif t == 1:
        state[int(n//boardsize)][int(n%boardsize)] = 1
    return state, n

def checkboard(state,t,n):
    if t == 0:
        state[int(n//boardsize)][int(n%boardsize)] = 0
    elif t == 1:
        state[int(n//boardsize)][int(n%boardsize)] = 1
    return state

def checkwin(state):
    boards = [state, np.transpose(state)]
    c = 0
    h = 0
    for board in boards:
        for row in board:
            if sum(row) == boardsize:
                h = 1
            elif sum(row) == 0:
                c = 1

        diagsum = 0
        diagsum2 = 0
        for diag in range(boardsize):
            diagsum += int(board[diag][diag])
            diagsum2 += int(board[diag][boardsize-1-diag])
        if diagsum == boardsize or diagsum2 == boardsize:
            h = 1
        elif diagsum == 0 or diagsum2 == 0:
            c = 1

    if (len(statetoarr(state)) == 0): # draw
        return 2 
    elif c == 1: # computer win
        return 0
    elif h == 1: # human win
        return 1
    
    return 3

def simulator(states,turn,times):
    w = 0

    for _ in range(times):
        state = deepcopy(states)
        t = turn
        arr = statetoarr(state)
        random.shuffle(arr)

        while True:
            if checkwin(state) != 3:
                
                if checkwin(state) == 2:
                    #print("draw")
                    
                    break
                elif checkwin(state) == 1:
                    #print("you win")
                    w -= 1
                    
                    break
                elif checkwin(state) == 0:
                    #print("com win")
                    w += 1
                    
                    break

            if len(arr) == 0:
                #print("draw")
                
                break

            state, n = randomchoice(state,t,arr)
            t = 1 - t

    if (w > 0):
        w = 1
    elif (w < 0) :
        w = -1
    elif (w == 0):
        w = 0

    return w

def Train(board,pt):
    
    turn = pt
    tree = Tree(board, turn)
    k = 10
    for i in range(1000):
        tree.selection()   
        t = tree.expansion()
        
        if t == 1:
            w = simulator(deepcopy(tree.now.state),tree.now.turn,k)
            tree.backpropagation(w, k)
        else:
            tree.backpropagation(0, k)

        if (i % 100 == 0):
            print(str(int(i/100)) +" %" )

    return tree
print("Type 0 if you are going to do it first")
print("Type 1 if you are going to do it later")
work = int(input("type here : "))

if (work == "train"):
    tree = Train()
    with open("mctsttt2.pickle","wb") as f:
        pickle.dump(tree,f)

elif (work == 1):
    
    board = initial()

    for i in range(20):
        start = time.time()
        math.factorial(10000)
        tree = Train(board,0)
        
        end = time.time()
        print(f"{end - start:.5f} sec")

        mi = -999
        ans = 0
        
        for i in tree.now.childs:
            
            if i.w > mi:
                ans = i
                mi = i.w 
        tree.now = ans
        print("Computer")
        print(tree.now)

        game = checkwin(tree.now.state)
            
        if game == 2:
            print("Draw")
            sys.exit()
        elif game == 1:
            print("You win")
            sys.exit()
        elif game == 0:
            print("Com win")
            sys.exit()

        arr = statetoarr(tree.now.state)
            
        if (len(arr) == 0):
            print("Draw")
            sys.exit()

        n = int(input("your turn : "))
        arr.remove(n)
        for i in tree.now.childs:
            if statetoarr(i.state) == arr:
                tree.now = i
                print(tree.now)
                break
        
        game = checkwin(tree.now.state)
            
        if game == 2:
            print("Draw")
            sys.exit()
        elif game == 1:
            print("You win")
            sys.exit()
        elif game == 0:
            print("Com win")
            sys.exit()
        print("Calculating...")
        board = tree.now.state 


elif (work == 0):
    board = initial()
    n = int(input("your turn : "))
    board[n//boardsize][n%boardsize] = 0

    for i in range(7):
        start = time.time()
        math.factorial(10000)
        tree = Train(board,1)
        end = time.time()
        print(f"{end - start:.5f} sec")

        mi = -999
        ans = 0
        
        for i in tree.now.childs:
            
            if i.w > mi:
                ans = i
                mi = i.w 
        tree.now = ans
        print("Computer")
        print(tree.now)

        game = checkwin(tree.now.state)
            
        if game == 2:
            print("Draw")
            sys.exit()
        elif game == 1:
            print("Com win")
            sys.exit()
        elif game == 0:
            print("You win")
            sys.exit()

        arr = statetoarr(tree.now.state)
            
        if (len(arr) == 0):
            print("Draw")
            sys.exit()

        n = int(input("your turn : "))
        arr.remove(n)
        for i in tree.now.childs:
            if statetoarr(i.state) == arr:
                tree.now = i
                print(tree.now)
                break
        
        game = checkwin(tree.now.state)
            
        if game == 2:
            print("Draw")
            sys.exit()
        elif game == 1:
            print("Com win")
            sys.exit()
        elif game == 0:
            print("You win")
            sys.exit()
        print("Calculating...")
        board = tree.now.state 
        