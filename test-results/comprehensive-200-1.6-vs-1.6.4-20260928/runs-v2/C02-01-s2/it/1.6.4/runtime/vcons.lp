task(8, ncons(closed(X))) :- microwave(X).
task(9, ncons(near(X, Y))) :- can(X), red(X), desk(Y).
task(10, cons(plate(X))) :- can(X), black(X).
task(11, cons(plate(X))) :- book(X), white(X).
task(12, cons(plate(X))) :- bottle(X), green(X).
task(13, ncons(closed(X))) :- closet(X).
task(14, cons(inside(X, Y))) :- bottle(X), green(X), cupboard(Y).
task(15, cons(near(X, Y))) :- bottle(X), green(X), human(Y).
task(16, cons(inside(X, Y))) :- can(X), black(X), cupboard(Y).
task(17, cons(near(X, Y))) :- can(X), black(X), human(Y).
task(18, cons(inside(X, Y))) :- book(X), white(X), closet(Y).
task(19, cons(near(X, Y))) :- book(X), white(X), table(Y).
task(20, cons(inside(X, Y))) :- bottle(X), green(X), closet(Y).
task(21, cons(near(X, Y))) :- bottle(X), green(X), table(Y).
task(22, cons(inside(X, Y))) :- can(X), black(X), closet(Y).
task(23, cons(inside(X, Y))) :- book(X), white(X), microwave(Y).
task(24, cons(near(X, Y))) :- book(X), white(X), desk(Y).
task(25, cons(inside(X, Y))) :- bottle(X), green(X), microwave(Y).
task(26, cons(inside(X, Y))) :- can(X), black(X), microwave(Y).
task(27, cons(near(X, Y))) :- can(X), black(X), desk(Y).
task(28, cons(inside(X, Y))) :- book(X), white(X), refrigerator(Y).
task(29, cons(near(X, Y))) :- bottle(X), green(X), cupboard(Y).
task(30, cons(inside(X, Y))) :- can(X), black(X), refrigerator(Y).
task(31, cons(near(X, Y))) :- can(X), black(X), cupboard(Y).
task(32, cons(near(X, Y))) :- book(X), white(X), closet(Y).
task(33, cons(near(X, Y))) :- bottle(X), green(X), closet(Y).
task(34, cons(near(X, Y))) :- can(X), black(X), closet(Y).
task(35, cons(near(X, Y))) :- book(X), white(X), microwave(Y).
task(36, cons(near(X, Y))) :- bottle(X), green(X), microwave(Y).
task(37, cons(near(X, Y))) :- can(X), black(X), microwave(Y).
task(38, cons(near(X, Y))) :- book(X), white(X), refrigerator(Y).
