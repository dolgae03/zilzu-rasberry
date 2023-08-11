import pygame
from pygame.locals import *

pygame.init()

# 화면 초기화
display = (800, 480)
screen = pygame.display.set_mode(display)
pygame.display.set_caption("Pygame Example")

# 이미지 로드
scale = 0.4
image = pygame.image.load('./map.png')
image = pygame.transform.scale(image, (int(1327 * scale), int(515 * scale)))  # 이미지 크기 조절

# 폰트 설정
font = pygame.font.Font(None, 150)

def draw_text_centered(text, center_x, center_y, size):
    font = pygame.font.Font(None, size)  # 지정한 크기의 폰트 생성
    text_surface = font.render(text, True, (255, 255, 255))
    text_width = text_surface.get_width()
    text_height = text_surface.get_height()

    # 텍스트 중심 좌표 계산
    text_x = center_x - text_width // 2
    text_y = center_y - text_height // 2

    screen.blit(text_surface, (text_x, text_y))

def draw_percentage_box(percentage, x, y, width, height):
    pygame.draw.rect(screen, (0, 0, 255), (x, y, width, height), 3)
    fill_height = height * percentage / 100
    pygame.draw.rect(screen, (0, 0, 255), (x, y + height - fill_height, width, fill_height))

def main():
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        screen.fill((0, 0, 0))  # 배경을 검은색으로 채우기

        rpm = 5555
        # 왼쪽에 텍스트 표시
        draw_text_centered(f"{rpm}",230, 480 - 340, 250)
        draw_text_centered(f"RPM",520, 480 - 315, 70)  # 여기에 원하는 값을 입력해주세요.

        # 오른쪽에 사각형 표시 (백분율: 50%)
        percentage = 50  # 여기에 원하는 백분율 값을 입력해주세요. (0 ~ 1 사이 값)
        #drawAccelPercentage(10)
        draw_text_centered(f"{percentage}%",685, 480 - 420, 100)
        #drawBatteryPercentage(30)

        draw_percentage_box(percentage, 620, 100, 130, 350)

        # 이미지 표시
        screen.blit(image, (50, 370 - 135))

        scale = 0.4
        #drawPicture(300, 135, 1327 * scale,515 * scale, textID)

        # 이미지 표시
        #screen.blit(image, (300, 135))

        pygame.display.flip()
        clock.tick(60)  # FPS 제한

if __name__ == "__main__":
    main()
