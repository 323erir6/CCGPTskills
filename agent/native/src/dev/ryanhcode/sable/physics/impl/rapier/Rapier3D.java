package dev.ryanhcode.sable.physics.impl.rapier;
public final class Rapier3D {
  static { System.load(System.getenv("SABLE_NATIVE_LIB")); }
  public static native long initialize(double x, double y, double z, double drag);
  public static native void dispose(long scene);
  public static native int newVoxelCollider(double friction,double volume,double restitution,boolean fluid,Object callback,boolean dynamic);
  public static native void addVoxelColliderBox(int index,double[] bounds);
  public static native void addChunk(long scene,int x,int y,int z,int[] data,boolean global,int objectId);
  public static native void createSubLevel(long scene,int id,double[] pose);
  public static native void setCenterOfMass(long scene,int id,double x,double y,double z);
  public static native void setLocalBounds(long scene,int id,int minX,int minY,int minZ,int maxX,int maxY,int maxZ);
  public static native void setMassProperties(long scene,int id,double mass,double[] com,double[] inertia);
  public static native void createBox(long scene, int id, double mass, double hx, double hy, double hz, double[] pose);
  public static native void removeBox(long scene, int id);
  public static native void getPose(long scene, int id, double[] out);
  public static native void getLinearVelocity(long scene, int id, double[] out);
  public static native void getAngularVelocity(long scene, int id, double[] out);
  public static native void applyForceAndTorque(long scene, int id, double fx, double fy, double fz, double tx, double ty, double tz, boolean wake);
  public static native void addLinearAngularVelocities(long scene,int id,double vx,double vy,double vz,double wx,double wy,double wz,boolean wake);
  public static native double[] clearCollisions(long scene);
  public static native void step(long scene,double seconds);
  public static native void tick(long scene,double seconds);
}
