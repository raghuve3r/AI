# Simple tetris program! v0.2
# D. Crandall, Sept 2016
#References:
#http://www.cs.uml.edu/ecg/uploads/AIfall10/eshahar_rwest_GATetris.pdf
#https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
#Discussed with Supreeth Suryaprakash Keragodu(skeragod)


from AnimatedTetris import *
from SimpleTetris import *
from kbinput import *
import time, sys
from copy import deepcopy


class HumanPlayer:
    def get_moves(self, tetris):
        print "Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\nThen press enter. E.g.: bbbnn\n"
        moves = raw_input()
        return moves

    def control_game(self, tetris):
        while 1:
            c = get_char_keyboard()
            commands = {"b": tetris.left, "n": tetris.rotate, "m": tetris.right, " ": tetris.down}
            commands[c]()


#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#


class ComputerPlayer:
    # This function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. tetris is an object that lets you inspect the board, e.g.:
    #   - tetris.col, tetris.row have the current column and row of the upper-left corner of the
    #     falling piece
    #   - tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
    #   - tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
    #     issue game commands
    #   - tetris.get_board() returns the current state of the board, as a list of strings.
    #


    #calculates the height of each column in the board and returns an array having the height of each column
    def calcHeight(self,board):
        h = []
        for i in range(0, tetris.BOARD_WIDTH):
            for j in range(len(board)):
                if board[j][i] == 'x':
                    h.append(len(board) - j)
                    break
                if j == len(board) - 1:
                    h.append(0)
        return h
    #calculates the bumpness in a given board configuration
    def calcBump(self,height):
        b = 0
        for i in range(len(height)):
            if i < len(height) - 1:
                b += abs(height[i] - height[i + 1])
        return b
    #calculates the number of holes in a given board configuration
    def calcHole(self,board,height):
        h = 0
        for i in range(0, tetris.BOARD_WIDTH):
            if sum(height) != 0:
                for j in range(len(board) - height[i], len(board)):
                    if board[j][i] == ' ':
                        h += 1
        return h
    #calculates the number of completed lines of a given board configuration
    def calcLines(self,board):

        l = 0

        for i in range(len(board)):
            if board[i].count(board[i][0]) == len(board[i]) and board[i][0] == 'x':
                l += 1
        return l
    #calculates the width of a given piece
    def piece_width(self,piece):
        width = 0
        for i in piece:
            count = len(i)
            if count > width:
                width = count
        return width

    #places the given piece and its next piece in all possible rotations and all possible rows and columns
    #and then calculates a score for each combination based on 4 criteria
    #The best column and the best angle is returned by this function
    def findBestPiece(self, boardx, piecex, next_piecex):
        board = deepcopy(boardx)
        piece = deepcopy(piecex)
        next_piece = deepcopy(next_piecex)
        bestScore = None
        bestCol = 0
        r=0
        #checking for each possible rotation for current piece
        for angle1 in range(0,360,90):
            rotated = TetrisGame.rotate_piece(piece, angle1)
            #checking for each possible column for current piece
            for c in range(tetris.BOARD_WIDTH-ComputerPlayer.piece_width(self,rotated)+1):
                row = 0
                #checking for each row if it has any collision for current piece
                while not TetrisGame.check_collision((board, 0), rotated, row+1, c) and row < tetris.BOARD_HEIGHT:
                    row += 1
                #the current piece is placed on the row before the last collision occured
                board1 = TetrisGame.place_piece((board, 0), rotated, row, c)[0]
                #checking for each possible roration for the next piece
                for angle2 in range(0,360,90):
                    rotated1 = TetrisGame.rotate_piece(next_piece,angle2)
                    # checking for each possible column for next piece
                    for c1 in range(tetris.BOARD_WIDTH-ComputerPlayer.piece_width(self,rotated1)+1):
                        row1 = 0
                        # checking for each row if it has any collision for next piece
                        while not TetrisGame.check_collision((board1, 0), rotated1, row1+1, c1) and row1 < tetris.BOARD_HEIGHT:
                            row1 += 1
                        #next occurring piece is placed on the row before the last collision occured
                        board2 = TetrisGame.place_piece((board1, 0), rotated1, row1, c1)[0]

                        #height of each column of the current configuration of board
                        height = ComputerPlayer.calcHeight(self,board2)

                        #bumpness in the current configuration of board
                        bump = ComputerPlayer.calcBump(self,height)

                        #number of completed lines in the current configuration of board
                        line = ComputerPlayer.calcLines(self,board2)

                        #number of holes in the current configuration of board
                        hole = ComputerPlayer.calcHole(self,board2,height)

                        #calculating the score
                        #score is calculated using the above 4 conditions
                        #each of the above properties are assigned a penalty based on our desiredness
                        #since the number of completed lines is highly desirable, the completed line property is multiplied by a factor of 3
                        #holes, bumpness and height are less desirable properties, hence they are assigned a penalty of -2,-1,-1 respectively.
                        score = 3.0 * line - 2.0 * hole - 1.0 * bump - 1.0 * sum(height)


                        #the best score is being calculated in the following module
                        #I also store the best angle of rotation and the best column
                        if score > bestScore or bestScore == None:
                            bestScore = score
                            angle = angle1
                            if angle == 0:
                                r = 0
                            elif angle == 90:
                                r = 1
                            elif angle == 180:
                                r = 2
                            else:
                                r = 3
                            bestCol = c

        #at this stage, the best angle of rotation and the best column is found and returned to the calling function
        return r,bestCol

    def get_moves(self, tetris):
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        board = tetris.get_board()
        piece = tetris.get_piece()[0]
        next_piece = tetris.get_next_piece()

        #the best angle of rotation and the best column is obtained
        a, c = ComputerPlayer.findBestPiece(self, board, piece, next_piece)

        #the offset from the best column and the current column
        index = tetris.col - c
        moves = ""
        if index > 0:
            for f in range(a):
                moves = moves+"n"
            while index != 0:
                moves = moves+"b"
                index -= 1
        elif index < 0:
            for f in range(a):
                moves = moves+"n"
            while index != 0:
                moves = moves+"m"
                index += 1
        else:
            for f in range(a):
                moves = moves+"m"

        #the required number of moves is recorded as a string in moves
        return moves

    # This is the versrion that's used by the animted version. This is really similar to get_moves,
    # except that it runs as a separate thread and you should access various methods and data in
    # the "tetris" object to control the movement. In particular:
    #   - tetris.col, tetris.row have the current column and row of the upper-left corner of the
    #     falling piece
    #   - tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
    #   - tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
    #     issue game commands
    #   - tetris.get_board() returns the current state of the board, as a list of strings.
    #
    def control_game(self, tetris):
        # another super simple algorithm: just move piece to the least-full column
        while 1:
            time.sleep(0.1)
            board = tetris.get_board()
            piece = tetris.get_piece()[0]
            next_piece = tetris.get_next_piece()

            #the best angle of rotation and the best column is obtained
            a,c = ComputerPlayer.findBestPiece(self,board,piece,next_piece)

            #the offset from the best column and the current column
            index = tetris.col - c
            if index > 0:
                for f in range(a):
                    tetris.rotate()
                while index != 0:
                    tetris.left()
                    index -= 1
                tetris.down()
            elif index < 0:
                for f in range(a):
                    tetris.rotate()
                while index != 0:
                    tetris.right()
                    index += 1
                tetris.down()
            else:
                for f in range(a):
                    tetris.rotate()
                tetris.down()
###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer()
    else:
        print "unknown player!"

    if interface_opt == "simple":
        tetris = SimpleTetris()
    elif interface_opt == "animated":
        tetris = AnimatedTetris()
    else:
        print "unknown interface!"

    tetris.start_game(player)

except EndOfGame as s:
    print "\n\n\n", s



