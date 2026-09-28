task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- can(X), blue(X).
task(10, cons(plate(X))) :- book(X), black(X).
task(11, cons(plate(X))) :- bottle(X), yellow(X).
task(12, cons(plate(X))) :- can(X), green(X).
task(13, cons(plate(X))) :- cup(X), black(X).
task(14, cons(inside(X, Y))) :- can(X), green(X), cupboard(Y).
task(15, cons(near(X, Y))) :- can(X), green(X), human(Y).
task(16, cons(inside(X, Y))) :- cup(X), black(X), cupboard(Y).
task(17, cons(near(X, Y))) :- cup(X), black(X), human(Y).
task(18, cons(inside(X, Y))) :- can(X), blue(X), cupboard(Y).
task(19, cons(near(X, Y))) :- can(X), blue(X), human(Y).
task(20, cons(inside(X, Y))) :- can(X), green(X), closet(Y).
task(21, cons(inside(X, Y))) :- cup(X), black(X), closet(Y).
task(22, cons(inside(X, Y))) :- book(X), black(X), closet(Y).
task(23, cons(near(X, Y))) :- book(X), black(X), table(Y).
task(24, cons(inside(X, Y))) :- can(X), blue(X), closet(Y).
task(25, cons(inside(X, Y))) :- can(X), green(X), microwave(Y).
task(26, cons(inside(X, Y))) :- cup(X), black(X), microwave(Y).
task(27, cons(near(X, Y))) :- cup(X), black(X), desk(Y).
task(28, cons(inside(X, Y))) :- book(X), black(X), microwave(Y).
task(29, cons(near(X, Y))) :- book(X), black(X), desk(Y).
task(30, cons(inside(X, Y))) :- can(X), blue(X), microwave(Y).
task(31, cons(near(X, Y))) :- can(X), blue(X), desk(Y).
task(32, cons(inside(X, Y))) :- can(X), green(X), refrigerator(Y).
task(33, cons(near(X, Y))) :- can(X), green(X), cupboard(Y).
task(34, cons(inside(X, Y))) :- cup(X), black(X), refrigerator(Y).
task(35, cons(near(X, Y))) :- cup(X), black(X), cupboard(Y).
task(36, cons(inside(X, Y))) :- book(X), black(X), refrigerator(Y).
task(37, cons(inside(X, Y))) :- can(X), blue(X), refrigerator(Y).
task(38, cons(near(X, Y))) :- can(X), blue(X), cupboard(Y).
