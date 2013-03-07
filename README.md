Minesweeper
===========

To run, `./minesweeper`. Run `ln -s /path/to/minesweeper.py /usr/local/bin/minesweeper` to add it to your `PATH`

*Make sure zoom your terminal, it helps with viewing the entire board.*

Usually, .2 is a good setting for percent of bombs.

This is pretty raw, so if you find any bugs/have any requests, add the issue to Github. Also, feel free to make a pull request if you make changes that you think would be valuable to the project.

##Commands:
- # #: mark a box that you believe does not have a bomb. E.x. 12 14. You can also prefix this command with 'g' as in 'g 12 14'.
- 'f' prefix: Mark a box with a flag. E.x. 'f 12 14'
- 'u' prefix: Unmark a flagged box. E.x. 'u 12 14'
- 's' prefix: Shorthand to guess all surrounding boxes to the given box. E.x. 's 12 14' would guess 11 13, 11 14, 11 15, 12 13, 12 15, 13 13, 13 14, and 13 15.
  - This command can only be used on boxes that have already been marked as not having bombs. This is a safeguard so that you don't screw yourself over.

##Special Arguments:
- If instead of a number you pass a list in the following format (#,#,...#), all of those indeces will be used with the indeces of the other axis.
  - E.x. 'f (1,3,5) 2' will call 'f 1 2', 'f 3 2' and 'f 5 2'. Note that if both arguments are lists, then all permutations will be guessed. So 'u (1,3) (2,4)' will call 'u 1 2', 'u 1 4', 'u 3 2' and 'u 3 4'.
- In any location where you can use a number, you can also pass a range and all of those numbers will be used. E.x. 'f 3-8 2' will mark the entire column from indeces 3-8 inclusive with flags. Note that these may be used in tandem with both arguments to select a box-region. They may also be used in a list: 'f (2,4-8,10) 3' will mark the entire column from 2-10 except for 3 and 9.