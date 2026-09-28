task(8, ncons(closed(X))) :- microwave(X).
task(9, ncons(near(X, Y))) :- can(X), black(X), table(Y).
task(10, cons(plate(X))) :- can(X), red(X).
task(11, cons(plate(X))) :- book(X), yellow(X).
task(12, cons(plate(X))) :- bottle(X), blue(X).
task(13, cons(inside(X, Y))) :- bottle(X), blue(X), cupboard(Y).
task(14, cons(near(X, Y))) :- bottle(X), blue(X), human(Y).
task(15, cons(inside(X, Y))) :- can(X), red(X), cupboard(Y).
task(16, cons(inside(X, Y))) :- book(X), yellow(X), closet(Y).
task(17, cons(near(X, Y))) :- book(X), yellow(X), table(Y).
task(18, cons(inside(X, Y))) :- can(X), red(X), closet(Y).
task(19, cons(near(X, Y))) :- can(X), red(X), table(Y).
task(20, cons(inside(X, Y))) :- book(X), yellow(X), microwave(Y).
task(21, cons(near(X, Y))) :- book(X), yellow(X), desk(Y).
task(22, cons(inside(X, Y))) :- bottle(X), blue(X), microwave(Y).
task(23, cons(near(X, Y))) :- bottle(X), blue(X), desk(Y).
task(24, cons(inside(X, Y))) :- can(X), red(X), microwave(Y).
task(25, cons(inside(X, Y))) :- book(X), yellow(X), refrigerator(Y).
task(26, cons(inside(X, Y))) :- bottle(X), blue(X), refrigerator(Y).
task(27, cons(near(X, Y))) :- bottle(X), blue(X), cupboard(Y).
task(28, cons(inside(X, Y))) :- can(X), red(X), refrigerator(Y).
task(29, cons(near(X, Y))) :- can(X), red(X), cupboard(Y).
task(30, cons(near(X, Y))) :- book(X), yellow(X), closet(Y).
task(31, cons(near(X, Y))) :- can(X), red(X), closet(Y).
task(32, cons(near(X, Y))) :- book(X), yellow(X), microwave(Y).
task(33, cons(near(X, Y))) :- bottle(X), blue(X), microwave(Y).
task(34, cons(near(X, Y))) :- can(X), red(X), microwave(Y).
task(35, cons(near(X, Y))) :- book(X), yellow(X), refrigerator(Y).
task(36, cons(near(X, Y))) :- bottle(X), blue(X), refrigerator(Y).
task(37, cons(near(X, Y))) :- can(X), red(X), refrigerator(Y).
task(38, cons(near(X, Y))) :- book(X), yellow(X), sofa(Y).
