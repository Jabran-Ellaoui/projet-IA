import random


def get_move(posX,posY):
    #haut
    i = random.randint(0,4)
    if (i ==0):
        return posX,posY+1
    #bas
    elif(i ==1):
        return posX,posY-1
    #gauche
    elif(i ==2):
        return posX-1,posY
    #droite
    elif(i ==3):
        return posX+1,posY