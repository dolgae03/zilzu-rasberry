import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from numpy import array

AccelRefPos = (620, 750)
BatteryRefPos = (650, 750)

def drawAccelPercentage(percentage):
      # 사각형 색상 설정 (파란색)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glColor3f(0.3, 0.7, 0.9)
    glVertex2f(AccelRefPos[0], 50)    # 왼쪽 아래 꼭지점
    glVertex2f(AccelRefPos[0], 350)     # 왼쪽 위 꼭지점
    glVertex2f(AccelRefPos[1], 350)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(AccelRefPos[1], 50) 
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(AccelRefPos[0], 50)    # 왼쪽 아래 꼭지점
    glVertex2f(AccelRefPos[0], 50 + 300 * percentage / 100)     # 왼쪽 위 꼭지점
    glVertex2f(AccelRefPos[1], 50 + 300 * percentage / 100)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(AccelRefPos[1], 50)  # 오른쪽 아래 꼭지점 (특정 백분율만큼)
    glEnd()

def drawBatteryPercentage(Columm_Consumption):
    Battery_Capacity = 240 * 3600

    percentage = (Battery_Capacity - Columm_Consumption) / Battery_Capacity

    glColor3f(0.3, 0.7, 0)  # 사각형 색상 설정 (파란색)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(BatteryRefPos[0], 100)    # 왼쪽 아래 꼭지점
    glVertex2f(BatteryRefPos[0], 250)     # 왼쪽 위 꼭지점
    glVertex2f(BatteryRefPos[1], 250)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(BatteryRefPos[1], 100) 
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(BatteryRefPos[0], 100)    # 왼쪽 아래 꼭지점
    glVertex2f(BatteryRefPos[0], 100 + 150 * percentage / 100)     # 왼쪽 위 꼭지점
    glVertex2f(BatteryRefPos[1], 100 + 150 * percentage / 100)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(BatteryRefPos[1], 100)  # 오른쪽 아래 꼭지점 (특정 백분율만큼)
    glEnd()


def draw_text_centered(text, center_x, center_y, size):
    font = pygame.font.Font(None, size)  # 폰트 설정과 크기 지정
    text_surface = font.render(text, True, (255, 255, 255))  # 텍스트 렌더링
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()

    text_data = pygame.image.tostring(text_surface, "RGBA", True)  # 렌더링한 텍스트 데이터 가져오기

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # 텍스트 중심 좌표 계산
    text_center_x = center_x - text_width / 2
    text_center_y = center_y - text_height / 2

    glRasterPos2f(text_center_x, text_center_y)  # 텍스트 중심 위치 설정
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glDisable(GL_BLEND)

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

def drawPicture(centerX, centerY, width, height, textureID):
    half_width = width / 2
    half_height = height / 2
    
    verts = ((half_width, half_height), (half_width, -half_height), (-half_width, -half_height), (-half_width, half_height))
    texts = ((1, 0), (1, 1), (0, 1), (0, 0))
    surf = (0, 1, 2, 3)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textureID)

    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)
    for i in surf:
        glTexCoord2f(texts[i][0], texts[i][1])
        glVertex2f(centerX + verts[i][0], centerY + verts[i][1])
    glEnd()

    glDisable(GL_TEXTURE_2D)

def main():
    pygame.init()
    image = pygame.image.load('./map.png')

    display = (800, 480)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL) #  | FULLSCREEN

    gluOrtho2D(0, 800, 0, 480)  # 2D 뷰포트 설정

    textID = loadTexture()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        rpm = 5555
        # 왼쪽에 텍스트 표시
        draw_text_centered(f"{rpm}",230, 340, 250)
        draw_text_centered(f"RPM",520, 315, 70)  # 여기에 원하는 값을 입력해주세요.

        # 오른쪽에 사각형 표시 (백분율: 50%)
        percentage = 100  # 여기에 원하는 백분율 값을 입력해주세요. (0 ~ 1 사이 값)
        drawAccelPercentage(10)
        draw_text_centered(f"{percentage}%",685, 420, 100)
        #drawBatteryPercentage(30)

        scale = 0.4
        drawPicture(300, 135, 1327 * scale,515 * scale, textID)

        pygame.display.flip()

        import time
        test = time.time()
        pygame.time.wait(20)

if __name__ == "__main__":
    main()
