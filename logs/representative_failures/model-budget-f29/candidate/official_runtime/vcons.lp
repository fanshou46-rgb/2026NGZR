task(8, ncons(closed(X))) :- microwave(X).
task(9, ncons(near(X, Y))) :- can(X), blue(X), table(Y).
task(10, cons(plate(X))) :- can(X), green(X).
task(11, cons(plate(X))) :- can(X), red(X).
task(12, cons(plate(X))) :- bottle(X), white(X).
task(13, cons(plate(X))) :- bottle(X), yellow(X).
task(14, cons(inside(X, Y))) :- can(X), red(X), cupboard(Y).
task(15, cons(inside(X, Y))) :- bottle(X), white(X), cupboard(Y).
task(16, cons(inside(X, Y))) :- can(X), green(X), cupboard(Y).
task(17, cons(inside(X, Y))) :- bottle(X), yellow(X), cupboard(Y).
task(18, cons(inside(X, Y))) :- can(X), red(X), closet(Y).
task(19, cons(inside(X, Y))) :- can(X), green(X), closet(Y).
task(20, cons(inside(X, Y))) :- bottle(X), yellow(X), closet(Y).
task(21, cons(inside(X, Y))) :- can(X), red(X), microwave(Y).
task(22, cons(inside(X, Y))) :- bottle(X), white(X), microwave(Y).
task(23, cons(inside(X, Y))) :- can(X), green(X), microwave(Y).
task(24, cons(inside(X, Y))) :- bottle(X), yellow(X), microwave(Y).
task(25, cons(inside(X, Y))) :- can(X), red(X), refrigerator(Y).
task(26, cons(inside(X, Y))) :- bottle(X), white(X), refrigerator(Y).
task(27, cons(inside(X, Y))) :- can(X), green(X), refrigerator(Y).
task(28, cons(near(X, Y))) :- bottle(X), white(X), human(Y).
task(29, cons(near(X, Y))) :- can(X), green(X), human(Y).
task(30, cons(near(X, Y))) :- bottle(X), yellow(X), human(Y).
task(31, cons(near(X, Y))) :- can(X), red(X), table(Y).
task(32, cons(near(X, Y))) :- can(X), green(X), table(Y).
task(33, cons(near(X, Y))) :- bottle(X), yellow(X), table(Y).
task(34, cons(near(X, Y))) :- bottle(X), white(X), desk(Y).
task(35, cons(near(X, Y))) :- bottle(X), yellow(X), desk(Y).
task(36, cons(near(X, Y))) :- can(X), red(X), cupboard(Y).
task(37, cons(near(X, Y))) :- bottle(X), white(X), cupboard(Y).
