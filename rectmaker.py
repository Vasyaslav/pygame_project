import pygame
import os
import sys
from PIL import Image, ImageSequence

pygame.init()
size = 1600, 900
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def frames_from_gif(frames):
    res = []
    for frame in frames:
        image = frame.copy()
        image = image.crop((0, 0, image.width, image.height - 15))
        res.append(image)
    return res


class Beautiful_rect():
    """Класс для создания прямоугольников с текстом которые можно выделить"""

    def __init__(self, x, y, w, h, color, text):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.color = color
        font = pygame.font.Font(os.path.join('data', '1_Minecraft-Regular.otf'), 50)
        self.text = font.render(text, True, (254, 254, 34))
        self.text_x = x + (w - self.text.get_width()) // 2
        self.text_y = y + (h - self.text.get_height()) // 2

    def draw(self, scr):
        scr.blit(self.text, (self.text_x, self.text_y))
        pygame.draw.rect(scr, self.color, ((self.x, self.y), (self.width, self.height)), 5)
        pygame.draw.rect(scr, (0, 0, 0), ((self.x - 5, self.y - 5), (self.width + 10, self.height + 10)), 5)

    def checked_draw(self, scr):
        pygame.draw.rect(scr, (210, 210, 210), ((self.x - 5, self.y - 5), (self.width + 10, self.height + 10)), 5)


def pause(scr):
    """Функция для создания экрана паузы"""
    # Таймер для паузы, все элементы будут отрисовываться с таким таймером
    MYEVENTTYPE = pygame.USEREVENT + 1
    pygame.time.set_timer(MYEVENTTYPE, 60)
    pause_screen = scr
    pause_rects = [
        Beautiful_rect(550, 120, 500, 100, (220, 56, 130), 'CONTINUE'),
        Beautiful_rect(550, 370, 500, 100, (120, 156, 130), 'SETTINGS'),
        Beautiful_rect(550, 620, 500, 100, (220, 56, 30), 'EXIT THE MAIN MENU')
    ]
    # Разбитие гифки дождя на фреймы
    rain_frames = frames_from_gif(ImageSequence.Iterator(Image.open(os.path.join('data', 'rain.gif'))))
    cur_frame = 0
    pos_y = 0
    pause_running = True
    while pause_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            # Реакция на нажатие определённых клавиш на клавиатуре, не реагируют на действия мыши
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    pos_y -= 1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    pos_y += 1
                elif event.key == pygame.K_ESCAPE:
                    # return 'main_game' #
                    return 'quit'
                elif event.key == pygame.K_SPACE:
                    if pos_y % 3 == 0:
                        # return 'main_game' #
                        return 'quit'
                    elif pos_y % 3 == 1:
                        # return 'settings' #
                        return 'quit'
                    elif pos_y % 3 == 2:
                        # return 'main_menu' #
                        return 'quit'
            elif event.type == MYEVENTTYPE:
                scr.fill((0, 0, 0))
                # Достаётся текущий кадр из списка кадров гифки дождя
                cur_frame = cur_frame % len(rain_frames)
                cur_rain_image = rain_frames[cur_frame]
                # Преобразования для создания адекватной поверхности с изображением дождя для отрисовки на экране паузы
                image_mode = cur_rain_image.mode
                image_size = cur_rain_image.size
                image_data = cur_rain_image.tobytes()
                py_image = pygame.transform.scale(pygame.image.fromstring(image_data, image_size, image_mode),
                                                  (1600, 900))
                new_palette = []
                rgb_triplet = []
                # Из восьмибитной поверхности в поверхность rgb
                for rgb_value in cur_rain_image.getpalette():
                    rgb_triplet.append(rgb_value)
                    if len(rgb_triplet) == 3:
                        new_palette.append((rgb_triplet[0], rgb_triplet[1], rgb_triplet[2]))
                        rgb_triplet = []
                py_image.set_palette(new_palette)
                # Убрать белый фон дождя
                py_image.set_colorkey((255, 255, 255))
                scr.blit(py_image, (0, 0))
                cur_frame += 1
                # отрисовка кнопок
                for i in pause_rects:
                    i.draw(pause_screen)
                pause_rects[pos_y % 3].checked_draw(pause_screen)
        pygame.display.flip()


if __name__ == '__main__':
    running = True
    # Стартовое окно(обычно главное меню), пауза поставлена, т.к готова только она
    cur_screen = 'pause'
    # Основной цикл
    while running:
        if cur_screen == 'main_menu':
            # cur_screen = main_menu() #
            pass
        elif cur_screen == 'pause':
            cur_screen = pause(screen)
        elif cur_screen == 'main_game':
            # cur_screen = main_game() #
            pass
        elif cur_screen == 'settings':
            # cur_screen = settings() #
            pass
        elif cur_screen == 'quit':
            running = False
        pygame.display.flip()
    pygame.quit()
