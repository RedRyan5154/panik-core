import pygame
from pygame.locals import *
import time
import random
import sys, math


class Window:
    class Camara:
        def __init__(self, x, y):
            self.x = x
            self.y = y

            self.chx = 0
            self.chy = 0

        def camara_shake(self, intensity):
            self.chx = random.randint(-intensity, intensity)
            self.chy = random.randint(-intensity, intensity)

        def camara_shake_float(self, intensity: int):
            """Give a int and camera shake will be 100 times smaller"""
            self.chx = random.randint(-intensity, intensity) / 100
            self.chy = random.randint(-intensity, intensity) / 100

    def __init__(self, title, width, height, icon=None):
        """
        Creates a window

        > Title: The window title
        > Width/Height: The window dimensions

        (Optional)> Icon: The window icon. | Default: Panik-Core logo


        Editable Variables:

        > devmode: Shows colisions and other developer useful data to
        > bg: The Window background
        > showfps/showtiming: Display The FPS or frame delay
        > fpspos: Position of the FPS counter
        > fpscolor: Color of the FPS counter"""

        ## window data

        self.title = title
        self.width = width
        self.height = height
        self.devmode = False
        self.icon = icon
        self.bg = (255, 255, 255)
        self.WIN = pygame.display.set_mode(
            (self.width, self.height), pygame.SCALED, display=0, vsync=0
        )
        pygame.display.set_caption(title)
        if self.icon:
            pygame.display.set_icon(
                pygame.transform.scale(
                    pygame.image.load(icon).convert_alpha(), (256, 256)
                )
            )
        else:
            pygame.display.set_icon(
                pygame.image.load("panik_core/asstes/logolowres.png").convert_alpha()
            )

        ##fps

        self.showfps = False
        self.showtiming = False
        self.fps_pos = (10, 15)
        self.fps_color = (0, 0, 0)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 25)
        self.starttime = 0.0
        self.endtime = 0.0
        self.delta_time = 0.0

        ## rendering data

        self.camara = self.Camara(0, 0)
        self.queue = []

        ## cache
        self.winsize_cache = self.winsize

    @property
    def winsize(self):
        self.winsize_cache = pygame.display.get_surface().get_size()
        return pygame.display.get_surface().get_size()

    def blit(self, object=[]):
        self.queue.extend(object)

    def tick(self, fps=30):
        self.delta_time = self.clock.tick(fps) / 1000.0
        return self.delta_time

    def setResizable(self):
        self.WIN = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

    def setFullscreen(self):
        self.WIN = pygame.display.set_mode((0, 0), FULLSCREEN | DOUBLEBUF, 16)
        self.winsize_cache = self.winsize

    def setTitle(self, title):
        pygame.display.set_caption(title)

    def setIcon(self, icon):
        pygame.display.set_icon(pygame.image.load(icon).convert_alpha())

    def render(self, ui=None):
        self.starttime = time.time()  ## for timing

        self.WIN.fill(self.bg)  # clear the window

        ## main loop
        for element in self.queue:
            if element == None:
                continue
            elif element.type == "element":

                ## transform image

                if element.rotation != 0:
                    image = pygame.transform.rotate(element.image, element.rotation)
                    if element.rotation > 360 or element.rotation < -360:
                        element.rotation = 0
                else:
                    image = element.image

                ## center image
                if element.parent:
                    draw_x = (
                        element.x
                        - image.get_width() / 2
                        - self.camara.x
                        - self.camara.chx
                        + element.parent.x
                    )
                    draw_y = (
                        element.y
                        - image.get_height() / 2
                        - self.camara.y
                        - self.camara.chy
                        + element.parent.y
                    )
                else:
                    draw_x = (
                        element.x
                        - image.get_width() / 2
                        - self.camara.x
                        - self.camara.chx
                    )
                    draw_y = (
                        element.y
                        - image.get_height() / 2
                        - self.camara.y
                        - self.camara.chy
                    )

                ## blit image
                self.WIN.blit(image, (draw_x, draw_y))

                ## colision
                if element.colision:
                    ## center colision
                    element.colision.x = (
                        element.x
                        + element.cx
                        - element.cw / 2
                        - self.camara.x
                        - self.camara.chx
                    )
                    element.colision.y = (
                        element.y
                        + element.cy
                        - element.ch / 2
                        - self.camara.y
                        - self.camara.chy
                    )

                    if self.devmode:
                        text = self.font.render("ID: " + element.id, True, (0, 0, 0))
                        pygame.draw.rect(self.WIN, (0, 0, 0), element.colision, 4)
                        self.WIN.blit(
                            text, (element.colision.x, element.colision.y - 25)
                        )
            elif element.type == "text":
                if element.parent:
                    self.WIN.blit(
                        element.text,
                        (
                            element.x
                            - self.camara.x
                            - self.camara.chx
                            + element.parent.x,
                            element.y
                            - self.camara.y
                            - self.camara.chy
                            + element.parent.y,
                        ),
                    )
                else:
                    self.WIN.blit(
                        element.text,
                        (
                            element.x - self.camara.x - self.camara.chx,
                            element.y - self.camara.y - self.camara.chy,
                        ),
                    )
            elif element.type == "tilemap":
                element.group.update(
                    self.camara.x,
                    self.camara.y,
                    self.camara.chx,
                    self.camara.chy,
                    (element.parent.x if element.parent else 0),
                    (element.parent.y if element.parent else 0),
                )
                element.group.draw(self.WIN)
            elif element.type == "rect":
                pygame.draw.rect(self.WIN, element.color, element)
            elif element.type == "particle":

                ## transform image

                if element.rotation != 0:
                    image = pygame.transform.rotate(element.image, element.rotation)
                    if element.rotation > 360 or element.rotation < -360:
                        element.rotation = 0
                else:
                    image = element.image

                ## center image
                if element.parent:
                    draw_x = (
                        element.x
                        - image.get_width() / 2
                        - self.camara.x
                        - self.camara.chx
                        + element.parent.x
                    )
                    draw_y = (
                        element.y
                        - image.get_height() / 2
                        - self.camara.y
                        - self.camara.chy
                        + element.parent.y
                    )
                else:
                    draw_x = (
                        element.x
                        - image.get_width() / 2
                        - self.camara.x
                        - self.camara.chx
                    )
                    draw_y = (
                        element.y
                        - image.get_height() / 2
                        - self.camara.y
                        - self.camara.chy
                    )

                ## blit image
                self.WIN.blit(image, (draw_x, draw_y))

                ## colision
                if element.colision:
                    ## center colision
                    element.colision.x = (
                        element.x
                        + element.cx
                        - element.cw / 2
                        - self.camara.x
                        - self.camara.chx
                    )
                    element.colision.y = (
                        element.y
                        + element.cy
                        - element.ch / 2
                        - self.camara.y
                        - self.camara.chy
                    )

                    if self.devmode:
                        text = self.font.render("ID: " + element.id, True, (0, 0, 0))
                        pygame.draw.rect(self.WIN, (0, 0, 0), element.colision, 4)
                        self.WIN.blit(
                            text, (element.colision.x, element.colision.y - 25)
                        )

        self.camara.chx = 0
        self.camara.chy = 0

        ## ui
        if ui:
            try:
                ui.manager.set_visual_debug_mode(self.devmode)
                ui.manager.update(float(self.delta_time))
                ui.manager.draw_ui(self.WIN)
            except Exception as e:
                print(e)

        ## show fps

        if self.showfps:
            text = self.font.render(
                "FPS: " + str(round(self.clock.get_fps())),
                True,
                self.fps_color,
            )
            self.WIN.blit(text, self.fps_pos)
        elif self.showtiming:
            text = self.font.render(
                "FPS: "
                + str(round(self.clock.get_fps()))
                + " | MS: "
                + str(round(self.clock.get_time()))
                + " | DT: "
                + str(round(self.clock.get_rawtime())),
                True,
                self.fps_color,
            )
            self.WIN.blit(text, self.fps_pos)

        ## update and return timing

        self.queue = []

        pygame.display.flip()

        self.endtime = time.time()

        return str((self.endtime - self.starttime) / 1000) + "ms"
        # return float((self.endtime - self.starttime) / 1000)
