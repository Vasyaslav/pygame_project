import pygame
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
import os
import sys


# Функции, которые не задействованы в какой-то одной большой функции
def cacher(some_func):
    cache = {}

    def new(arg, key):
        if key in cache:
            return cache[key]
        else:
            cache[key] = some_func(arg, key)
            return cache[key]

    return new


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


@cacher
def normal_frames(some_frames, key):
    norm_frames = []
    n = 0
    for i in some_frames:
        cur_image = i
        image_mode = cur_image.mode
        image_size = cur_image.size
        image_data = cur_image.tobytes()
        norm_image = pygame.transform.scale(pygame.image.fromstring(image_data, image_size, image_mode),
                                            (1600, 900))
        new_palette = []
        rgb_triplet = []
        # Из восьмибитной поверхности в поверхность rgb
        for rgb_value in cur_image.getpalette():
            rgb_triplet.append(rgb_value)
            if len(rgb_triplet) == 3:
                new_palette.append((rgb_triplet[0], rgb_triplet[1], rgb_triplet[2]))
                rgb_triplet = []
        norm_image.set_palette(new_palette)
        norm_frames.append((norm_image, n))
        n += 1
    return norm_frames


class Beautiful_rect(pygame.sprite.Sprite):
    """Класс для создания прямоугольников с текстом которые можно выделить"""

    def __init__(self, x, y, w, h, color, color_2, text, group):
        super().__init__(group)
        self.image = pygame.Surface((w, h))
        font = pygame.font.Font(os.path.join('data', '1_Minecraft-Regular.otf'), 50)
        self.text = font.render(text, True, (254, 254, 34))
        self.text_x = x + (w - self.text.get_width()) // 2
        self.text_y = y + (h - self.text.get_height()) // 2
        self.image.blit(self.text, (self.text_x - x, self.text_y - y))
        pygame.draw.rect(self.image, color, (0, 0, w, h), 7)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.color_2 = color_2

    def checked_draw(self, scr):
        pygame.draw.rect(scr, self.color_2, ((self.rect.x - 5, self.rect.y - 5),
                                             (self.rect.width + 10, self.rect.height + 10)), 5)


class Particles(pygame.sprite.Sprite):
    drop = pygame.Surface((2, 8))
    pygame.draw.rect(drop, (255, 255, 0), (0, 0, 2, 8), 1)

    def __init__(self, pos, dx, dy, group):
        super().__init__(group)
        self.image = Particles.drop
        self.rect = self.image.get_rect()
        self.gravity = 0.5
        self.rect.x, self.rect.y = pos
        self.velocity = [dx, dy]

    def update(self, group=None):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect((0, 0, 1600, 900)):
            self.kill()


# Функции, задействованные в функции main_game
class tablet(pygame.sprite.Sprite):
    def __init__(self, pos, params, dp, group):
        super().__init__(group)
        self.image = pygame.surface.Surface(params)
        self.image.fill((0, 0, 0))
        pygame.draw.circle(self.image, (245, 160, 60), (params[0] / 2, params[1] / 2),
                           ((params[0] + params[1]) + (dp[0] + dp[1]) // 2) / 5)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] + dp[0]
        self.rect.y = pos[1] + dp[1]


class berry(pygame.sprite.Sprite):
    def __init__(self, pos, params, dp, group):
        """pos - x, y; params - w, h; dp - сдвиг, чтоб по центру было"""
        super().__init__(group)
        self.image = pygame.surface.Surface(params)
        self.image.fill((0, 0, 0))
        pygame.draw.circle(self.image, (245, 160, 60), (params[0] / 2, params[1] / 2),
                           (params[0] + params[1]) / 4)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] + dp[0]
        self.rect.y = pos[1] + dp[1]


class wall(pygame.sprite.Sprite):
    def __init__(self, pos, params, group):
        """pos - x, y; params - w, h;"""
        super().__init__(group)
        self.image = pygame.surface.Surface(params)
        pygame.draw.rect(self.image, (65, 105, 225), ((0, 0),
                                                      (params[0], params[1])))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class checker(pygame.sprite.Sprite):
    def __init__(self, pos, params, group):
        super().__init__(group)
        self.image = pygame.surface.Surface(params)
        pygame.draw.circle(self.image, (245, 160, 60), (params[0] / 2, params[1] / 2),
                           (params[0] + params[1]) / 4)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


def winning():
    class MyWidget(QMainWindow):
        def __init__(self):
            super().__init__()
            uic.loadUi('wins.ui', self)
            self.answer = self.saving.clicked.connect(self.run)

        def run(self):
            if self.name.text():
                return self.name.text()
            else:
                return 'Неизвестный'

    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    app.exec_()
    return ex.answer


def losing():
    class MyWidget(QMainWindow):
        def __init__(self):
            super().__init__()
            uic.loadUi('loses.ui', self)
            self.finish.clicked.connect(self.run)

        def run(self):
            self.close()

    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    app.exec_()
