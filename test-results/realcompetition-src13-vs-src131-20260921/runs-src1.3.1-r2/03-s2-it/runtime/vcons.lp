task(1, ncons(near(X, Y))) :- cup(X), green(X), cup(Y), black(Y).
task(2, ncons(near(X, Y))) :- can(X), red(X), cup(Y), black(Y).
task(3, ncons(near(X, Y))) :- bottle(X), blue(X), cup(Y), black(Y).
task(4, ncons(near(X, Y))) :- remotecontrol(X), yellow(X), cup(Y), black(Y).
task(5, ncons(near(X, Y))) :- book(X), white(X), cup(Y), black(Y).
task(6, ncons(near(X, Y))) :- can(X), blue(X), cup(Y), black(Y).
task(7, cons(near(X, Y))) :- can(X), blue(X), table(Y).
task(8, cons(near(X, Y))) :- book(X), white(X), table(Y).
task(9, cons(near(X, Y))) :- bottle(X), blue(X), couch(Y).
task(10, cons(near(X, Y))) :- can(X), red(X), chair(Y).
task(11, cons(near(X, Y))) :- cup(X), green(X), teapoy(Y).
task(12, cons(goto(X))) :- table(X).
task(13, cons(goto(X))) :- chair(X).
task(14, cons(goto(X))) :- couch(X).
task(15, cons(goto(X))) :- teapoy(X).
