function C = auto_C(dth,l,m2,th)
%auto_C
%    C = auto_C(DTH,L,M2,TH)

%    This function was generated by the Symbolic Math Toolbox version 9.2.
%    03-Apr-2023 23:46:16

C = reshape([0.0,0.0,-dth.*l.*m2.*sin(th),0.0],[2,2]);
