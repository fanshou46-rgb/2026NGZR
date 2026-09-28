task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- can(X), white(X).
task(10, cons(plate(X))) :- book(X), blue(X).
task(11, cons(plate(X))) :- bottle(X), red(X).
task(12, ncons(inside(X, Y))) :- cup(X), red(X), microwave(Y).
task(13, cons(near(X, Y))) :- cup(X), red(X), table(Y).
task(14, ncons(inside(X, Y))) :- book(X), white(X), microwave(Y).
task(15, cons(near(X, Y))) :- book(X), white(X), desk(Y).
task(16, cons(plate(X))) :- can(X), yellow(X).
task(17, cons(plate(X))) :- cup(X), red(X).
task(18, cons(plate(X))) :- book(X), white(X).
task(19, cons(inside(X, Y))) :- can(X), yellow(X), cupboard(Y).
task(20, cons(near(X, Y))) :- can(X), yellow(X), human(Y).
task(21, cons(inside(X, Y))) :- bottle(X), red(X), cupboard(Y).
task(22, cons(near(X, Y))) :- bottle(X), red(X), human(Y).
task(23, cons(inside(X, Y))) :- can(X), white(X), cupboard(Y).
task(24, cons(near(X, Y))) :- can(X), white(X), human(Y).
task(25, cons(inside(X, Y))) :- cup(X), red(X), cupboard(Y).
task(26, cons(near(X, Y))) :- cup(X), red(X), human(Y).
task(27, cons(inside(X, Y))) :- book(X), white(X), cupboard(Y).
task(28, cons(near(X, Y))) :- book(X), white(X), human(Y).
task(29, cons(inside(X, Y))) :- can(X), yellow(X), closet(Y).
task(30, cons(inside(X, Y))) :- book(X), blue(X), closet(Y).
task(31, cons(near(X, Y))) :- book(X), blue(X), table(Y).
task(32, cons(near(X, Y))) :- bottle(X), red(X), table(Y).
task(33, cons(inside(X, Y))) :- can(X), white(X), closet(Y).
task(34, cons(inside(X, Y))) :- cup(X), red(X), closet(Y).
task(35, cons(inside(X, Y))) :- book(X), white(X), closet(Y).
task(36, cons(near(X, Y))) :- book(X), white(X), table(Y).
task(37, cons(inside(X, Y))) :- can(X), yellow(X), microwave(Y).
