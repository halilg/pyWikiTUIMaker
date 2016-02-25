#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, curses, traceback
import curses.textpad as textpad

class _Textbox(textpad.Textbox):
    """
    Class code taken from: http://nullege.com/codes/show/src%40p%40y%40pyaxo-HEAD%40examples%40axochat.py/85/curses.textpad.Textbox.do_command/python
    curses.textpad.Textbox requires users to ^g on completion, which is sort
    of annoying for an interactive chat client such as this, which typically only
    reuquires an enter. This subclass fixes this problem by signalling completion
    on Enter as well as ^g. Also, map <Backspace> key to ^h.
    """
    def __init__(*args, **kwargs):
        textpad.Textbox.__init__(*args, **kwargs)
        lastKey = 0
        
    def do_command(self, ch):
        och=ch
        if ch == 9: # tab
            self.lastKey = 9
            return 0
        if ch == 127: # Backspace
            # return curses.KEY_BACKSPACE
            och=curses.KEY_BACKSPACE
        if ch == 360: # End
            och=562
        if ch == 262: # Home
            och=162
        self.lastKey = och
        return textpad.Textbox.do_command(self, och)

class widget(object):
    desc="widget"
    
    def __init__(self, name, win):
        self.name=name
        self.label=""
        self.win=win
        self.lastKey=0

    def printLabel(self):
        self.win.addstr(self.posY,self.posX, self.label)
        
class wButton(widget):
    
    def __init__(self, name, win, y, x, label):
        super(self.__class__,self).__init__(name, win) # Call the init method of the base class
        self.posX=x
        self.posY=y
        self.label=label
        type="x"
        self.__exit_keys=[curses.KEY_ENTER, 32, 27, 9, 10]
    
    def printField(self):
        self.win.addstr(self.posY,self.posX , "[ ", curses.A_REVERSE)
        self.win.addstr(self.posY,self.posX + 2 + len(self.label) , " ]", curses.A_REVERSE)
        self.win.addstr(self.posY,self.posX + 2 , self.label, curses.A_REVERSE)
        
    def setFocus(self):
        self.win.move(self.posY,self.posX + 2)
        while True:
            c = self.win.getch()
            self.lastKey = c
            if c in self.__exit_keys:
                return 


class wTextBox(widget):
    
    def __init__(self, name, win, y, x, size, label):
        super(self.__class__,self).__init__(name, win) # Call the init method of the base class
        self.posX=x
        self.posY=y
        self.fieldSize=size
        self.label=label
        self.text=""
        type="t"
        self.swin = win.subwin(1, self.fieldSize+1, self.posY,self.posX + 3 + len(self.label)) #nlines, ncols, begin_y, begin_x
        # self.swin.bkgd(' ', curses.color_pair(1))
        self.win.refresh()
        self.swin.refresh()
        
    def __validate(self, c):
        self.win.addstr(9,1,str(c))
        self.win.refresh()
        return c
        
    def printField(self):
        self.win.addstr(self.posY,self.posX + 2 + len(self.label), "[")
        self.win.addstr(self.posY,self.posX + 4 + len(self.label) + self.fieldSize, "]")
        
    def setFocus(self):
        self.swin.move(0,0)#(self.posY,self.posX + 3 + len(self.label))
        tb=_Textbox(self.swin, insert_mode=True)
        self.text=tb.edit(self.__validate)
        # self.win.addstr(10,1,self.text)
        # self.win.addstr(11,1,str(tb.lastKey))
        self.lastKey = tb.lastKey
        return #tb.lastKey
        

def init():
    stdscr=curses.initscr()
    isColorTerm=True
    # print curses.has_colors()
    # sys.exit()
    curses.start_color() 
    try:
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
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
    # win.addstr(8,1, "          [OK]")

def define_widgets(win):
    widgets = []
    t0=wTextBox("t0", win, 2, 7, 10, "Name")
    t1=wTextBox("t1", win, 9, 7, 10, "Surname")
    b0=wButton("b0", win, 8, 10, "OK")
    widgets.append(t0)
    widgets.append(t1)
    widgets.append(b0)
    return widgets
     
def main(stdscr):
    # Frame the interface area at fixed VT100 size
    screen = stdscr.subwin(0, 0, 0, 0)#(23, 79, 0, 0)
    screen.box()
    # screen.hline(2, 1, curses.ACS_HLINE, 77)
    draw_screen(screen)
    widgets=define_widgets(screen)
    for widget in widgets:
        widget.printLabel()
        widget.printField()
        screen.refresh()
    
    focus=0
    while True:
        screen.addstr(1,30, str(focus))
        screen.addstr(2,30, widgets[focus].name)
        screen.refresh()
        widgets[focus].setFocus()
        lastkey=widgets[focus].lastKey
        screen.addstr(3,30, str(lastkey))
        screen.refresh()
        
        if widgets[focus].name=="b0":
            if lastkey == 10: #enter
                quit(stdscr)
                print widgets[0].text
                print widgets[1].text
                sys.exit()
        focus=(focus+1) % len(widgets)
            
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
    
