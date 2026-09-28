task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- can(X), red(X).
task(10, cons(plate(X))) :- book(X), yellow(X).
task(11, cons(plate(X))) :- bottle(X), blue(X).
task(12, cons(give(human, X))) :- bottle(X), blue(X).
task(13, cons(puton(X, Y))) :- bottle(X), blue(X), table(Y).
task(14, cons(puton(X, Y))) :- bottle(X), blue(X), cupboard(Y).
task(15, cons(puton(X, Y))) :- bottle(X), blue(X), closet(Y).
task(16, cons(puton(X, Y))) :- bottle(X), blue(X), microwave(Y).
task(17, cons(puton(X, Y))) :- bottle(X), blue(X), refrigerator(Y).
task(18, cons(puton(X, Y))) :- bottle(X), blue(X), sofa(Y).
task(19, cons(inside(X, Y))) :- can(X), black(X), cupboard(Y).
task(20, cons(inside(X, Y))) :- bottle(X), blue(X), cupboard(Y).
task(21, cons(near(X, Y))) :- bottle(X), blue(X), human(Y).
task(22, cons(inside(X, Y))) :- can(X), red(X), cupboard(Y).
task(23, cons(near(X, Y))) :- can(X), red(X), human(Y).
task(24, cons(inside(X, Y))) :- can(X), black(X), closet(Y).
task(25, cons(inside(X, Y))) :- book(X), yellow(X), closet(Y).
task(26, cons(near(X, Y))) :- book(X), yellow(X), table(Y).
task(27, cons(inside(X, Y))) :- bottle(X), blue(X), closet(Y).
task(28, cons(inside(X, Y))) :- can(X), red(X), closet(Y).
task(29, cons(near(X, Y))) :- can(X), red(X), table(Y).
task(30, cons(inside(X, Y))) :- can(X), black(X), microwave(Y).
task(31, cons(inside(X, Y))) :- book(X), yellow(X), microwave(Y).
task(32, cons(near(X, Y))) :- book(X), yellow(X), desk(Y).
task(33, cons(inside(X, Y))) :- bottle(X), blue(X), microwave(Y).
task(34, cons(inside(X, Y))) :- can(X), red(X), microwave(Y).
task(35, cons(inside(X, Y))) :- can(X), black(X), refrigerator(Y).
task(36, cons(near(X, Y))) :- can(X), black(X), cupboard(Y).
task(37, cons(inside(X, Y))) :- book(X), yellow(X), refrigerator(Y).
task(38, cons(inside(X, Y))) :- bottle(X), blue(X), refrigerator(Y).
