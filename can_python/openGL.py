import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

AccelRefPos = (500, 600)
BatteryRefPos = (650, 750)

def drawAccelPercentage(percentage):
    glColor3f(0.3, 0.7, 0.9)  # 사각형 색상 설정 (파란색)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(AccelRefPos[0], 100)    # 왼쪽 아래 꼭지점
    glVertex2f(AccelRefPos[0], 380)     # 왼쪽 위 꼭지점
    glVertex2f(AccelRefPos[1], 380)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(AccelRefPos[1], 100) 
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(AccelRefPos[0], 100)    # 왼쪽 아래 꼭지점
    glVertex2f(AccelRefPos[0], 100 + 280 * percentage / 100)     # 왼쪽 위 꼭지점
    glVertex2f(AccelRefPos[1], 100 + 280 * percentage / 100)  # 오른쪽 위 꼭지점 (특정 백분율만큼)
    glVertex2f(AccelRefPos[1], 100)  # 오른쪽 아래 꼭지점 (특정 백분율만큼)
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


def draw_text(text):
    font = pygame.font.Font(None, 120)  # 폰트 설정과 크기 지정
    text_surface = font.render(text, True, (255, 255, 255))  # 텍스트 렌더링
    text_data = pygame.image.tostring(text_surface, "RGBA", True)  # 렌더링한 텍스트 데이터 가져오기

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glRasterPos2f(200, 240)  # 텍스트 위치 설정
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glDisable(GL_BLEND)


def main():

    pygame.init()
    display = (800, 480)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL) #  | FULLSCREEN

    gluOrtho2D(0, 800, 0, 480)  # 2D 뷰포트 설정

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                

                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT)

        # 왼쪽에 텍스트 표시
        draw_text(f"hihihih")  # 여기에 원하는 값을 입력해주세요.

        # 오른쪽에 사각형 표시 (백분율: 50%)
        percentage = 1  # 여기에 원하는 백분율 값을 입력해주세요. (0 ~ 1 사이 값)
        drawAccelPercentage(10)
        drawBatteryPercentage(30)

        pygame.display.flip()

        import time
        test = time.time()
        
        pygame.time.wait(20)
        print(test)

if __name__ == "__main__":
    main()
