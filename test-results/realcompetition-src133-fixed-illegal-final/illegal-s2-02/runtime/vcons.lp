task(2, cons(inside(X, Y))) :- cup(X), red(X), closet(Y), container(Y).
task(3, cons(inside(X, Y))) :- container(Y), closet(Y), red(X), cup(X).
