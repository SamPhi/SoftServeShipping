function G = auto_G(g,l,m2,th)
%auto_G
%    G = auto_G(g,L,M2,TH)

%    This function was generated by the Symbolic Math Toolbox version 9.2.
%    18-Apr-2023 13:00:31

G = [0.0;g.*l.*m2.*sin(th)];
