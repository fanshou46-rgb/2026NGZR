task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- can(X), yellow(X).
task(10, cons(plate(X))) :- book(X), green(X).
task(11, cons(plate(X))) :- bottle(X), black(X).
task(12, ncons(inside(X, Y))) :- cup(X), black(X), microwave(Y).
task(13, cons(near(X, Y))) :- cup(X), black(X), desk(Y).
task(14, ncons(inside(X, Y))) :- book(X), yellow(X), microwave(Y).
task(15, cons(near(X, Y))) :- book(X), yellow(X), table(Y).
task(16, cons(plate(X))) :- can(X), white(X).
task(17, cons(plate(X))) :- cup(X), black(X).
task(18, cons(plate(X))) :- book(X), yellow(X).
task(19, cons(inside(X, Y))) :- can(X), white(X), cupboard(Y).
task(20, cons(near(X, Y))) :- can(X), white(X), human(Y).
task(21, cons(inside(X, Y))) :- bottle(X), black(X), cupboard(Y).
task(22, cons(near(X, Y))) :- bottle(X), black(X), human(Y).
task(23, cons(inside(X, Y))) :- can(X), yellow(X), cupboard(Y).
task(24, cons(near(X, Y))) :- can(X), yellow(X), human(Y).
task(25, cons(inside(X, Y))) :- cup(X), black(X), cupboard(Y).
task(26, cons(near(X, Y))) :- cup(X), black(X), human(Y).
task(27, cons(inside(X, Y))) :- book(X), yellow(X), cupboard(Y).
task(28, cons(near(X, Y))) :- book(X), yellow(X), human(Y).
task(29, cons(inside(X, Y))) :- can(X), white(X), closet(Y).
task(30, cons(inside(X, Y))) :- book(X), green(X), closet(Y).
task(31, cons(near(X, Y))) :- book(X), green(X), table(Y).
task(32, cons(inside(X, Y))) :- can(X), yellow(X), closet(Y).
task(33, cons(near(X, Y))) :- can(X), yellow(X), table(Y).
task(34, cons(inside(X, Y))) :- cup(X), black(X), closet(Y).
task(35, cons(near(X, Y))) :- cup(X), black(X), table(Y).
task(36, cons(inside(X, Y))) :- book(X), yellow(X), closet(Y).
task(37, cons(inside(X, Y))) :- can(X), white(X), microwave(Y).
