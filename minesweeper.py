#!/usr/bin/env python

import math
import random
import re
import sys
import termios
import tty

class COLOR:
    END = '\033[0m'
    RED = '\033[0;31m'
    BLACK = '\033[0;30m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    BACK_RED = '\033[41m'
    BACK_GREEN = '\033[42m'
    BACK_YELLOW = '\033[43m'
    BACK_BLUE = '\033[44m'
    BACK_PURPLE = '\033[45m'
    BACK_CYAN = '\033[46m'

GUESS = 'g'

BLOCK = u"\u2588"
FLAG = u"\u2690"
INCORRECT_FLAG = 'i'

CURSOR = u"\u2592"
CURSOR_PRINTABLE = COLOR.PURPLE + CURSOR + COLOR.END

class Printable:
    def __init__(self, printable, color_without_cursor="", color_on_cursor=""):
        self.printable = printable
        self.color_without_cursor = color_without_cursor
        self.color_on_cursor = color_on_cursor

    def get_printable(self, is_cursor):
        _str = ""
        if is_cursor:
            _str += COLOR.BLACK + self.color_on_cursor
        else:
            _str += self.color_without_cursor

        if self.printable == BLOCK and is_cursor:
            _str += CURSOR_PRINTABLE
        elif self.printable == ' ' and is_cursor:
            _str = CURSOR_PRINTABLE
        else:
            _str += self.printable
            
        _str += COLOR.END
        return _str

    
PRINTABLES = {
    0: Printable(' ', '', ''),
    1: Printable('1', COLOR.BLUE, COLOR.BACK_BLUE),
    2: Printable('2', COLOR.GREEN, COLOR.BACK_GREEN),
    3: Printable('3', COLOR.RED, COLOR.BACK_RED),
    4: Printable('4', COLOR.PURPLE, COLOR.BACK_PURPLE),
    5: Printable('5', COLOR.YELLOW, COLOR.BACK_YELLOW),
    6: Printable('6', COLOR.CYAN, COLOR.BACK_CYAN),
    7: Printable('7', COLOR.CYAN, COLOR.BACK_CYAN),
    8: Printable('8', COLOR.CYAN, COLOR.BACK_CYAN),
    BLOCK: Printable(BLOCK, '', COLOR.BACK_PURPLE),
    FLAG: Printable(FLAG,
                    COLOR.BLACK + COLOR.BACK_YELLOW,
                    COLOR.BLACK + COLOR.BACK_PURPLE),
    'x': Printable('x', COLOR.BLACK + COLOR.BACK_RED, COLOR.BLACK + COLOR.BACK_RED),
    'i': Printable(FLAG, COLOR.BLACK + COLOR.BACK_BLUE, COLOR.BLACK + COLOR.BACK_BLUE),
}

def _read_keystroke(count=1):
    file_descriptor = sys.stdin.fileno()
    old_settings = termios.tcgetattr(file_descriptor)
    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(count)
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)
    return char

class Keys:
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    

def get_keystroke():
    _str = _read_keystroke()
    if _str == '\x1b':
        _str += _read_keystroke(2)
        
    if _str == '\x1b[A' or _str == 'k':
        return Keys.UP
    elif _str == '\x1b[B' or _str == 'j':
        return Keys.DOWN
    elif _str == '\x1b[C' or _str == 'l':
        return Keys.RIGHT
    elif _str == '\x1b[D' or _str == 'h':
        return Keys.LEFT
    elif _str == '\x03' or _str == '\x04':
        sys.exit()
    elif _str == '\r':
        return GUESS
    return _str

class Minesweeper(object):
    
    
    def __init__(self, rows, cols, difficulty):
        """Creates a minesweeper board, ensuring that the first guess is a box
        with no surrounding mines.
        """
        self.cursor_x = rows/2
        self.cursor_y = cols/2
        self.rows = rows
        self.cols = cols

        self._generate_board(rows, cols, difficulty)
        self.difficulty = difficulty
        self.viewable_board = list(list(
            BLOCK for x in range(self.cols)) for x in range(self.rows))

    def _generate_board(self, rows, cols, difficulty):
        """Helper to generate the board and calculate the appropriate values
        for the board.
        """
        self.rows = rows
        self.cols = cols
        self.board = board = list(list(
                False for x in range(cols)) for y in range(rows))
        self.values = values = list(list(
                -1 for x in range(cols)) for y in range(rows))

        self.flags_marked = 0
        self.num_mines = int(rows*cols*difficulty)
        if self.num_mines >= rows*cols/2:            
            self.num_mines = rows*cols/2
            
        for x in range(self.num_mines):
            box = self._random_box()
            while board[box[0]][box[1]]:
                box = self._random_box()
            board[box[0]][box[1]] = True
            
        for r in range(rows):
            for c in range(cols):
                if board[r][c]:
                    self.values[r][c] = 'x'
                else:
                    count = 0
                    if r > 0 and c > 0 and board[r-1][c-1]: count += 1
                    if r > 0 and board[r-1][c]: count += 1
                    if r > 0 and c < cols-1 and board[r-1][c+1]: count += 1
                    if c > 0 and board[r][c-1]: count += 1
                    if c < cols-1 and board[r][c+1]: count += 1
                    if r < rows-1 and c > 0 and board[r+1][c-1]: count += 1
                    if r < rows-1 and board[r+1][c]: count += 1
                    if r < rows-1 and c < cols-1 and board[r+1][c+1]: count += 1
                    self.values[r][c] = count

    def _random_box(self):
        """Select a random box in the grid"""
        return (random.randint(0, self.rows-1), random.randint(0, self.cols-1))

    def _print_board(self, data):
        """Helper method to print the visible board or the full answers"""
        
        print "  ", # len(log(board_size))
        for x in range(self.rows):
            tens_digit = int(x / 10)
            if tens_digit != 0:
                print tens_digit,
            else:
                print " ",
        print ""
        print "  ", # len(log(board_size))
        for x in range(self.rows):
            print x % 10,
        print ""

        y = 0
        for row in data:
            print str(y).rjust(2),
            x = 0
            for item in row:
                print '%s' %PRINTABLES[item].get_printable(
                    x is self.cursor_x and y is self.cursor_y),
                x += 1
            print y
            y += 1
            
        print "  ", # len(log(board_size))
        for x in range(self.rows):
            tens_digit = int(x / 10)
            if tens_digit != 0:
                print tens_digit,
            else:
                print x % 10,
        print ""
        print "  ", # len(log(board_size))
        for x in range(self.rows):
            tens_digit = int(x / 10)
            if tens_digit == 0:
                print " ",
            else:
                print x % 10,
        print ""
        
    def print_board(self):
        """Print what has been guessed by the user"""
        self._print_board(self.viewable_board)

    def corrected_board(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if (self.viewable_board[r][c] == FLAG and
                    self.values[r][c] != 'x'):
                    self.viewable_board[r][c] = INCORRECT_FLAG
        self.print_board()

    def _answers(self):
        self._print_board(self.values)

    def consistent(self):
        count = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col]:
                    count += 1
        return (count is self.num_mines, count, self.num_mines)

    def _validate(self, r, c):
        if r >= self.rows or r < 0 or c >= self.cols or c < 0:
            raise OutOfBoundsError

    def move_cursor(self, key):
        if key == Keys.LEFT and self.cursor_x != 0:
            self.cursor_x -= 1
        elif key == Keys.RIGHT and self.cursor_x != self.cols - 1:
            self.cursor_x += 1
        elif key == Keys.UP and self.cursor_y != 0:
            self.cursor_y -= 1
        elif key == Keys.DOWN and self.cursor_y != self.rows - 1:
            self.cursor_y += 1

    def guess(self, r, c):
        self._validate(r, c)
        if self.viewable_board[r][c] == FLAG:
            return
        if type(self.viewable_board[r][c]) is int:
            self.guess_surrounding(r,c)
            return
        
        value = self.values[r][c]
        self.viewable_board[r][c] = value
        
        if value is 0:
            self.guess_surrounding(r,c)
            
    def guess_on_cursor(self):
        self.guess(self.cursor_y, self.cursor_x)

    def first_guess(self):
        while self.values[self.cursor_y][self.cursor_x] is not 0 or self.values == 'x':
            self._generate_board(self.rows, self.cols, self.difficulty)
        self.guess(self.cursor_y, self.cursor_x)

    def guess_surrounding(self, r, c):
        self._validate(r, c)
        if type(self.viewable_board[r][c]) is not int:
            print ('You may only use the global-guessing function on boxes you '
                   'have unconvered')
            return
        rows = self.rows
        cols = self.cols
        if (r > 0 and c > 0 and 
            self.viewable_board[r-1][c-1] == BLOCK):
            self.viewable_board[r-1][c-1] = self.values[r-1][c-1]
            if self.values[r-1][c-1] is 0:
                self.guess_surrounding(r-1, c-1)
        if (r > 0 and
            self.viewable_board[r-1][c] == BLOCK):
            self.viewable_board[r-1][c] = self.values[r-1][c]
            if self.values[r-1][c] is 0:
                self.guess_surrounding(r-1, c)
        if (r > 0 and c < cols-1 and 
            self.viewable_board[r-1][c+1] == BLOCK):
            self.viewable_board[r-1][c+1] = self.values[r-1][c+1]
            if self.values[r-1][c+1] is 0:
                self.guess_surrounding(r-1, c+1)
        if (c > 0 and 
            self.viewable_board[r][c-1] == BLOCK):
            self.viewable_board[r][c-1] = self.values[r][c-1]
            if self.values[r][c-1] is 0:
                self.guess_surrounding(r, c-1)
        if (c < cols-1 and 
            self.viewable_board[r][c+1] == BLOCK):
            self.viewable_board[r][c+1] = self.values[r][c+1]
            if self.values[r][c+1] is 0:
                self.guess_surrounding(r, c+1)
        if (r < rows-1 and c > 0 and 
            self.viewable_board[r+1][c-1] == BLOCK):
            self.viewable_board[r+1][c-1] = self.values[r+1][c-1]
            if self.values[r+1][c-1] is 0:
                self.guess_surrounding(r+1, c-1)
        if (r < rows-1 and 
            self.viewable_board[r+1][c] == BLOCK):
            self.viewable_board[r+1][c] = self.values[r+1][c]
            if self.values[r+1][c] is 0:
                self.guess_surrounding(r+1, c)
        if (r < rows-1 and c < cols-1 and 
            self.viewable_board[r+1][c+1] == BLOCK):
            self.viewable_board[r+1][c+1] = self.values[r+1][c+1]
            if self.values[r+1][c+1] is 0:
                self.guess_surrounding(r+1, c+1)

    def guess_surrounding_on_cursor(self):
        self.guess_surrounding(self.cursor_y, self.cursor_x)

    def toggle_flag(self):
        col = self.cursor_x
        row = self.cursor_y
        if self.viewable_board[row][col] == BLOCK:
            self.viewable_board[row][col] = FLAG
            self.flags_marked += 1
        elif self.viewable_board[row][col] == FLAG:
            self.viewable_board[row][col] = BLOCK
            self.flags_marked -= 1

    def won(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if (self.viewable_board[r][c] == BLOCK and
                    self.values[r][c] != 'x'):
                    return False
                elif (self.viewable_board[r][c] == FLAG and
                      self.values[r][c] != 'x'):
                    return False
        return True

    def mines_left(self):
        return self.num_mines - self.flags_marked
                
    def lost(self):
        for row in self.viewable_board:
            for item in row:
                if item == 'x':
                    return True
        return False

class OutOfBoundsError(Exception):
    def __str__(self):
        return 'That spot is not on the board!'


def apply_ranges(list):
    more = []
    for item in list:
        if re.match(r'\d*-\d*', item):
            list.remove(item)
            pieces = item.split('-')
            r = None
            if pieces[0] < pieces[1]:
                r = range(int(pieces[0]), int(pieces[1])+1)
            else:
                r = range(int(pieces[1]), int(pieces[0])-1, -1)
            for num in r:
                more.append(str(num))
    list.extend(more)
    
if __name__ == '__main__':
    rows = int(raw_input( "How big of a board would you like to play with? "))
    difficulty = float(raw_input(
            'What percentage of the squares should be mines? '))
    
    m = Minesweeper(rows, rows, difficulty)
    m.print_board()

    has_guessed = False
    while not m.won() and not m.lost():
        key = get_keystroke()
        m.move_cursor(key)
        if (key == 'f' or key == 'x') and has_guessed:
            m.toggle_flag()
        elif key == GUESS:
            if has_guessed:
                m.guess_on_cursor()
            else:
                m.first_guess()
                has_guessed = True
        elif key == 's' and has_guessed:
            m.guess_surrounding_on_cursor()
        m.print_board()
        print ''

    print ''
    if m.won():
        m.print_board()
        print 'You won!'
    elif m.lost():
        m.corrected_board()
        print 'You lost!'
    else:
        print 'HUH?'
        
