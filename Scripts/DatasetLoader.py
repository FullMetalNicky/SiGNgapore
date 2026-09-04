import numpy as np
import os
from scipy.spatial.transform import Rotation
from PIL import Image
from tqdm import tqdm
from DataUtils import video_to_frames, unzipFolder

def load_depth(path, confidence=None, filter_level=0):
    if path[-4:] == '.npy':
        depth_mm = np.load(path, allow_pickle=True)
    elif path[-4:] == '.png':
        depth_mm = np.array(Image.open(path))
    depth_m = depth_mm.astype(np.float32) / 1000.0

    return depth_m

def load_confidence(path):
    return np.array(Image.open(path))

def load_rgb(path):
    return np.array(Image.open(path).convert("RGB"))




class DatasetLoader():

    def __init__(self, path):

        self.odometry = np.loadtxt(os.path.join(path, 'odometry.csv'), delimiter=',', skiprows=1)
        self.imu = np.loadtxt(os.path.join(path, 'imu.csv'), delimiter=',', skiprows=1)

        rgb_dir = os.path.join(path, 'images')
        if not os.path.exists(rgb_dir):
            video_to_frames(path + "rgb.mp3", rgb_dir)

        rgb_files = [os.path.join(rgb_dir, p) for p in sorted(os.listdir(rgb_dir))]
        self.rgb_files = [f for f in rgb_files if '.npy' in f or '.png' in f]

        confidence_dir = os.path.join(path, 'confidence')
        if not os.path.isdir(confidence_dir):
            unzipFolder(os.path.join(path, 'confidence.zip'))

        conf_files = [os.path.join(confidence_dir, p) for p in sorted(os.listdir(confidence_dir))]
        self.conf_files = [f for f in conf_files if '.npy' in f or '.png' in f]

       
        depth_dir = os.path.join(path, 'depth')
        if not os.path.isdir(depth_dir):
            unzipFolder(os.path.join(path, 'depth.zip'))
        depth_files = [os.path.join(depth_dir, p) for p in sorted(os.listdir(depth_dir))]
        self.depth_files = [f for f in depth_files if '.npy' in f or '.png' in f or '.tiff' in f]

        self.intrinsics = np.loadtxt(os.path.join(path, 'camera_matrix.csv'), delimiter=',')

        self.imu_index = []

        frame_ts = [line[0] for line in self.odometry]
        imu_ts =  [line[0] for line in self.imu]
        for t in frame_ts:
            imu_ind = np.argmin(np.abs(imu_ts - t))
            self.imu_index.append(imu_ind)

        self.index = 0

    def getFrameCount(self):

        return len(self.rgb_files)
    
    def getCameraCalibration(self):

        return self.intrinsics


    def loadAllFrames(self):

        poses = []
        rgbs = []
        confidences = []
        depths = []
        imus = []
        gyros = []
        t_gyros = []

        for line in self.odometry:
            # timestamp, frame, x, y, z, qx, qy, qz, qw
            position = line[2:5]
            quaternion = line[5:]
            worldFrameTrans = np.eye(4)
            worldFrameTrans[:3, :3] = Rotation.from_quat(quaternion).as_matrix()
            worldFrameTrans[:3, 3] = position
            poses.append(worldFrameTrans)

        for line in self.imu:
            # timestamp, a_x, a_y, a_z, alpha_x, alpha_y, alpha_z
            gyros.append(line[1:])


        for i in tqdm(range(len(self.rgb_files))):

            confidence = load_confidence(self.conf_files[i])
            depth = load_depth(self.depth_files[i], confidence, filter_level=0)
            rgb = load_rgb(self.rgb_files[i])
            confidences.append(confidence)
            depths.append(depth)
            rgbs.append(rgb)
            imus.append(gyros[self.imu_index[i]])

        return rgbs, depths, confidences, poses, imus


    def getTimeStampByIndex(self, index):

        line = self.odometry[index]

        return line[0]
    
    def getTimeStampByImageFilename(self, filename): # full filename!!

        index = self.rgb_files.index(filename)

        return self.getTimeStampByIndex(index)


    def loadNextFrame(self):

        line = self.odometry[self.index]
        position = line[2:5]
        quaternion = line[5:]
        worldFrameTrans = np.eye(4)
        worldFrameTrans[:3, :3] = Rotation.from_quat(quaternion).as_matrix()
        worldFrameTrans[:3, 3] = position

        imu = self.imu[self.imu_index[self.index]][1:]

        confidence = load_confidence(self.conf_files[self.index])
        depth = load_depth(self.depth_files[self.index], confidence, filter_level=0)
        rgb = load_rgb(self.rgb_files[self.index])

        self.index += 1

        return rgb, depth, confidence, worldFrameTrans, imu


    def loadFramebyIndex(self, index):

        line = self.odometry[index]
        position = line[2:5]
        quaternion = line[5:]
        worldFrameTrans = np.eye(4)
        worldFrameTrans[:3, :3] = Rotation.from_quat(quaternion).as_matrix()
        worldFrameTrans[:3, 3] = position

        imu = self.imu[self.imu_index[self.index]][1:]

        confidence = load_confidence(self.conf_files[index])
        depth = load_depth(self.depth_files[index], confidence, filter_level=0)
        rgb = load_rgb(self.rgb_files[index])

        return rgb, depth, confidence, worldFrameTrans, imu
    
    # def loadFramebyIndex2(self, index):

    #     line = self.odometry[index]
    #     odom = line[2:]
    #     imu = self.imu[self.imu_index[self.index]][1:]

    #     confidence = load_confidence(self.conf_files[index])
    #     depth = load_depth(self.depth_files[index], confidence, filter_level=0)
    #     rgb = load_rgb(self.rgb_files[index])

    #     return rgb, depth, confidence, odom, imu


def main():

    path = "/Data/" # path to the location of the dataset
    sdl = DatasetLoader(path)

    frameCount = sdl.getFrameCount()
    for i in tqdm(range(0, frameCount)):
        rgb, depth, confidence, pose, imu = sdl.loadFramebyIndex(i) 



if __name__ == "__main__":
    main()