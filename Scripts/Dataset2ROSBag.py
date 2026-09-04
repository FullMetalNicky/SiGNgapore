
import numpy as np
from tqdm import tqdm
from DatasetLoader import *

from cv_bridge import CvBridge
from rclpy.serialization import serialize_message
from sensor_msgs.msg import CameraInfo, Imu
from nav_msgs.msg import Odometry
from rclpy.time import Time
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TransformStamped
import rosbag2_py




def createRos2bag(datasetPath, bagpath, rgbTopic, cameraInfoTopic, depthTopic, odomTopic, imuTopic):


    dl = DatasetLoader(datasetPath)
    fc = dl.getFrameCount()
    intrinsics = dl.getCameraCalibration().flatten()
    print(intrinsics)

    writer = rosbag2_py.SequentialWriter()
    storage_options = rosbag2_py.StorageOptions(
        uri=bagpath, # The name of the bag file directory
        storage_id='sqlite3'
    )
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr'
    )

    writer.open(storage_options, converter_options)

    topic_info = rosbag2_py.TopicMetadata(
        name=rgbTopic,
        type='sensor_msgs/msg/Image',
        serialization_format='cdr'
    )
    writer.create_topic(topic_info)

    topic_info = rosbag2_py.TopicMetadata(
        name=cameraInfoTopic,
        type='sensor_msgs/msg/CameraInfo',
        serialization_format='cdr'
    )
    writer.create_topic(topic_info)

    topic_info = rosbag2_py.TopicMetadata(
        name=depthTopic,
        type='sensor_msgs/msg/Image',
        serialization_format='cdr'
    )
    writer.create_topic(topic_info)

    topic_info = rosbag2_py.TopicMetadata(
        name=odomTopic,
        type='nav_msgs/msg/Odometry',
        serialization_format='cdr'
    )
    writer.create_topic(topic_info)

    topic_info = rosbag2_py.TopicMetadata(
        name=imuTopic,
        type='sensor_msgs/msg/Imu',
        serialization_format='cdr'
    )
    writer.create_topic(topic_info)

    topic_info = rosbag2_py.TopicMetadata(
        name='/tf',
        type='tf2_msgs/msg/TFMessage',
        serialization_format='cdr'
    )
    writer.create_topic(topic_info)

    topic_info = rosbag2_py.TopicMetadata(
        name='/tf_static',
        type='tf2_msgs/msg/TFMessage',
        serialization_format='cdr'
    )
    writer.create_topic(topic_info)

    t = dl.getTimeStampByIndex(0)
    t_nano = int(t * (10 ** 9))
    timestamp = Time(seconds=t).to_msg()
    tf_static_msg = TFMessage()
    transform = TransformStamped()
    transform.header.stamp = timestamp
    transform.header.frame_id = 'base_link'
    transform.child_frame_id = 'camera'
    transform.transform.translation.x = 0.0
    transform.transform.translation.y = 0.0
    transform.transform.translation.z = 0.0
    transform.transform.rotation.x = 0.0
    transform.transform.rotation.y = 0.0
    transform.transform.rotation.z = 0.0
    transform.transform.rotation.w = 1.0
    tf_static_msg.transforms.append(transform)
    writer.write('/tf_static', serialize_message(tf_static_msg), t_nano)

    bridge = CvBridge()


    for i in tqdm(range(fc)):

        t = dl.getTimeStampByIndex(i)
        t_nano = int(t * (10 ** 9))
        timestamp = Time(seconds=t).to_msg()
        rgb, depth, confidence, odom, _ = dl.loadFramebyIndex2(i)
        
        cam_msg = CameraInfo()
        cam_msg.height = rgb.shape[0]
        cam_msg.width = rgb.shape[1]
        cam_msg.k = list(intrinsics) 
        cam_msg.header.stamp = timestamp
        cam_msg.header.frame_id = 'camera'
        writer.write(cameraInfoTopic, serialize_message(cam_msg), t_nano)
        
        rgb_msg = bridge.cv2_to_imgmsg(np.array(rgb), "bgr8")
        rgb_msg.header.stamp = timestamp
        rgb_msg.header.frame_id = 'camera'
        writer.write(rgbTopic, serialize_message(rgb_msg), t_nano)

        depth_msg = bridge.cv2_to_imgmsg(np.array(depth), '32FC1')
        depth_msg.header.stamp = timestamp
        depth_msg.header.frame_id = 'camera'
        writer.write(depthTopic, serialize_message(depth_msg), t_nano)
     
        odom_msg = Odometry()
        odom_msg.pose.pose.position.x = odom[0]
        odom_msg.pose.pose.position.y = odom[1]
        odom_msg.pose.pose.position.z = odom[2]
        odom_msg.pose.pose.orientation.x = odom[3]
        odom_msg.pose.pose.orientation.y = odom[4]
        odom_msg.pose.pose.orientation.z = odom[5]
        odom_msg.pose.pose.orientation.w = odom[6]
        odom_msg.header.stamp = timestamp
        odom_msg.header.frame_id = 'odom'
        writer.write(odomTopic, serialize_message(odom_msg), t_nano)

        tf_msg = TFMessage()
        transform = TransformStamped()
        transform.header.stamp = timestamp
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_link'
        transform.transform.translation.x = odom[0]
        transform.transform.translation.y = odom[1]
        transform.transform.translation.z = odom[2]
        transform.transform.rotation.x = odom[3]
        transform.transform.rotation.y = odom[4]
        transform.transform.rotation.z = odom[5]
        transform.transform.rotation.w = odom[6]
        tf_msg.transforms.append(transform)
        writer.write('/tf', serialize_message(tf_msg), t_nano)

        tf_static_msg.transforms[0].header.stamp = timestamp
        writer.write('/tf_static', serialize_message(tf_static_msg), t_nano)

    for line in dl.imu:

        imu = line[1:]
        t = line[0]
        t_nano = int(t * (10 ** 9))
        timestamp = Time(seconds=t).to_msg()

        imu_msg = Imu()
        imu_msg.linear_acceleration.x = imu[0]
        imu_msg.linear_acceleration.y = imu[1]
        imu_msg.linear_acceleration.z = imu[2]
        imu_msg.angular_velocity.x = imu[3]
        imu_msg.angular_velocity.y = imu[4]
        imu_msg.angular_velocity.z = imu[5]
        imu_msg.header.stamp = timestamp
        imu_msg.header.frame_id = 'camera'
        writer.write(imuTopic, serialize_message(imu_msg), t_nano)


def main():

    datasetPath = "/Data/E1/S0/" # path to the location of a specific scenario in the dataset you wish to convert to a ROSbag
    bagpath = datasetPath + "ros2bag"

    rgbTopic = '/rgb/image_raw'
    cameraInfoTopic = '/rgb/camera_info'
    depthTopic = '/depth/image_raw'
    odomTopic = '/odom'
    imuTopic = '/imu'

    createRos2bag(datasetPath, bagpath, rgbTopic, cameraInfoTopic, depthTopic, odomTopic, imuTopic)
   




if __name__ == "__main__":
    main()