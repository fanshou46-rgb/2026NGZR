task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- can(X), red(X).
task(10, cons(plate(X))) :- book(X), yellow(X).
task(11, cons(plate(X))) :- bottle(X), blue(X).
task(12, cons(plate(X))) :- can(X), black(X).
task(13, cons(plate(X))) :- cup(X), yellow(X).
task(14, cons(inside(X, Y))) :- can(X), black(X), cupboard(Y).
task(15, cons(near(X, Y))) :- can(X), black(X), human(Y).
task(16, cons(inside(X, Y))) :- cup(X), yellow(X), cupboard(Y).
task(17, cons(near(X, Y))) :- cup(X), yellow(X), human(Y).
task(18, cons(inside(X, Y))) :- can(X), red(X), cupboard(Y).
task(19, cons(near(X, Y))) :- can(X), red(X), human(Y).
task(20, cons(inside(X, Y))) :- can(X), black(X), closet(Y).
task(21, cons(inside(X, Y))) :- cup(X), yellow(X), closet(Y).
task(22, cons(near(X, Y))) :- cup(X), yellow(X), table(Y).
task(23, cons(inside(X, Y))) :- book(X), yellow(X), closet(Y).
task(24, cons(near(X, Y))) :- book(X), yellow(X), table(Y).
task(25, cons(inside(X, Y))) :- can(X), red(X), closet(Y).
task(26, cons(near(X, Y))) :- can(X), red(X), table(Y).
task(27, cons(inside(X, Y))) :- can(X), black(X), microwave(Y).
task(28, cons(inside(X, Y))) :- cup(X), yellow(X), microwave(Y).
task(29, cons(inside(X, Y))) :- book(X), yellow(X), microwave(Y).
task(30, cons(near(X, Y))) :- book(X), yellow(X), desk(Y).
task(31, cons(inside(X, Y))) :- can(X), red(X), microwave(Y).
task(32, cons(inside(X, Y))) :- can(X), black(X), refrigerator(Y).
task(33, cons(near(X, Y))) :- can(X), black(X), cupboard(Y).
task(34, cons(inside(X, Y))) :- cup(X), yellow(X), refrigerator(Y).
task(35, cons(near(X, Y))) :- cup(X), yellow(X), cupboard(Y).
task(36, cons(inside(X, Y))) :- book(X), yellow(X), refrigerator(Y).
task(37, cons(inside(X, Y))) :- can(X), red(X), refrigerator(Y).
task(38, cons(near(X, Y))) :- can(X), red(X), cupboard(Y).
