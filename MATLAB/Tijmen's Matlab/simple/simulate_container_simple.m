% Simulate double pendulum dynamics
function simulate_container_simple()
    clf
    clear

    global tlast
    q0 = [0; %x
          deg2rad(0)]; %th
    dq0 = [0;
           0] ;
    z0 = [q0;
          dq0] ;
      
    % Simulate dynamics
    [t_sol, x_sol] = ode45(@double_pendulum_dynamics, [0 20], z0) ;
    
    plot(t_sol, x_sol(:,1)) ; legend('x')
    xlabel('Time (s)') ; ylabel('deg') ;
    
    %animate_pendulum(t_sol, x_sol) ;
    
end

function dz = double_pendulum_dynamics(t, z)
    global tlast
    tlast = 0;
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
    
    % control:
    Kp = 7;
    xdes = 5;
    Kd = 15;
    
    u = Kp*10 - (Kp*2*x + Kd*dx) ;
    
    if tlast ~= t
        tlast = t;
    end

    dz = [dq ; %dq
          inv(D)*( -C*dq - G + B*u )] ; %d2q
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
        axis([-3+x 3+x -3 3]) ; grid on ;
        pause(0.05) ;
    end
end