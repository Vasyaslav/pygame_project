import pygame
import os
import sqlite3
import random
from playing_objs import *
from PIL import Image, ImageSequence


def main_game(scr):
    global cur_lvl, lvl_params, save_lvl, timer
    berries_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    tablets = pygame.sprite.Group()
    particale_group = pygame.sprite.Group()
    checker_group = pygame.sprite.Group()

    main_hero = pygame.sprite.Group()
    pac_man_timer = pygame.USEREVENT + 6
    pygame.time.set_timer(pac_man_timer, 250)

    enemies = pygame.sprite.Group()
    enemies_timer = pygame.USEREVENT + 7
    pygame.time.set_timer(enemies_timer, 300)

    main_game_event = pygame.USEREVENT + 4
    pygame.time.set_timer(main_game_event, 50)

    just_timer = pygame.USEREVENT + 8
    pygame.time.set_timer(just_timer, 1000)

    timer_group = pygame.sprite.Group()
    Beautiful_rect(100, 100, 150, 60, (255, 160, 122),
                   (173, 255, 47),
                   ':'.join((str(timer // 60).rjust(2, '0'), str(timer % 60).rjust(2, '0'))),
                   timer_group)
    timer_group.draw(scr)

    ending = False

    class enemy_1(pygame.sprite.Sprite):
        def __init__(self, pos, group):
            super().__init__(group)
            self.pars = sorted(lvl_params[1:3])[0]
            self.image = pygame.surface.Surface((40, 40))
            self.image.fill((0, 0, 0))
            pygame.draw.circle(self.image, (245, 160, 60), (20, 20),
                               21)
            self.image = pygame.transform.scale(red_ghost_im, (int(self.pars), int(self.pars)))
            self.rect = self.image.get_rect()
            self.rect.x = pos[0]
            self.rect.y = pos[1]

        def update(self, ev):
            if ev.type == enemies_timer:
                start = ((self.rect.x - 350) // lvl_params[1], self.rect.y // lvl_params[2])
                where = ((PacMan.rect.x - 350) // lvl_params[1], PacMan.rect.y // lvl_params[2])
                INF = 0
                x, y = start
                dist = [[INF] * len(lvl_params[0]) for x in range(len(lvl_params[0]))]
                dist[y][x] = 13
                prev = [[None] * len(lvl_params[0]) for x in range(len(lvl_params[0]))]
                queue = [(x, y)]
                while queue:
                    x, y = queue.pop(0)
                    for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                        next_x, next_y = x + dx, y + dy
                        if lvl_params[-1][next_y][next_x] != 0 and dist[next_y][next_x] == INF:
                            dist[next_y][next_x] = dist[y][x] + 1
                            prev[next_y][next_x] = (x, y)
                            queue.append((next_x, next_y))
                x, y = where
                if start == where or dist[y][x] == INF:
                    target = False
                else:
                    while prev[y][x] != start:
                        x, y = prev[y][x]
                    target = x, y
                if target:
                    self.rect.x += (target[0] - start[0]) * lvl_params[1]
                    self.rect.y += (target[1] - start[1]) * lvl_params[2]

    class pacman(pygame.sprite.Sprite):
        def __init__(self, pos, group):
            super().__init__(group)
            self.pars = sorted(lvl_params[1:3])[0]
            self.image = pygame.transform.scale(pac_image, (int(self.pars), int(self.pars)))
            self.right_image = self.image
            self.left_image = pygame.transform.flip(self.image, True, False)
            self.up_image = pygame.transform.rotate(self.image, 90)
            self.down_image = pygame.transform.rotate(self.image, 270)
            self.true_im = 'r'
            self.rect = self.image.get_rect()
            self.dp = [self.pars, '']
            self.next = ''
            self.rect.x = pos[0]
            self.rect.y = pos[1]

            self.speed = False
            self.how_long = 0

        def update(self, ev):
            """Функция, обрабатывающая: нажатия на клавиатуре, срабатывание таймера, пересечение с ягодками"""
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_w or ev.key == pygame.K_UP:
                    self.image = self.up_image
                    if len([
                        wall for wall in walls_group if wall.rect.y == self.rect.y - self.pars \
                                                        and wall.rect.x == self.rect.x]):
                        self.next = 'w'
                    else:
                        self.dp[1] = 'w'
                elif ev.key == pygame.K_s or ev.key == pygame.K_DOWN:
                    self.image = self.down_image
                    if len([
                        wall for wall in walls_group if wall.rect.y == self.rect.y + self.pars \
                                                        and wall.rect.x == self.rect.x]):
                        self.next = 's'
                    else:
                        self.dp[1] = 's'
                elif ev.key == pygame.K_d or ev.key == pygame.K_RIGHT:
                    self.image = self.right_image
                    if len([
                        wall for wall in walls_group if wall.rect.x == self.rect.x + self.pars \
                                                        and wall.rect.y == self.rect.y]):
                        self.next = 'd'
                    else:
                        self.dp[1] = 'd'
                elif ev.key == pygame.K_a or ev.key == pygame.K_LEFT:
                    self.image = self.left_image
                    if len([
                        wall for wall in walls_group if wall.rect.x == self.rect.x - self.pars \
                                                        and wall.rect.y == self.rect.y]):
                        self.next = 'a'
                    else:
                        self.dp[1] = 'a'
            if self.next:
                if self.next == 'w':
                    if not len([
                        wall for wall in walls_group if wall.rect.y == self.rect.y - self.pars \
                                                        and wall.rect.x == self.rect.x]):
                        self.dp[1] = 'w'
                        self.next = ''
                elif self.next == 's':
                    if not len([
                        wall for wall in walls_group if wall.rect.y == self.rect.y + self.pars \
                                                        and wall.rect.x == self.rect.x]):
                        self.dp[1] = 's'
                        self.next = ''
                elif self.next == 'd':
                    if not len([
                        wall for wall in walls_group if wall.rect.x == self.rect.x + self.pars \
                                                        and wall.rect.y == self.rect.y]):
                        self.dp[1] = 'd'
                        self.next = ''
                elif self.next == 'a':
                    if not len([
                        wall for wall in walls_group if wall.rect.x == self.rect.x - self.pars \
                                                        and wall.rect.y == self.rect.y]):
                        self.dp[1] = 'a'
                        self.next = ''
            if ev.type == pac_man_timer:
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
            if pygame.sprite.spritecollide(self, tablets, True):
                pygame.time.set_timer(pac_man_timer, 180)
                self.speed = True
            if self.speed and event.type == pac_man_timer:
                if self.how_long == 24:
                    self.speed = False
                    self.how_long = 0
                    pygame.time.set_timer(pac_man_timer, 250)
                else:
                    self.how_long += 1

    def load_lvl(lvl_file):
        # Загрузка с сохранения
        if type(lvl_file) == list:
            lvl = lvl_file
            block_w = 900 // len(sorted(lvl, key=lambda z: len(z))[0])
            block_h = 900 // len(lvl)
            ber_w = 280 // len(sorted(lvl, key=lambda z: len(z))[0])
            ber_h = 310 // len(lvl)
            table_w = 480 // len(sorted(lvl, key=lambda z: len(z))[0])
            table_h = 510 // len(lvl)
            for i in range(len(lvl)):
                for y in range(len(lvl[i])):
                    if y < 28:
                        if lvl[i][y] == '.':
                            wall((y * block_w + 350, i * block_h), (block_w, block_h), walls_group)
                        elif lvl[i][y] == '+':
                            berry((y * block_w + 350, i * block_h), (ber_w, ber_h),
                                  (block_w // 2 - ber_w // 2, ber_h), berries_group)
                        elif lvl[i][y] == 'O':
                            tablet((y * block_w + 350, i * block_h),
                                   (table_w, table_h),
                                   (block_w // 2 - table_w // 2, ber_h // 1.5), tablets)
            return [lvl, block_w, block_h, ber_w, ber_h, [lvl_params[-2][0], lvl_params[-2][1]], lvl_params[-1]]
        # Загрузка с файла
        with open(lvl_file, 'r') as lvl:
            lvl = lvl.read().split('\n')
            block_w = 900 // len(sorted(lvl, key=lambda z: len(z))[0])
            block_h = 900 // len(lvl)
            ber_w = 280 // len(sorted(lvl, key=lambda z: len(z))[0])
            ber_h = 310 // len(lvl)
            table_w = 480 // len(sorted(lvl, key=lambda z: len(z))[0])
            table_h = 510 // len(lvl)
            pac_pos = 0
            enemy_pos = (-1, -1)
            lvl_ints = []
            for i in range(len(lvl)):
                int_row = ''
                for y in range(len(lvl[i])):
                    if y < 28:
                        if lvl[i][y] == '.':
                            wall((y * block_w + 350, i * block_h), (block_w, block_h), walls_group)
                        elif lvl[i][y] == 'P':
                            pac_pos = y * block_w + 350, i * block_h
                        elif lvl[i][y] == '+':
                            berry((y * block_w + 350, i * block_h), (ber_w, ber_h),
                                  (block_w // 2 - ber_w // 2, ber_h), berries_group)
                        elif lvl[i][y] == 'O':
                            tablet((y * block_w + 350, i * block_h),
                                   (table_w, table_h),
                                   (block_w // 2 - table_w // 2, ber_h // 1.5), tablets)
                        elif lvl[i][y] == 'R':
                            enemy_pos = y * block_w + 350, i * block_h
                        if lvl[i][y] == '.':
                            int_row += '0'
                        else:
                            int_row += '1'
                lvl_ints.append([int(char) for char in int_row])
            return [lvl, block_w, block_h, ber_w, ber_h, [pac_pos, enemy_pos], lvl_ints]

    if save_lvl == '':
        lvl_params = load_lvl(os.path.join('data', cur_lvl))
    else:
        lvl_params = load_lvl(save_lvl)
    PacMan = pacman(lvl_params[-2][0], main_hero)
    if lvl_params[-2][1] != (-1, -1):
        RedGhost = enemy_1(lvl_params[-2][1], enemies)
    # Если выйти в главное меню и зайти обратно в игру, то враг ультра ускорится, поэтому ставлю его таймер ещё раз
    pygame.time.set_timer(enemies_timer, 300)
    main_game_running = True
    while main_game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == just_timer:
                timer += 1
                Beautiful_rect(100, 100, 150, 60, (255, 160, 122),
                               (173, 255, 47),
                               ':'.join((str(timer // 60).rjust(2, '0'), str(timer % 60).rjust(2, '0'))),
                               timer_group)
            if event.type == pac_man_timer and not ending:
                if len(berries_group) == 0:
                    winning(cur_lvl, timer)
                    timer = 0
                    save_lvl = ''
                    return 'main_menu'
                main_hero.update(event)
                scr.fill((0, 0, 0))
                berries_group.draw(scr)
                walls_group.draw(scr)
                main_hero.draw(scr)
                tablets.draw(scr)
                enemies.draw(scr)
                timer_group.draw(scr)
                pygame.display.flip()
            if event.type == enemies_timer and not ending:
                enemies.update(event)
                pygame.display.flip()
            if lvl_params[-2][1] != (-1, -1):
                if PacMan.rect == RedGhost.rect:
                    if not PacMan.speed:
                        for i in range(150):
                            particle = Particles((PacMan.rect.x, PacMan.rect.y),
                                                 random.choice(range(-5, 5)),
                                                 random.choice(range(-5, 5)), particale_group)
                        for i in range(30):
                            particale_group.update(scr)
                            particale_group.draw(scr)
                        pygame.display.flip()
                        losing()
                        save_lvl = ''
                        return 'main_menu'
                    else:
                        al = 0
                        while al != 1:
                            new_enemy_pos = (random.choice(range(len(lvl_params[0]))),
                                             random.choice(range(len(lvl_params[0]))))
                            if save_lvl[new_enemy_pos[0]][new_enemy_pos[1]] != '.':
                                RedGhost.rect.x = 350 + new_enemy_pos[0] * lvl_params[1]
                                RedGhost.rect.y = new_enemy_pos[1] * lvl_params[1]
                                al = 1
            if event.type == pygame.KEYDOWN:
                main_hero.update(event)
                save_lvl = ''
                # Цикл создающий длинную строку, содержащую карту(x - column, y - raw)
                for raw in range(len(lvl_params[0])):
                    for column in range(len(lvl_params[0][1])):
                        if lvl_params[0][raw][column] == '.':
                            save_lvl += '.'
                        elif lvl_params[0][raw][column] == '-' or lvl_params[0][raw][column] == 'P':
                            save_lvl += '-'
                        else:
                            checker((int(lvl_params[1] * column + lvl_params[1] / 2 - lvl_params[3] / 2) + 350, int(
                                lvl_params[2] * raw + lvl_params[4])),
                                    (2, 2), checker_group)
                            for i in checker_group:
                                if pygame.sprite.spritecollide(i, berries_group, False):
                                    save_lvl += '+'
                                if pygame.sprite.spritecollide(i, tablets, False):
                                    save_lvl += 'O'
                                i.kill()
                        if len(save_lvl.split('\n')[raw]) != column + 1:
                            save_lvl += '-'
                    save_lvl += '\n'
                save_lvl = save_lvl.split('\n')[:-1]
                # Cрань для записи положения ГГ в список строк(карту).
                # Она не помещадась в 1 строчку поэтому разбил её на 2.
                ### Пока не нужна, т.к враг определяет положение гг оп координатам
                # before_player = save_lvl[PacMan.rect.y // lvl_params[2]][:(PacMan.rect.x - 350) // lvl_params[1]] + 'P'
                # after_him = save_lvl[PacMan.rect.y // lvl_params[2]][(PacMan.rect.x - 350) // lvl_params[1] + 1:]
                # save_lvl[PacMan.rect.y // lvl_params[2]] = before_player + after_him
                lvl_params[-2][0] = PacMan.rect.x, PacMan.rect.y
                if lvl_params[-2][1] != (-1, -1):
                    lvl_params[-2][1] = RedGhost.rect.x, RedGhost.rect.y
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    answer = pause(scr)
                    if answer == 'main_menu':
                        save_lvl = ''
                        timer = 0
                        return 'main_menu'


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
                pygame.mixer.music.play()
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


def records(scr):
    records_group = pygame.sprite.Group()
    Beautiful_rect(550, 80, 500, 100, (23, 254, 25), (254, 140, 23), 'RECORDS', records_group)
    scr.fill((0, 0, 0))
    records_group.draw(scr)
    pygame.display.flip()

    path = os.path.join('data', 'records.db')
    if 'records.db' in os.listdir('data'):
        con = sqlite3.connect(path)
        cur = con.cursor()
        all_records = cur.execute('''SELECT * FROM Результат''').fetchall()
        print(all_records)
        if len(all_records) > 0:
            for i in range(len(all_records)):
                y_coord = 100 + (i + 1) * 150
                Beautiful_rect(100, y_coord, 400, 100, (0, 255, 255), (0, 0, 0), all_records[i][1], records_group)
                Beautiful_rect(600, y_coord, 400, 100, (0, 255, 255), (0, 0, 0), all_records[i][2], records_group)
                Beautiful_rect(1100, y_coord, 400, 100, (0, 255, 255), (0, 0, 0), all_records[i][3], records_group)
        else:
            Beautiful_rect(400, 400, 800, 100, (220, 20, 60), (0, 0, 0), 'RECORDS ARE NOT FOUND', records_group)
    else:
        Beautiful_rect(400, 400, 800, 100, (220, 20, 60), (0, 0, 0), 'RECORDS ARE NOT FOUND', records_group)
    records_group.draw(scr)
    pygame.display.flip()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'main_menu'


def main_menu(scr):
    global main_menu_image
    main_menu_buttons = pygame.sprite.Group()
    main_menu_rects = [
        Beautiful_rect(550, 80, 500, 100, (23, 254, 25), (254, 140, 23), 'NEW GAME', main_menu_buttons),
        Beautiful_rect(550, 290, 500, 100, (23, 254, 25), (254, 140, 23), 'SETTINGS', main_menu_buttons),
        Beautiful_rect(550, 500, 500, 100, (23,254, 25), (254, 140, 23), 'RECORDS', main_menu_buttons),
        Beautiful_rect(550, 720, 500, 100, (23, 254, 25), (254, 140, 23), 'EXIT', main_menu_buttons)
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

    scr.fill((0, 0, 0))
    scr.blit(main_menu_image, (0, 0))
    main_menu_rects[pos_y % 3].checked_draw(scr)
    main_menu_buttons.draw(scr)
    pygame.display.flip()

    main_menu_running = True
    while main_menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                pygame.mixer.music.play()
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    pos_y -= 1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    pos_y += 1
                elif event.key == pygame.K_ESCAPE:
                    return 'quit'
                elif event.key == pygame.K_SPACE:
                    if pos_y % 4 == 0:
                        return 'main_game'
                    elif pos_y % 4 == 1:
                        scr.fill((0, 0, 0))
                        if settings(scr, 'menu') == 'quit':
                            return 'quit'
                    elif pos_y % 4 == 2:
                        return 'records'
                    elif pos_y % 4 == 3:
                        return 'quit'
            if event.type == pygame.KEYDOWN:
                scr.fill((0, 0, 0))
                scr.blit(main_menu_image, (0, 0))
                main_menu_rects[pos_y % 4].checked_draw(scr)
                main_menu_buttons.draw(scr)
                pygame.display.flip()


def settings(scr, where='menu'):
    global music_volume, sound_volume, cur_lvl, save_lvl
    pos_y = 0
    pos_x = 0
    lvl = ''
    all_disable = False
    music_enable = False
    sound_enable = False

    settings_buttons = pygame.sprite.Group()
    # settings_image = pygame.transform.scale(load_image('settings.jpg', -1), (1600, 900))
    settings_rects = [
        [Beautiful_rect(500, 120, 200, 50, (72, 209, 204), (254, 140, 23), 'MUSIC', settings_buttons),
         Beautiful_rect(500, 320, 200, 50, (255, 105, 180), (254, 140, 23), 'SOUND', settings_buttons),
         Beautiful_rect(500, 490, 630, 80, (23, 254, 25), (254, 140, 23), 'CHOOSE LVL', settings_buttons)],
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
                pygame.mixer.music.play()
                if all_disable:
                    if event.key == 13 or event.key == 1073741912:
                        all_disable = False
                        settings_rects[0][3].kill()
                        settings_rects[0][3] = (
                            Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23), cur_lvl,
                                           settings_buttons))
                        if len(lvl) > 4:
                            if lvl[-4:] == '.txt' and lvl in os.listdir(path="data"):
                                with open(os.path.join('data', lvl), 'r') as file:
                                    strs = file.read()
                                    # Проверка чтобы карты была квадратной(создаётся список с единиицами где единиица
                                    # ставится если длина строки равна длине файла, находится сумма этого списка и
                                    # сравнивается с длиной файла
                                    if len(strs.split('\n')) == sum(
                                            [1 for i in strs.split('\n') if len(i) == len(strs.split('\n'))]):
                                        settings_rects[0][3].kill()
                                        settings_rects[0][3] = Beautiful_rect(500, 690, 630, 80, (23, 254, 25),
                                                                              (254, 140, 23),
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
                    if music_enable:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            music_volume = (music_volume - 1) % 11
                            settings_rects[1][0].kill()
                            settings_rects[1][0] = Beautiful_rect(1050, 120, 80, 50, (72, 209, 204), (254, 140, 23),
                                                                  f'{music_volume}', settings_buttons)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            music_volume = (music_volume + 1) % 11
                            settings_rects[1][0].kill()
                            settings_rects[1][0] = Beautiful_rect(1050, 120, 80, 50, (72, 209, 204), (254, 140, 23),
                                                                  f'{music_volume}', settings_buttons)
                    elif sound_enable:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            sound_volume = (sound_volume - 1) % 11
                            settings_rects[1][1].kill()
                            settings_rects[1][1] = Beautiful_rect(1050, 320, 80, 50, (255, 105, 180),
                                                                  (254, 140, 23),
                                                                  f'{sound_volume}', settings_buttons)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            sound_volume = (sound_volume + 1) % 11
                            settings_rects[1][1].kill()
                            settings_rects[1][1] = Beautiful_rect(1050, 320, 80, 50, (255, 105, 180),
                                                                  (254, 140, 23),
                                                                  f'{sound_volume}', settings_buttons)
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        pos_y -= 1
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        pos_y += 1
                    if event.key == pygame.K_ESCAPE:
                        if music_enable:
                            music_enable = False
                        elif sound_enable:
                            sound_enable = False
                        elif prev_screen == 'pause':
                            return 'pause'
                        else:
                            return 'main_menu'
                    elif event.key == pygame.K_SPACE:
                        if where == 'game':
                            pos_y = pos_y % 2
                        if pos_y % len(settings_rects[0]) == 0:
                            if pos_x == 0:
                                music_enable = True
                        elif pos_y % len(settings_rects[0]) == 1:
                            if pos_x == 0:
                                sound_enable = True
                        elif pos_y % len(settings_rects[0]) == 2:
                            settings_rects[0].append(
                                Beautiful_rect(500, 690, 630, 80, (23, 254, 25), (254, 140, 23), cur_lvl,
                                               settings_buttons))
                        elif pos_y % len(settings_rects[0]) == 3:
                            all_disable = True
                scr.fill((0, 0, 0))
                settings_buttons.draw(scr)
                if where == 'game':
                    settings_rects[0][pos_y % 2].checked_draw(scr)
                else:
                    if music_enable or sound_enable:
                        if len(settings_rects[0]) == 4:
                            settings_rects[0][pos_y % 4].checked_draw(scr)
                        else:
                            settings_rects[0][pos_y % 3].checked_draw(scr)
                    else:
                        if len(settings_rects[0]) == 4:
                            settings_rects[0][pos_y % 4].checked_draw(scr)
                        else:
                            settings_rects[0][pos_y % 3].checked_draw(scr)
                pygame.display.flip()
                pygame.mixer.music.set_volume(sound_volume / 10)


if __name__ == '__main__':
    pygame.init()
    size = 1600, 900
    screen = pygame.display.set_mode(size)
    music_volume = 5
    sound_volume = 5
    rain_frames = frames_from_gif(ImageSequence.Iterator(Image.open(os.path.join('data', 'rain.gif'))))
    main_menu_image = load_image('main_menu.png')
    pac_image = load_image('pacman.png')
    red_ghost_im = load_image('red_ghost.jpg', -1)
    pygame.mixer.music.load(os.path.join('data', 'button.mp3'))
    pygame.mixer.music.set_volume(sound_volume / 10)
    pygame.display.set_caption('PACMAN')
    cur_lvl = 'lvl.txt'
    save_lvl = ''
    lvl_params = [0, 0, 0, 0, 0, (0, 0), 0]
    # Таймер для игры
    timer = 0

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
        else:
            cur_screen = records(screen)
        pygame.display.flip()
    pygame.quit()
