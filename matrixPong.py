'''
============================================
=Gerrit Roessler                           =
=11/23/21                                  =
=Displaying a Pong game on a 8x8 LED Matrix=
============================================
'''

from RPi import GPIO
from time import sleep
from array import *
GPIO.setmode(GPIO.BCM)

#the delay has to be crazy low since it ticks once for every matrix dot
delay = 0.000001

#simply the row and column numbers
#there is forwards and backwards arrays
#because of how I want them displayed
row = [27, 24, 4, 23, 25, 22, 18, 17]
#light1 = [1, 1, 0, 0, 0, 0, 0]
#row = [17, 18, 22, 25, 23, 4, 24, 27]
#col = [16, 13, 20, 19, 6, 21, 26, 12]
col = [12, 26, 21, 6, 19, 20, 13, 16]

#sets up the GPIO pins
for x in range(8):
    GPIO.setup(row[x], GPIO.OUT)
for y in range(8):
    GPIO.setup(col[y], GPIO.OUT)

#turns on and off a entire board
def all(toggle):
    if(toggle):
        for x in range(8):
            GPIO.output(row[x], GPIO.HIGH)
        for y in range(8):
            GPIO.output(col[y], GPIO.HIGH)
    elif(not toggle):
        for x in range(8):
            GPIO.output(row[x], GPIO.LOW)
        for y in range(8):
            GPIO.output(col[y], GPIO.LOW)

#turns on or off a LED at a specific coordinate
#the on/off is nice if you have a board of booleans
def single(_row, _col, toggle):
    if(toggle):
        GPIO.output(row[_row], GPIO.HIGH)
        GPIO.output(col[_col], GPIO.HIGH)
    else:
        GPIO.output(row[_row], GPIO.LOW)
        GPIO.output(col[_col], GPIO.LOW)

'''
a very nice function if I say so myself,
it uses the 'single' method to turn on a full 8x8 matrix with a 2d 8x8 array
'''
def full(lst, seconds):
    x = 0
    while(True):
        for i in range(8):
            for j in range(8):
                    if(lst[i][j] > 0):
                        single(i, j, True)
                    else:
                        single(i, j, False)
                    sleep(delay)
                    all(False)
                    x += 1

        #so I can keep track of how long I want to board displayed
        if(x >= 10000 * seconds):
            all(False)
            break
    #for if it ever manages to spectacularly break
    all(False)

#player 1 y coords
p1 = [2, 3, 4]
#player 2 y coords
p2 = [2, 3, 4]
#Ball coords
bx = 1
by = 3
#ball velocity x/y
bVx = 1
bVy = 1

baseState = [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [2, 0, 0, 0, 0, 0, 0, 2],
             [2, 0, 0, 1, 0, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 0, 2],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0]]
#a bit of a artafact from when I wanted to
#make the game play over and over, and I see no reason to remove it
gameBoard = baseState

#input the x & y with velocities added
#returns 'x' to reverse x, 'y' to reverse y,
#'k' to kill, 'n' for nothing
def ballRebound (x, y, vx, vy, board):
    if (y == 0 or y == 7):
        print("hit bounce wall")
        return "y"
    elif(x == 0 or x == 7):
        return "k"
        print("kill")
    elif(x + vx == 8 or y + vy == 8):
        return "k"
        print("kill")
    elif((board[y + vy][x + vx] == 2) and (x + vx != 8 or y + vy != 8)):
        print("hit player")
        return "x"
    elif(x + vx == 8 or y + vy == 8):
        return "x"
        print("Weird one")
    else:
        return "n"


'''
A nice little method to update a newly cleared gameBoard to the different states
I think that a lot of the assignments of types
other then 0 and 1 on the board is a artifact from previous ideas,
but it doesn't break anything so it's easier to keep then remove,
and it made debugging a little easier
'''
def reassignment():
    for x in range(8):
        for y in range(8):
            if(x == bx and y == by):
                gameBoard[y][x] = 1
                print("ball assigned")
            elif(x == 0):
                if(y == p1[0] or y == p1[1] or y == p1[2]):
                    gameBoard[y][x] = 2
            elif(x == 7):
                if(y == p2[0] or y == p2[1] or y == p2[2]):
                    gameBoard[y][x] = 2

'''
Quick and simple method to clear the board, with a little extra to
check if the ball is allowed to be reassigned
'''
def clearBoard(bx, bVx, by, bVy):
    #clearing screen
    for x in range(8):
        for y in range(8):
            gameBoard[x][y] = 0
    print("Board Cleared")
    if(bx + bVx <= 7 and by + bVy <= 7):
        return True
    else:
        return False

'''
Player movement script.
It will move if
-the ball is moving towards it
-the center is not in line with the ball
-the the movement would not put the player out of bounds

*the 'z' is there so it can be called multiple times without error, before and
after the ball is moved and so it moves a little faster
'''
def playerMove(z):
    #left player logic
    if(p1[1] != by and p1[2] + bVy <= 7 and p1[0] + bVy >= 0 and bVx < 0):
        if(bx != (0+z)):
            for x in range(3):
                p1[x] += bVy

    #right player logic
    if(p2[1] != by and p2[2] + bVy <= 7 and p2[0] + bVy >= 0 and bVx > 0):
        if(bx != (7-z)):
            for x in range(3):
                p2[x] += bVy

try:
    all(False)
    #I don't think the gameloop is required
    #anymore but I'm too afraid to remove it to check
    gameloop = True
    while(gameloop):
        playerMove(1)
        #figuring out what to do with the ball,
        #if it bounces, dies or nothing
        if(ballRebound(bx, by, bVx, bVy, gameBoard) == "y"):
            bVy *= -1
        elif(ballRebound(bx, by, bVx, bVy, gameBoard) == "x"):
            bVx *= -1
        elif(ballRebound(bx, by, bVx, bVy, gameBoard) == "k"):
            print("hit kill wall")
            break
        else:
            print("Nothing hit")

        playerMove(0)

        #clearing the board and reassignment
        if(clearBoard(bx, bVx, by, bVy)):
            bx += bVx
            by += bVy
        reassignment()
        print(str(bx) + ", " + str(by) + "\n")
        full(gameBoard, 1/4.5)

        #I put this in and it works now,
        #it's a nice catch-all anyway
        if(bx == 0 or bx == 7):
            break



    #after gameover, so we can have a nice post game
    reassignment()
    print("Ended")
    full(gameBoard, 3)
    GPIO.cleanup()

#these two are down here to make debugging easier, just catching
#out of bounds and cleaning up after keyboard interrupts
except IndexError:
    print("Tried to assign out of bounds")
    print(str(bx) + " pos x, " + str(by) + " pos y")
    print(str(bVx) + " V x, " + str(bVy) + " V y")
    GPIO.cleanup()
except KeyboardInterrupt:
    print("Keyboard interupt")
    all(False)
    GPIO.cleanup()