from settings import *

import threading
from interactive import Button, Slider
from functions import centerImage, centerText


class Menu:
    def __init__(self, createLevel, config, switchFPS):
        # Setup
        self.displaySurface = pygame.display.get_surface()
        self.createLevel = createLevel
        self.config = config
        self.switchFPS = switchFPS
        self.logoImage = pygame.image.load('assets/images/gui/logo.png').convert_alpha()
        self.bgImage = pygame.image.load('assets/images/gui/mainMenuBG.png').convert()
        self.starting = False
        self.bgOffset = pygame.mouse.get_pos()[0]
        self.transition = 0

        # Progress
        levelList = {0: level_1, 1: level_2, 2: level_3}
        self.progress = int(self.config.get('level', 'Progress'))
        self.currentLevel = levelList[self.progress]

        # Menu Theme
        self.menuTheme = pygame.mixer.Sound('assets/sounds/music/MainMenuTheme Trap Remix.wav')
        self.menuTheme.set_volume(0.4 * int(self.config.get('musicVolume', 'Settings')) / 100)

        # Buttons
        interfaceVolume = int(self.config.get('interfaceVolume', 'Settings'))
        self.playBtn = Button('Играть', 430, self.displaySurface, interfaceVolume)
        self.settingsBtn = Button('Настройки', 550, self.displaySurface, interfaceVolume)
        self.creditsBtn = Button('Credits', 670, self.displaySurface, interfaceVolume)
        self.exitBtn = Button('Выход', 790, self.displaySurface, interfaceVolume)

        # Footer
        self.footerText = mainFont.render('Tempus Corp. v1.0', False, '#ffffff')

        # Settings Window
        self.settings = False
        self.settingsSliders = [
            Slider(self.displaySurface, screenSize[0] / 16 * 4, screenSize[1] / 4, int(self.config.get('musicVolume', 'Settings')),
                   'Музыка', interfaceVolume = interfaceVolume, editingFunc = self.volumeChanging, type = 'musicVolume'),
            Slider(self.displaySurface, screenSize[0] / 16 * 4, screenSize[1] / 4 + 64, int(self.config.get('effectsVolume', 'Settings')),
                   'Эффекты', interfaceVolume = interfaceVolume, doneFunc = self.volumeChanging, type = 'effectsVolume'),
            Slider(self.displaySurface, screenSize[0] / 16 * 4, screenSize[1] / 4 + 128, int(self.config.get('interfaceVolume', 'Settings')),
                   'Интерфейс', interfaceVolume = interfaceVolume, doneFunc = self.volumeChanging, type = 'interfaceVolume')
        ]

        showFPS = not self.switchFPS(); self.switchFPS()
        self.showFPSButton = Button('Включено' if showFPS else 'Выключено', screenSize[1] / 16 * 8, self.displaySurface, interfaceVolume, screenSize[0] / 16 * 4 + 231 / 2)
        self.showFPSButton.sprite = pygame.image.load(
            'assets/images/gui/holoSwitchButtonON.png') if showFPS else pygame.image.load(
            'assets/images/gui/holoSwitchButtonOFF.png')

        self.resetButton = Button('Сброс', screenSize[1] / 16 * 8, self.displaySurface, interfaceVolume, screenSize[0] / 16 * 7 + 231 / 2)

        disableFades = self.config.get('disableFades', 'Settings') == 'True'
        self.disableFadesButton = Button('Контраст' if disableFades else 'Нормально', screenSize[1] / 16 * 8, self.displaySurface, interfaceVolume, screenSize[0] / 16 * 10 + 231 / 2)
        self.disableFadesButton.sprite = pygame.image.load(
            'assets/images/gui/holoSwitchButtonON.png') if disableFades else pygame.image.load(
            'assets/images/gui/holoSwitchButtonOFF.png')

        # Credits Popup
        self.credits = False
        self.creditsImage = pygame.image.load('assets/images/gui/holoWindow.png').convert_alpha()
        self.creditsBackBtn = Button('Назад', (screenSize[1] + self.creditsImage.get_height() - 99) / 2,
                                     self.displaySurface, interfaceVolume,
                                     (screenSize[0] - self.creditsImage.get_width() + 231) / 2)

        self.menuTheme.play(loops=-1)

    def run(self):
        # Background
        threading.Thread(target=self.bgMoving(), name='bgMoving').start()

        # Settings Window Check
        if self.settings:
            self.displaySurface.blit(self.creditsImage, ((screenSize[0] - self.creditsImage.get_width()) / 2, (screenSize[1] - self.creditsImage.get_height() - 119) / 2))

            centerText('Настройки', screenSize[1] / 8, self.displaySurface, True, bigFont)
            self.displaySurface.blit(mainFont.render('Звук', False, '#666666'), (screenSize[0] / 16 * 4 + 3, screenSize[1] / 16 * 3.2 + 3))
            self.displaySurface.blit(mainFont.render('Звук', False, 'White'), (screenSize[0] / 16 * 4, screenSize[1] / 16 * 3.2))

            for slider in self.settingsSliders:
                slider.update()
                slider.draw()

            # Show FPS Button Processing
            self.displaySurface.blit(mainFont.render('Отображение FPS', False, '#666666'), (screenSize[0] / 16 * 4 + 3, screenSize[1] / 16 * 7.2 + 3))
            self.displaySurface.blit(mainFont.render('Отображение FPS', False, 'White'), (screenSize[0] / 16 * 4, screenSize[1] / 16 * 7.2))

            if self.showFPSButton.checkClick():
                showFPS = self.switchFPS()
                self.config.set('showFPS', str(showFPS), 'Settings')
                self.showFPSButton.changeText('Включено' if showFPS else 'Выключено')
                self.showFPSButton.sprite = pygame.image.load(
                    'assets/images/gui/holoSwitchButtonON.png') if showFPS else pygame.image.load(
                    'assets/images/gui/holoSwitchButtonOFF.png')
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.showFPSButton.draw()

            # Show Disable Fades Button Processing
            self.displaySurface.blit(mainFont.render('Спец. возможности', False, '#666666'),
                                     (screenSize[0] / 16 * 10 + 3, screenSize[1] / 16 * 7.2 + 3))
            self.displaySurface.blit(mainFont.render('Спец. возможности', False, 'White'),
                                     (screenSize[0] / 16 * 10, screenSize[1] / 16 * 7.2))

            if self.disableFadesButton.checkClick():
                disableFades = not self.config.get('disableFades', 'Settings') == 'True'
                self.config.set('disableFades', str(disableFades), 'Settings')
                self.disableFadesButton.changeText('Контраст' if disableFades else 'Нормально')
                self.disableFadesButton.sprite = pygame.image.load(
                    'assets/images/gui/holoSwitchButtonON.png') if disableFades else pygame.image.load(
                    'assets/images/gui/holoSwitchButtonOFF.png')
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.disableFadesButton.draw()

            # Reset Button Processing
            self.displaySurface.blit(mainFont.render('Сброс Прогресса', False, '#666666'), (screenSize[0] / 16 * 7 + 3, screenSize[1] / 16 * 7.2 + 3))

            if self.progress > 0:
                self.displaySurface.blit(mainFont.render('Сброс Прогресса', False, 'White'), (screenSize[0] / 16 * 7, screenSize[1] / 16 * 7.2))
                if self.resetButton.checkClick():
                    self.config.set('level', '0', 'Progress')
                    self.config.set('objectives', '', 'Progress')
                    self.config.save()
                    self.currentLevel = level_1
                    self.progress = 0
                self.resetButton.draw()

            if self.creditsBackBtn.checkClick():
                self.config.save()
                self.settings = False
            self.creditsBackBtn.draw()

        # Credits Popup Check
        elif self.credits:
            self.displaySurface.blit(self.creditsImage, ((screenSize[0] - self.creditsImage.get_width()) / 2, (screenSize[1] - self.creditsImage.get_height() - 119) / 2))

            lines = [
                'Tempus Corp.', '',
                'Created on Python',
                'by Pixel Pioneers', '',
                'Programming',
                'Ryzhenkov Evgeniy', '', '',
                'Original Songs for Remixes', '',
                'Main Menu Theme: Uppbeat.io',
                'Cunning Fox: Tunetank.com',
                'Danger by Vislevski: Tunetank.com',
                'Arcade Machine by Nuclear Wave: Tunetank.com',
                'Pulse of Time by Anton Kramar: Tunetank.com', '',
                'Graphics', '',
                'Textures & Sprites: Ryzhenkov Evgeniy ',
                '                    Korolyov Alexander',
                'Energy Explosion: Envato.com'
            ]
            startOffset = 64
            for line in lines:
                centerText(line, (screenSize[1] - self.creditsImage.get_height() - 119) / 2 + startOffset, self.displaySurface, True)
                startOffset += 30

            if self.creditsBackBtn.checkClick():
                self.credits = False
            self.creditsBackBtn.draw()

        # Otherwise draw Main Menu
        else:
            ### Logo
            centerImage(self.logoImage, 50, self.displaySurface)

            ### Buttons
            # Play Button
            if self.playBtn.checkClick() and not self.starting:
                self.starting = True
                self.menuTheme.fadeout(2000)
            self.playBtn.draw()

            # Settings Button
            if self.settingsBtn.checkClick():
                self.settings = not self.settings
            self.settingsBtn.draw()

            # Credits Button
            if self.creditsBtn.checkClick():
                self.credits = not self.credits
            self.creditsBtn.draw()

            # Quit Button
            if self.exitBtn.checkClick():
                pygame.quit()
                return
            else:
                self.exitBtn.draw()

            ### Footer
            self.displaySurface.blit(self.footerText, (screenSize[0] - self.footerText.get_width() - 16, screenSize[1] - self.footerText.get_height() - 16))

            ### Starting
            if self.starting:
                self.starting += 1
                self.transition = self.starting
                if self.starting >= 70:
                    self.createLevel(self.currentLevel)  # LOADING LEVEL BY PRESSING PLAY BUTTON; Importing level dictionaries from settings.py

            if self.transition:
                transitionSurf = pygame.Surface(screenSize)
                pygame.draw.circle(transitionSurf, (255, 255, 255),
                                   (screenSize[0] // 2, screenSize[1] // 2 - 50),
                                   (60 - abs(self.transition)) * 32)
                transitionSurf.set_colorkey((255, 255, 255))
                self.displaySurface.blit(transitionSurf, (0, 0))

    def volumeChanging(self, type: str, value: float):
        self.config.set(type, str(int(value)), 'Settings')
        musicVolume = int(self.config.get('musicVolume', 'Settings'))
        interfaceVolume = int(self.config.get('interfaceVolume', 'Settings')) / 100

        for slider in self.settingsSliders:
            slider.interfaceVolume = interfaceVolume
            if slider.label == 'Эффекты':
                slider.effectsVolume = int(slider.value) / 100

        self.menuTheme.set_volume(0.5 * musicVolume / 100)
        self.playBtn.interfaceVolume = interfaceVolume
        self.settingsBtn.interfaceVolume = interfaceVolume
        self.showFPSButton.interfaceVolume = interfaceVolume
        self.creditsBtn.interfaceVolume = interfaceVolume
        self.creditsBackBtn.interfaceVolume = interfaceVolume
        self.exitBtn.interfaceVolume = interfaceVolume

    def bgMoving(self):
        mousePos = pygame.mouse.get_pos()
        self.bgOffset = self.bgOffset + (mousePos[0] - self.bgOffset) * 0.005

        self.displaySurface.blit(self.bgImage, (self.bgOffset - screenSize[0], 0))