import pygame
from pygame.locals import *
from snake import *

def snakeSpeed(length):
    """
    Retourne une valeur représentant la vitesse du snake.
    Cette valeur doit idéalement être entière, positive et inférieure à 5
    (c'est pour votre bien ;-) )
    La vitesse du snake dépend de la longueur du serpent.
    """
    if length < 10:
        return 1
    elif length < 20:
        return 2
    elif length < 50:
        return 3
    elif length < 100:
        return 4
    else:
        return 5

def collides(x1, y1, x2, y2):
    """
    Retourne vrai si les positions (x1, y1) et (X2, y2) sont les mêmes.
    """
    return (x1 == x2 and y1 == y2)

def collidesWithWall(headX, headY, screenWidth, screenHeight):
    """
    Retourne vrai si la position (headX, headY) est en dehors de l'écran.
    L'écran va de 0 à screenWidth-1 compris pour la coordonnée x,
    et de 0 à screenHeight-1 compris pour la coordonnée y.
    """
    return (headX < 0 or headX >= screenWidth or headY < 0 or headY >= screenHeight)

def pointInCorner(x, y, screenWidth, screenHeight):
    """
    Retourne vrai si la position (x, y) se situe dans un coin d'écran.
    Les coins de l'écran sont (0, 0), (0, screenHeight-1),
    (screenWidth-1, 0), (screenWidth-1, screenHeight-1)
    """
    return (x==0 or x==screenWidth-1) and (y==0 or y==screenHeight-1)

def collidesWithSelf(player):
    """
    Retourne vrai si le joueur se marche sur lui-même.
    Le serpent se marche sur lui-même si sa tête est
    sur l'un des autres morceaux de son corps.
    Les positions de chacun de ses morceaux sont accessibles
    dans player.x et player.y (ce sont des listes).
    La longueur du serpent est dans player.length,
    mais vous pouvez l'obtenir d'une autre manière (laquelle ?).
    """
    for i in range(1, player.length):
        if player.x[i] == player.x[0] and player.y[i] == player.y[0]:
            return True
    return False

def emptyPosition(app, x, y):
    """
    Retourne vrai si la position (x, y) est vide.
    Une position peut être occupée par le joueur
    app.player ou par le joueur app.otherPlayer,
    ou par une pomme (app.apple).
    Les positions (x et y) des différents morceaux
    du snake sont dans deux listes,
    app.player.x et app.player.y pour le premier,
    app.otherPlayer.x et app.otherPlayer.y pour le second.
    La position de la pomme est dans app.apple.x et app.apple.y
    """
    for player in app.players:
        for i in range(0, player.length):
            if player.x[i] == x and player.y[i] == y:
                return False
    for apple in app.apples:
        if apple.x == x and apple.y == y:
            return False
    return True

#def validPosition(app, x, y):
#    return emptyPosition and not collidesWithWall(x, y, app.width, app.height)

def setLevel(app, level):
    app.level = level

if __name__ == "__main__":
    app = App(keys="WASD")
    setLevel(app, 1)
    app.start()

