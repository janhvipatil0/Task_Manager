
import pygame
import json
import os
from tkinter import messagebox
import tkinter as tk
#import pync

root = tk.Tk()
root.withdraw()

pygame.init()


#def play(sound):
    #os.system("afplay " + sound + "&")


def write_to_json(path, file_name, data):
    filePathNameWExt = './' + path + '/' + file_name + '.json'
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp)


def add_json_to_existing(path, file_name, data):
    os.remove("./" + path + "/" + file_name + ".json")
    write_to_json(path, file_name, data)


def get_info(path, file_name):
    with open("./" + path + "/" + file_name + ".json") as file:
        data = json.load(file)
        return data


def add_info(key, info):
    global jsonData
    jsonData[key] = info


jsonData = {}

wnWidth = 500
wnHeight = 700
wnColor = (30, 30, 30)
wnTitle = "Task Manager"
wnIcon = "assets/icon.png"

rectHeight = 50
rectColor = (230, 230, 230)
lineColor = (30, 30, 30)

COLOR_INACTIVE = (160, 160, 160)
COLOR_ACTIVE = (83, 173, 85)
FONT = pygame.font.Font("assets/American Captain.otf", 32)
DESCRIBE_FONT = pygame.font.Font("assets/American Captain.otf", 92)

tickImg = "assets/tick.png"

doneFont = pygame.font.Font("assets/American Captain.otf", 37)
doneFontColor = (83, 173, 85)
doneHoverFontColor = (66, 132, 66)

toggleSound = pygame.mixer.Sound("assets/toggle.wav")
addedSound = pygame.mixer.Sound("assets/added.wav")
deletedSound = pygame.mixer.Sound("assets/deleted.wav")
clearSound = pygame.mixer.Sound("assets/clear.wav")

taskCompleteColor = (83, 173, 85)
taskNotCompleteColor = (255, 101, 79)

barColor = (200, 200, 200)
barInputX = 70


wn = pygame.display.set_mode((wnWidth, wnHeight))
pygame.display.set_caption(wnTitle)
tickImg = pygame.image.load(tickImg)
pygame.display.set_icon(pygame.image.load(wnIcon))
newRectY = 70
run = True

try:
    if len(get_info("./", "data")) != 0:
        jsonLoadRectanglesAmount = get_info("./", "data")["rectangle_amount"]
    else:
        jsonLoadRectanglesAmount = 0
except FileNotFoundError:
    write_to_json("./", "data", jsonData)
    jsonLoadRectanglesAmount = 0


# classes and functions
class Rectangle:
    def __init__(self, y, color, completed=False):
        self.rect = [0, y, wnWidth, rectHeight]
        self.color = color
        self.complete = completed
        self.completeRect = [0, y, 40, rectHeight]

    def draw(self):
        pygame.draw.rect(wn, self.color, self.rect)
        pygame.draw.rect(wn, taskCompleteColor if self.complete else taskNotCompleteColor, self.completeRect)
        pygame.draw.line(wn, lineColor, (0, self.rect[1]+rectHeight-2), (wnWidth, self.rect[1]+rectHeight-2), 4)

    def completed(self):
        self.complete = True

    def uncomplete(self):
        self.complete = False

    def get_rect(self):
        return self.completeRect

    def get_completed(self):
        return self.complete


class InputBox:
    def __init__(self, x, y, w, h, text='', title_namer=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.titleNamer = title_namer

    def handle_event(self, update):
        global newRectY, newTitle, showTitleInput, changed

        if update.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(update.pos[0], update.pos[1]):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            if pygame.Rect(doneButton.get_rect()).collidepoint(update.pos[0], update.pos[1]):
                self.active = True
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if update.type == pygame.KEYDOWN:
            if self.active:
                if update.key == pygame.K_RETURN:
                    changed = True
                    if not self.titleNamer:
                        if len(rectangles) is not 11:
                            if self.text != "":
                                saved = self.text
                                play(addedSound)
                                self.clear()
                                rectangles.append(Rectangle(newRectY, rectColor))
                                rectangleText.append(Text(saved, (60, newRectY + 10), (30, 30, 30)))
                                cancelButtons.append(ImgButton("assets/clear.png", wnWidth - 50, newRectY + 10))
                                newRectY += rectHeight
                    else:
                        newTitle = self.text.capitalize() + " - To Do Manager"
                        play(addedSound)
                        self.clear()
                        showTitleInput = False

                elif update.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if self.txt_surface.get_width() < 270:
                        self.text += update.unicode
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        width = max(300, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def clear(self):
        self.text = ""
        self.txt_surface = FONT.render(self.text, True, self.color)


class Button:
    def __init__(self, text, x, y):
        self.x = x
        self.y = y
        self.text = pygame.font.Font.render(doneFont, text, True, doneFontColor)
        self.string = text

    def draw(self):
        wn.blit(self.text, (self.x, self.y))

    def update(self):
        if pygame.Rect(self.x, self.y, self.text.get_width(),
                       self.text.get_height()).collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
            self.text = pygame.font.Font.render(doneFont, self.string, True, doneHoverFontColor)
        else:
            self.text = pygame.font.Font.render(doneFont, self.string, True, doneFontColor)

    def get_rect(self):
        return self.x, self.y, self.text.get_width(), self.text.get_height()


class Text:
    def __init__(self, string, pos, color):
        self.pos = list(pos)
        self.string = string
        self.text = pygame.font.Font.render(FONT, string, True, color)

    def draw(self):
        wn.blit(self.text, self.pos)


class ImgButton:
    def __init__(self, path, x, y):
        self.img = pygame.image.load(path)
        self.pos = [x, y]

    def draw(self):
        wn.blit(self.img, self.pos)

    def get_rect(self):
        return self.pos[0], self.pos[1], self.img.get_width(), self.img.get_height()


def write(text, pos, color):
    text = pygame.font.Font.render(doneFont, text, True, color)
    wn.blit(text, pos)


inputBox = InputBox(barInputX, 20, 200, 32)
titleInputBox = InputBox(wnWidth/2-150, wnHeight-50, 200, 32, title_namer=True)
showTitleInput = False


def render():
    wn.fill(wnColor)
    pygame.draw.rect(wn, barColor, (0, 0, wnWidth, 70))
    inputBox.draw(wn)
    inputBox.update()

    for rectang in rectangles:
        rectang.draw()
        if rectang.get_completed():
            wn.blit(tickImg, (2, rectang.rect[1]+7))

    for text in rectangleText:
        text.draw()

    for button in cancelButtons:
        button.draw()

    pygame.draw.line(wn, (30, 30, 30), (0, 68), (wnWidth, 68), 4)

    doneButton.update()
    doneButton.draw()

    if not showTitleInput:
        clearButton.update()
        clearButton.draw()
        titleButton.update()
        titleButton.draw()
    else:
        titleInputBox.update()
        titleInputBox.draw(wn)

    if len(rectangles) == 0:
        write("YOU HAVE NO TO-DO'S RIGHT NOW.", (55, 200), (40, 40, 40))


rectangles = []
rectangleText = []
doneButton = Button("GO!", 380, 21)
clearButton = Button("CLEAR", wnWidth/2-70, wnHeight-55)
titleButton = Button("TITLE", wnWidth/2+25, wnHeight-55)
cancelButtons = []
newTitle = wnTitle
changed = False

# loads the .json file and puts it on the screen
for i in range(jsonLoadRectanglesAmount):
    rectangles.append(Rectangle(newRectY, rectColor, get_info("./", "data")["rectangle"+str(i)+"complete"]))
    cancelButtons.append(ImgButton("assets/clear.png", wnWidth-50, newRectY+10))
    rectangleText.append(Text(get_info("./", "data")[str(i+1)], (60, newRectY+10), (30, 30, 30)))
    newRectY += rectHeight

try:
    newTitle = get_info("./", "data")["title"]
except KeyError:
    pass

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect in rectangles:
                if not rect.get_completed():
                    if pygame.Rect(rect.get_rect()).collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                        rect.completed()
                        pygame.mixer.Sound.play(toggleSound)
                        changed = True
                else:
                    if pygame.Rect(rect.get_rect()).collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                        rect.uncomplete()
                        pygame.mixer.Sound.play(toggleSound)
                        changed = True

            if pygame.Rect(doneButton.get_rect()).collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                if len(rectangles) != 11:
                    if inputBox.text != "":
                        pygame.mixer.Sound.play(addedSound)
                        savedText = inputBox.text
                        inputBox.clear()
                        rectangles.append(Rectangle(newRectY, rectColor))
                        rectangleText.append(Text(savedText, (60, newRectY+10), (30, 30, 30)))
                        cancelButtons.append(ImgButton("assets/clear.png", wnWidth-50, newRectY+10))
                        newRectY += rectHeight
                        changed = True

            if not showTitleInput:
                mousePos = pygame.mouse.get_pos()
                if pygame.Rect(clearButton.get_rect()).collidepoint(mousePos[0], mousePos[1]):
                    pygame.mixer.Sound.play(clearSound)
                    rectangles = []
                    rectangleText = []
                    cancelButtons = []
                    newRectY = 70
                    changed = True

            for but in cancelButtons:
                if pygame.Rect(but.get_rect()).collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                    index = cancelButtons.index(but)
                    cancelButtons.remove(but)
                    rectangleText.pop(index)
                    rectangles.pop(index)
                    pygame.mixer.Sound.play(deletedSound)
                    savedRectY = newRectY
                    changed = True

                    for rectangle in rectangles:
                        rectIndex = rectangles.index(rectangle)
                        if rectangles.index(rectangle)+1 > index:
                            rectangle.rect[1] -= rectHeight
                            rectangle.completeRect[1] -= rectHeight
                            cancelButtons[rectIndex].pos[1] -= rectHeight
                            rectangleText[rectIndex].pos[1] -= rectHeight
                            newRectY -= 20

                    newRectY = savedRectY-rectHeight

            if not showTitleInput:
                mousePos = pygame.mouse.get_pos()
                if pygame.Rect(titleButton.get_rect()).collidepoint(mousePos[0], mousePos[1]):
                    showTitleInput = True

        inputBox.handle_event(event)
        if showTitleInput:
            titleInputBox.handle_event(event)

    try:
        if rectangles[0].rect[1] != 70:
            rectangles[0].rect[1] = 70
            cancelButtons[0].pos[1] = 80
            rectangleText[0].pos[1] = 80

            for rect in rectangles:
                rect.rect[1] = 70*(rectangles.index(rect)+1)
                cancelButtons[rectangles.index(rect)].pos[1] -= rectHeight
                rectangleText[rectangles.index(rect)].pos[1] -= rectHeight
    except IndexError:
        pass

    render()

    if len(rectangles) == 0:
        newRectY = 70

    pygame.display.set_caption(newTitle)
    pygame.display.update()

if changed:
    if messagebox.askyesno("Save?", "Do you want to save?"):
       # pync.notify("Saved!", title="Task Manager")
        # saves the most recent data to the .json file
        add_info("rectangle_amount", len(rectangles))
        for stringText in rectangleText:
            add_info(str(rectangleText.index(stringText)+1), stringText.string)

        for rectangle in rectangles:
            add_info("rectangle" + str(rectangles.index(rectangle)) + "complete", rectangle.get_completed())

        add_info("title", newTitle)

        add_json_to_existing("./", "data", jsonData)

    root.destroy()

pygame.quit()
