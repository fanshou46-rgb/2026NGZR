task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- can(X), white(X).
task(10, cons(plate(X))) :- book(X), blue(X).
task(11, cons(plate(X))) :- bottle(X), red(X).
task(12, cons(give(human, X))) :- bottle(X), red(X).
task(13, cons(puton(X, Y))) :- bottle(X), red(X), desk(Y).
task(14, cons(puton(X, Y))) :- bottle(X), red(X), cupboard(Y).
task(15, cons(puton(X, Y))) :- bottle(X), red(X), closet(Y).
task(16, cons(puton(X, Y))) :- bottle(X), red(X), microwave(Y).
task(17, cons(puton(X, Y))) :- bottle(X), red(X), refrigerator(Y).
task(18, cons(puton(X, Y))) :- bottle(X), red(X), sofa(Y).
task(19, cons(inside(X, Y))) :- can(X), yellow(X), cupboard(Y).
task(20, cons(inside(X, Y))) :- bottle(X), red(X), cupboard(Y).
task(21, cons(near(X, Y))) :- bottle(X), red(X), human(Y).
task(22, cons(inside(X, Y))) :- can(X), white(X), cupboard(Y).
task(23, cons(near(X, Y))) :- can(X), white(X), human(Y).
task(24, cons(inside(X, Y))) :- can(X), yellow(X), closet(Y).
task(25, cons(inside(X, Y))) :- book(X), blue(X), closet(Y).
task(26, cons(near(X, Y))) :- book(X), blue(X), table(Y).
task(27, cons(inside(X, Y))) :- bottle(X), red(X), closet(Y).
task(28, cons(inside(X, Y))) :- can(X), white(X), closet(Y).
task(29, cons(inside(X, Y))) :- can(X), yellow(X), microwave(Y).
task(30, cons(inside(X, Y))) :- book(X), blue(X), microwave(Y).
task(31, cons(near(X, Y))) :- book(X), blue(X), desk(Y).
task(32, cons(inside(X, Y))) :- bottle(X), red(X), microwave(Y).
task(33, cons(inside(X, Y))) :- can(X), white(X), microwave(Y).
task(34, cons(near(X, Y))) :- can(X), white(X), desk(Y).
task(35, cons(inside(X, Y))) :- can(X), yellow(X), refrigerator(Y).
task(36, cons(near(X, Y))) :- can(X), yellow(X), cupboard(Y).
task(37, cons(inside(X, Y))) :- book(X), blue(X), refrigerator(Y).
task(38, cons(inside(X, Y))) :- bottle(X), red(X), refrigerator(Y).
