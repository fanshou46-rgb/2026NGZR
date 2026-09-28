task(8, ncons(closed(X))) :- microwave(X).
task(9, cons(plate(X))) :- cup(X), green(X).
task(10, cons(plate(X))) :- book(X), green(X).
task(11, cons(plate(X))) :- bottle(X), black(X).
task(12, cons(inside(X, Y))) :- can(X), white(X), cupboard(Y).
task(13, cons(near(X, Y))) :- can(X), white(X), human(Y).
task(14, cons(inside(X, Y))) :- cup(X), green(X), cupboard(Y).
task(15, cons(near(X, Y))) :- cup(X), green(X), human(Y).
task(16, cons(inside(X, Y))) :- bottle(X), black(X), cupboard(Y).
task(17, cons(near(X, Y))) :- bottle(X), black(X), human(Y).
task(18, cons(inside(X, Y))) :- can(X), white(X), closet(Y).
task(19, cons(inside(X, Y))) :- cup(X), green(X), closet(Y).
task(20, cons(inside(X, Y))) :- book(X), green(X), closet(Y).
task(21, cons(near(X, Y))) :- book(X), green(X), table(Y).
task(22, cons(inside(X, Y))) :- can(X), white(X), microwave(Y).
task(23, cons(inside(X, Y))) :- cup(X), green(X), microwave(Y).
task(24, cons(inside(X, Y))) :- book(X), green(X), microwave(Y).
task(25, cons(near(X, Y))) :- book(X), green(X), desk(Y).
task(26, cons(inside(X, Y))) :- bottle(X), black(X), microwave(Y).
task(27, cons(near(X, Y))) :- bottle(X), black(X), desk(Y).
task(28, cons(inside(X, Y))) :- can(X), white(X), refrigerator(Y).
task(29, cons(near(X, Y))) :- can(X), white(X), cupboard(Y).
task(30, cons(inside(X, Y))) :- cup(X), green(X), refrigerator(Y).
task(31, cons(near(X, Y))) :- cup(X), green(X), cupboard(Y).
task(32, cons(inside(X, Y))) :- book(X), green(X), refrigerator(Y).
task(33, cons(inside(X, Y))) :- bottle(X), black(X), refrigerator(Y).
task(34, cons(near(X, Y))) :- bottle(X), black(X), cupboard(Y).
task(35, cons(near(X, Y))) :- can(X), white(X), closet(Y).
task(36, cons(near(X, Y))) :- cup(X), green(X), closet(Y).
task(37, cons(near(X, Y))) :- book(X), green(X), closet(Y).
task(38, cons(near(X, Y))) :- can(X), white(X), microwave(Y).
