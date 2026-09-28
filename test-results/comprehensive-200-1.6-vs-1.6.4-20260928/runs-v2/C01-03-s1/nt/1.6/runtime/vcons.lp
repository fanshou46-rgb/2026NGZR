task(8, ncons(closed(X))) :- microwave(X).
task(9, ncons(near(X, Y))) :- bottle(X), red(X), sofa(Y).
task(10, cons(plate(X))) :- cup(X), green(X).
task(11, cons(plate(X))) :- book(X), green(X).
task(12, cons(plate(X))) :- bottle(X), black(X).
task(13, cons(inside(X, Y))) :- can(X), white(X), cupboard(Y).
task(14, cons(near(X, Y))) :- can(X), white(X), human(Y).
task(15, cons(inside(X, Y))) :- cup(X), green(X), cupboard(Y).
task(16, cons(near(X, Y))) :- cup(X), green(X), human(Y).
task(17, cons(inside(X, Y))) :- bottle(X), black(X), cupboard(Y).
task(18, cons(near(X, Y))) :- bottle(X), black(X), human(Y).
task(19, cons(inside(X, Y))) :- can(X), white(X), closet(Y).
task(20, cons(inside(X, Y))) :- cup(X), green(X), closet(Y).
task(21, cons(inside(X, Y))) :- book(X), green(X), closet(Y).
task(22, cons(near(X, Y))) :- book(X), green(X), table(Y).
task(23, cons(inside(X, Y))) :- can(X), white(X), microwave(Y).
task(24, cons(inside(X, Y))) :- cup(X), green(X), microwave(Y).
task(25, cons(inside(X, Y))) :- book(X), green(X), microwave(Y).
task(26, cons(near(X, Y))) :- book(X), green(X), desk(Y).
task(27, cons(inside(X, Y))) :- bottle(X), black(X), microwave(Y).
task(28, cons(near(X, Y))) :- bottle(X), black(X), desk(Y).
task(29, cons(inside(X, Y))) :- can(X), white(X), refrigerator(Y).
task(30, cons(near(X, Y))) :- can(X), white(X), cupboard(Y).
task(31, cons(inside(X, Y))) :- cup(X), green(X), refrigerator(Y).
task(32, cons(near(X, Y))) :- cup(X), green(X), cupboard(Y).
task(33, cons(inside(X, Y))) :- book(X), green(X), refrigerator(Y).
task(34, cons(inside(X, Y))) :- bottle(X), black(X), refrigerator(Y).
task(35, cons(near(X, Y))) :- bottle(X), black(X), cupboard(Y).
task(36, cons(near(X, Y))) :- can(X), white(X), closet(Y).
task(37, cons(near(X, Y))) :- cup(X), green(X), closet(Y).
task(38, cons(near(X, Y))) :- book(X), green(X), closet(Y).
