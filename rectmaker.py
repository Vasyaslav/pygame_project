import pygame
import os
import sys
from PIL import Image, ImageSequence


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
    pygame.draw.rect(drop, (135, 186, 220), (0, 0, 2, 8), 1)

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


def main_game(scr):
    global cur_lvl
    berries_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()

    class berry(pygame.sprite.Sprite):
        def __init__(self, pos, params, dp, group):
            """pos - x, y; params - w, h; dp - сдвиг, чтоб по центру было"""
            super().__init__(group)
            self.image = pygame.surface.Surface(params)
            self.image.fill((176, 224, 230))
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
            pygame.draw.rect(self.image, (160, 60, 245), ((params[0] / 100, params[1] / 100),
                                                          (params[0] - params[0] / 100, params[1] - params[1] / 100)))
            self.rect = self.image.get_rect()
            self.rect.x = pos[0]
            self.rect.y = pos[1]

    def load_lvl(lvl_file):
        with open(lvl_file, 'r') as lvl:
            lvl = lvl.read().split('\n')
            block_w = 1600 / len(sorted(lvl, key=lambda z: len(z))[0])
            block_h = 900 / len(lvl)
            ber_w = 280 / len(sorted(lvl, key=lambda z: len(z))[0])
            ber_h = 310 / len(lvl)
            for i in range(len(lvl)):
                for y in range(len(lvl[i])):
                    if y < 28:
                        if lvl[i][y] == '.':
                            wall((y * block_w, i * block_h), (block_w, block_h), walls_group)
                        elif lvl[i][y] == '+':
                            berry((y * block_w, i * block_h), (ber_w, ber_h),
                                  (block_w / 2 - ber_w / 2, ber_h), berries_group)

    load_lvl(os.path.join('data', cur_lvl))

    main_game_running = True
    while main_game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    return 'pause'
        scr.fill((176, 224, 230))
        berries_group.draw(scr)
        walls_group.draw(scr)
        pygame.display.flip()


def pause(scr):
    """Функция для создания экрана паузы"""
    rain_frames_group = pygame.sprite.Group()
    pause_buttons = pygame.sprite.Group()

    class raining(pygame.sprite.Sprite):
        def __init__(self, im, num):
            super().__init__(rain_frames_group)
            self.type = num
            self.image = im
            self.rect = self.image.get_rect()

        def draw(self):
            scr.blit(self.image, self.rect)

    # Таймер для паузы, все элементы будут отрисовываться с таким таймером
    rain_event_type = pygame.USEREVENT + 1
    pygame.time.set_timer(rain_event_type, 60)
    pause_rects = [
        Beautiful_rect(550, 120, 500, 100, (220, 56, 130), (210, 56, 210), 'CONTINUE', pause_buttons),
        Beautiful_rect(550, 370, 500, 100, (120, 156, 130), (210, 56, 210), 'SETTINGS', pause_buttons),
        Beautiful_rect(550, 620, 500, 100, (220, 56, 30), (210, 210, 210), 'EXIT THE MAIN MENU', pause_buttons)
    ]
    # Разбитие гифки дождя на фреймы
    rain_frames = frames_from_gif(ImageSequence.Iterator(Image.open(os.path.join('data', 'rain.gif'))))
    n = 0
    for i in rain_frames:
        cur_rain_image = i
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
        raining(py_image, n)
        n += 1
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
                    return 'main_game'
                elif event.key == pygame.K_SPACE:
                    if pos_y % 3 == 0:
                        return 'main_game'
                    elif pos_y % 3 == 1:
                        return 'settings'
                    elif pos_y % 3 == 2:
                        return 'main_menu'
            elif event.type == rain_event_type:
                cur_frame = cur_frame % len(rain_frames)
                for i in rain_frames_group:
                    if i.type == cur_frame:
                        i.draw()
                rain_frames_group.update()
                cur_frame += 1
                # отрисовка кнопок
                pause_rects[pos_y % 3].checked_draw(scr)
                pause_buttons.draw(scr)
                pygame.display.flip()


def main_menu(scr):
    main_menu_buttons = pygame.sprite.Group()
    main_menu_rects = [
        Beautiful_rect(550, 120, 500, 100, (23, 254, 25), (254, 140, 23), 'NEW GAME', main_menu_buttons),
        Beautiful_rect(550, 370, 500, 100, (23, 254, 25), (254, 140, 23), 'SETTINGS', main_menu_buttons),
        Beautiful_rect(550, 620, 500, 100, (23, 254, 25), (254, 140, 23), 'EXIT', main_menu_buttons)
    ]
    main_menu_image = load_image('main_menu.png')
    pygame.draw.rect(main_menu_image, (0, 0, 0), (94, 33, 148, 37))
    pygame.draw.line(main_menu_image, (0, 0, 190), (214, 33), (214, 69))
    pygame.draw.line(main_menu_image, (0, 0, 190), (219, 33), (219, 69))
    pygame.draw.line(main_menu_image, (0, 0, 71), (213, 33), (213, 69))
    pygame.draw.line(main_menu_image, (0, 0, 71), (218, 33), (218, 69))
    pygame.draw.line(main_menu_image, (0, 0, 118), (215, 33), (215, 69))
    pygame.draw.line(main_menu_image, (0, 0, 118), (220, 33), (220, 69))
    main_menu_image = pygame.transform.scale(main_menu_image, (1600, 900))
    pos_y = 0

    main_menu_running = True
    while main_menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    pos_y -= 1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    pos_y += 1
                elif event.key == pygame.K_ESCAPE:
                    return 'quit'
                elif event.key == pygame.K_SPACE:
                    if pos_y % 3 == 0:
                        return 'main_game'
                    elif pos_y % 3 == 1:
                        scr.fill((0, 0, 0))
                        return 'settings'
                    elif pos_y % 3 == 2:
                        return 'quit'
        scr.fill((0, 0, 0))
        scr.blit(main_menu_image, (0, 0))
        main_menu_rects[pos_y % 3].checked_draw(scr)
        main_menu_buttons.draw(scr)
        pygame.display.flip()


def settings(scr):
    global music_volume, sound_volume, cur_lvl
    settings_buttons = pygame.sprite.Group()
    # settings_image = pygame.transform.scale(load_image('settings.jpg', -1), (1600, 900))
    settings_rects = [
        [Beautiful_rect(500, 120, 200, 50, (72, 209, 204), (254, 140, 23), 'MUSIC', settings_buttons),
         Beautiful_rect(500, 320, 200, 50, (255, 105, 180), (254, 140, 23), 'SOUND', settings_buttons),
         Beautiful_rect(500, 490, 630, 80, (23, 254, 25), (254, 140, 23), 'CHOOSE LVL', settings_buttons)],
        [Beautiful_rect(750, 120, 60, 50, (72, 209, 204), (254, 140, 23), '+', settings_buttons),
         Beautiful_rect(750, 320, 60, 50, (255, 105, 180), (254, 140, 23), '+', settings_buttons)],
        [Beautiful_rect(900, 120, 60, 50, (72, 209, 204), (254, 140, 23), '-', settings_buttons),
         Beautiful_rect(900, 320, 60, 50, (255, 105, 180), (254, 140, 23), '-', settings_buttons)],
        [Beautiful_rect(1050, 120, 80, 50, (72, 209, 204), (254, 140, 23), f'{music_volume}', settings_buttons),
         Beautiful_rect(1050, 320, 80, 50, (255, 105, 180), (254, 140, 23), f'{sound_volume}', settings_buttons)]
    ]
    pos_y = 0
    pos_x = 0
    lvl = ''
    all_disable = False

    scr.fill((0, 0, 0))
    # scr.blit(settings_image, (0, 0))
    settings_buttons.draw(scr)
    if pos_y % 3 == 2 and len(settings_rects[0]) != 4:
        print(1)
        settings_rects[0][pos_y % 3].checked_draw(scr)
    elif len(settings_rects[0]) == 4 and pos_y % 4 == 3 or pos_y % 4 == 2:
        settings_rects[0][pos_y % 4].checked_draw(scr)
    elif len(settings_rects[0]) != 4:
        settings_rects[pos_x % 3][pos_y % 3].checked_draw(scr)
    else:
        settings_rects[pos_x % 3][pos_y % 4].checked_draw(scr)
    pygame.display.flip()

    settings_running = True
    while settings_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if all_disable:
                    if event.key == 13 or event.key == 1073741912:
                        all_disable = False
                        settings_rects[0][3].kill()
                        settings_rects[0][3] = (
                            Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23), cur_lvl,
                                           settings_buttons))
                        if len(lvl) > 4:
                            print(lvl[-4:] == '.txt', lvl in os.listdir(path="data"))
                            print(lvl, lvl[-4:], lvl[0])
                            if lvl[-4:] == '.txt' and lvl in os.listdir(path="data"):
                                print(1, lvl)
                                settings_rects[0][3].kill()
                                settings_rects[0][3] = Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23),
                                                                      lvl, settings_buttons)
                                cur_lvl = lvl
                        lvl = ''
                    elif event.key == pygame.K_ESCAPE:
                        all_disable = False
                        settings_rects[0][3].kill()
                        settings_rects[0][3] = (
                            Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23), cur_lvl,
                                           settings_buttons))
                        lvl = ''
                    elif event.key == pygame.K_BACKSPACE:
                        if len(lvl) > 0:
                            print(lvl)
                            x = lvl[:-1]
                            lvl = x
                            print(lvl)
                        settings_rects[0][3].kill()
                        settings_rects[0][3] = (
                            Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23), lvl,
                                           settings_buttons))
                    else:
                        lvl += event.unicode
                        settings_rects[0][3].kill()
                        settings_rects[0][3] = (
                            Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23), lvl,
                                           settings_buttons))
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        pos_y -= 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        pos_y += 1
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        pos_x -= 1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        pos_x += 1
                    elif event.key == pygame.K_ESCAPE:
                        if prev_screen == 'pause':
                            return 'pause'
                        else:
                            return 'main_menu'
                    elif event.key == pygame.K_SPACE:
                        if pos_y % len(settings_rects[0]) == 0:
                            if pos_x == 0:
                                pos_x += 1
                            elif pos_x == 1:
                                music_volume = (music_volume + 1) % 11
                                settings_rects[3][0].kill()
                                settings_rects[3][0] = Beautiful_rect(1050, 120, 80, 50, (72, 209, 204), (254, 140, 23),
                                                                      f'{music_volume}', settings_buttons)
                            elif pos_x == 2:
                                music_volume = (music_volume - 1) % 11
                                settings_rects[3][0].kill()
                                settings_rects[3][0] = Beautiful_rect(1050, 120, 80, 50, (72, 209, 204), (254, 140, 23),
                                                                      f'{music_volume}', settings_buttons)
                        elif pos_y % len(settings_rects[0]) == 1:
                            if pos_x == 0:
                                pos_x += 1
                            elif pos_x == 1:
                                sound_volume = (sound_volume + 1) % 11
                                settings_rects[3][1].kill()
                                settings_rects[3][1] = Beautiful_rect(1050, 320, 80, 50, (255, 105, 180),
                                                                      (254, 140, 23),
                                                                      f'{sound_volume}', settings_buttons)
                            elif pos_x == 2:
                                sound_volume = (sound_volume - 1) % 11
                                settings_rects[3][1].kill()
                                settings_rects[3][1] = Beautiful_rect(1050, 320, 80, 50, (255, 105, 180),
                                                                      (254, 140, 23),
                                                                      f'{sound_volume}', settings_buttons)
                        elif pos_y % len(settings_rects[0]) == 2:
                            settings_rects[0].append(
                                Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23), cur_lvl,
                                               settings_buttons))
                        elif pos_y % len(settings_rects[0]) == 3:
                            all_disable = True
                scr.fill((0, 0, 0))
                # scr.blit(settings_image, (0, 0))
                settings_buttons.draw(scr)
                if pos_y % 3 == 2 and len(settings_rects[0]) != 4:
                    settings_rects[0][pos_y % 3].checked_draw(scr)
                elif len(settings_rects[0]) == 4 and (pos_y % 4 == 3 or pos_y % 4 == 2):
                    settings_rects[0][pos_y % 4].checked_draw(scr)
                elif len(settings_rects[0]) != 4:
                    settings_rects[pos_x % 3][pos_y % 3].checked_draw(scr)
                else:
                    settings_rects[pos_x % 3][pos_y % 4].checked_draw(scr)
                pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    size = 1600, 900
    screen = pygame.display.set_mode(size)
    music_volume = 10
    sound_volume = 10
    cur_lvl = 'lvl.txt'

    running = True
    # Стартовое окно
    cur_screen = 'main_menu'
    # Предыдущее окно(нужно чтобы было понятно куда выходить из настроек
    prev_screen = ''
    # Основной цикл
    while running:
        if cur_screen == 'main_menu':
            prev_screen = cur_screen
            cur_screen = main_menu(screen)
        elif cur_screen == 'pause':
            prev_screen = cur_screen
            cur_screen = pause(screen)
        elif cur_screen == 'main_game':
            cur_screen = main_game(screen)
            pass
        elif cur_screen == 'settings':
            cur_screen = settings(screen)
            pass
        elif cur_screen == 'quit':
            running = False
        pygame.display.flip()
    pygame.quit()
