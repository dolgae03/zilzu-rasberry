import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from numpy import array

def loadTexture():
    textID = None

    with Image.open("map.png") as text:
        textData = array(list(text.getdata()))
        textID = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, textID)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text.size[0], text.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, textData)
    
    return textID

def drawQuad(centerX, centerY, textureID):
    verts = ((1, 1), (1,-1), (-1,-1), (-1,1))
    texts = ((1, 0), (1, 2), (0, 2), (0, 0))
    surf = (0, 1, 2, 3)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textureID)

    glBegin(GL_QUADS)
    for i in surf:
        glTexCoord2f(texts[i][0], texts[i][1])
        glVertex2f(centerX + verts[i][0], centerY + verts[i][1])
    glEnd()
    
    glDisable(GL_TEXTURE_2D)

def main():
    pygame.init()
    disp = (1600, 1600)
    pygame.display.set_mode(disp, DOUBLEBUF|OPENGL)
    textID = loadTexture()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        drawQuad(0, 0, textID)
        pygame.display.flip()
        pygame.time.wait(10)
        
main()