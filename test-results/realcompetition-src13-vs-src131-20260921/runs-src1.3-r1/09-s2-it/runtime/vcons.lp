task(3, cons(near(X, Y))) :- remotecontrol(X), black(X), bottle(Y), black(Y).
task(4, cons(near(X, Y))) :- remotecontrol(X), black(X), cup(Y), black(Y).
task(5, cons(near(X, Y))) :- remotecontrol(X), black(X), book(Y), yellow(Y).
task(6, cons(near(X, Y))) :- remotecontrol(X), black(X), can(Y), green(Y).
task(7, cons(near(X, Y))) :- remotecontrol(X), black(X), can(Y), yellow(Y).
task(8, cons(near(X, Y))) :- remotecontrol(X), black(X), remotecontrol(Y), yellow(Y).
task(9, cons(near(X, Y))) :- remotecontrol(X), black(X), bottle(Y), yellow(Y).
task(11, cons(near(X, Y))) :- can(X), black(X), book(Y), white(Y).
task(12, cons(near(X, Y))) :- can(X), black(X), bottle(Y), blue(Y).
task(13, cons(near(X, Y))) :- can(X), black(X), can(Y), white(Y).
task(14, cons(near(X, Y))) :- can(X), black(X), remotecontrol(Y), white(Y).
task(15, cons(near(X, Y))) :- can(X), black(X), bottle(Y), white(Y).
task(16, ncons(closed(X))) :- closet(X).
task(18, cons(near(X, Y))) :- cup(X), white(X), can(Y), white(Y).
task(19, cons(near(X, Y))) :- cup(X), white(X), remotecontrol(Y), white(Y).
task(20, cons(near(X, Y))) :- cup(X), white(X), bottle(Y), white(Y).
task(21, cons(near(X, Y))) :- bottle(X), black(X), book(Y), white(Y).
task(22, cons(near(X, Y))) :- bottle(X), black(X), remotecontrol(Y), white(Y).
task(23, cons(near(X, Y))) :- bottle(X), black(X), bottle(Y), white(Y).
task(24, cons(near(X, Y))) :- bottle(X), black(X), can(Y), white(Y).
task(25, cons(near(X, Y))) :- book(X), black(X), bottle(Y), black(Y).
task(26, cons(near(X, Y))) :- book(X), black(X), cup(Y), black(Y).
task(27, cons(near(X, Y))) :- book(X), black(X), book(Y), yellow(Y).
task(28, cons(near(X, Y))) :- book(X), black(X), can(Y), green(Y).
task(29, cons(on(X, Y))) :- bottle(X), black(X), closet(Y).
