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
syms kpx kdx real
syms kpt kdt real

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

    fder = [dq ;
         inv(D)*( -C*dq - G)] ;
    gder = [zeros(2,1) ;
         inv(D)*B] ;

u = simplify(FeedbackControl(q, dq, fder, gder, t, x_des, kpx, kdx, kpt, kdt));


matlabFunction(u, 'File', 'auto_u_container') ;

%% functions

function th_des = calculateTheta(x_des, pos_x, t, kpt, kdt)

    e = pos_x-x_des/2;
    %pd control + Kd*(e - epast)/(t)
    th_des = (kpt*e) + kdt; % + Kd*(e-epast)/0.01; %- Kd*(e - epast)/(tstep);


end

function u = FeedbackControl(q, dq, fx, gx ,t, x_des, kpx, kdx, kpt, kdt)
    pos_x = q(1) ; th = q(2) ;
    dx = dq(1) ; dth = dq(2) ;
    % System constants
    m1=1 ; m2=0.5; l1=1; %g=9.81; 
    
    th_des = calculateTheta(x_des, pos_x, t, kpt, kdt);
    h = auto_h(th,th_des);
    %h = auto_h(x, x_des);
    dh_dq = auto_dh_dq() ;
    d2h__ = auto_d2h__() ;
    
    % Compute Lie Derivatives
    Lfh = dh_dq*dq ;
    Lf2h = d2h__*fx ;
    LgLfh = d2h__*gx ;
    
    % Compute Control
    v = -kpx*h - kdx*Lfh ;

    u = inv(LgLfh)*(-Lf2h + v) ; % IO Linearization
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
