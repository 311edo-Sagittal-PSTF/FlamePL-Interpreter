Hi everyone, I’m Stephen Ignatius Abel, You can also call me Sagit Achylychyli or Sagit 8:10:12:15. I'm the creator of FlamePL and the author of its interpreter.

From August 24, 2026 to now, FlamePL has already gone through updates from version 1.0 to 1.4. Today, FlamePL is a complete system, with its own standard library, a syntax based on Python but unique in its own way, and an official documentation — [right here](https://esolangs.org/wiki/FlamePL).

Here’s the changelog for this programming language:

1.0: I created this language and wrote a bug-ridden interpreter.
1.0f: I patched up the interpreter.
1.1α: I added the modulo operation.
1.1β: I added the for loop.
1.2: I added the language’s first standard library — Math.
1.3: I added more standard libraries.
1.4: I added self-evaluating and self-executing functions and added an REPL like Python.

This language has also been criticized for being too similar to R, but that’s not the point — every programming language has its meaning. For example, FlamePL actually serves higher-precision or even pure decimal computations. If this language really seems too similar to R, maybe it’s just a coincidence, but during its creation, I did draw inspiration from R, or even earlier, APL — you can see that from the left arrow.

This language is obviously not suited for golfing — after all, `i<-1` can only be distinguished as either assigning 1 to i or checking if i is less than -1 based on context. That’s the biggest taboo in code golf.

Actually, in the interpreter I declared that `<-` is a symbol and `(-1)` is an expression, so if you really want to mash these together, you can try using `i<(-1)` for comparison and `i<-1` for assignment.

This language wasn’t created for binary computation either — you can tell from my introduction of the Decimal standard library in the interpreter, and the lack of anything about bitwise operations in the language specification.

Anyway, when I built the environment for this language with my own hands, I felt really good — even though debugging is annoying.

To run this interpreter, all you need is a Python environment and a few FlamePL programs, that’s it.

Alright, that’s all I wanted to say. Have fun. :)
