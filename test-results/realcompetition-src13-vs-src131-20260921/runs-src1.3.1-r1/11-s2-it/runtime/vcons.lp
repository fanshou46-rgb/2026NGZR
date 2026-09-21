task(6, cons(goto(X))) :- can(X), blue(X).
task(7, cons(goto(X))) :- bottle(X), white(X).
task(8, cons(goto(X))) :- bottle(X), green(X).
task(9, cons(goto(X))) :- sofa(X).
task(10, cons(goto(X))) :- chair(X).
task(11, cons(goto(X))) :- human(X).
task(23, ncons(near(X, Y))) :- can(X), blue(X), sofa(Y).
task(24, ncons(near(X, Y))) :- can(X), green(X), desk(Y).
task(25, ncons(near(X, Y))) :- bottle(X), blue(X), bottle(Y), green(Y).
