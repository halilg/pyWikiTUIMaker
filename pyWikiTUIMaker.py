#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, curses, traceback
import curses.textpad as textpad

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
        self.__exit_keys=[curses.KEY_ENTER, 10]
        self.swin = self.win.subwin(1, len(self.label)+5, self.posY, self.posX) #nlines, ncols, begin_y, begin_x

    def printField(self, attr=curses.A_NORMAL): 
        self.swin.addstr(0, 0, "[ ", attr)
        self.swin.addstr(0, 2, self.label, attr)
        self.swin.addstr(0, len(self.label)+2 , " ]", attr)
        
        self.swin.refresh()
    
    def key_pressed(self, c):
        if c in self.__exit_keys:
            self.printField()
            self.parent.callback(self, "click", c)
    
    def lost_focus(self):
        self.printField(curses.A_NORMAL)
        
    def set_focus(self):
        curses.curs_set(0)
        # self.win.move(self.posY,self.posX + 2)
        self.printField(curses.A_REVERSE)
        self.swin.refresh()

class _Textbox(textpad.Textbox):
    """
    Textbox control refinements subclass.
    """
    def __init__(*args, **kwargs):
        textpad.Textbox.__init__(*args, **kwargs)
        
    def do_command(self, ch):
        och=ch
        if ch == 127: # Backspace
            och=curses.KEY_BACKSPACE
        if ch == 360: # End
            och=562
        if ch == 262: # Home
            och=162
        # if ch == 68: # Home
        #     och=0#curses.KEY_LEFT
        # if ch == 67: # Home
        #     och=0#curses.KEY_RIGHT
        return textpad.Textbox.do_command(self, och)
        
class wTextBox(widget):
    def __init__(self, name, y, x, size, label, parent, default=""):
        super(self.__class__,self).__init__(name, y, x, label, parent) # Call the init method of the base class
        self.fieldSize=size
        self.default=default
        self.text=default
        if len(self.text) > self.fieldSize: self.text = self.text[:self.fieldSize]
        self.type="t"
        # self.swin = self.win.subwin(1, self.fieldSize+1, self.posY, self.posX + 3 + len(self.label)) #nlines, ncols, begin_y, begin_x
        self.swin = curses.newpad(1, 1024) #nlines, ncols, begin_y, begin_x
        self.swin.addstr(0, 0, self.text)
        self.tb=_Textbox(self.swin) #, insert_mode=True

    def __refresh(self):
        self.swin.refresh(0, 0, self.posY, self.posX + 3 + len(self.label), self.posY, self.posX + len(self.label)+13)

    def key_pressed(self, ch):
        self.tb.do_command(ch)
        self.__refresh()
        
    def printField(self):
        self.win.addstr(self.posY,self.posX + 2 + len(self.label), "[")
        self.win.addstr(self.posY,self.posX + 4 + len(self.label) + self.fieldSize, "]")
        
    def getText(self):
        self.text=self.tb.gather()
        return self.text
    
    def lost_focus(self):
        self.text=self.tb.gather()
    
    def set_focus(self):
        # self.win.getch()
        curses.curs_set(1)
        # (y, x) = self.tb.getyx()
        # self.tb.win.move(0, 0)
        # self.swin.move(0,1)
        # self.key_pressed(562)
        self.__refresh()

class window():
    def __init__(self, name, y1, x1, y2, x2, callback, parent, label=""):
        from collections import OrderedDict
        self.name=name
        self.__callback = callback
        self.__parent = parent
        self.__parent.windows.append(self)
        # self.screen=screen
        # self.y1=y1
        # self.x1=x1
        # self.y2=y2
        # self.x2=x2
        self.label=label
        self.widgets=OrderedDict()
        self.win = curses.newwin(y1, x1, y2, x2)#(23, 79, 0, 0)
        self.win.bkgd(' ', curses.color_pair(1))
        self.win.box()
        self.__focus=0

    def signal(self, sig):
        self.__parent.signal(sig)
        
    def draw(self):
        for w in self.widgets.keys():
            self.widgets[w].printLabel()
            self.widgets[w].printField()
        # q=self.win.getch()
        self.widgets[self.widgets.keys()[self.__focus]].set_focus()
        # self.win.move(0,0)#refresh()

    def key_pressed(self, key):
        iWidget=self.widgets.keys()[self.__focus]
        if key == 9  : #tab, move focus to next widget
            self.widgets[iWidget].lost_focus()
            self.__focus=(self.__focus+1) % len(self.widgets)
            iWidget=self.widgets.keys()[self.__focus]
            self.widgets[iWidget].set_focus()
        else: #pass the keypress to widget
            self.widgets[iWidget].key_pressed(key)

    def callback(self, obj, event, data):
        text = ",".join([obj.name, event, str(data)])
        self.__callback(obj, event, data)

class cursesApp(object):
    def __init__(self, stdscr, callback):
        self.windows=[]
        self.callback = callback
        self.__screen = stdscr
        self.__signal = 0
        
    def signal(self, sig):
        self.__signal=sig

    def loop(self):
        cWin=self.windows[0]
        cWin.draw()
        curses.doupdate()
        while True:
            try:
                c = cWin.win.getch()
                # cWin.win.addstr(1,30, "         ")
                # cWin.win.addstr(1,30, str(focus))
                # cWin.win.refresh()
            except KeyboardInterrupt:
                self.__signal = 2
                break
            
            cWin.key_pressed(c)
            if self.__signal != 0 : break
            

def draw_screen(win):
    # win.addstr(2,1, "       Name [     ]")
    win.addstr(3,1, "   Student? [x]")
    win.addstr(4,1, "Choose File [...]")
    win.addstr(5,1, " Choose Asd [...|v]")
    win.addstr(6,1, "        Age [     ]")
    win.refresh()
    # win.addstr(8,1, "          [OK]")

def callback(obj, event, data):
    if obj.name=="b0":
        if event == "click": #enter
            print obj.parent.widgets["t0"].text
            print obj.parent.widgets["t1"].text
            obj.parent.signal(1)

def define_widgets(parent):
    t0=wTextBox("t0", 2, 7, 10, "Name", parent, "1234567890")
    t1=wTextBox("t1", 8, 7, 10, "Surname", parent)
    b0=wButton("b0", 10, 10, "OK", parent)
    

     
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
        
    app=cursesApp(stdscr, callback)
    
    mwindow=window("main",0, 0, 0, 0, callback, app)
    # win=mwindow.win
    
    # screen = curses.newwin(0, 0, 0, 0)#(23, 79, 0, 0)
    # screen.bkgd(' ', curses.color_pair(1))
    # screen.box()
    draw_screen(mwindow.win)
    define_widgets(mwindow)
    # win.addstr(1,30, str(mwindow.widgets))
    # for widget in widgets:
    app.loop()
    quit_curses(stdscr)
    # except:
        # In event of error, restore terminal to sane state.
        # stdscr.keypad(0)
        # curses.echo()
        # curses.nocbreak()
        # curses.endwin()
        # traceback.print_exc()           # Print the exception
    
