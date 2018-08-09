from random import randint
from collections import namedtuple
import pygame
from pygame.locals import *
import time
import sys
from mysnake import *

LEFT = 0
UP = 1
RIGHT = 2
DOWN = 3

# Coordinates increase in x as we go to the right, and increase in y as we go to the bottom
STEP = 40 # Pixels per square step
WIDTH = 800//STEP # Default width and height of the window
HEIGHT = 600//STEP
Point = namedtuple('Point', 'x y')
FRAME_SPEED = 10
POINTS_EARNED = 10 # Points gagnés à chaque pomme avalée

def inverse(direction):
    return (direction + 2) % 4

def make_pos(posX, posY, direction):
    if direction == LEFT:
        return (posX - 1, posY)
    elif direction == UP:
        return (posX, posY - 1)
    elif direction == RIGHT:
        return (posX + 1, posY)
    else:
        return (posX, posY + 1)

def getSpeed(speed):
    speeds = [1, 1.2, 1.5, 2, 3, 5]
    if speed >= len(speeds):
        return speeds[-1]
    elif speed < 0:
        return speeds[0]
    else:
        return speeds[speed]

class Apple(object):
    def __init__(self, app, x=0, y=0):
        self.app = app
        self.x = x
        self.y = y
        self.appleImage = app.appleImage

    def render(self, surface):
        surface.blit(self.appleImage, (STEP * self.x, STEP * self.y))
    def replace(self):
        print("In replace")
        x = randint(0, self.app.width - 1)
        y = randint(0, self.app.height - 1)
        while not emptyPosition(self.app, x, y) or pointInCorner(x, y, self.app.width, self.app.height):
            x = randint(0, self.app.width - 1)
            y = randint(0, self.app.height - 1)
        print("Final x and y: " + str(x) + " " + str(y))
        self.x = x
        self.y = y

    def update(self):
        pass

class Player(object):
    def __init__(self, app, keyhandler, name, x=0, y=0, direction=RIGHT, length=3):
        self.app = app                  # For list of players, apples, and dimensions of the screen
        self.name = name
        self.x = [x]                     # List of x positions
        self.y = [y]                     # List of y positions
        self.direction = direction      # Direction of the movement
        self.points = 0                 # Points earned by eating apples
        self.gameOver = False
        self.keyHandler = keyhandler
        self.speed = 1
        self.snakeBodyImage = app.snakeBodyImage
        for i in range(1, length):
            newpos = make_pos(self.x[-1], self.y[-1], inverse(direction))
            self.x.append(newpos[0])
            self.y.append(newpos[1])
        self.length = len(self.x)
        self.ok()

    def addScore(self, dscore):
        self.points += dscore

    def ok(self):
        assert self.length == len(self.x) and self.length == len(self.y)

    def collidesWithApple(self, apple):
        self.ok()
        for i in range(0, self.length):
            if collides(self.x[i], self.y[i], apple.x, apple.y):
                return True
        return False

    def collidesWithSelf(self):
        self.ok()
        collidesWithSelf(self)

    def collidesWithOtherPlayer(self, snake):
        self.ok()
        snake.ok()
        for i in range(0, snake.length):
            if collides(self.x[0], self.y[0], snake.x[i], snake.y[i]):
                return True
        return False

    def collidesWithWall(self):
        self.ok()
        for i in range(0, self.length):
            if collidesWithWall(self.x[i], self.y[i], self.app.width, self.app.height):
                return True
        return False

    def move(self, keys):
        direction = self.keyHandler.getDirection(keys)
        print(direction)
        if direction == LEFT:
            self.moveLeft()
        elif direction == UP:
            self.moveUp()
        elif direction == RIGHT:
            self.moveRight()
        elif direction == DOWN:
            self.moveDown()

    # Dans les 4 fonctions suivantes, on ignore l'effet d'un retournement
    def moveLeft(self):
        if self.direction != RIGHT:
            self.direction = LEFT

    def moveUp(self):
        if self.direction != DOWN:
            self.direction = UP

    def moveRight(self):
        if self.direction != LEFT:
            self.direction = RIGHT

    def moveDown(self):
        if self.direction != UP:
            self.direction = DOWN

    def render(self, surface):
        self.ok()
        for i in range(0, self.length):
            surface.blit(self.snakeBodyImage, (self.x[i] * STEP, self.y[i] * STEP))

    def grow(self):
        self.ok()
        self.x.append(0)
        self.y.append(0)
        self.length += 1
        self.ok()
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]
        newhead = make_pos(self.x[1], self.y[1], self.direction)
        self.x[0] = newhead[0]
        self.y[0] = newhead[1]
        self.ok()

    def shrink(self):
        self.ok()
        self.x.pop()
        self.y.pop()
        self.length -= 1
        self.ok()

    def update(self):
        """En l'absence de prises de pomme, c'est ce qu'il faut faire. Mais on ne le fera pas"""
        assert False
        self.grow()
        self.shrink()

class KeyHandler(object):
    def __init__(self, leftk, upk, rightk, downk):
        self.keys = {leftk: LEFT, upk: UP, rightk: RIGHT, downk: DOWN}

    def getDirection(self, keys):
        for k, d in self.keys.items():
            if keys[k]:
                return d

class App(object):
    pauseText = "Pause!\nAppuyez sur Espace pour reprendre"
    winnerText = "Le gagnant est {} ({} points)\nAppuyez sur espace pour continuer"

    def __init__(self, keys="WASD", width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.windowWidth = width * STEP
        self.windowHeight = height * STEP
        # Init pygame as we need it
        pygame.init()
        self._displaySurface = pygame.display.set_mode((int(self.windowWidth), int(self.windowHeight)), pygame.HWSURFACE)
        self.appleImage = pygame.image.load("apple.png").convert()
        self.snakeBodyImage = pygame.image.load("snakebody.png").convert()
        self._whiteBackground = Rect((self.windowWidth//6, self.windowHeight//6), ((4*self.windowWidth)//6, (4*self.windowHeight)//6))
        self._textFont = pygame.font.SysFont("monospace", 20, True)
        self._textSpacing = 30
        self._keys = keys
        self.init()
        print(str(K_UP) + " " + str(K_DOWN) + " " + str(K_LEFT) + " " + str(K_RIGHT))

    def allPlayersDead(self):
        return self.deadPlayers == len(self.players)

    def displayPause(self):
        self.displayWindow(self.pauseText)

    def displayWinner(self):
        self.displayWindow(self.winnerText.format(self.winner.name, self.winner.points))

    def displayWindow(self, multiText):
        pygame.draw.rect(self._displaySurface, pygame.Color('white'), self._whiteBackground)
        texts = multiText.split('\n')
        ntexts = len(texts)
        i = 0
        for text in texts:
            textSurface = self._textFont.render(text, 1, pygame.Color('red'))
            textRect = textSurface.get_rect()
            textRect.midtop = (self.windowWidth//2, self.windowHeight//2 + self._textSpacing * (i - ntexts))
            self._displaySurface.blit(textSurface, textRect)
            i += 1

    def init(self):
        self.gameOver = False
        self.paused = False
        self.speed = 1
        self.players = []
        self.winner = None # Currently, there is none
        self._wasdHandler = KeyHandler(K_a, K_w, K_d, K_s)
        self._zqsdHandler = KeyHandler(K_q, K_z, K_d, K_s)
        self.keyHandlers = [KeyHandler(K_LEFT, K_UP, K_RIGHT, K_DOWN)]
        if self._keys == "WASD":
            self.keyHandlers.append(self._wasdHandler)
        else:
            self.keyHandlers.append(self._zqsdHandler)
        self.players = [
                Player(self, self.keyHandlers[0], "Player 1", self.width//4, self.height//4, RIGHT),
                Player(self, self.keyHandlers[1], "Player 2", (3*self.width)//4, (3*self.height)//4, LEFT)
        ]
        self.player = self.players[0]
        self.otherPlayer = self.players[1]
        self.deadPlayers = 0 # Used to detect the end of game
        self.apples = [Apple(self, self.width//2, self.height//2)]
        self.apple = self.apples[0]

    def on_loop(self, pressedKeys):
        print("Coucou")
        newspeed = self.players[0].speed
        for player in self.players:
            if not player.gameOver:
                # Move and check for apples
                player.move(pressedKeys)
                player.grow()
                appleEaten = False
                for apple in self.apples:
                    if player.collidesWithApple(apple):
                        appleEaten = True
                        player.addScore(POINTS_EARNED)
                        apple.replace() # The apple will be at the correct place
                        break # We can't have another apple here
                if not appleEaten:
                    player.shrink()
                # Check collisions with itself and other snakes
                for otherplayer in self.players:
                    # Feature: dead snakes are still deadly!
                    if otherplayer is not player:
                        if player.collidesWithOtherPlayer(otherplayer):
                            print("Collision other")
                            player.gameOver = True
                            self.deadPlayers += 1
                            # Maybe add score for killing other snake ?
                            break
                    else:
                        if player.collidesWithSelf():
                            print("collision self")
                            player.gameOver = True
                            self.deadPlayers += 1
                            break
                if player.collidesWithWall():
                    print("collision wall")
                    player.gameOver = True
                    self.deadPlayers += 1
                if not player.gameOver:
                    player.speed = snakeSpeed(player.length)
                    if player.speed < newspeed:
                        newspeed = player.speed # take the minimum
        self.speed = newspeed
        if self.allPlayersDead():
            self.gameOver = True
            playerWinner = self.players[0]
            for player in self.players:
                if player.points > playerWinner.points:
                    playerWinner = player
            self.winner = playerWinner

    def quit(self):
        pygame.quit()
        exit()

    def render(self):
        print("goeiedag")
        self._displaySurface.fill((0, 0, 0))
        for player in self.players:
            player.render(self._displaySurface)
        for apple in self.apples:
            apple.render(self._displaySurface)
        if self.paused:
            self.displayPause()
        elif self.gameOver:
            self.displayWinner()

        pygame.display.flip()

    def restart(self):
        # Objectively, this is useless
        self.init()

    def start(self):
        """
        Actually, this is more a main-like function than a start-like function...
        """
        self._running = True
        while self._running:
            pygame.event.pump()
            pressedKeys = pygame.key.get_pressed()
            if pressedKeys[K_ESCAPE] or pygame.event.peek(QUIT):
                self._running = False
                break
            if pressedKeys[K_SPACE]:
                if self.paused:
                    self.paused = False
                else:
                    self.paused = True
                if self.gameOver:
                    self.restart() # Will enable back the things
            if not self.paused and not self.gameOver:
                self.on_loop(pressedKeys) # All the code for when the game is actually active
            self.render() # Don't forget to render here!
            time.sleep(1 / (10 * getSpeed(self.speed) * self.level))
        self.quit() # When we're done

    def update(self):
        for player in players:
            if not player.gameOver:
                player.update()

# End of file

