30/Jan/2008 Finally a new RomiChess, Version P3k. Well it is about time! Anyway, I guess, 
that I thought too much about my abilities to get a large improvement from P3j that the 
delay was due to me trying to reach a little higher level.

I am going to be devoting my ever dwindling amount of free time to a new chess engine. It 
will not be named RomiChess as I wish to keep open the possibility, to continue development on this one.

The new usefull commands are:

learn_off -- will not save any learning data
learn_on  -- will save learning data
book_off  -- will not use learning data
book_on   -- will use learning data

For those that do not want any learning and/or book, just start RomiChess from the command line and then 
type 'learn_off' and/or 'book_off' and then 'quit'. The reason that 'quit' is needed is because Romi stores 
flags in the learn.dat file to block or enable learning or the use of it and 'quit' flushes the file system 
to make sure that the data goes to the disk. If the learn.dat file is deleted, Romi will create a new one 
with learning and the use of it enabled by default.

I hope that it was worth the wait!

