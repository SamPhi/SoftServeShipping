% Lagrangian dynamics of a double pendulum

% System constants:
syms m1 m2 l g real

% System variables:
syms x th real
syms dx dth real
syms d2x d2th real
syms th_des x_des real
syms u real
syms t real

% Generalized coordinates
q = [x;
     th] ;
% Generalized velocity
dq = [dx;
      dth]; 
% Generalized acceleration:
d2q = [dx;
       d2th] ; 

% Kinematics: Position of pendulum bobs
p1 = [x;0];
p2 = l*[sin(th);
              -cos(th)] + [x;0] ;
% Velocity of pendulum bobs
dp1 = jacobian(p1, q) * dq ;
dp2 = jacobian(p2, q) * dq ;

% Kinetic Energy:
T1 = 1/2 * dp1' * m1 * dp1 ;
T2 = 1/2 * dp2' * m2 * dp2 ;
T = T1 + T2 ;

% Potential Energy:
U1 = m1*g*p1'*[0; 1] ;
U2 = m2*g*p2'*[0; 1] ;
U = U1 + U2 ;

% Lagrangian:
L = T - U ;

% Eqns. of Motion
% d/dt(partial L/partial dq)   -  partial L/partia q   = u
z = [q;
     dq] ;
dz = [dq ;
      d2q] ;

% Compute LHS of Robot Manipulator Dynamics:
% D(q)*d2q + C(q,dq)*dq + G(q) = B(q)*u
q_act = [x] ;
[D, C, G, B] = LagrangianDynamics(T, U, q, dq, q_act) ;

% Define Virtual Constraints
h = [th - th_des];
%h = [x - x_des];

dh_dq = jacobian(h, q) ;
d2h__ = [jacobian(dh_dq * dq,  q)          dh_dq] ;
matlabFunction(h, 'File', 'auto_h') ;
matlabFunction(dh_dq, 'File', 'auto_dh_dq') ;
matlabFunction(d2h__, 'File', 'auto_d2h__') ;

% Write out dynaics
matlabFunction(D, 'File', 'auto_D')
matlabFunction(C, 'File', 'auto_C')
matlabFunction(G, 'File', 'auto_G')
matlabFunction(B, 'File', 'auto_B')

matlabFunction(p1, 'File', 'auto_p1') ;
matlabFunction(p2, 'File', 'auto_p2') ;

%% compute u
global params;
params.xdes = x_des;
params.th = th;
params.th_des = th_des;

    fder = [dq ;
         inv(D)*( -C*dq - G)] ;
    gder = [zeros(2,1) ;
         inv(D)*B] ;

u = simplify(FeedbackControl(q, dq, fder, gder, params, t));

matlabFunction(u, 'File', 'auto_u_container') ;

%% simulate
clf
global params;
global epast;
params.xdes = 5;
epast = params.xdes;
params.th = th;
params.th_des = deg2rad(-5);
global tpast
tpast = 0;

% Simulate double pendulum dynamic
q0 = [0; %x
      deg2rad(0)]; %th
dq0 = [0;
       0] ;
z0 = [q0;
      dq0] ;
 
% Simulate dynamics
[t_sol, x_sol] = ode45(@double_pendulum_dynamics, [0 100], z0) ;

hold on
nexttile ; plot(t_sol, rad2deg(x_sol(:,2))) ; legend('th') %[x_sol(:,1)/100, rad2deg(x_sol(:,2))]
xlabel('Time (s)') ; ylabel('deg') ;
nexttile
plot(t_sol, x_sol(:,1)); legend('x')
xlabel('Time (s)') ; ylabel('x (m)') ;

%animate_pendulum(t_sol, x_sol) ;

%% functions

%damping ratio and natural frequency

function dz = double_pendulum_dynamics(t, z, params)
    global params;

    % Extract coordinates
    q = z(1:2) ;
    dq = z(3:4) ;
    x = q(1) ; th = q(2) ;
    dx = dq(1) ; dth = dq(2) ;
    
    % System constants
    m1=1 ; m2=0.5; l=1; g=9.81; 

    D = auto_D(l,m1,m2,th) ;
    C = auto_C(dth,l,m2,th);
    G = auto_G(g,l,m2,th) ;
    B = auto_B() ;
    
    f = [dq ;
         inv(D)*( -C*dq - G)] ;
    g = [zeros(2,1) ;
         inv(D)*B] ;
    
    u = FeedbackControl(q, dq, f, g, params,t) ;
    
    dz = f + g*u ;
end

function beta = EventControl(params, xcurrent,t)
    global epast
    global tpast
    e = xcurrent-params.xdes;
    Kp = 0.001; %0.000001
    Kd = .01; %0.0001
    Ki = 0.0001;
    if t == 0
        t = 0.01;
    end

    tstep = t-tpast;
    if tstep == 0
        tstep = 0.01;
    end
    %pd control + Kd*(e - epast)/(t)
    beta = (Kp*e) + Kd*(e-epast)/tstep; %- Kd*(e - epast)/(tstep);
%     th_des = params.th_des - beta;
%     params.th_des = th_des;

    if t ~= tpast
        tpast = t;
    end
    
    epast = e;

end

function u = FeedbackControl(q, dq, f, g, params,t)
    global kppast
    x = q(1) ; th = q(2) ;
    dx = dq(1) ; dth = dq(2) ;
    th_des = params.th_des;
    x_des = params.xdes;
    % System constants
    m1=1 ; m2=0.5; l1=1; %g=9.81; 
    
    th_des = EventControl(params, x,t);
    h = auto_h(th,th_des);
    %h = auto_h(x, x_des);
    dh_dq = auto_dh_dq() ;
    d2h__ = auto_d2h__() ;
    
    % Compute Lie Derivatives
    Lfh = dh_dq*dq ;
    Lf2h = d2h__*f ;
    LgLfh = d2h__*g ;
    
    % Compute Control
    kp = 2.5 ;%2.5 
    kd =  0.1 ;

    v = -kp*h - kd*Lfh ;

    u = inv(LgLfh)*(-Lf2h + v) ; % IO Linearization
end

function animate_pendulum(t, z)
    % System constants
    m1=1 ; m2=0.5; l=1; g=9.81; 
    
    figure ;
    for j=1:length(t)
        % Extract coordinates
        q = z(j,1:2) ;
        x = q(1) ; th = q(2) ;
        p1 = auto_p1(x);
        p2 = auto_p2(l,th,x) ;
        pts = [0 0 ;
               p1' ;
               p2'] ;
        plot(pts(:,1), pts(:,2), '-o') ;
        legend(num2str(rad2deg(th)));
        axis([-3+x 3+x -3 3]) ; grid on ;
        pause(0.05) ;
    end
end

function [D, C, G, B] = LagrangianDynamics(T, U, q, dq, q_act)

D = simplify( jacobian(jacobian(T,dq), dq) ) ;
for k=1:length(q)
    for j=1:length(q)
        C(k,j) = sym(0) ;
        for i=1:length(q)
            C(k,j) = C(k,j) + 1/2 * ( diff(D(k,j),q(i)) + diff(D(k,i),q(j)) - diff(D(i,j),q(k)) ) * dq(i) ;
        end
    end
end


C = simplify(C) ;
G = simplify( jacobian(U,q) )' ;
B = jacobian(q_act, q)' ;
end
