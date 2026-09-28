task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- can(X), red(X).
task(10, cons(plate(X))) :- book(X), white(X).
task(11, cons(plate(X))) :- bottle(X), green(X).
task(12, cons(inside(X, Y))) :- can(X), red(X), cupboard(Y).
task(13, cons(near(X, Y))) :- can(X), red(X), human(Y).
task(14, cons(inside(X, Y))) :- cup(X), white(X), cupboard(Y).
task(15, cons(near(X, Y))) :- cup(X), white(X), human(Y).
task(16, cons(inside(X, Y))) :- bottle(X), green(X), cupboard(Y).
task(17, cons(near(X, Y))) :- bottle(X), green(X), human(Y).
task(18, cons(inside(X, Y))) :- can(X), red(X), closet(Y).
task(19, cons(inside(X, Y))) :- cup(X), white(X), closet(Y).
task(20, cons(inside(X, Y))) :- book(X), white(X), closet(Y).
task(21, cons(near(X, Y))) :- book(X), white(X), table(Y).
task(22, cons(near(X, Y))) :- bottle(X), green(X), table(Y).
task(23, cons(inside(X, Y))) :- can(X), red(X), microwave(Y).
task(24, cons(inside(X, Y))) :- cup(X), white(X), microwave(Y).
task(25, cons(inside(X, Y))) :- book(X), white(X), microwave(Y).
task(26, cons(near(X, Y))) :- book(X), white(X), desk(Y).
task(27, cons(inside(X, Y))) :- bottle(X), green(X), microwave(Y).
task(28, cons(inside(X, Y))) :- can(X), red(X), refrigerator(Y).
task(29, cons(near(X, Y))) :- can(X), red(X), cupboard(Y).
task(30, cons(inside(X, Y))) :- cup(X), white(X), refrigerator(Y).
task(31, cons(near(X, Y))) :- cup(X), white(X), cupboard(Y).
task(32, cons(inside(X, Y))) :- book(X), white(X), refrigerator(Y).
task(33, cons(inside(X, Y))) :- bottle(X), green(X), refrigerator(Y).
task(34, cons(near(X, Y))) :- bottle(X), green(X), cupboard(Y).
task(35, cons(near(X, Y))) :- can(X), red(X), closet(Y).
task(36, cons(near(X, Y))) :- cup(X), white(X), closet(Y).
task(37, cons(near(X, Y))) :- book(X), white(X), closet(Y).
task(38, cons(near(X, Y))) :- can(X), red(X), microwave(Y).
