import dev.ryanhcode.sable.physics.impl.rapier.Rapier3D;
import java.io.*;
import java.util.*;
/**
 * Text-only JNI bridge to the unmodified native Sable 2.0.5 Rapier binary.
 * Protocol is intentionally limited; input must come from trusted local test code.
 * CLI commands: INIT gX gY gZ drag | MATERIAL mu | SHAPE id x1 y1 z1 x2 y2 z2 |
 * SHIP id px py pz qx qy qz qw mass comx comy comz ix iy iz minx miny minz maxx maxy maxz |
 * BLOCK bodyId bx by bz materialId | LOAD bodyId | GROUND surfaceY cx cz radius |
 * IMPULSE bodyId fx fy fz tx ty tz | STEP dt | STATE bodyId | CLOSE.
 */
public final class NativeHarness {
 static final class Chunk { final int x,y,z; Chunk(int x,int y,int z){this.x=x;this.y=y;this.z=z;}
  public boolean equals(Object o){return o instanceof Chunk c && x==c.x && y==c.y && z==c.z;}
  public int hashCode(){return Objects.hash(x,y,z);} }
 static final class Body { int id; double[] pose; double mass; double[] com, inertia; int[] bounds;
  Map<Chunk,int[]> chunks=new HashMap<>(); }
 static long scene=0L; static final Map<Integer,Body> bodies=new HashMap<>();
 static final double[] statePose=new double[7], v=new double[3], w=new double[3];
 static double n(String[] p,int i){double x=Double.parseDouble(p[i]);if(!Double.isFinite(x))throw new IllegalArgumentException("nonfinite");return x;}
 static int ni(String[] p,int i){return Integer.parseInt(p[i]);}
 static void require(String[] p,int expected){if(p.length!=expected)throw new IllegalArgumentException("arguments="+p.length+" expected="+expected);}
 static String key(String s){return s.toUpperCase(Locale.ROOT);}
 static String run(String[] p){
  switch(key(p[0])){
   case "INIT": {require(p,5); if(scene!=0)throw new IllegalStateException("already initialized");
     scene=Rapier3D.initialize(n(p,1),n(p,2),n(p,3),n(p,4));return "OK INIT";}
   case "MATERIAL": {require(p,2);int id=Rapier3D.newVoxelCollider(n(p,1),1,0,false,null,false);return "OK MATERIAL "+id;}
   case "SHAPE": {require(p,8);double[] box=new double[6];for(int k=0;k<6;k++)box[k]=n(p,k+2);
     Rapier3D.addVoxelColliderBox(ni(p,1),box);return "OK SHAPE";}
   case "SHIP": {require(p,22);Body b=new Body();b.id=ni(p,1);b.pose=new double[7];
     for(int k=0;k<7;k++)b.pose[k]=n(p,k+2);
     b.mass=n(p,9);b.com=new double[]{n(p,10),n(p,11),n(p,12)};
     b.inertia=new double[]{n(p,13),0,0,0,n(p,14),0,0,0,n(p,15)};
     b.bounds=new int[6];for(int k=0;k<6;k++)b.bounds[k]=ni(p,k+16);
     if(bodies.putIfAbsent(b.id,b)!=null)throw new IllegalArgumentException("duplicate body");
     Rapier3D.createSubLevel(scene,b.id,b.pose);
     Rapier3D.setLocalBounds(scene,b.id,b.bounds[0],b.bounds[1],b.bounds[2],b.bounds[3],b.bounds[4],b.bounds[5]);
     Rapier3D.setCenterOfMass(scene,b.id,b.com[0],b.com[1],b.com[2]);
     Rapier3D.setMassProperties(scene,b.id,b.mass,new double[]{0,0,0},b.inertia);return "OK SHIP"; }
   case "BLOCK": {require(p,6);Body b=Objects.requireNonNull(bodies.get(ni(p,1)),"unknown body");
     int x=ni(p,2),y=ni(p,3),z=ni(p,4),material=ni(p,5);
     Chunk c=new Chunk(Math.floorDiv(x,16),Math.floorDiv(y,16),Math.floorDiv(z,16));
     int[] arr=b.chunks.computeIfAbsent(c,ignored->new int[4096]);
     int index=Math.floorMod(x,16)+(Math.floorMod(z,16)<<4)+(Math.floorMod(y,16)<<8);
     arr[index]=((material+1)<<16)|2;return "OK BLOCK"; }
   case "LOAD": {require(p,2);Body b=Objects.requireNonNull(bodies.get(ni(p,1)),"unknown body");
     for(Map.Entry<Chunk,int[]> entry:b.chunks.entrySet()){Chunk c=entry.getKey();Rapier3D.addChunk(scene,c.x,c.y,c.z,entry.getValue(),false,b.id);}
     b.chunks.clear();return "OK LOAD"; }
   case "GROUND": {require(p,6);int y=ni(p,1)-1,cx=ni(p,2),cz=ni(p,3),radius=ni(p,4), material=ni(p,5);
     if(radius<0 || radius>5)throw new IllegalArgumentException("ground radius capped at 5");
     int cy=Math.floorDiv(y,16),ly=Math.floorMod(y,16);
     for(int x=cx-radius;x<=cx+radius;x++)for(int z=cz-radius;z<=cz+radius;z++){
       int[] data=new int[4096];for(int ix=0;ix<16;ix++)for(int iz=0;iz<16;iz++)
         data[ix+(iz<<4)+(ly<<8)]=((material+1)<<16)|2;
       Rapier3D.addChunk(scene,x,cy,z,data,true,-1);
     }
     return "OK GROUND"; }
   case "BOX": {require(p,13);int id=ni(p,1);double[] pose=new double[7];for(int i=0;i<7;i++)pose[i]=n(p,i+6);
     Rapier3D.createBox(scene,id,n(p,2),n(p,3),n(p,4),n(p,5),pose);return "OK BOX";}
   case "IMPULSE": {require(p,8);Rapier3D.applyForceAndTorque(scene,ni(p,1),n(p,2),n(p,3),n(p,4),n(p,5),n(p,6),n(p,7),true);return "OK IMPULSE";}
   case "STEP": {require(p,2);Rapier3D.step(scene,n(p,1));return "OK STEP";}
   case "COLLISIONS": {require(p,1);double[] contacts=Rapier3D.clearCollisions(scene);
     StringBuilder sb=new StringBuilder("CONTACTS").append(' ').append(contacts.length);
     for(double value:contacts)sb.append(' ').append(value);return sb.toString();}
   case "STATE": {require(p,2);int id=ni(p,1);Rapier3D.getPose(scene,id,statePose);
     Rapier3D.getLinearVelocity(scene,id,v);Rapier3D.getAngularVelocity(scene,id,w);
     StringBuilder sb=new StringBuilder("STATE");for(double d:statePose)sb.append(' ').append(d);
     for(double d:v)sb.append(' ').append(d);for(double d:w)sb.append(' ').append(d);return sb.toString();}
   case "CLOSE":{require(p,1);if(scene!=0){Rapier3D.dispose(scene);scene=0;}return "OK CLOSE";}
   default:throw new IllegalArgumentException("unknown command: "+p[0]);
  }
 }
 public static void main(String[] args)throws Exception {
  try(BufferedReader in=new BufferedReader(new InputStreamReader(System.in))){
   for(String line;(line=in.readLine())!=null;){
    if(line.isBlank())continue;
    try{String result=run(line.trim().split(" +"));System.out.println(result);System.out.flush();if(line.equalsIgnoreCase("CLOSE"))break;}
    catch(Exception e){System.out.println("ERROR "+e);System.out.flush();}
   }
  } finally {if(scene!=0)Rapier3D.dispose(scene);}
 }
}
