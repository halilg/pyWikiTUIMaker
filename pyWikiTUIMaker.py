#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, curses, traceback

class widget:
    tab_index=0
    label=""
    pos=(0,0)
    fpos=(0,0)
    type=""
    

def init():
    stdscr=curses.initscr()
    stdscr.keypad(1)
    curses.noecho()
    curses.cbreak()
    return stdscr

def quit(stdscr):
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()

def draw_screen(win):
    win.addstr(2,1, "       Name [     ]")
    win.addstr(3,1, "   Student? [x]")
    win.addstr(4,1, "Choose File [...]")
    win.addstr(5,1, " Choose Asd [...|v]")
    win.addstr(6,1, "        Age [     ]")
    win.addstr(8,1, "          [OK]")

def define_widgets():
    widgets = []
    w=widget()
     
def main(stdscr):
    # Frame the interface area at fixed VT100 size
    global screen
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.box()
    # screen.hline(2, 1, curses.ACS_HLINE, 77)
    draw_screen(screen)
    screen.refresh()
    while True:
        c = screen.getch()
        print c
        if c == ord("q"):
            break
            
if __name__ == '__main__':
    try:
        # Initialize curses
        stdscr=init()
        global widgets
        define_widgets()
        main(stdscr)                    # Enter the main loop
        # Set everything back to normal
        quit(stdscr)
    except:
        # In event of error, restore terminal to sane state.
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        traceback.print_exc()           # Print the exception
    
