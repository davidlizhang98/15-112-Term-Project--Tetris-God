from tkinter import *
import pygame
import random
import copy

class tetrisGame(object):
    
####################################
# Majority of the base Tetris Framework created by David Zhang @dlzhang Week6
# Adapted to Pygame and added notable features for the Term Project
# Used pieces of the Pygame Framework from Lukas Peraza @http://blog.lukasperaza.com/getting-started-with-pygame/

####################################
# Tetris
####################################

#####################################
# Event Handlers
#####################################

    #initializes the game
    def __init__(self, runAI = True, xPos = 0, yPos = 0, AISpeedInput = 10, AIDifficultyInput = 5, puzzleBoard = False, width = 400, height = 600, fps = 60, title = "Tetris", doubleManual = 0):
        self.runAI = runAI
        self.xPos = xPos
        self.yPos = yPos
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.bgColor = (178, 7, 25)
        self.AISpeedInput = AISpeedInput
        self.AIDifficultyInput = AIDifficultyInput
        self.puzzleBoard = puzzleBoard
        self.doubleManual = doubleManual
        pygame.init()
    
    def mousePressed(self, x, y):
        # use event.x and event.y
        pass
    
    def mouseReleased(self, x, y):
        pass
    
    def mouseMotion(self, x, y):
        pass
    
    def mouseDrag(self, x, y):
        pass
    
    #Responds based on keys pressed
    def keyPressed(self, keyCode, modifier, screen):
        #if the game has ended, the only valid key press should be to restart
        if (self.isGameOver or self.isGameWon):
            if (keyCode == 114): self.init()
        #otherwise, give the option to pause or rotate/move the piece
        elif (keyCode == 112): self.isPaused = not self.isPaused
        elif (keyCode == 114): 
            if (self.isPaused): self.init()
        elif (self.runAI == False):
            #if there is only one manual player, use standard controls
            if (self.doubleManual == 0):
                if (keyCode == 276): self.moveFallingPiece(0, -1)
                elif (keyCode == 275): self.moveFallingPiece(0, 1)
                elif (keyCode == 274): self.moveFallingPiece(1, 0)
                elif (keyCode == 273): self.rotateFallingPiece()
                elif (keyCode == 303) or (keyCode == 304): self.doHold()
                elif (keyCode == 32): self.hardDrop()
            #if there are two manual players, change the keys for player 1
            elif (self.doubleManual == 1):
                if (keyCode == 97): self.moveFallingPiece(0, -1)
                elif (keyCode == 100): self.moveFallingPiece(0, 1)
                elif (keyCode == 115): self.moveFallingPiece(1, 0)
                elif (keyCode == 119): self.rotateFallingPiece()
                elif (keyCode == 304): self.doHold()
                elif (keyCode == 122): self.hardDrop()
            #if there are two manual players, change the keys for player 2
            elif (self.doubleManual == 2): 
                if (keyCode == 276): self.moveFallingPiece(0, -1)
                elif (keyCode == 275): self.moveFallingPiece(0, 1)
                elif (keyCode == 274): self.moveFallingPiece(1, 0)
                elif (keyCode == 273): self.rotateFallingPiece()
                elif (keyCode == 303): self.doHold()
                elif (keyCode == 13): self.hardDrop()
    
    #calls timerFired to modify the board every time the timerDelay passes
    def timerFired(self, dt):            
        #if the game is over or the game is paused, don't move any pieces
        if (not self.isGameOver and not self.isPaused and not self.isGameWon):
            self.time += dt
            self.stopwatch += dt
            if (self.runAI == True):
                self.AIStep += dt
                #does a move based on the AI speed
                if self.AIStep >= self.AISpeed:
                    self.AIStep %= self.AISpeed
                    self.doStep = True
                    self.findBestPlacement()
            if self.time >= 1000:
                #move the piece and if the piece can't move, returns False
                move = self.moveFallingPiece(1, 0)
                self.time %= 1000
            #if the piece can't move, place the piece and try to remove the full
            #rows, then spawn a new piece
                if (not move):
                    self.removeGhostPiece()
                    self.placeFallingPiece()
                    self.removeFullRows()
                    self.newFallingPiece()
                    #if the newly spawned piece can't be legally placed, display Game
                    #Over
                    if (not self.isLegal(self.board,self.fallingPiece,self.fallingPieceRow,
                                        self.fallingPieceCol,self.fallingPieceRows,self.fallingPieceCols)):
                        self.isGameOver = True
                    
    #calls all the draw functions when it is called
    def redrawAll(self, screen):
        # draws the game screen, the score at the top left, 
        #and the gameOver screen if the game is over
        self.drawGame(screen)
        self.drawScore(screen)
        self.drawPaused(screen)
        self.drawGameOver(screen)
        self.drawGameWon(screen)
    
    def isKeyPressed(self, key):
        pass

######################################
# Game Data
######################################

    #initializes the variables that will be used by the Tetris program
    def init(self,rows=20,cols=10,margin=100,cellWidth=18,cellHeight=18,randomRow=11):
        self.stopwatch = 0
        self.stopwatchTime = ""
        self.rows = rows
        self.cols = cols
        self.margin = margin
        self.cellWidth = cellWidth
        self.cellHeight = cellHeight
        ######################################
        # initializes the board
        ######################################
        self.font = pygame.font.SysFont("gillsansultra", 15)
        self.emptyColor = (0,0,0)
        self.board = [[self.emptyColor]*self.cols for row in range(self.rows)]
        #defines the tetrominoes
        self.tetrisPieces = dict({'iPiece':((91,212,252),[[True, True, True, True]]),
                                  'jPiece':((0,0,255),[[True, False, False],
                                                       [True, True, True]]),
                                  'lPiece':((232,126,5),[[False, False, True],
                                                         [True, True, True]]),
                                  'oPiece':((232,217,5),[[True, True],
                                                         [True, True]]),
                                  'sPiece':((0,255,0),[[False, True, True],
                                                       [True, True, False]]),
                                  'zPiece':((255,0,0),[[True, True, False],
                                                       [False, True, True]]),
                                  'tPiece':((156,5,232),[[False, True, False],
                                                         [True, True, True]])})
        ############################
        # Vars for the hold piece and the queue pieces
        ############################
        self.holdPiece = None
        self.currentPiece = None
        self.heldPiece = False
        self.queue = []
        #############################
        # Vars for the falling piece
        #############################
        self.fallingPiece = 0
        self.fallingPieceColor = ""
        self.fallingPieceRows = 0
        self.fallingPieceCols = 0
        self.fallingPieceRow = 0
        self.fallingPieceCol = 0
        ##############################
        # Vars for the ghost piece
        ##############################
        self.ghostPiece = 0
        self.ghostColor = (222,222,222)
        self.ghostPieceRows = 0
        self.ghostPieceCols = 0
        self.ghostPieceRow = 0
        self.ghostPieceCol = 0
        self.ghostBoard = [[self.emptyColor]*self.cols for row in range(self.rows)]
        ##############################
        # Vars for extraneous events
        ##############################
        self.score = 0
        self.isGameOver = False
        self.isPaused = False
        self.time = 0
        ###############################
        # Vars for AI Calculating the Best Move
        ###############################
        self.colHeights = [0]*cols
        self.holes = [0]*cols
        self.gaps = [0]*cols
        self.AIlinesCleared = 0
        self.boardScore = 0
        self.holeWeight = 5.9288669341469555
        self.colHeightWeight = 1.9162926946223073
        self.gapWeight = 3.3878742140370637
        self.clearWeight = 4.641363224169059
        self.oldBoard = self.board
        self.simBoard = self.board
        self.simPiece = None
        self.placementColor = (100,100,100)
        ###############################
        # Vars for AI performing the Best Move
        ###############################
        self.AIStep = 0
        self.doStep = False
        self.completedMove = True
        self.rotationNumber = 0
        self.bestPiece = None
        self.bestCol = 0
        ################################
        # Testing with a "puzzle" board
        ################################
        if (self.puzzleBoard == True):
            self.randomRow = randomRow
            self.nonEmptyColor = (100,100,100)
            for i in range(20):
               row = random.randint(self.randomRow,19)
               col = random.randint(0,9)
               if (self.board[row][col] == self.emptyColor): 
                   self.board[row][col] = self.nonEmptyColor
        ################################
        # Modifying the AI Difficulty/Speed
        ################################
        self.AISpeed = (11-self.AISpeedInput)*100
        self.AIDifficulty = 0.96**(5-self.AIDifficultyInput)
        ################################
        # Multiplayer Vars
        ################################
        self.linesCleared = 0
        self.garbageRows = 0
        self.garbageColor = (50,50,50)
        self.addGarb = False
        self.isGameWon = False
        ###############################
        # Record Saving
        ###############################
        self.addedHistory = False
        self.recordedHistory = False
        ##############################
        # initializes the game
        ##############################
        self.makeQueue()
        self.newFallingPiece()

####################################################
# Fundamental Game Functions
####################################################

    #draws the background rectangle and then calls drawBoard and drawFallingPiece
    def drawGame(self, screen):
        pygame.draw.rect(screen, (19,2,28), (55+self.xPos,55+self.yPos,280,460))
        pygame.draw.rect(screen, (57,66,133), (50+self.xPos,50+self.yPos,280,460))
        pygame.draw.rect(screen,(19,2,28),(100+self.xPos,100+self.yPos,180,360))
        if (self.runAI == True):
            AIText = self.font.render("AI", 1, (146,148,150))
            screen.blit(AIText, (170+self.xPos, 520+self.yPos))
            if (self.AISpeedInput == 10.99):
                speedText = self.font.render("Speed: GOD", 1, (146,148,150))
            else:
                speedText = self.font.render("Speed: " + str(self.AISpeedInput) + "/10", 1, (146,148,150))
            screen.blit(speedText, (125+self.xPos,540+self.yPos))
            if (self.AISpeedInput == 10.99):
                difficultyText = self.font.render("Intelligence: GOD", 1, (146,148,150))
            else:
                difficultyText = self.font.render("Intelligence: " + str(self.AIDifficultyInput) + "/5", 1, (146,148,150))
            screen.blit(difficultyText, (105+self.xPos,560+self.yPos))
        else:
            manualText = self.font.render("Manual", 1, (146,148,150))
            screen.blit(manualText, (150+self.xPos, 550+self.yPos))
        #draws the stopwatch
        timeHours = self.stopwatch//(3600*1000)
        timeMinutes = (self.stopwatch//(60*1000))%60
        timeSeconds = (self.stopwatch//1000)%60
        timeMilliseconds = (self.stopwatch%1000)
        self.stopwatchTime = "%d:%02d:%02d.%03d" % (timeHours,timeMinutes,timeSeconds,timeMilliseconds)
        timerText = self.font.render(str(self.stopwatchTime), 1, (146,148,150))
        darkTimerText = self.font.render(str(self.stopwatchTime), 1, (0,0,0))
        screen.blit(darkTimerText, (251+self.xPos, 10+self.yPos))
        screen.blit(timerText, (250+self.xPos, 10+self.yPos))
        self.drawQueue(screen)
        self.drawHold(screen)
        self.drawBoard(screen)
        self.drawGhostPiece(screen)
        self.drawFallingPiece(screen)
    
    #draws the board by calling drawCell for each cell in the board
    def drawBoard(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                self.drawCell(screen, row, col, self.board[row][col])
    
    #gets the x0, y0, x1, y1, of each cell/square based on the row and column of
    #the square in the board
    def getCellBounds(self, row, col):
        x0 = self.margin + (col*self.cellWidth)
        y0 = self.margin + (row*self.cellHeight)
        x1 = x0 + self.cellWidth
        y1 = y0 + self.cellHeight
        return (x0, y0, x1, y1)
    
    #draws each cell based on the row and column of the cell and its given color
    def drawCell(self, screen, row, col, color):
        (x0, y0, x1, y1) = self.getCellBounds(row, col)
        m = 2 #cell margin
        if (color == (0,0,0)):
            pygame.draw.rect(screen, (55,55,55), (x0+self.xPos, y0+self.yPos, x1-x0-m, y1-y0-m), 1)
        else:
            m = 3
            (color1, color2, color3) = color
            darkColor1 = max(0, color1 - 50)
            darkColor2 = max(0, color2 - 50)
            darkColor3 = max(0, color3 - 50)
            pygame.draw.rect(screen, (darkColor1,darkColor2,darkColor3), (x0+self.xPos,y0+self.yPos,x1-x0-m,y1-y0-m))
            pygame.draw.rect(screen, color, (x0+m+self.xPos, y0+m+self.yPos, x1-x0-m-m, y1-y0-m-m))
    
    #spawns a new falling piece
    def newFallingPiece(self):
        self.queue.append(random.choice(['iPiece','jPiece','lPiece','oPiece',
                                         'sPiece','zPiece','tPiece']))
        self.currentPiece = self.queue[0]
        self.queue = self.queue[1:]
        self.fallingPiece = self.tetrisPieces[self.currentPiece][1]
        self.fallingPieceColor = self.tetrisPieces[self.currentPiece][0]
        #identifies the number of rows and cols that the piece has
        self.fallingPieceRows = len(self.fallingPiece)
        self.fallingPieceCols = len(self.fallingPiece[0])
        #identifies which row and which column the top-left corner of the falling
        #piece is located in
        self.fallingPieceRow = 0
        self.fallingPieceCol = self.cols//2 - (self.fallingPieceCols//2)
        self.removeGhostPiece()
        self.placeGhostPiece()
    
    #holds the current piece and replaces it with the piece in the hold queue
    def doHold(self):
        #you cannot hold twice in a row, so if a piece has just been held,
        #prevents the player from holding again
        if (self.heldPiece == False):
            self.heldPiece = True
            #if there is no piece in the hold queue, then place the current piece
            #in the hold queue, and use the next piece as the current piece, otherwise
            #replace the hold piece with the current piece
            if (self.holdPiece != None):
                (self.holdPiece,self.currentPiece) = (self.currentPiece,self.holdPiece)
                self.newHeldPiece(self.currentPiece)
            else:
                self.holdPiece = self.currentPiece
                self.newFallingPiece()

    #draws the falling piece by drawing the piece over the board, similar to how
    #the board was drawn, but only drawing when the section of the piece is true
    def drawFallingPiece(self, screen):
        self.removeGhostPiece()
        self.drawGhostPiece(screen)
        for row in range(self.fallingPieceRows):
            printRow = row + self.fallingPieceRow
            for col in range(self.fallingPieceCols):
                if (self.fallingPiece[row][col]):
                    printCol = col + self.fallingPieceCol
                    color = self.fallingPieceColor
                    self.drawCell(screen, printRow, printCol, color)

    
    #moves the falling piece by altering the position of the top-left corner of
    #the piece. If the piece cannot move in said direction, undo the move. If the  
    #move is possible, returns True, else returns False.
    def moveFallingPiece(self, drow, dcol):
        if (self.isGameOver == False) and (self.isPaused == False):
            self.fallingPieceRow += drow
            self.fallingPieceCol += dcol
            if (not self.isLegal(self.board,self.fallingPiece,self.fallingPieceRow,
                                self.fallingPieceCol,self.fallingPieceRows,self.fallingPieceCols)):
                self.fallingPieceRow -= drow
                self.fallingPieceCol -= dcol
                return False
            self.removeGhostPiece()
            self.placeGhostPiece()
            return True
    
    #rotates the falling piece clockwise 90 degrees
    def rotateFallingPiece(self):
        #keeps track of all of the values of the falling piece in case we need to
        #undo the rotation
        if (self.isGameOver == False) and (self.isPaused == False):
            oldPiece = self.fallingPiece
            oldRow = self.fallingPieceRow
            oldCol = self.fallingPieceCol
            oldRows = self.fallingPieceRows
            oldCols = self.fallingPieceCols
            newPiece = [[False]*oldRows for i in range(oldCols)]
            #creates the new piece by assigning the appropriate indices in the initial
            #piece to the appropriate indices in the final piece
            for row in range(oldRows):
                for col in range(oldCols):
                    newPiece[col][oldRows - 1 - row] = oldPiece[row][col]
            #updates the falling piece to the newly rotated falling piece
            self.fallingPiece = newPiece
            self.fallingPieceRows = len(newPiece)
            self.fallingPieceCols = len(newPiece[0])
            #if the rotation isn't legal, undo all the previous changes
            if (not self.isLegal(self.board,self.fallingPiece,self.fallingPieceRow,
                                 self.fallingPieceCol,self.fallingPieceRows,self.fallingPieceCols)):
                self.fallingPiece = oldPiece
                self.fallingPieceRow = oldRow
                self.fallingPieceCol = oldCol
                self.fallingPieceRows = oldRows
                self.fallingPieceCols = oldCols
            self.removeGhostPiece()
            self.placeGhostPiece()
    
    #tests if the piece is legal by making sure the proposed move/rotation is both
    #still inside the board and does not place the piece inside another non-empty
    #piece/block.
    def isLegal(self, board, piece, pieceRow, pieceCol, pieceRows, pieceCols):
        for row in range(pieceRows):
            checkRow = row + pieceRow
            for col in range(pieceCols):
                checkCol = col + pieceCol
                if ((checkRow >= self.rows) or (checkCol >= self.cols) or
                    (checkRow < 0) or (checkCol < 0)):
                    return False
                #if the square in the piece is True and the square is also taken
                #by another piece, return True
                if (piece[row][col]) and (board[checkRow][checkCol] != self.emptyColor): 
                    return False
        return True
    
    #once the piece has reached the bottom, place the falling piece by adding it to
    #the board
    def placeFallingPiece(self):
        for row in range(self.fallingPieceRows):
            placeRow = row + self.fallingPieceRow
            for col in range(self.fallingPieceCols):
                placeCol = col + self.fallingPieceCol
                if (self.fallingPiece[row][col]):
                    self.board[placeRow][placeCol] = self.fallingPieceColor
        self.heldPiece = False

    #if the game is paused, display that the game is paused
    def drawPaused(self, screen):
        if (self.isPaused):
            pygame.draw.rect(screen, (0,0,0), (105+self.xPos,205+self.yPos,180,100))
            pygame.draw.rect(screen, (155,155,155), (100+self.xPos,200+self.yPos,180,100))
            pauseText = self.font.render("PAUSED", 1, (255,255,255))
            screen.blit(pauseText, (150+self.xPos,225+self.yPos))
            restartText = self.font.render("(press r to restart)", 1, (255,255,255))
            screen.blit(restartText, (102+self.xPos,265+self.yPos))

    #if the player has won, print the win screen
    def drawGameWon(self, screen):
        if (self.isGameWon):
            pygame.draw.rect(screen, (0,0,0), (65+self.xPos,255+self.yPos,300,70))
            pygame.draw.rect(screen, (255,255,255), (60+self.xPos,250+self.yPos,300,70))
            scoreText = self.font.render("You win! Final Score:" + str(self.score), 1, (46,48,50))
            screen.blit(scoreText, (100+self.xPos,265+self.yPos))
            restartText = self.font.render("(press r to restart)", 1, (46,48,50))
            screen.blit(restartText, (112+self.xPos,290+self.yPos))

    #if the player has lost, print the game over screen
    def drawGameOver(self, screen):
        if (self.isGameOver):
            pygame.draw.rect(screen, (0,0,0), (65+self.xPos,255+self.yPos,300,70))
            pygame.draw.rect(screen, (46,48,50), (60+self.xPos,250+self.yPos,300,70))
            scoreText = self.font.render("Game Over! Final Score:" + str(self.score), 1, (255,255,255))
            screen.blit(scoreText, (100+self.xPos,265+self.yPos))
            restartText = self.font.render("(press r to restart)", 1, (255,255,255))
            screen.blit(restartText, (122+self.xPos,290+self.yPos))
        
    #removes full Rows and increments the score accordingly
    def removeFullRows(self):
        newRow = self.rows
        oldScore = self.score
        self.linesCleared = 0
        #makes an empty newBoard which will replace the old board
        newBoard = [[self.emptyColor]*self.cols for row in range(self.rows)]
        for row in range(self.rows-1, 0, -1):
            addRow = False
            #if we see garbage or an empty piece, the row is not cleared so we must add it to the new board
            for col in range(self.cols):
                if (self.board[row][col] == (self.emptyColor) or (self.board[row][col] == self.garbageColor)):
                    addRow = True
            if (addRow == True):
                newRow -= 1
                for col in range(self.cols):
                    newBoard[newRow][col] = self.board[row][col]
            #if we don't add the row then the row is cleared and we increment the score
            else:
                self.score += 1
                self.linesCleared += 1
        #if there is garbage on the board and the player has cleared line(s) remove appropriate amounts of garbage
        while (self.hasGarbage(newBoard) == True) and (self.linesCleared > 0):
            newBoard = self.removeGarbage(newBoard)
        #if the newBoard is different then the board has changed and we update the board
        if (newBoard != self.board): 
            self.board = newBoard
            self.removeGhostPiece()
            self.placeGhostPiece()

    #adds rows of garbage to the bottom of the board
    def addGarbage(self, rows):
        for addRow in range(rows):
            tempBoard = copy.deepcopy(self.board)
            for row in range(self.rows):
               for col in range(self.cols):
                   #if the top row is already filled, then the player is shoved past the top and loses
                   if (self.board[0][col] != self.emptyColor): self.isGameOver = True
                   #since we are moving every block one row up, we must construct the bottom row
                   elif (row == self.rows-1): self.board[row][col] = self.garbageColor
                   else: self.board[row][col] = tempBoard[row+1][col]

    #removes garbage from the board based on the number of lines cleared
    def removeGarbage(self, board):
        self.linesCleared -= 1
        tempBoard = copy.deepcopy(board)
        for row in range(self.rows):
            for col in range(self.cols):
                #since we move each block one row down, we must construct the top-most row
                if (row == 0): board[row][col] = self.emptyColor
                else: board[row][col] = tempBoard[row-1][col]
        return board

    #checks if the board contains a garbage row or not
    def hasGarbage(self, board):
        if (board[self.rows-1][0] == self.garbageColor):
            return True
        else:
            return False

    #counts the number of full rows (but does not clear them), used to calculate board
    #score
    def countFullRows(self):
        self.AIlinesCleared = 0
        for row in range(self.rows-1, 0, -1):
            clearedLine = True
            for col in range(self.cols):
                if (self.simBoard[row][col] == (self.emptyColor)):
                    clearedLine = False
                    break
            if (clearedLine == True):
                self.AIlinesCleared += 1

    #returns how many lines are cleared so that it can be used by the multiplayer feature
    def sendGarbage(self):
        return self.linesCleared

    #returns if one of the players loses for the multiplayer feature
    def gameLost(self):
        return self.isGameOver  

    #if gameWon is called, the player has won the game
    def gameWon(self):
        self.isGameWon = True

############################################
# Extraneous Game Functions (for better gameplay)
############################################

    #draws the score of the player in the top left corner
    def drawScore(self, screen):
        score = "Score: " + str(self.score)
        scoreText = self.font.render(score, 1, (146,148,150))
        darkScoreText = self.font.render(score, 1, (0,0,0))
        screen.blit(darkScoreText, (11+self.xPos,10+self.yPos))
        screen.blit(scoreText, (10+self.xPos,10+self.yPos))

    #hard drops the tetriminoe
    def hardDrop(self):
        if (not self.isPaused):
            while (self.moveFallingPiece(1,0)):
                pass
            self.placeFallingPiece()
            self.removeFullRows()
            self.newFallingPiece()

##############################################
# Queue/Hold Functions
##############################################

    #makes the queue
    def makeQueue(self):
        for i in range(5):
            self.queue.append(random.choice(['iPiece','jPiece','lPiece','oPiece',
                                             'sPiece','zPiece','tPiece']))
    
    #Draws the queue
    def drawQueue(self, screen):
        pygame.draw.rect(screen, (19,2,28),(290+self.xPos,135+self.yPos,100,250))
        pygame.draw.rect(screen, (57,66,133),(285+self.xPos,130+self.yPos,100,250))
        pygame.draw.rect(screen, (19,2,28),(295+self.xPos,170+self.yPos,80,200))
        #draws each of the five pieces in the queue
        for i in range(5):
            piece = self.queue[i]
            xIndex = 310
            yIndex = 175 + i*40
            self.drawComponents(screen, xIndex, yIndex, self.tetrisPieces[piece][0],
                           self.tetrisPieces[piece][1])
        queueText = self.font.render("Next", 1, (146,148,150))
        screen.blit(queueText, (310+self.xPos,140+self.yPos))
        
    #Draws the hold
    def drawHold(self, screen):
        pygame.draw.rect(screen, (19,2,28),(15+self.xPos,135+self.yPos,80,110))
        pygame.draw.rect(screen, (57,66,133),(10+self.xPos,130+self.yPos,80,110))
        pygame.draw.rect(screen, (19,2,28),(20+self.xPos,170+self.yPos,60,60))
        holdText = self.font.render("Hold", 1, (146,148,150))
        screen.blit(holdText, (25+self.xPos,145+self.yPos))
        #draws the piece in the hold queue
        if (self.holdPiece != None):
            color = self.tetrisPieces[self.holdPiece][0]
            shape = self.tetrisPieces[self.holdPiece][1]
            (xIndex, yIndex) = (30,195)
            self.drawComponents(screen, xIndex, yIndex, color, shape)

    #spawns the held piece after the player holds
    def newHeldPiece(self, currentPiece):
        self.fallingPiece = self.tetrisPieces[currentPiece][1]
        self.fallingPieceColor = self.tetrisPieces[currentPiece][0]
        #identifies the number of rows and cols that the piece has
        self.fallingPieceRows = len(self.fallingPiece)
        self.fallingPieceCols = len(self.fallingPiece[0])
        #identifies which row and which column the top-left corner of the falling
        #piece is located in
        self.fallingPieceRow = 0
        self.fallingPieceCol = self.cols//2 - (self.fallingPieceCols//2)
        self.removeGhostPiece()
        self.placeGhostPiece()
            
    #draws the pieces that aren't on the board (i.e. hold and queue)
    def drawComponents(self, screen, xIndex, yIndex, color, shape):
        rows = len(shape)
        cols = len(shape[0])
        for row in range(rows):
            yPos = yIndex + row*(self.cellHeight-6)
            for col in range(cols):
                xPos = xIndex + col*(self.cellWidth-6)
                if (shape[row][col] == True):
                    m = 3
                    (color1, color2, color3) = color
                    darkColor1 = max(0, color1 - 50)
                    darkColor2 = max(0, color2 - 50)
                    darkColor3 = max(0, color3 - 50)
                    pygame.draw.rect(screen, (darkColor1,darkColor2,darkColor3), (xPos+self.xPos-2,yPos+self.yPos-2,self.cellWidth-7,self.cellWidth-7))
                    pygame.draw.rect(screen, color, (xPos+self.xPos,yPos+self.yPos,self.cellWidth-9,self.cellHeight-9))

####################################################
# Ghost Piece Functions
####################################################

    #places the ghost piece in the correct position
    def placeGhostPiece(self):
        self.ghostPiece = self.fallingPiece
        self.ghostPieceRow = self.fallingPieceRow
        self.ghostPieceRows = self.fallingPieceRows
        self.ghostPieceCol = self.fallingPieceCol
        self.ghostPieceCols = self.fallingPieceCols
        loop = True
        #pushes the piece as low as it can go while still being legal
        while (loop == True):
            self.ghostPieceRow += 1
            if (not self.isLegal(self.board,self.ghostPiece,self.ghostPieceRow,
                                self.ghostPieceCol,self.ghostPieceRows,self.ghostPieceCols)):
                self.ghostPieceRow -= 1
                loop = False
        #places the ghost tile in each of the specified positions
        for row in range(self.ghostPieceRows):
            placeGhostRow = row + self.ghostPieceRow
            for col in range(self.ghostPieceCols):
                placeGhostCol = col + self.ghostPieceCol
                if (self.ghostPiece[row][col] == True):
                    self.ghostBoard[placeGhostRow][placeGhostCol] = self.ghostColor

    #draws the ghost piece onto the screen
    def drawGhostPiece(self, screen):
        for row in range(self.ghostPieceRows):
            printRow = row + self.ghostPieceRow
            for col in range(self.ghostPieceCols):
                if (self.ghostPiece[row][col]):
                    printCol = col + self.ghostPieceCol
                    color = self.ghostColor
                    self.drawCell(screen, printRow, printCol, color)

    #removes the old ghost piece every time the ghost piece moves position
    def removeGhostPiece(self):
        ghostCount = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if (self.ghostBoard[row][col] == self.ghostColor):
                    ghostCount += 1
                    self.ghostBoard[row][col] = self.emptyColor
                if (ghostCount == 4): break
            if (ghostCount == 4): break

########################################################
# AI Functions
########################################################

    #gets the row of the highest block in each column
    def getColHeights(self):
        (rows, cols) = (self.rows, self.cols)
        for col in range(cols):
            for row in range(rows):
                #searches for the highest block in the column and adds it to the list
                if (self.simBoard[row][col] != (self.emptyColor or self.ghostColor)):
                    self.colHeights[col] = (rows - 1) - (row - 1)
                    break
                #if we are at the bottom row, add it to the list
                elif (row == rows - 1):
                    self.colHeights[col] = 0

    #counts the number of holes in the board (i.e. the number of empty squares underneath filled squares)
    #also counts the height of columns over the holes (number of filled squares over holes)
    def countHoles(self):
        self.holes = [0]*self.cols
        self.holeWeight = 10
        (rows, cols) = (self.rows, self.cols)
        for col in range(cols):
            #starts the counting of the column at the first filled square of the column
            startRow = rows - self.colHeights[col] 
            colHeight = rows - startRow
            for row in range(colHeight):
                #counts the tiles before we reach a hole and stores it. If no
                #hole is reached then we ignore the tiles.
                if (self.simBoard[startRow + row][col] == self.emptyColor):
                    self.holes[col] += 1
                    #the more holes there are, the more heavily holes are weighted
                    self.hasHole = True

    #counts the gap between each column and the neighboring columns. Gaps are bad when they are on both sides
    #(i.e. the gap is one tile wide) so we take the min of the gap on the left and the gap on the right
    def getGaps(self):
        (rows, cols) = (self.rows, self.cols)
        for col in range(cols):
            #if we are checking the first or last column, then we only need to compare to one other column
            if (col == 0):
                self.gaps[col] = self.colHeights[1] - self.colHeights[col]
            elif (col == 9):
                self.gaps[col] = self.colHeights[8] - self.colHeights[col]
            else:
                leftGap = self.colHeights[col-1] - self.colHeights[col]
                rightGap = self.colHeights[col+1] - self.colHeights[col]
                self.gaps[col] = min(leftGap, rightGap)
        for col in range(cols):
            if (self.gaps[col] < 0): self.gaps[col] = 0

    #returns a 3D list of the possible rotations of the given piece
    def possibleRotations(self, piece):
        if (piece == "iPiece"):
            return [[[True,True,True,True]],
                    [[True],[True],[True],[True]]]
        elif (piece == "jPiece"):
            return [[[True, False, False],[True, True, True]],
                    [[True, True],[True,False],[True,False]],
                    [[True, True, True],[False, False, True]],
                    [[False, True],[False, True], [True,True]]]
        elif (piece == "lPiece"):
            return [[[False,False,True],[True,True,True]],
                    [[True,False],[True,False],[True,True]],
                    [[True,True,True],[True,False,False]],
                    [[True,True],[False,True],[False,True]]]
        elif (piece == "oPiece"):
            return [[[True,True],[True,True]]]
        elif (piece == "sPiece"):
            return [[[False,True,True],[True,True,False]],
                    [[True,False],[True,True],[False,True]]]
        elif (piece == "zPiece"):
            return [[[True,True,False],[False,True,True]],
                    [[False,True],[True,True],[True,False]]]
        elif (piece == "tPiece"):
            return [[[False,True,False],[True,True,True]],
                    [[True,False],[True,True],[True,False]],
                    [[True,True,True],[False,True,False]],
                    [[False,True],[True,True],[False,True]]]

    #calculates the "score" of the board using the appropriate weights
    def calculateBoardScore(self):
        self.boardScore = 0
        for colHeight in self.colHeights:
            self.boardScore -= (colHeight ** self.colHeightWeight)
        for hole in self.holes:
            self.boardScore -= (hole * self.holeWeight)
        self.gapWeight = 5
        for gap in self.gaps:
            if (gap > 2):
                self.boardScore -= (self.gapWeight * gap)
        self.clearWeight = 10
        #clearing more lines at one time is better
        for clear in range(self.AIlinesCleared):
            self.boardScore += self.clearWeight
            self.clearWeight += 5
        return self.boardScore

    #iterates through all of the possible rotations and placements of the piece and 
    #the hold piece and finds the best possible move
    def findBestPlacement(self):
        self.oldBoard = self.board
        #only finds the new best move after the last move has been completed
        if (self.completedMove == True):
            self.completedMove = False
            highestScore = -9999
            #loops twice, once for the current piece and once for the hold
            #piece
            for i in range(2):
                if (i == 0): piece = self.currentPiece
                else:
                    if (self.heldPiece == False):
                        if (self.holdPiece != None): piece = self.holdPiece
                        else: piece = self.queue[0]
                    else: piece = self.currentPiece
                #has a chance of doing a random move (only tests to do a random move once per piece)
                doesWrongMove = random.uniform(0,1)
                if (i == 0) and (doesWrongMove >= self.AIDifficulty):
                    self.rotationNumber = random.randint(0,3)
                    self.bestPiece = self.currentPiece
                    pieceWidth = len(self.possibleRotations(self.bestPiece)[0][0])
                    self.bestCol = random.randint(0,(10-pieceWidth))
                    self.doAIMove()
                    return
                rotations = self.possibleRotations(piece)
                rotationNumber = -1
                #goes through all the possible rotations of the piece and finds the score
                for rotation in rotations:
                    rotationNumber += 1
                    pieceWidth = len(rotation[0])
                    #goes through all the possible cols the piece can be placed
                    for col in range(self.cols-(pieceWidth-1)):
                        self.simBoard = copy.deepcopy(self.oldBoard)
                        score = self.hardDropCandidate(rotation, col)
                        if (score > highestScore):
                            (self.rotationNumber, self.bestCol, self.bestPiece) = (rotationNumber, col, piece)
                            highestScore = score
        #after the ideal move has been calculated, perform the best move
        self.doAIMove()

    #places each candidate move and returns the board score of the move
    def hardDropCandidate(self, piece, colPos):
        (rowPos, rows, cols) = (0, len(piece), len(piece[0]))
        #if the move is not possible, return an extremely low score
        if (not self.isLegal(self.simBoard, piece, rowPos, colPos, rows, cols)): return -9999
        #because the isLegal is checked after incrementing row, will always go one over
        while (self.isLegal(self.simBoard, piece, rowPos, colPos, rows, cols)):
            rowPos += 1
        rowPos -= 1
        #places the piece
        for row in range(rows):
            rowCheck = row + rowPos
            for col in range(cols):
                colCheck = col + colPos
                if (piece[row][col]): self.simBoard[rowCheck][colCheck] = self.placementColor
        self.getColHeights()
        self.countHoles()
        self.getGaps()
        self.countFullRows()
        score = self.calculateBoardScore()
        return score

    #moves the pieces to the ideal position one rotation or one movement at a time and updates
    #the display so that the user can see what the AI is doing
    def doAIMove(self):
        (col, rotation, bestPiece) = (self.bestCol, self.rotationNumber, self.bestPiece)
        #if we can hold and the ideal move is to hold, then we hold
        if (bestPiece != self.currentPiece) and (self.doStep == True) and (self.heldPiece == False):
            self.doHold()
            pygame.display.flip()
            self.doStep = False
        #if the ideal move requires more rotations, continue rotating the piece until the 
        #desired rotation is achieved
        while (rotation > 0) and (self.doStep == True):
            self.rotationNumber -= 1
            if (self.rotateFallingPiece() == False): 
                self.isGameOver = True
                return None
            pygame.display.flip()
            self.doStep = False
        if (col == self.fallingPieceCol): pass
        #if the goal column is less than the falling piece's current column, move it to the left,
        #same for if the goal column is greater than the falling piece's current column
        elif (col < self.fallingPieceCol):
            while (col < self.fallingPieceCol) and (self.doStep == True): 
                if (self.moveFallingPiece(0,-1) == False):
                    self.isGameOver = True
                    return None
                pygame.display.flip()
                self.doStep = False
        elif (col > self.fallingPieceCol):
            while (col > self.fallingPieceCol) and (self.doStep == True):
                if (self.moveFallingPiece(0, 1) == False):
                    self.isGameOver = True
                    return None
                pygame.display.flip()
                self.doStep = False
        #if the piece is in the proper rotation and column, hard drop the piece in place
        if ((bestPiece == self.currentPiece) and (rotation == 0) and (col == self.fallingPieceCol)):
            self.completedMove = True
            self.hardDrop()

######################################
# Past Games
######################################

    #when the game ends, returns the relevant information describing the game
    def addToHistory(self):
        if (self.addedHistory == False):
            self.addedHistory = True
            if (self.runAI == True): gameType = "AI"
            else: gameType = "Manual"
            gameTime = self.stopwatchTime
            finalScore = self.score
            winLoss = None
            if (self.isGameWon == True):
                winLoss = "Win"
            elif (self.isGameOver == True):
                winLoss = "Loss"
            if (self.runAI == True):
                speedLevel = self.AISpeedInput
                intelligenceLevel = self.AIDifficultyInput
                return [gameType, gameTime, finalScore, speedLevel, intelligenceLevel,winLoss]
            return[gameType,gameTime,finalScore,winLoss]
     
#adds game history data to a text file
def recordHistory(recordedHistory, data1, data2=None):
    if (recordedHistory == False):
        fileHistory = open('scores.txt','a')
        if (data2 == None):
            data1 = "\n1 " + str(data1)
            fileHistory.write(data1)
        else:
            data1 = "\n2 " + str(data1)
            data2 = " " + str(data2)
            fileHistory.write(data1)
            fileHistory.write(data2)
        fileHistory.close()
        return True

#analyzes the history text file 
def analyzeHistory(data):
    fileHistory = open('scores.txt', 'r')
    #converts the text file data into a 3D list
    history = []
    for line in fileHistory:
        splitLine = line.split("[")
        eventHistory = []
        for element in splitLine:
            if (len(element) == 1): pass
            elif (element[-2] == "]"):
                element = element[:-2]
            elif (element[-1] == "]"):
                element = element[:-1]
            gameData = []
            splitElement = element.split(",")
            for dataPiece in splitElement:
                dataPiece = dataPiece.strip()
                gameData.append(dataPiece)
            eventHistory.append(gameData)
        history.append(eventHistory)
    #searches through the 3D list for the highest score manually
    for game in history:
        #if it's one player, check the line count
        if (game[0] == ['1']):
            #only keeps high score if it is a user playing
            if (game[1][0] == "'Manual'"):
                #print(game[1][2])
                score = int(game[1][2])
                #print(score)
                if (score > data.highscore):
                    data.highscore = score
                    data.bestGame = game
        #if it's two player, check line counts
        elif (game[0] == ['2']):
            #only keeps the high scores if it is a user playing. checks both players
            for i in range(1,3):
                if (game[i][0] == "'Manual'"):
                    score = int(game[i][2])
                    if (score > data.highscore):
                        data.highscore = score
                        data.bestGame = game

    #searches through the 3D list for the best win over an AI
    for game in history:
        if (game[0] == ['2']):
            if (game[1][0] == "'Manual'") and (game[2][0] == "'AI'"):
                if (game[1][3] == "'Win'"):
                    beatAITime = game[1][1]
                    beatAISpeed = int(game[2][3])
                    beatAIIntelligence = int(game[2][4])
                    compareStats(data,game,beatAITime,beatAISpeed,beatAIIntelligence)
            elif (game[1][0] == "'AI'") and (game[2][0] == "'Manual'"):
                if (game[2][3] == "'Win'"):
                    beatAITime = game[1][1]
                    beatAISpeed = int(game[1][3])
                    beatAIIntelligence = int(game[1][4])
                    compareStats(data,beatAITime,beatAISpeed,beatAIIntelligence)
    data.history = history
    fileHistory.close()

#compares if the given AI win is more difficult than another AI win
def compareStats(data, game,beatAITime, beatAISpeed, beatAIIntelligence):
    if (beatAISpeed*beatAIIntelligence > data.bestAISpeed*data.bestAIIntelligence):
        data.bestAIGame = game
        data.bestAITime = beatAITime
        data.bestAISpeed = beatAISpeed
        data.bestAIIntelligence = beatAIIntelligence
    elif (beatAISpeed*beatAIIntelligence == data.bestAISpeed*data.bestAIIntelligence):
        if (beatAITime < data.bestAITime):
            data.bestAIGame = game
            data.bestAITime = beatAITime
            data.bestAISpeed = beatAISpeed
            data.bestAIIntelligence = beatAIIntelligence

######################################
# Genetic Algorithm
######################################

#tests the genetic algorithm by performing the AI without pausing
class geneticAlgorithm(tetrisGame):

    #modifies the weights of the board calculation based on the inputs
    def __init__(self, holeWeight, colHeightWeight, gapWeight, clearWeight, lineCap, randomRow = 19):
        super().__init__()
        self.holeInput = holeWeight
        self.colHeightInput = colHeightWeight
        self.gapInput = gapWeight
        self.clearInput = clearWeight
        self.lineCap = lineCap
        self.randomRow = randomRow
        print(self.randomRow)

    #initializes the board
    def init(self):
        import random
        super().init()
        self.holeWeight = self.holeInput
        self.colHeightWeight = self.colHeightInput
        self.gapWeight = self.gapInput
        self.clearWeight = self.clearInput
        self.nonEmptyColor = (100,100,100)
        for i in range(20):
            row = random.randint(self.randomRow,19)
            col = random.randint(0,9)
            if (self.board[row][col] == self.emptyColor): 
                self.board[row][col] = self.nonEmptyColor
        self.doMove = 0

    #standard run function
    def run(self):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)        
        clock = pygame.time.Clock()
        self._keys = dict()
        self.init()
        
        runGame = True
        while runGame:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mousePressed(*(event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.mouseReleased(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons == (0, 0, 0)):
                    self.mouseMotion(*(event.pos))
                elif (event.type == pygame.MOUSEMOTION and
                      event.buttons[0] == 1):
                    self.mouseDrag(*(event.pos))
                elif event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    self.keyPressed(event.key, event.mod, screen)
                elif event.type == pygame.QUIT:
                    runGame = False
            screen.fill(self.bgColor)
            self.redrawAll(screen)
            pygame.display.flip()
            if (self.isGameOver == True): 
                return self.score
                runGame = False
            if (self.score > self.lineCap):
                return self.score
                runGame = False
        pygame.quit()


    def timerFired(self, dt):            
        #if the game is over or the game is paused, don't move any pieces
        if (not self.isGameOver and not self.isPaused and not self.isGameWon):
           self.findBestPlacement()

    #finds the best placement of the piece by searching through all the possible moves,
    #calculating the score of each move, and then performing the move. similar to the
    #other findBestPlacement function however does not have the randomly do bad moves feature
    def findBestPlacement(self):
        if (self.isGameOver == False):
            self.oldBoard = self.board
            (bestRotation, bestCol, bestPiece) = (None, None, self.currentPiece)
            highestScore = -9999
            #iterates twice, once for the current piece, once for the hold
            for i in range(2):
                if (i == 0): piece = self.currentPiece
                else:
                    if (self.heldPiece == False):
                        if (self.holdPiece != None): piece = self.holdPiece
                        else: piece = self.queue[0]
                    else: piece = self.currentPiece
                rotations = self.possibleRotations(piece)
                rotationNumber = -1
                #goes through the possible rotations of the piece
                for rotation in rotations:
                    rotationNumber += 1
                    pieceWidth = len(rotation[0])
                    #goes through the columns the piece can be placed
                    for col in range(self.cols-(pieceWidth-1)):
                        self.simBoard = copy.deepcopy(self.oldBoard)
                        score = self.hardDropCandidate(rotation, col)
                        if (score > highestScore):
                            (self.rotationNumber, self.bestCol, self.bestPiece) = (rotationNumber, col, piece)
                            highestScore = score
            self.doAIMove()
        else:
            return None
    
    #similar to the doAIMove of the tetrisGame object, however, does the entire move at once instead of
    #splitting into separate steps
    def doAIMove(self):
        (col, bestPiece) = (self.bestCol, self.bestPiece)
        #holds the piece if necessary
        if (bestPiece != self.currentPiece) and (self.heldPiece == False):
            self.doHold()
        #rotates the piece as many times as possible
        while (self.rotationNumber > 0):
            self.rotationNumber -= 1
            if (self.rotateFallingPiece() == False):
                self.isGameOver = True
                return None
        #moves the piece left/right
        if (col == self.fallingPieceCol): pass
        elif (col < self.fallingPieceCol):
            while (col < self.fallingPieceCol):
                if (self.moveFallingPiece(0,-1) == False):
                    self.isGameOver = True
                    return None
        elif (col > self.fallingPieceCol):
            while (col > self.fallingPieceCol):
                if (self.moveFallingPiece(0,1) == False):
                    self.isGameOver = True
                    return None
        #if the piece is in the best possible position, hard drop it
        if (bestPiece != self.currentPiece) and (self.heldPiece == True):
            self.hardDrop()
            self.heldPiece = False
        if (bestPiece == self.currentPiece) and (self.rotationNumber == 0) and (col == self.fallingPieceCol):
            self.hardDrop()
            self.heldPiece = False

#########################################
# Main()
#########################################

def run(width = 800, height = 600, fps = 60, title = "Tetris"):
    class Struct(object): pass
    data = Struct()
    screen = pygame.display.set_mode((width,height))
    pygame.display.set_caption(title)        
    clock = pygame.time.Clock()
    init(data)
    backgroundColor = (255,255,255)
    runGame = True
    while (runGame == True):
        time = clock.tick(fps)
        timerFired(time, data)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mousePressed(data, *(event.pos))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouseReleased(data, *(event.pos))
            elif (event.type == pygame.MOUSEMOTION and
                  event.buttons == (0, 0, 0)):
                mouseMotion(data, *(event.pos))
            elif (event.type == pygame.MOUSEMOTION and
                  event.buttons[0] == 1):
                mouseDrag(data, *(event.pos))
            elif event.type == pygame.KEYDOWN:
                keyPressed(event.key, event.mod, screen, data)
            elif event.type == pygame.QUIT:
                runGame = False
        screen.fill(backgroundColor)
        redrawAll(screen, data)            
        pygame.display.flip()
    pygame.quit()

###########################################
# Mode Dispatcher
###########################################

def init(data):
    pygame.init()
    data.page = "HomePage"
    data.game0 = None
    data.game1 = None
    data.godGame = None
    data.turquoise = (44,177,222)
    data.darkTurquoise = (17, 73, 92)
    data.gray = (38,40,42)
    data.lastPage = "HomePage"
    data.visitedGame = False
    data.choseGameMode = "Solo"
    data.puzzleBoard = False
    data.playerOne = "Manual"
    data.playerTwo = "Manual"
    data.oneAIIntelligence = 5
    data.oneAISpeed = 1
    data.twoAIIntelligence = 5
    data.twoAISpeed = 1
    data.sendGame0 = None
    data.sendGame1 = None
    data.gameOver0 = None
    data.gameOver1 = None
    data.font = pygame.font.SysFont("gillsansultra", 20)
    data.font0 = pygame.font.SysFont("gillsansultra", 40)
    data.font1 = pygame.font.SysFont("gillsansultra", 14)
    data.font2 = pygame.font.SysFont("gillsansultra", 12)
    data.font3 = pygame.font.SysFont("gillsansultra", 30)
    data.recordedHistory = False
    data.highscore = 0
    data.history = []
    data.bestGame = []
    data.bestAIGame = []
    data.bestAISpeed = 0
    data.bestAIIntelligence = 0
    data.bestAITime = ""
    data.newHighscore = False
    data.newHighscoreCounter = 0

def timerFired(time, data):
    if (data.page == "GamePage"): gamePageTimerFired(time, data)
    elif (data.page == "GodPage"): godPageTimerFired(time,data)

def mousePressed(data, x, y):
    if (data.page == "HomePage"): homePageMousePressed(data, x, y)
    elif (data.page == "HelpPage"): helpPageMousePressed(data, x, y)
    elif (data.page == "SelectionPage"): selectionPageMousePressed(data, x, y)
    elif (data.page == "GamePage"): gamePageMousePressed(data, x, y)
    elif (data.page == "GodPage"): godPageMousePressed(data, x, y)
    elif (data.page == "highscorePage"): highscorePageMousePressed(data,x,y)
    
def mouseReleased(data, x, y):
    if (data.page == "SelectionPage"): selectionPageMouseReleased(data, x, y)
    
def mouseMotion(data, x, y):
    if (data.page == "HomePage"): homePageMouseMotion(data, x, y)
    elif (data.page == "HelpPage"): helpPageMouseMotion(data, x, y)
    elif (data.page == "SelectionPage"): selectionPageMouseMotion(data, x, y)

def mouseDrag(data, x, y):
    if (data.page == "SelectionPage"): selectionPageMouseDrag(data, x, y)
    
#Responds based on keys pressed
def keyPressed(keyCode, modifier, screen, data):
    if (data.page == "HomePage"): homePageKeyPressed(keyCode, modifier, screen, data)
    elif (data.page == "HelpPage"): helpPageKeyPressed(keyCode, modifier, screen, data)
    elif (data.page == "SelectionPage"): selectionPageKeyPressed(keyCode, modifier, screen, data)
    elif (data.page == "GamePage"): gamePageKeyPressed(keyCode, modifier, screen, data)
    elif (data.page == "GodPage"): godPageKeyPressed(keyCode, modifier, screen, data)
    elif (data.page == "highscorePage"): highscorePageKeyPressed(keyCode, modifier, screen,data)

def redrawAll(screen, data):
    if (data.page == "HomePage"): homePageRedrawAll(screen, data)
    elif (data.page == "HelpPage"): helpPageRedrawAll(screen, data)
    elif (data.page == "SelectionPage"): selectionPageRedrawAll(screen, data)
    elif (data.page == "GamePage"): gamePageRedrawAll(screen, data)
    elif (data.page == "GodPage"): godPageRedrawAll(screen, data)
    elif (data.page == "highscorePage"): highscorePageRedrawAll(screen, data)
    newHighScoreRedrawAll(screen,data)


##########################################
# Universally Used Functions
##########################################

#draws the tetris header
def header(screen):
    #image from official tetris website @http://tetris.com/about-tetris/
    tetrisImage = pygame.image.load('images/Tetris_Web_Border.jpg').convert_alpha()
    screen.blit(tetrisImage, (0,0))

#draws the help and home button
def helpHomeButton(screen):
    #help image from @http://www.freeiconspng.com/free-images/help-desk-icon-13739
    helpImage = pygame.image.load('images/helpButton.jpg').convert_alpha()
    screen.blit(helpImage, (740,570))
    #home image from @http://www.freeiconspng.com/free-images/address-icon-1741
    homeImage = pygame.image.load('images/homeButton.jpg').convert_alpha()
    screen.blit(homeImage, (770,570))

#draws a dark turquoise button with a shadow
def darkButton(data,screen, xPos, yPos):
    pygame.draw.rect(screen, (0,0,0), (xPos+5,yPos+5,200,40))
    pygame.draw.rect(screen, data.darkTurquoise, (xPos,yPos,200,40))

def newHighScoreRedrawAll(screen,data):
    if (data.newHighscore == True):
        data.newHighscoreCounter += 1
        pygame.draw.rect(screen, (0,0,0), (205,205,400,200))
        pygame.draw.rect(screen, data.darkTurquoise, (200,200,400,200))
        highscoreText = data.font0.render("New Highscore!", 1, (255,255,255))
        screen.blit(highscoreText, (210,280))
        if (data.newHighscoreCounter >= 100):
            data.newHighscoreCounter = 0
            data.newHighscore = False

##########################################
# Home Page
##########################################

def homePageMousePressed(data, x, y):
    # print ("highscore", data.highscore)
    # print("history",data.history)
    # print("best score game", data.bestGame)
    # print("best AI defeat", data.bestAIGame)
    # print("best AI speed", data.bestAISpeed)
    # print("best AI intel", data.bestAIIntelligence)
    # print("best AI defeat Time", data.bestAITime)
    data.lastPage = "HomePage"
    if (x >= 300) and (x <= 500) and (y >= 250) and (y <= 290):
        data.page = "SelectionPage"
    elif (data.visitedGame == True) and (x >= 300) and (x <= 500) and (y >= 300) and (y <= 340):
        data.page = "GamePage"
    elif (x >= 300) and (x <= 500) and (y >= 350) and (y <= 390):
        data.page = "HelpPage"
    elif (x >= 300) and (x <= 500) and (y >= 400) and (y <= 440):
        data.page = "highscorePage"
    elif (x >= 290) and (x <= 510) and (y >= 500) and (y <= 540):
        data.godGame = tetrisGame(True,200,0,10.99,5)
        data.godGame.init()
        data.page = "GodPage"

def homePageMouseMotion(data, x, y):
    pass

def homePageKeyPressed(keyCode, modifier, screen, data):
    data.lastPage = "HomePage"
    #'h' for help, 'n' for selection page (new game), 'c' for continue game
    if (keyCode == 104): data.page = "HelpPage"
    elif (keyCode == 110): data.page = "SelectionPage"
    elif (keyCode == 99) and (data.visitedGame == True): data.page = "GamePage"

def homePageRedrawAll(screen, data):
    analyzeHistory(data)
    header(screen)
    #draws the gradient background
    for i in range(90):
        pygame.draw.rect(screen, (30,188-(2*i),255-(2*i)), (0,92+(6*i),800,6))
    #New Play Button
    darkButton(data,screen,300,250)
    playText = data.font.render("Play New Game", 1, (146,148,150))
    screen.blit(playText, (305, 255))
    #Continue Play Button
    darkButton(data,screen,300,300)
    continueText = data.font.render("Continue Game", 1, (146,148,150))
    screen.blit(continueText, (305, 305))
    #Help Button
    darkButton(data,screen,300,350)
    helpText = data.font.render("Help", 1, (146,148,150))
    screen.blit(helpText, (375, 355))
    #Highscore Button
    darkButton(data,screen,300,400)
    highscoreText = data.font.render("HighScores", 1, (146,148,150))
    screen.blit(highscoreText, (335, 405))
    #God AI Button
    pygame.draw.rect(screen, (0,0,0), (295,505,220,40))
    pygame.draw.rect(screen, data.darkTurquoise, (290,500,220,40))
    godText = data.font.render("Spectate God AI", 1, (146,148,150))
    screen.blit(godText, (300, 505))

############################################
# Help Page
############################################
from textwrap import fill
import string

def helpPageMousePressed(data, x, y):
    if (x >= 300) and (x <= 500) and (y >= 530) and (y <= 570):
        data.page = data.lastPage
    elif (x >= 740) and (x <= 770) and (y >= 570) and (y <= 600):
        data.page = "HelpPage"
    elif (x >= 770) and (x <= 800) and (y >= 570) and (y <= 600):
        data.page = "HomePage"

def helpPageKeyPressed(keyCode, modifier, screen, data):
    #'q' for quit to home page, 'b' for back
    if (keyCode == 113): data.page = "HomePage"
    elif (keyCode == 98): data.page = data.lastPage

def helpPageMouseMotion(data, x, y):
    pass

def helpPageRedrawAll(screen, data):
    header(screen)
    #draws the gradient background
    for i in range(90):
        pygame.draw.rect(screen, (30,188-(2*i),255-(2*i)), (0,92+(6*i),800,6))
    #draws the Help header
    helpText = data.font0.render("Help", 1, (146,148,150))
    darkHelpText = data.font0.render("Help", 1, (0,0,0))
    screen.blit(darkHelpText, (351, 100))
    screen.blit(helpText, (350, 100))
    #displays "What is Tetris?" Paragraph
    whatParagraph(data,screen)
    #displays "How to Play?" Paragraph
    howParagraph(data,screen)
    #displays controls section
    controlsText = data.font.render("Controls", 1, (146,148,150))
    darkControlsText = data.font.render("Controls", 1, (0,0,0))
    screen.blit(darkControlsText, (101,350))
    screen.blit(controlsText, (100,350))
    #displayers One Player Controls
    onePlayerControls(data,screen)
    #displays Two Player Controls
    twoPlayerControls(data,screen)
    #return button
    pygame.draw.rect(screen, data.darkTurquoise, (300,530,200,40))
    returnText = data.font.render("Return", 1, (146,148,150))
    screen.blit(returnText, (355, 535))
    helpHomeButton(screen)

#displays the What is Tetris Paragraph
def whatParagraph(data,screen):
    whatTetrisText = data.font.render("What is Tetris?", 1, (146,148,150))
    darkWhatTetrisText = data.font.render("What is Tetris?", 1, (0,0,0))
    screen.blit(darkWhatTetrisText, (101, 140))
    screen.blit(whatTetrisText, (100, 140))
    whatParagraph = "Tetris is one of the oldest and most recognizable arcade games ever made. Despite being over thirty years old, the game is still enjoyed by many who enjoy intellectual sport. Whether pursuing a record or simple mental stimulation, Tetris offers a fun experience for all!"
    splitWhat = (fill(whatParagraph,70).splitlines())
    i = 0
    for line in splitWhat:
        lineText = data.font1.render(line, 1, (198,200,202))
        darkLineText = data.font1.render(line, 1, (0,0,0))
        screen.blit(darkLineText, (121, 170+(20*i)))
        screen.blit(lineText, (120, 170+(20*i)))
        i += 1

#displays the How to Play paragraph
def howParagraph(data,screen):
    playText = data.font.render("How to Play?", 1, (146,148,150))
    darkPlayText = data.font.render("How to Play?", 1, (0,0,0))
    screen.blit(darkPlayText, (101, 250))
    screen.blit(playText, (100, 250))
    howParagraph = "The goal of Tetris is to clear as many rows as possible as quickly as possible. A row is cleared when an entire row is filled with Tetris blocks. Tetris is played using the keyboard. "
    splitHow = (fill(howParagraph,70).splitlines())
    i = 0
    for line in splitHow:
        lineText = data.font1.render(line, 1, (198,200,202))
        darkLineText = data.font1.render(line, 1, (0,0,0))
        screen.blit(darkLineText, (121, 280+(20*i)))
        screen.blit(lineText, (120, 280+(20*i)))
        i += 1

#displays the one player controls
def onePlayerControls(data,screen):
    onePlayerText = data.font.render("One Player", 1, (146,148,150))
    darkOnePlayerText = data.font.render("One Player", 1, (0,0,0))
    screen.blit(darkOnePlayerText, (121,380))
    screen.blit(onePlayerText, (120,380))
    oneControls = """UP - rotate piece
                    LEFT - move left
                    RIGHT - move right
                    DOWN - move down
                    SPACE - hard drop 
                    SHIFT - hold
                  """
    splitOneControls = oneControls.splitlines()
    i = 0
    for line in splitOneControls:
        line = line.strip()
        lineText = data.font1.render(line, 1, (198,200,202))
        darkLineText = data.font1.render(line, 1, (0,0,0))
        screen.blit(darkLineText, (111, 410+(20*i)))
        screen.blit(lineText, (110, 410+(20*i)))
        i += 1

#displays the two player controls
def twoPlayerControls(data,screen):
    twoPlayerText = data.font.render("Two Player", 1, (146,148,150))
    darkTwoPlayerText = data.font.render("Two Player", 1, (0,0,0))
    screen.blit(darkTwoPlayerText, (471,380))
    screen.blit(twoPlayerText, (470,380))
    #displays Player One controls
    playerOneControls(data,screen)
    #displays Player Two Controls
    playerTwoControls(data,screen)

#displays the player one controls
def playerOneControls(data,screen):
    playerOneText = data.font1.render("Player One", 1, (146,148,150))
    darkPlayerOneText = data.font1.render("Player One", 1, (0,0,0))
    screen.blit(darkPlayerOneText, (401,410))
    screen.blit(playerOneText, (400,410))    
    playerOneControls = """W - rotate piece
                A - move left
                D - move right
                S - move down
                Z - hard drop 
                SHIFT - hold
              """
    splitPlayerOneControls = playerOneControls.splitlines()
    i = 0
    for line in splitPlayerOneControls:
        line = line.strip()
        lineText = data.font2.render(line, 1, (198,200,202))
        darkLineText = data.font2.render(line, 1, (0,0,0))
        screen.blit(darkLineText, (381, 430+(15*i)))
        screen.blit(lineText, (380, 430+(15*i)))
        i += 1

#displays the player two controls:
def playerTwoControls(data,screen):
    playerTwoText = data.font1.render("Player Two", 1, (146,148,150))
    darkPlayerTwoText = data.font1.render("Player Two", 1, (0,0,0))
    screen.blit(darkPlayerTwoText, (601,410))
    screen.blit(playerTwoText, (600,410))
    playerTwoControls = """UP - rotate piece
            LEFT - move left
            RIGHT - move right
            DOWN - move down
            SPACE - hard drop 
            SHIFT - hold
          """
    splitPlayerTwoControls = playerTwoControls.splitlines()
    i = 0
    for line in splitPlayerTwoControls:
        line = line.strip()
        lineText = data.font2.render(line, 1, (198,200,202))
        darkLineText = data.font2.render(line, 1, (0,0,0))
        screen.blit(darkLineText, (601, 430+(15*i)))
        screen.blit(lineText, (600, 430+(15*i)))
        i += 1

#############################################
# Selection Page
#############################################

def selectionPageMousePressed(data, x, y):
    data.lastPage = "SelectionPage"
    if (x >= 400) and (x <= 490) and (y >= 195) and (y <= 235):
        data.choseGameMode = "Solo"
    elif (x >= 500) and (x <= 590) and (y >= 195) and (y <= 235):
        data.choseGameMode = "VS"
    elif (x >= 300) and (x <= 440) and (y >= 295) and (y <= 335):
        data.playerOne = "Manual"
    elif (x >= 450) and (x <= 540) and (y >= 295) and (y <= 335):
        data.playerOne = "AI"
    elif (x >= 300) and (x <= 390) and (y >= 245) and (y <= 285):
        data.puzzleBoard = True
    elif (x >= 400) and (x <= 490) and (y >= 245) and (y <= 285):
        data.puzzleBoard = False
    elif (x >= 740) and (x <= 770) and (y >= 570) and (y <= 600):
        data.page = "HelpPage"
    elif (x >= 770) and (x <= 800) and (y >= 570) and (y <= 600):
        data.page = "HomePage"
    #modifies the AI bars
    if (data.playerOne == "AI"):
        if (x >= 300) and (x <= 400) and (y >= 350) and (y <= 370):
            data.oneAIIntelligence = min(((x - 300)//20) + 1,5)
        elif (x >= 530) and (x <= 730) and (y >= 350) and (y <= 370):
            data.oneAISpeed = min(((x - 530)//20) + 1,10)
    if (data.choseGameMode == "VS"):
        if (x >= 300) and (x <= 440) and (y >= 395) and (y <= 435):
            data.playerTwo = "Manual"
        elif (x >= 450) and (x <= 540) and (y >= 395) and (y <= 435):
            data.playerTwo = "AI"
        #modifies the AI bars
        elif (data.playerTwo == "AI"):
            if (x >= 300) and (x <= 400) and (y >= 450) and (y <= 470):
                data.twoAIIntelligence = min(((x - 300)//20) + 1,5)
            elif (x >= 530) and (x <= 730) and (y >= 450) and (y <= 470):
                data.twoAISpeed = min(((x - 530)//20) + 1,10)
    if (x >= 300) and (x <= 500) and (y >= 500) and (y <= 540):
        startGame(data)

#creates the necessary tetris game objects and initializes them. 
#If it cannot start a game, returns False
def startGame(data):
    if (data.choseGameMode != None) and (data.playerOne != None):
        if (data.choseGameMode == "VS") and (data.playerTwo == None): return False
        if (data.choseGameMode == "Solo"): 
            data.game1 = None
            if (data.playerOne == "Manual"): 
                data.game0 = tetrisGame(False, 200, 0, puzzleBoard=data.puzzleBoard)
                data.game0.init()
            elif (data.playerOne == "AI"):
                data.game0 = tetrisGame(True, 200, 0, data.oneAISpeed, data.oneAIIntelligence,data.puzzleBoard)
                data.game0.init()
        elif (data.choseGameMode == "VS"):
            #if there are two manual players, need to change the keys used
            if (data.playerOne == "Manual") and (data.playerTwo == "Manual"):
                data.game0 = tetrisGame(False,0,0, puzzleBoard=data.puzzleBoard,doubleManual=1)
                data.game0.init()
                data.game1 = tetrisGame(False,400,0, puzzleBoard=data.puzzleBoard,doubleManual=2)
                data.game1.init()
            else:    
                if (data.playerOne == "Manual"):
                    data.game0 = tetrisGame(False,0,0, puzzleBoard=data.puzzleBoard)
                    data.game0.init()
                elif (data.playerOne == "AI"):
                    data.game0 = tetrisGame(True,0,0,data.oneAISpeed,data.oneAIIntelligence,data.puzzleBoard)
                    data.game0.init()
                if (data.playerTwo == "Manual"):
                    data.game1 = tetrisGame(False,400,0, puzzleBoard=data.puzzleBoard)
                    data.game1.init()
                elif (data.playerTwo == "AI"):
                    data.game1 = tetrisGame(True,400,0,data.twoAISpeed,data.twoAIIntelligence,data.puzzleBoard)
                    data.game1.init()
        data.recordedHistory = False
        data.page = "GamePage"
    else: return False

def selectionPageMouseReleased(data, x, y):
    pass

def selectionPageMouseDrag(data, x, y):
    pass

def selectionPageMouseMotion(data, x, y):
    pass

def selectionPageKeyPressed(keyCode, modifier, screen, data):
    #'h' for help, 'q' for quit to home page, 'ENTER' to start game
    if (keyCode == 104): data.page = "HelpPage"
    elif (keyCode == 113): data.page = "HomePage"
    #loads the game if you press enter and the game has the necessary info to start
    elif (keyCode == 13) and (startGame(data) != False): data.page = "GamePage"

def selectionPageRedrawAll(screen, data):
    header(screen)
    #draws the gradient background
    for i in range(90):
        pygame.draw.rect(screen, (30,188-(2*i),255-(2*i)), (0,92+(6*i),800,6))
    #draws the header
    startText = data.font.render("Start a New Game:", 1, (146,148,150))
    darkStartText = data.font.render("Start a New Game:", 1, (0,0,0))
    screen.blit(darkStartText, (291,100))
    screen.blit(startText, (290, 100))
    #Choose a game mode text
    gameModeText = data.font.render("Choose a game mode:", 1, (146,148,150))
    darkGameModeText = data.font.render("Choose a game mode:", 1, (0,0,0))
    screen.blit(darkGameModeText, (101,200))
    screen.blit(gameModeText, (100, 200))
    #AI Selection Text
    intelligenceText = data.font.render("Intelligence", 1, (146,148,150))
    darkIntelligenceText = data.font.render("Intelligence", 1, (0,0,0))
    speedText = data.font.render("Speed", 1, (146,148,150))
    darkSpeedText = data.font.render("Speed", 1, (0,0,0))
    #game mode buttons
    gameModeButtons(data,screen)
    #board selection buttons
    boardSelectionButtons(data,screen)
    #player 1 buttons
    playerOneButtons(data,screen)
    #Player One AI intelligence/speed selection
    playerOneAISelect(data,screen)
    #player 2 buttons
    if (data.choseGameMode == "VS"):
        playerTwoButtons(data,screen)
    #Start button
    pygame.draw.rect(screen, data.darkTurquoise, (300,500,200,40))
    returnText = data.font.render("Start Game", 1, (146,148,150))
    screen.blit(returnText, (325, 505))
    helpHomeButton(screen)

#draws the game mode buttons
def gameModeButtons(data,screen):
    if (data.choseGameMode == "Solo"):
        pygame.draw.rect(screen, data.darkTurquoise, (400,195,90,40))
    else:
        pygame.draw.rect(screen, data.turquoise, (400,195,90,40), 2)
    onePlayerText = data.font.render("Solo", 1, (146,148,150))
    screen.blit(onePlayerText, (420, 200))
    if (data.choseGameMode == "VS"):
        pygame.draw.rect(screen, data.darkTurquoise, (500,195,90,40))
    else:
        pygame.draw.rect(screen, data.turquoise, (500,195,90,40), 2)
    twoPlayerText = data.font.render("Vs.", 1, (146,148,150))
    screen.blit(twoPlayerText, (530, 200))

#draws the board selection buttons
def boardSelectionButtons(data,screen):
    puzzleBoardText = data.font.render("Puzzle Board:", 1, (146,148,150))
    darkPuzzleBoardText = data.font.render("Puzzle Board:", 1, (0,0,0))
    screen.blit(darkPuzzleBoardText, (101,250))
    screen.blit(puzzleBoardText, (100,250))
    if (data.puzzleBoard == True):
        pygame.draw.rect(screen, data.darkTurquoise, (300,245,90,40))
    else:
        pygame.draw.rect(screen, data.turquoise, (300,245,90,40), 2)
    yesText = data.font.render("Yes", 1, (146,148,150))
    screen.blit(yesText, (320, 250))
    if (data.puzzleBoard == False):
        pygame.draw.rect(screen, data.darkTurquoise, (400,245,90,40))
    else:
        pygame.draw.rect(screen, data.turquoise, (400,245,90,40), 2)
    noText = data.font.render("No", 1, (146,148,150))
    screen.blit(noText, (420,250))

#draws the player one buttons
def playerOneButtons(data,screen):
    darkPlayerOneText = data.font.render("Player One:", 1, (0,0,0))
    playerOneText = data.font.render("Player One:", 1, (146,148,150))
    screen.blit(darkPlayerOneText, (101, 300))
    screen.blit(playerOneText, (100, 300))
    if (data.playerOne == "Manual"):
        pygame.draw.rect(screen, data.darkTurquoise, (300,295,140,40))
    else:
        pygame.draw.rect(screen, data.turquoise, (300,295,140,40), 2)
    manualText = data.font.render("Manual", 1, (146,148,150))
    screen.blit(manualText, (323, 300))
    if (data.playerOne == "AI"):
        pygame.draw.rect(screen, data.darkTurquoise, (450,295,90,40))
    else:
        pygame.draw.rect(screen, data.turquoise, (450,295,90,40), 2)
    AIText = data.font.render("AI", 1, (146,148,150))
    screen.blit(AIText, (478, 300))

#draws the AI selection bars
def playerOneAISelect(data,screen):
    if (data.playerOne == "AI"):
        for xPos in range(300,400,20):
            pygame.draw.rect(screen, data.turquoise, (xPos,350,20,20), 2)
        for filled in range(data.oneAIIntelligence):
            pygame.draw.rect(screen, data.darkTurquoise, (300+(20*filled),350,20,20))
        intelligenceText = data.font.render("Intelligence", 1, (146,148,150))
        darkIntelligenceText = data.font.render("Intelligence", 1, (0,0,0))
        screen.blit(darkIntelligenceText, (141, 350))
        screen.blit(intelligenceText, (140, 350))
        for xPos in range(530,730,20):
            pygame.draw.rect(screen, data.turquoise, (xPos,350,20,20), 2)
        for filled in range(data.oneAISpeed):
            pygame.draw.rect(screen, data.darkTurquoise, (530+(20*filled),350,20,20))
        speedText = data.font.render("Speed", 1, (146,148,150))
        darkSpeedText = data.font.render("Speed", 1, (0,0,0))
        screen.blit(darkSpeedText, (441, 350))
        screen.blit(speedText, (440, 350))

#draws the player Two buttons
def playerTwoButtons(data,screen):
    playerTwoText = data.font.render("Player Two:", 1, (146,148,150))
    darkPlayerTwoText = data.font.render("Player Two:", 1, (0,0,0))
    screen.blit(darkPlayerTwoText, (101, 400))
    screen.blit(playerTwoText, (100, 400))
    if (data.playerTwo == "Manual"):
        pygame.draw.rect(screen, data.darkTurquoise, (300,395,140,40))
    else:
        pygame.draw.rect(screen, data.turquoise, (300,395,140,40), 2)
    manualText = data.font.render("Manual", 1, (146,148,150))
    screen.blit(manualText, (323, 400))
    if (data.playerTwo == "AI"):
        pygame.draw.rect(screen, data.darkTurquoise, (450,395,90,40))
    else:
        pygame.draw.rect(screen, data.turquoise, (450,395,90,40), 2)
    AIText = data.font.render("AI", 1, (146,148,150))
    screen.blit(AIText, (478, 400))
    #Player Two AI intelligence/speed selection
    if (data.playerTwo == "AI"):
        playerTwoAISelect(data,screen)

#player two AI select
def playerTwoAISelect(data,screen):
    for xPos in range(300,400,20):
        pygame.draw.rect(screen, data.turquoise, (xPos,450,20,20), 2)
    for filled in range(data.twoAIIntelligence):
        pygame.draw.rect(screen, data.darkTurquoise, (300+(20*filled),450,20,20))
    intelligenceText = data.font.render("Intelligence", 1, (146,148,150))
    darkIntelligenceText = data.font.render("Intelligence", 1, (0,0,0))
    screen.blit(darkIntelligenceText, (141, 450))
    screen.blit(intelligenceText, (140, 450))
    for xPos in range(530,730,20):
        pygame.draw.rect(screen, data.turquoise, (xPos,450,20,20), 2)
    for filled in range(data.twoAISpeed):
        pygame.draw.rect(screen, data.darkTurquoise, (530+(20*filled),450,20,20))
    speedText = data.font.render("Speed", 1, (146,148,150))
    darkSpeedText = data.font.render("Speed", 1, (0,0,0))
    screen.blit(darkSpeedText, (441, 450))
    screen.blit(speedText, (440, 450))

##############################################
# Game Page
##############################################

def gamePageTimerFired(time, data):
    data.game0.timerFired(time)
    #if the game mode is Vs. send lines between games
    if (data.game1 != None): 
        data.game1.timerFired(time)
        #takes how many lines have been cleared by the opposing player
        data.sendGame0 = data.game1.sendGarbage()
        data.sendGame1 = data.game0.sendGarbage()
        #updates how many lines have been cleared
        data.game0.removeFullRows()
        data.game1.removeFullRows()
        #if lines were cleared, send the lines to the appropriate player
        if (data.sendGame0 > 0):
            data.game0.addGarbage(data.sendGame0)
            data.sendGame0 = 0
        if (data.sendGame1 > 0):
            data.game1.addGarbage(data.sendGame1)
            data.sendGame1 = 0
        #if one of the players lost, then display appropriate win/lose screens
        data.gameOver0 = data.game0.gameLost()
        data.gameOver1 = data.game1.gameLost()
        if (data.gameOver0 == True):
            data.game1.gameWon()
            history1 = data.game0.addToHistory()
            history2 = data.game1.addToHistory()
            if (history1 != None):
                if (history1[0] == "Manual") and (history1[2] >= data.highscore): data.newHighscore = True
            if (history2 != None):
                if (history2[0] == "Manual") and (history2[2] >= data.highscore): data.newHighscore = True
            data.recordedHistory = recordHistory(data.recordedHistory, history1, history2)
        if (data.gameOver1 == True):
            data.game0.gameWon()
            history1 = data.game0.addToHistory()
            history2 = data.game1.addToHistory()
            if (history1 != None):
                if (history1[0] == "Manual") and (history1[2] >= data.highscore): data.newHighscore = True
            if (history2 != None):
                if (history2[0] == "Manual") and (history2[2] >= data.highscore): data.newHighscore = True
            data.recordedHistory = recordHistory(data.recordedHistory, history1, history2)
    else:
        if (data.game0.gameLost() == True):
            history = data.game0.addToHistory()
            if (history != None):
                if (history[0] == "Manual") and (history[2] >= data.highscore): data.newHighscore = True
            data.recordedHistory = recordHistory(data.recordedHistory, history)


def gamePageMousePressed(data, x, y):
    data.lastPage = "GamePage"
    data.visitedGame = True
    if (x >= 740) and (x <= 770) and (y >= 570) and (y <= 600):
        data.page = "HelpPage"
    elif (x >= 770) and (x <= 800) and (y >= 570) and (y <= 600):
        data.page = "HomePage"

def gamePageKeyPressed(keyCode, modifier, screen, data):
    data.visitedGame = True
    data.lastPage = "GamePage"
    #'h' for help, 'q' for quit
    if (keyCode == 104): data.page = "HelpPage"
    elif (keyCode == 113): data.page = "HomePage"
    data.game0.keyPressed(keyCode, modifier, screen)
    if (data.game1 != None):
        data.game1.keyPressed(keyCode, modifier, screen)

def gamePageRedrawAll(screen, data):
    #draws gradient
    for i in range(90):
        pygame.draw.rect(screen, (30,188-(2*i),255-(2*i)), (0,(7*i),800,7))
    #draws the game screens
    data.game0.redrawAll(screen)
    if (data.game1 != None) and (data.choseGameMode == "VS"):
        data.game1.redrawAll(screen)
    helpHomeButton(screen)


############################
# God Page
############################

def godPageTimerFired(time, data):
    data.godGame.timerFired(time)

def godPageMousePressed(data, x, y):
    data.lastPage = "GodPage"
    if (x >= 740) and (x <= 770) and (y >= 570) and (y <= 600):
        data.page = "HelpPage"
    elif (x >= 770) and (x <= 800) and (y >= 570) and (y <= 600):
        data.page = "HomePage"

def godPageKeyPressed(keyCode, modifier, screen, data):
    data.lastPage = "GodPage"
    #'h' for help, 'q' for quit
    if (keyCode == 104): data.page = "HelpPage"
    elif (keyCode == 113): data.page = "HomePage"

def godPageRedrawAll(screen, data):
    #draws the gradient
    for i in range(90):
        pygame.draw.rect(screen, (30,188-(2*i),255-(2*i)), (0,(7*i),800,7))
    #draws the game
    data.godGame.redrawAll(screen)
    helpHomeButton(screen)

###############################
# Highscores/history page
###############################

def highscorePageMousePressed(data, x, y):
    data.lastPage = "highscorePage"
    if (x >= 740) and (x <= 770) and (y >= 570) and (y <= 600):
        data.page = "HelpPage"
    elif (x >= 770) and (x <= 800) and (y >= 570) and (y <= 600):
        data.page = "HomePage"

def highscorePageKeyPressed(keyCode, modifier, screen, data):
    data.lastPage = "GodPage"
    #'h' for help, 'q' for quit
    if (keyCode == 104): data.page = "HelpPage"
    elif (keyCode == 113): data.page = "HomePage"

def highscorePageRedrawAll(screen,data):
    #draws the gradient
    for i in range(90):
        pygame.draw.rect(screen, (30,188-(2*i),255-(2*i)), (0,(7*i),800,7))
    header(screen)
    highscoreText = data.font.render("Highscore: " + str(data.highscore), 1, (146,148,150))
    darkHighscoreText = data.font.render("Highscore: " + str(data.highscore), 1, (0,0,0))
    screen.blit(darkHighscoreText, (281, 150))
    screen.blit(highscoreText, (280, 150))
    bestAIText = data.font.render("Best AI Defeated:", 1, (146,148,150))
    darkBestAIText = data.font.render("Best AI Defeated: ", 1, (0,0,0))
    screen.blit(darkBestAIText, (141, 250))
    screen.blit(bestAIText, (140, 250))
    bestIntelligenceText = data.font1.render("Intelligence: " + str(data.bestAIIntelligence), 1, (146,148,150))
    darkBestIntelligenceText = data.font1.render("Intelligence: " + str(data.bestAIIntelligence), 1, (0,0,0))
    screen.blit(darkBestIntelligenceText, (241, 280))
    screen.blit(bestIntelligenceText, (240, 280))
    bestSpeedText = data.font1.render("Speed: " + str(data.bestAISpeed), 1, (146,148,150))
    darkBestSpeedText = data.font1.render("Speed: " + str(data.bestAISpeed), 1, (0,0,0))
    screen.blit(darkBestSpeedText, (241, 300))
    screen.blit(bestSpeedText, (240, 300))
    bestTimeText = data.font1.render("Time Taken: " + str(data.bestAITime), 1, (146,148,150))
    darkBestTimeText = data.font1.render("Time Taken: " + str(data.bestAITime), 1, (0,0,0))
    screen.blit(darkBestTimeText, (241, 320))
    screen.blit(bestTimeText, (240, 320))
    helpHomeButton(screen)
    
def main():
    run()


    ########################################
    # genetic algorithm data collection
    #######################################

    #testAIs(5, 5, 2.5, 2.5, 5, 1000)
    #testAIs(4, 6.320137824311881, 2.4387815064452654, 3.6389088406045977, 4.544367801566513, 1000)
    #testAIs(2, 6.130166771222496, 2.0654103293995507, 3.59707624497361, 4.672541911687853, 2000)
    #testAIs(1, 5.991736855642347, 2.003127291362843, 3.378532554163095, 4.6412455071804315, 4000)
    #testAIs(0.5, 5.901419259597659, 1.98171354255989, 3.4414534763120814, 4.635329773443859, 8000)

    #these iterations test using the random board feature, where the board is filled with random
    #tiles at the start instead of being empty

    #testAIs(0.25, 5.899202540171207, 1.9682746621983596, 3.408388891059141, 4.615364672019854, 100, 9)
    #testAIs(0.125, 5.933157019361572, 1.9333422585880735, 3.4047164812712967, 4.630153044753769, 100, 8)
    #testAIs(0.0625, 5.937421495482078, 1.9231952984247034, 3.3927635617811003, 4.634046272707411, 100, 7)
    #testAIs(0, 5.9288669341469555, 1.9162926946223073, 3.3878742140370637, 4.641363224169059, 100, 11)

#tests the AI using a genetic algorithm, starts with random weights to calculate
#the board score and returns the final score achieved by the AI given the weights.
#If the score is less than the linecap, then the weights did not survive to the
#line cap, so we ignore them. Note that the score caps at 1000 (otherwise some 
#would probably run forever) so the weights that don't make it to 1000 are removed
#from the "gene pool".
def testAIs(rangeVal, startHole, startColHeight, startGap, startClear, lineCap, randomRow = 19):
    import random
    scoresList = []
    badWeights = []
    for i in range(200):
        #picks random weights for the relevant variables
        holeWeight = random.uniform(startHole-rangeVal, startHole+rangeVal)
        minColHeight = max(startColHeight-rangeVal,0)
        colHeightWeight = random.uniform(minColHeight, startColHeight+rangeVal)
        gapWeight = random.uniform(startGap-rangeVal,startGap+rangeVal)
        clearWeight = random.uniform(startClear-rangeVal,startClear+rangeVal)
        #runs the AI using the given weights and returns the final score acheived
        aiTest = geneticAlgorithm(holeWeight,colHeightWeight,gapWeight,clearWeight, lineCap, randomRow)
        score = aiTest.run()
        #if the AI gets to the lineCap, then it is an acceptable list of weights for
        #the AI calculations, otherwise, they are bad
        if (score == None): break
        elif (score >= lineCap):
            scoresList.append([holeWeight,colHeightWeight,gapWeight,clearWeight])
        else:
            badWeights.append([holeWeight,colHeightWeight,gapWeight,clearWeight])
        print(scoresList)
        print(i)
    #neatly prints the output of the necessary data
    print("bad", badWeights)
    print("good\n", len(scoresList), "\n", scoresList)

if __name__ == '__main__':
    main()

        