task(1, ncons(closed(X))) :- cupboard(X).
task(2, ncons(inside(X, Y))) :- cup(X), red(X), cupboard(Y), container(Y).
task(3, cons(near(X, Y))) :- cup(X), red(X), human(Y).
