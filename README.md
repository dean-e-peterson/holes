# Holes
_Find solutions for a problem no one cares about_

## How did you come up with this problem, and Why is this called holes?

Years ago (yes, it's a prose info-dump as story format readme, you may want to bail out now).  Anyway, years ago, I was at a restaurant playing around drawing circles.  Since I didn't have a compass, I poked holes in a bookmark, put a pen through one hole to anchor the center, and put another pen in the other hole to draw the circle.  Here is an artists impression of the bookmark:
```
.      .
```

I wanted circles of different sizes, so I poked multiple holes at regular intervals.  Here is a bookmark allowing circles radius 1 through 5, with an extra hole for the center.
```
. . . . . .
```

I realized that I did not need holes at every interval.  Instead, I could put holes every 5 intervals, but have 5 holes at single intervals at the end.  Now, by picking the correct holes to put the pen through, I could draw circles radius 1 through 20.
```
. . . . . .         .         .         .
```

This got me to thinking.  What is the minimum number of holes needed to draw circles radius 1 up to a given size, with no intervals missing?  How would the holes need to be arranged?  Here is an arrangement of 4 holes that lets you draw circles of any radius 1 through 6.
```
. .     .   .
```

I came up with patterns for larger radii, but how could I be sure I had found the most optimal pattern?  I tried but failed to come up with a procedure that would guarentee an optimal pattern with the fewest number of holes to measure the given radii.

## Enter the computer

This is when I decided to make a computer program, which I called `holey.py`.  It basically searches the possible permutations of hole locations with only 2 holes, then with only 3 holes, then only 4 holes, etc. until it finds a solution that lets you measure radii of 1 through a length you specify on the command line.Once it finds a solution at a given number of holes, it continues to search for alternate permutations that also measure 1 through the length, but only with that same number of holes.  When it exhausts the permutations for that number of holes, it finishes.  Because it searches all relevant permutations, and because it starts searching with 2, then 3, etc holes, it should be guarenteed to always find optimal solutions--that is, solutions that have holes spaced apart by every measurement from 1 to a given length, using the minimum number of holes for that length.

Here is a run showing that radii 1 through 9 can be measured with 5 holes.  Timing information at the end of the run is omitted for brevity.  Note that the second two solutions are the same as the first two solutions but reversed:
```
holey.py 9

            0         5        10
            | ' ' ' ' | ' ' ' ' |

   9 / 5    . . .       .     .      (0, 1, 2, 6, 9)
   9 / 5    . .     .     .   .      (0, 1, 4, 7, 9)
   9 / 5    .   .     .     . .      (0, 2, 5, 8, 9)
   9 / 5    .     .       . . .      (0, 3, 7, 8, 9)
...
```

## Performance Optimization

Because this project involves checking permutations, which grow factorially, it turned out to be a great project for me to practice performance profiling, optimization, and periodic progress logging.

With the help of the O'Reilly book _High Performance Python: Practical Performant Programming for Humans_, by Micha Gorelick and Ian Ozsvald, I improved the original performance significantly.  (I don't have exact numbers, or if I do, they are buried in log files of run completions.)  Here is a run for length 23:

```
D:\src\holes> holey.py 23

            0         5        10        15        20        25
            | ' ' ' ' | ' ' ' ' | ' ' ' ' | ' ' ' ' | ' ' ' ' |

  23 / 8    . . .                 .       .     .     .   .      (0, 1, 2, 11, 15, 18, 21, 23)
  23 / 8    . .     .           .           .   .     .   .      (0, 1, 4, 10, 16, 18, 21, 23)
  23 / 8    .   .     .   .           .           .     . .      (0, 2, 5, 7, 13, 19, 22, 23)
  23 / 8    .   .     .     .       .                 . . .      (0, 2, 5, 8, 12, 21, 22, 23)
```

In the process of optimizing holey.py, I wrote multiple implementations, and instead of discarding them, I assigned them to command-line parameters so I could continue to compare them (and because I was too chicken to eliminate something that was working too soon.)  Here is the holey.py usage help.  Note that the best optimization requires a working installation of numpy:

```
 holey.py -h
usage: holey.py [-h] [-b | -i | -o | -n] [-d] [--version] [-t] [-m MESSAGE]
                length

Find sets of dots that include dot pairs all integer distances apart, from 1
through n. The dots could represent the minimum number of tick marks on a
straightedge or holes in a template that could measure all distances <= n.

positional arguments:
  length      Show best dot combos for this length.

optional arguments:
  -h, --help  show this help message and exit
  -b          Use bitwise operation implementation (the default).
  -i          Use iterator-based implementation.
  -o          Use old, non-class-based iterator implementation.
  -n          Use bitwise implementation with numpy.
  -d          Enable additional debug logging.
  --version   show program's version number and exit
  -t          Show best combos for all lengths 1 thru given length.
  -m MESSAGE  Optional user message, unused but logged in logfile.
```

## Question for any mathematicians out there

Is there a name for this kind of calculation?  I wonder if I'm missing a deterministic, non-brute-force algorithm to find an optimal solution, but I don't even know what to search for.  If you know, please contact me at dean.e.penguin@gmail.com.  Thank you.

