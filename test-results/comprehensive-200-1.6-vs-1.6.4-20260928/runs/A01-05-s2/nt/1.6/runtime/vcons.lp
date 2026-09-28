task(8, ncons(closed(X))) :- microwave(X).
task(9, ncons(near(X, Y))) :- can(X), yellow(X), desk(Y).
task(10, cons(plate(X))) :- can(X), white(X).
task(11, cons(plate(X))) :- book(X), blue(X).
task(12, cons(plate(X))) :- bottle(X), red(X).
task(13, cons(plate(X))) :- bottle(X), black(X).
task(14, cons(inside(X, Y))) :- bottle(X), red(X), cupboard(Y).
task(15, cons(near(X, Y))) :- bottle(X), red(X), human(Y).
task(16, cons(inside(X, Y))) :- can(X), white(X), cupboard(Y).
task(17, cons(near(X, Y))) :- can(X), white(X), human(Y).
task(18, cons(near(X, Y))) :- bottle(X), black(X), human(Y).
task(19, cons(inside(X, Y))) :- book(X), blue(X), closet(Y).
task(20, cons(near(X, Y))) :- book(X), blue(X), table(Y).
task(21, cons(near(X, Y))) :- bottle(X), red(X), table(Y).
task(22, cons(inside(X, Y))) :- can(X), white(X), closet(Y).
task(23, cons(inside(X, Y))) :- bottle(X), black(X), closet(Y).
task(24, cons(near(X, Y))) :- bottle(X), black(X), table(Y).
task(25, cons(inside(X, Y))) :- book(X), blue(X), microwave(Y).
task(26, cons(near(X, Y))) :- book(X), blue(X), desk(Y).
task(27, cons(inside(X, Y))) :- bottle(X), red(X), microwave(Y).
task(28, cons(inside(X, Y))) :- can(X), white(X), microwave(Y).
task(29, cons(near(X, Y))) :- can(X), white(X), desk(Y).
task(30, cons(inside(X, Y))) :- bottle(X), black(X), microwave(Y).
task(31, cons(near(X, Y))) :- bottle(X), black(X), desk(Y).
task(32, cons(inside(X, Y))) :- book(X), blue(X), refrigerator(Y).
task(33, cons(inside(X, Y))) :- bottle(X), red(X), refrigerator(Y).
task(34, cons(near(X, Y))) :- bottle(X), red(X), cupboard(Y).
task(35, cons(inside(X, Y))) :- can(X), white(X), refrigerator(Y).
task(36, cons(near(X, Y))) :- can(X), white(X), cupboard(Y).
task(37, cons(inside(X, Y))) :- bottle(X), black(X), refrigerator(Y).
task(38, cons(near(X, Y))) :- book(X), blue(X), closet(Y).
