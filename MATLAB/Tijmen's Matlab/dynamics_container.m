% Lagrangian dynamics of a double pendulum

% System constants:
syms m1 m2 l g real

% System variables:
syms x th real
syms dx dth real
syms d2x d2th real

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
h = [th];

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

