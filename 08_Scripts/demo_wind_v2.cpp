// Educational 2D D2Q9 BGK flow through PLATEAU projected obstacles.
// Periodic boundaries + constant body force; lattice units, not calibrated m/s.
// Build: g++ -O3 -std=c++17 demo_wind.cpp -o demo_wind
#include <vector>
#include <fstream>
#include <iostream>
#include <cmath>
#include <algorithm>
#include <ctime>
#include <iomanip>
int main(int argc,char**argv){
 if(argc!=5){std::cerr<<"input output coming_from_bearing_degrees scenario(0,1)\n";return 1;}
 std::ifstream in(argv[1]); int nx,ny;in>>nx>>ny;int n=nx*ny,dir=atoi(argv[3]),sc=atoi(argv[4]);
 std::vector<int> solid(n);std::vector<double> drag(n);for(auto&x:solid)in>>x;for(auto&x:drag)in>>x;
 if(!in||nx<4||ny<4||n>1000000)return 2;
 const int cx[9]={0,1,0,-1,0,1,-1,-1,1},cy[9]={0,0,1,0,-1,1,1,-1,-1},opp[9]={0,3,4,1,2,7,8,5,6};
 const double w[9]={4./9,1./9,1./9,1./9,1./9,1./36,1./36,1./36,1./36};
 double tau=.85,force=2e-6;double angle=dir*3.14159265358979323846/180;double forceX=-sin(angle)*force,forceY=-cos(angle)*force;int steps=4500,fluid=0;
 std::vector<double> f(n*9),g(n*9),avgx(n),avgy(n),oldx(n),oldy(n);std::vector<int> next(n*9);
 for(int j=0;j<ny;j++)for(int i=0;i<nx;i++){int p=j*nx+i;if(!solid[p])fluid++;for(int q=0;q<9;q++){
  f[p*9+q]=solid[p]?0:w[q];next[p*9+q]=((j+cy[q]+ny)%ny)*nx+(i+cx[q]+nx)%nx;}}
 auto start=std::clock(); std::cout<<std::setprecision(9);double drift=0,maxu=0,minrho=1,maxrho=1,residual=0;
 for(int t=0;t<steps;t++){
  std::fill(g.begin(),g.end(),0);double mass=0,du=0,unorm=0;maxu=0;minrho=10;maxrho=0;
  for(int p=0;p<n;p++){if(solid[p])continue;double rho=0,u=0,v=0;for(int q=0;q<9;q++){double a=f[p*9+q];rho+=a;u+=a*cx[q];v+=a*cy[q];}
   u/=rho;v/=rho;double fx=forceX-(sc?drag[p]*u:0),fy=forceY-(sc?drag[p]*v:0);
   u+=.5*fx/rho;v+=.5*fy/rho;double u2=u*u+v*v;maxu=std::max(maxu,sqrt(u2));mass+=rho;minrho=std::min(minrho,rho);maxrho=std::max(maxrho,rho);
   if(!std::isfinite(rho)||rho<.8||rho>1.2||u2>.04){std::cerr<<"unstable cell "<<p<<" step "<<t<<"\n";return 3;}
   if(t>=steps-500){avgx[p]+=u/500;avgy[p]+=v/500;}
   if((t+1)%500==0){du+=(u-oldx[p])*(u-oldx[p])+(v-oldy[p])*(v-oldy[p]);unorm+=u2;oldx[p]=u;oldy[p]=v;}
   for(int q=0;q<9;q++){double cu=cx[q]*u+cy[q]*v,eq=w[q]*rho*(1+3*cu+4.5*cu*cu-1.5*u2);
    double guo=w[q]*(1-.5/tau)*((3*(cx[q]-u)+9*cu*cx[q])*fx+(3*(cy[q]-v)+9*cu*cy[q])*fy);
    double post=f[p*9+q]-(f[p*9+q]-eq)/tau+guo;int np=next[p*9+q];if(solid[np])g[p*9+opp[q]]=post;else g[np*9+q]=post;
   }
  }
  f.swap(g);drift=mass/fluid-1;
  if((t+1)%500==0){residual=sqrt(du/std::max(unorm,1e-30));std::cout<<"step="<<t+1<<" mass_drift="<<drift<<" max_lattice_speed="<<maxu<<" rho="<<minrho<<","<<maxrho<<" relative_change_500="<<residual<<"\n";}
 }
 std::ofstream out(argv[2]);out<<std::setprecision(8)<<"{\"nx\":"<<nx<<",\"ny\":"<<ny<<",\"steps\":"<<steps<<",\"tau\":"<<tau<<",\"force\":"<<force<<",\"direction\":"<<dir<<",\"scenario\":"<<sc<<",\"mass_drift\":"<<drift<<",\"last_relative_change_500\":"<<residual<<",\"peak_lattice_speed\":"<<maxu<<",\"rho_min\":"<<minrho<<",\"rho_max\":"<<maxrho<<",\"cpu_seconds\":"<<double(std::clock()-start)/CLOCKS_PER_SEC<<",\"u\":[";
 for(int p=0;p<n;p++){if(p)out<<",";out<<avgx[p];}out<<"],\"v\":[";for(int p=0;p<n;p++){if(p)out<<",";out<<avgy[p];}out<<"]}";
 std::cout<<"PASS finite density bounds; solid velocity=0; cpu_seconds="<<double(std::clock()-start)/CLOCKS_PER_SEC<<"\n";
 return 0;
}
