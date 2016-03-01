#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, curses, traceback
import curses.textpad as textpad

class _Textbox(textpad.Textbox):
    """
    Textbox control refinements subclass.
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
            och=curses.KEY_BACKSPACE
        if ch == 360: # End
            och=562
        if ch == 262: # Home
            och=162
        self.lastKey = och
        return textpad.Textbox.do_command(self, och)

class widget(object):
    desc="widget"
    def __init__(self, name, y, x, label, parent):
        self.name=name
        self.posY=y
        self.posX=x
        self.label=label
        self.lastKey=0
        self.parent=parent
        self.win=parent.win
        #register self to parent
        self.parent.widgets[self.name]=self
        
    def printLabel(self):
        self.win.addstr(self.posY,self.posX, self.label)
        
class wButton(widget):
    def __init__(self, name, y, x, label, parent):
        super(self.__class__,self).__init__(name, y, x, label, parent) # Call the init method of the base class
        self.label=label
        type="x"
        self.__exit_keys=[curses.KEY_ENTER, 32, 27, 9, 10]
    
    def printField(self, attr=curses.A_NORMAL): 
        self.win.addstr(self.posY,self.posX , "[ ", attr)
        self.win.addstr(self.posY,self.posX + 2 + len(self.label) , " ]", attr)
        self.win.addstr(self.posY,self.posX + 2 , self.label, attr)
        
    def setFocus(self):
        curses.curs_set(0)
        self.win.move(self.posY,self.posX + 2)
        self.printField(curses.A_REVERSE)
        while True:
            c = self.win.getch()
            self.parent.callback(self, "keypress", c)
            self.lastKey = c
            if c in self.__exit_keys:
                self.printField()
                return 

class wTextBox(widget):
    def __init__(self, name, y, x, size, label, parent, default=""):
        super(self.__class__,self).__init__(name, y, x, label, parent) # Call the init method of the base class
        self.fieldSize=size
        self.default=default
        self.text=default
        if len(self.text) > self.fieldSize: self.text = self.text[:self.fieldSize]
        self.type="t"
        self.swin = self.win.subwin(1, self.fieldSize+1, self.posY,self.posX + 3 + len(self.label)) #nlines, ncols, begin_y, begin_x
        self.swin.addstr(0, 0, self.text)
        self.win.refresh()
        self.swin.refresh()
        
    def __validate(self, c):
        # self.win.addstr(9,1,str(c))
        # self.win.refresh()
        return c
        
    def printField(self):
        self.win.addstr(self.posY,self.posX + 2 + len(self.label), "[")
        self.win.addstr(self.posY,self.posX + 4 + len(self.label) + self.fieldSize, "]")
        
    def setFocus(self):
        curses.curs_set(1)
        self.swin.move(0,0)
        tb=_Textbox(self.swin, insert_mode=True)
        self.text=tb.edit(self.__validate)
        # self.win.addstr(10,1,self.text)
        # self.win.addstr(11,1,str(tb.lastKey))
        self.lastKey = tb.lastKey
        return #tb.lastKey

class window():
    def __init__(self, name, y1, x1, y2, x2, callback, label=""):
        from collections import OrderedDict
        self.name=name
        self.__callback = callback
        # self.screen=screen
        self.y1=y1
        self.x1=x1
        self.y2=y2
        self.x2=x2
        self.label=label
        self.widgets=OrderedDict()
        self.win = curses.newwin(y1, x1, y2, x2)#(23, 79, 0, 0)
        self.win.bkgd(' ', curses.color_pair(1))
        self.win.box()
        self.__signal=0

    def loop(self):
        self.__draw()
        focus=0
        while True:
            # screen.addstr(1,30, str(focus))
            # screen.addstr(2,30, widgets[focus].name)
            # self.win.refresh()
            iWidget=self.widgets.keys()[focus]
            self.widgets[iWidget].setFocus()
            lastkey=self.widgets[iWidget].lastKey
            # screen.addstr(3,30, str(lastkey))
            self.win.refresh()
            if self.__signal != 0 : break            
            focus=(focus+1) % len(self.widgets)
    
    def __draw(self):
        for w in self.widgets.keys():
            self.widgets[w].printLabel()
            self.widgets[w].printField()
        self.win.refresh()

    def signal(self, sig):
        self.__signal=sig

    def callback(self, obj, event, data):
        text = ",".join([obj.name, event, str(data)])
        self.win.addstr(15,1, text)
        self.win.refresh()
        self.__callback(obj, event, data)

def draw_screen(win):
    # win.addstr(2,1, "       Name [     ]")
    win.addstr(3,1, "   Student? [x]")
    win.addstr(4,1, "Choose File [...]")
    win.addstr(5,1, " Choose Asd [...|v]")
    win.addstr(6,1, "        Age [     ]")
    # win.addstr(8,1, "          [OK]")

def callback(obj, event, data):
    if obj.name=="b0":
        if data == 10: #enter
            print obj.parent.widgets["t0"].text
            print obj.parent.widgets["t1"].text
            obj.parent.signal(1)

def define_widgets(parent):
    widgets = []
    t0=wTextBox("t0", 2, 7, 10, "Name", parent, "12345678901")
    t1=wTextBox("t1", 9, 7, 10, "Surname", parent)
    b0=wButton("b0", 8, 10, "OK", parent)
    widgets.append(t0)
    widgets.append(t1)
    widgets.append(b0)
    return widgets
     
def main(stdscr):
    mwindow=window("main",0, 0, 0, 0, callback)
    win=mwindow.win
    # screen = curses.newwin(0, 0, 0, 0)#(23, 79, 0, 0)
    # screen.bkgd(' ', curses.color_pair(1))
    # screen.box()
    # draw_screen(win)
    widgets=define_widgets(mwindow)
    # win.addstr(1,30, str(mwindow.widgets))
    # for widget in widgets:
    mwindow.loop()

def init_curses():
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

def quit_curses(stdscr):
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()
            
if __name__ == '__main__':
    # curses.curs_set(visibility)
    # try:
        # Initialize curses
        stdscr, isColorTerm=init_curses()
        global widgets
        
        main(stdscr)                    # Enter the main loop
        # Set everything back to normal
        quit_curses(stdscr)
    # except:
        # In event of error, restore terminal to sane state.
        # stdscr.keypad(0)
        # curses.echo()
        # curses.nocbreak()
        # curses.endwin()
        # traceback.print_exc()           # Print the exception
    
