import pygame
import os
import sys
from PIL import Image, ImageSequence


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
    global cur_lvl, lvl_params, save_lvl
    berries_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    main_hero = pygame.sprite.Group()
    main_game_event = pygame.USEREVENT + 4
    pygame.time.set_timer(main_game_event, 500)

    class pacman(pygame.sprite.Sprite):
        def __init__(self, pos):
            super().__init__(main_hero)
            pars = sorted(lvl_params[1:3])[0]
            self.image = pygame.transform.scale(pac_image, (int(pars), int(pars)))
            self.right_image = self.image
            self.left_image = pygame.transform.flip(self.image, True, False)
            self.up_image = pygame.transform.rotate(self.image, 90)
            self.down_image = pygame.transform.rotate(self.image, 270)
            self.true_im = 'r'
            self.rect = self.image.get_rect()
            self.dp = [pars, '']
            self.next = ''
            self.rect.x = pos[0]
            self.rect.y = pos[1]

        def update(self, ev):
            if event.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w or ev.key == pygame.K_UP:
                    self.image = self.up_image
                    self.dp[1] = 'w'
                elif ev.key == pygame.K_s or ev.key == pygame.K_DOWN:
                    self.image = self.down_image
                    self.dp[1] = 's'
                elif ev.key == pygame.K_d or ev.key == pygame.K_RIGHT:
                    self.image = self.right_image
                    self.dp[1] = 'd'
                elif ev.key == pygame.K_a or ev.key == pygame.K_LEFT:
                    self.image = self.left_image
                    self.dp[1] = 'a'
            elif event.type == main_game_event:
                if self.dp[1] == 'w':
                    self.rect.y -= self.dp[0]
                    if pygame.sprite.spritecollideany(self, walls_group):
                        self.rect.y += self.dp[0]
                elif self.dp[1] == 's':
                    self.rect.y += self.dp[0]
                    if pygame.sprite.spritecollideany(self, walls_group):
                        self.rect.y -= self.dp[0]
                elif self.dp[1] == 'd':
                    self.rect.x += self.dp[0]
                    if pygame.sprite.spritecollideany(self, walls_group):
                        self.rect.x -= self.dp[0]
                elif self.dp[1] == 'a':
                    self.rect.x -= self.dp[0]
                    if pygame.sprite.spritecollideany(self, walls_group):
                        self.rect.x += self.dp[0]
            pygame.sprite.spritecollide(self, berries_group, True)

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
            pygame.draw.rect(self.image, (65, 105, 225), ((params[0] / 100, params[1] / 100),
                                                          (params[0] - params[0] / 100, params[1] - params[1] / 100)))
            self.rect = self.image.get_rect()
            self.rect.x = pos[0]
            self.rect.y = pos[1]

    def load_lvl(lvl_file):
        # Загрузка с сохранения
        if type(lvl_file) == list:
            lvl = lvl_file
            block_w = 900 // len(sorted(lvl, key=lambda z: len(z))[0])
            block_h = 900 // len(lvl)
            ber_w = 280 // len(sorted(lvl, key=lambda z: len(z))[0])
            ber_h = 310 // len(lvl)
            for i in range(len(lvl)):
                for y in range(len(lvl[i])):
                    if y < 28:
                        if lvl[i][y] == '.':
                            wall((y * block_w + 350, i * block_h), (block_w, block_h), walls_group)
                        elif lvl[i][y] == '+':
                            berry((y * block_w + 350, i * block_h), (ber_w, ber_h),
                                  (block_w // 2 - ber_w // 2, ber_h), berries_group)
            return [lvl, block_w, block_h, ber_w, ber_h, (0, 0)]
        # Загрузка с файла
        with open(lvl_file, 'r') as lvl:
            lvl = lvl.read().split('\n')
            block_w = 900 // len(sorted(lvl, key=lambda z: len(z))[0])
            block_h = 900 // len(lvl)
            ber_w = 280 // len(sorted(lvl, key=lambda z: len(z))[0])
            ber_h = 310 // len(lvl)
            pac_pos = 0
            for i in range(len(lvl)):
                for y in range(len(lvl[i])):
                    if y < 28:
                        if lvl[i][y] == '.':
                            wall((y * block_w + 350, i * block_h), (block_w, block_h), walls_group)
                        elif lvl[i][y] == 'P':
                            pac_pos = y * block_w + 350, i * block_h
                        elif lvl[i][y] == '+':
                            berry((y * block_w + 350, i * block_h), (ber_w, ber_h),
                                  (block_w // 2 - ber_w // 2, ber_h), berries_group)
            return [lvl, block_w, block_h, ber_w, ber_h, pac_pos]

    if save_lvl == '':
        lvl_params = load_lvl(os.path.join('data', cur_lvl))
    else:
        load_lvl(save_lvl)
    PacMan = pacman(lvl_params[-1])
    main_game_running = True
    while main_game_running:
        for event in pygame.event.get():
            main_hero.update(event)
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == main_game_event:
                save_lvl = ''
                # Цикл создающий длинную строку, содержащую карту(x - column, y - raw)
                for raw in range(len(lvl_params[0])):
                    for column in range(len(lvl_params[0][1])):
                        if lvl_params[0][raw][column] == '.':
                            save_lvl += '.'
                        elif lvl_params[0][raw][column] == '-' or lvl_params[0][raw][column] == 'P':
                            save_lvl += '-'
                        else:
                            for berry in berries_group:
                                if berry.rect.x == int(
                                        lvl_params[1] * column + lvl_params[1] / 2 - lvl_params[3] / 2) + 350 \
                                        and berry.rect.y == int(lvl_params[2] * raw + lvl_params[4]):
                                    save_lvl += '+'
                        if len(save_lvl.split('\n')[raw]) != column + 1:
                            save_lvl += '-'
                    save_lvl += '\n'
                save_lvl = save_lvl.split('\n')[:-1]
                # Cрань для записи положения ГГ в список строк(карту)
                save_lvl[PacMan.rect.y // lvl_params[2]] = save_lvl[
                    PacMan.rect.y // lvl_params[2]][:(PacMan.rect.x - 350) // lvl_params[1]] + 'P' + save_lvl[
                    PacMan.rect.y // lvl_params[2]][(PacMan.rect.x - 350) // lvl_params[1] + 1:]
                lvl_params[-1] = (PacMan.rect.x, PacMan.rect.y)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    return 'pause'
        scr.fill((0, 0, 0))
        berries_group.draw(scr)
        walls_group.draw(scr)
        main_hero.draw(scr)
        pygame.display.flip()


def pause(scr):
    """Функция для создания экрана паузы"""

    class raining(pygame.sprite.Sprite):
        def __init__(self, im, num):
            super().__init__(rain_frames_group)
            self.type = num
            self.image = im
            self.rect = self.image.get_rect()

        def draw(self):
            scr.blit(self.image, self.rect)

    rain_frames_group = pygame.sprite.Group()
    pause_buttons = pygame.sprite.Group()
    pause_rects = [
        Beautiful_rect(550, 120, 500, 100, (220, 56, 130), (210, 56, 210), 'CONTINUE', pause_buttons),
        Beautiful_rect(550, 370, 500, 100, (120, 156, 130), (210, 56, 210), 'SETTINGS', pause_buttons),
        Beautiful_rect(550, 620, 500, 100, (220, 56, 30), (210, 210, 210), 'EXIT THE MAIN MENU', pause_buttons)
    ]

    rain_event_type = pygame.USEREVENT + 1
    rain_images = normal_frames(rain_frames, 'rain')
    for i in rain_images:
        raining(i[0], i[1])
    pygame.time.set_timer(rain_event_type, 60)
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
                        settings(scr, 'game')
                    elif pos_y % 3 == 2:
                        return 'main_menu'
            elif event.type == rain_event_type:
                cur_frame = cur_frame % len(rain_frames)
                for i in rain_frames_group:
                    if i.type == cur_frame:
                        i.draw()
                # rain_frames_group.update()
                cur_frame += 1
                pause_rects[pos_y % 3].checked_draw(scr)
                pause_buttons.draw(scr)
                pygame.display.flip()


def main_menu(scr):
    global main_menu_image
    main_menu_buttons = pygame.sprite.Group()
    main_menu_rects = [
        Beautiful_rect(550, 120, 500, 100, (23, 254, 25), (254, 140, 23), 'NEW GAME', main_menu_buttons),
        Beautiful_rect(550, 370, 500, 100, (23, 254, 25), (254, 140, 23), 'SETTINGS', main_menu_buttons),
        Beautiful_rect(550, 620, 500, 100, (23, 254, 25), (254, 140, 23), 'EXIT', main_menu_buttons)
    ]
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
                        settings(scr, 'menu')
                    elif pos_y % 3 == 2:
                        return 'quit'
        scr.fill((0, 0, 0))
        scr.blit(main_menu_image, (0, 0))
        main_menu_rects[pos_y % 3].checked_draw(scr)
        main_menu_buttons.draw(scr)
        pygame.display.flip()


def settings(scr, where='menu'):
    global music_volume, sound_volume, cur_lvl, save_lvl
    pos_y = 0
    pos_x = 0
    lvl = ''
    all_disable = False

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

    scr.fill((0, 0, 0))
    # scr.blit(settings_image, (0, 0))
    settings_buttons.draw(scr)
    if pos_y % 3 == 2 and len(settings_rects[0]) != 4:
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
                            if lvl[-4:] == '.txt' and lvl in os.listdir(path="data"):
                                settings_rects[0][3].kill()
                                settings_rects[0][3] = Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23),
                                                                      lvl, settings_buttons)
                                cur_lvl = lvl
                                save_lvl = ''
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
                            x = lvl[:-1]
                            lvl = x
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
                        if where == 'game':
                            pos_y = pos_y % 2
                        pos_x = pos_x % 3
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
                if where == 'game':
                    settings_rects[pos_x % 3][pos_y % 2].checked_draw(scr)
                else:
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
    rain_frames = frames_from_gif(ImageSequence.Iterator(Image.open(os.path.join('data', 'rain.gif'))))
    main_menu_image = load_image('main_menu.png')
    pac_image = load_image('pacman.png')
    cur_lvl = 'lvl.txt'
    save_lvl = ''
    lvl_params = [0, 0, 0, 0, 0, (0, 0)]

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
        elif cur_screen == 'quit':
            running = False
        pygame.display.flip()
    pygame.quit()
