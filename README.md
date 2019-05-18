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

This is when I decided to make a computer program
