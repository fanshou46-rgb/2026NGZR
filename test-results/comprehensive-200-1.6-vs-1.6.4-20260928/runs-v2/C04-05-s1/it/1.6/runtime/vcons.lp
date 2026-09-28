task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- book(X), blue(X).
task(10, cons(plate(X))) :- bottle(X), red(X).
task(11, cons(plate(X))) :- can(X), white(X).
task(12, cons(inside(X, Y))) :- can(X), yellow(X), cupboard(Y).
task(13, cons(near(X, Y))) :- can(X), yellow(X), human(Y).
task(14, cons(inside(X, Y))) :- cup(X), blue(X), cupboard(Y).
task(15, cons(near(X, Y))) :- cup(X), blue(X), human(Y).
task(16, cons(inside(X, Y))) :- bottle(X), red(X), cupboard(Y).
task(17, cons(near(X, Y))) :- bottle(X), red(X), human(Y).
task(18, cons(inside(X, Y))) :- can(X), white(X), cupboard(Y).
task(19, cons(near(X, Y))) :- can(X), white(X), human(Y).
task(20, cons(inside(X, Y))) :- can(X), yellow(X), closet(Y).
task(21, cons(inside(X, Y))) :- cup(X), blue(X), closet(Y).
task(22, cons(inside(X, Y))) :- book(X), blue(X), closet(Y).
task(23, cons(near(X, Y))) :- book(X), blue(X), table(Y).
task(24, cons(near(X, Y))) :- bottle(X), red(X), table(Y).
task(25, cons(inside(X, Y))) :- can(X), white(X), closet(Y).
task(26, cons(inside(X, Y))) :- can(X), yellow(X), microwave(Y).
task(27, cons(inside(X, Y))) :- cup(X), blue(X), microwave(Y).
task(28, cons(inside(X, Y))) :- book(X), blue(X), microwave(Y).
task(29, cons(near(X, Y))) :- book(X), blue(X), desk(Y).
task(30, cons(inside(X, Y))) :- bottle(X), red(X), microwave(Y).
task(31, cons(inside(X, Y))) :- can(X), white(X), microwave(Y).
task(32, cons(near(X, Y))) :- can(X), white(X), desk(Y).
task(33, cons(inside(X, Y))) :- can(X), yellow(X), refrigerator(Y).
task(34, cons(near(X, Y))) :- can(X), yellow(X), cupboard(Y).
task(35, cons(inside(X, Y))) :- cup(X), blue(X), refrigerator(Y).
task(36, cons(near(X, Y))) :- cup(X), blue(X), cupboard(Y).
task(37, cons(inside(X, Y))) :- book(X), blue(X), refrigerator(Y).
task(38, cons(inside(X, Y))) :- bottle(X), red(X), refrigerator(Y).
