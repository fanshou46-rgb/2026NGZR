task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- can(X), black(X).
task(10, cons(plate(X))) :- book(X), white(X).
task(11, cons(plate(X))) :- bottle(X), green(X).
task(12, ncons(inside(X, Y))) :- cup(X), green(X), microwave(Y).
task(13, cons(near(X, Y))) :- cup(X), green(X), table(Y).
task(14, ncons(inside(X, Y))) :- book(X), black(X), microwave(Y).
task(15, cons(near(X, Y))) :- book(X), black(X), desk(Y).
task(16, cons(plate(X))) :- can(X), red(X).
task(17, cons(plate(X))) :- cup(X), green(X).
task(18, cons(plate(X))) :- book(X), black(X).
task(19, cons(inside(X, Y))) :- can(X), red(X), cupboard(Y).
task(20, cons(near(X, Y))) :- can(X), red(X), human(Y).
task(21, cons(inside(X, Y))) :- bottle(X), green(X), cupboard(Y).
task(22, cons(near(X, Y))) :- bottle(X), green(X), human(Y).
task(23, cons(inside(X, Y))) :- can(X), black(X), cupboard(Y).
task(24, cons(near(X, Y))) :- can(X), black(X), human(Y).
task(25, cons(inside(X, Y))) :- cup(X), green(X), cupboard(Y).
task(26, cons(near(X, Y))) :- cup(X), green(X), human(Y).
task(27, cons(inside(X, Y))) :- book(X), black(X), cupboard(Y).
task(28, cons(near(X, Y))) :- book(X), black(X), human(Y).
task(29, cons(inside(X, Y))) :- can(X), red(X), closet(Y).
task(30, cons(inside(X, Y))) :- book(X), white(X), closet(Y).
task(31, cons(near(X, Y))) :- book(X), white(X), table(Y).
task(32, cons(near(X, Y))) :- bottle(X), green(X), table(Y).
task(33, cons(inside(X, Y))) :- can(X), black(X), closet(Y).
task(34, cons(inside(X, Y))) :- cup(X), green(X), closet(Y).
task(35, cons(inside(X, Y))) :- book(X), black(X), closet(Y).
task(36, cons(near(X, Y))) :- book(X), black(X), table(Y).
task(37, cons(inside(X, Y))) :- can(X), red(X), microwave(Y).
