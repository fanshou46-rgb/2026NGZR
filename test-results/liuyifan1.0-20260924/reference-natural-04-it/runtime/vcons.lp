task(1, ncons(inside(X, Y))) :- book(X), red(X), cupboard(Y), container(Y).
task(2, ncons(closed(X))) :- cupboard(X).
