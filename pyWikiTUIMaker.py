#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, curses, traceback
import curses.textpad as textpad

class widget(object):
    desc="widget"
    
    def __init__(self, name, win):
        self.name=name
        self.label=""
        self.posX=1
        self.posY=1
        self.win=win
        self.fieldSize=10
        self.win=win

    def printLabel(self):
        self.win.addstr(self.posY,self.posX, self.label)

    def moveTo(self, y, x):
        self.win.addstr(y,x,'')
        

class wTextBox(widget):
    
    def __init__(self, name, win):
        super(self.__class__,self).__init__(name, win) # Call the init method of the base class
        type="t"
         # stdscr.subwin(23, 79, 0, 0)

    def printField(self):
        self.win.addstr(self.posY,self.posX + 2 + len(self.label), "[")
        self.win.addstr(self.posY,self.posX + 2 + len(self.label) + self.fieldSize, "]")
        
    def getFocus(self):
        self.moveTo(self.posY,self.posX + 3 + len(self.label))
        text=textpad.Textbox(self.win, insert_mode=True).edit()
        curses.addstr(10,1,text.encode('utf_8'))
        

def init():
    stdscr=curses.initscr()
    isColorTerm=True
    # print curses.has_colors()
    # sys.exit()
    try:
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
        stdscr.bkgd(' ', curses.color_pair(1))
    except curses.error:
        print "color not available. set TERM=xterm-color"
        isColorTerm=False
    stdscr.keypad(1)
    curses.noecho()
    curses.cbreak()
    return stdscr,isColorTerm

def quit(stdscr):
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()

def draw_screen(win):
    # win.addstr(2,1, "       Name [     ]")
    win.addstr(3,1, "   Student? [x]")
    win.addstr(4,1, "Choose File [...]")
    win.addstr(5,1, " Choose Asd [...|v]")
    win.addstr(6,1, "        Age [     ]")
    win.addstr(8,1, "          [OK]")

def define_widgets(win):
    widgets = []
    t0=wTextBox("t0", win)
    t0.label="Name"
    t0.posY=2    
    t0.posX=7
    
    widgets.append(t0)
    return widgets
     
def main(stdscr):
    # Frame the interface area at fixed VT100 size
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.box()
    # screen.hline(2, 1, curses.ACS_HLINE, 77)
    draw_screen(screen)
    widgets=define_widgets(screen)
    for widget in widgets:
        widget.printLabel()
        widget.printField()
    widgets[0].getFocus()
    screen.refresh()
    while True:
        c = screen.getch()
        print c
        if c == ord("q"):
            break
            
if __name__ == '__main__':
    # curses.curs_set(visibility)
    # try:
        # Initialize curses
        stdscr, isColorTerm=init()
        global widgets
        
        main(stdscr)                    # Enter the main loop
        # Set everything back to normal
        quit(stdscr)
    # except:
        # In event of error, restore terminal to sane state.
        # stdscr.keypad(0)
        # curses.echo()
        # curses.nocbreak()
        # curses.endwin()
        # traceback.print_exc()           # Print the exception
    
