import os
import json
import numpy as np
from scipy.spatial.transform import Rotation as R
from tqdm import tqdm
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

def calculate_frustum_overlap(frustum1, frustum2, K):
    """
    Calculate the overlap between two camera frustums using 2D projection.
    
    Args:
    - frustum1 (numpy.ndarray): An 8x4 array representing the 3D coordinates of the eight corners of the first frustum.
    - frustum2 (numpy.ndarray): An 8x4 array representing the 3D coordinates of the eight corners of the second frustum.
    - K (numpy.ndarray): A 3x3 intrinsic matrix of the camera.
    
    Returns:
    - float: The overlap ratio between the two frustums on the image plane. Returns 0.0 if there is no overlap.
    """
    
    # Take only the x, y, z coordinates from the frustums for the dot product
    corners1 = np.dot(frustum1[:, :3], K.T)
    corners1 = corners1[:, :2] / corners1[:, 2:]
    min_x1, min_y1 = np.min(corners1, axis=0)
    max_x1, max_y1 = np.max(corners1, axis=0)
    
    corners2 = np.dot(frustum2[:, :3], K.T)
    corners2 = corners2[:, :2] / corners2[:, 2:]
    min_x2, min_y2 = np.min(corners2, axis=0)
    max_x2, max_y2 = np.max(corners2, axis=0)
    
    # Calculate overlap in x and y directions
    dx = min(max_x1, max_x2) - max(min_x1, min_x2)
    dy = min(max_y1, max_y2) - max(min_y1, min_y2)
    
    if dx >= 0 and dy >= 0:
        # Calculate overlap area and ratio
        overlap_area = dx * dy
        area1 = (max_x1 - min_x1) * (max_y1 - min_y1)
        overlap_ratio = overlap_area / area1
        return overlap_ratio
    else:
        return 0.0

def calculate_frustum(pose, K, camera, n, f):
    """
    Calculates the frustum corners for a given camera pose, intrinsic matrix, 
    and near and far plane distances.
    
    Args:
    - pose (list): The camera pose containing quaternion and translation.
    - K (numpy.ndarray): The intrinsic matrix of the camera.
    - n (float): The distance to the near plane.
    - f (float): The distance to the far plane.
    
    Returns:
    - corners_world_homo (numpy.ndarray): The corners of the frustum in world coordinates.
    """
    q, t = pose[:4], pose[4:]
    r = R.from_quat(q)
    rot_mat = r.as_matrix()
    trans_vec = np.array(t).reshape(3, 1)
    transform_mat = np.hstack((rot_mat, trans_vec))
    transform_mat = np.vstack((transform_mat, [0, 0, 0, 1]))
    transform_mat = np.linalg.inv(transform_mat)
    transform_mat[1, :] *= -1
    transform_mat[:, 1] *= -1
    
    fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]
    t = n / fx * (camera['height'] / 2 - cy)
    b = -t
    r_ = n / fy * (camera['width'] / 2 - cx)
    l_ = -r_
    n_corners = np.array([[l_, b, -n], [l_, t, -n], [r_, t, -n], [r_, b, -n]])
    f_corners = np.array([[l_, b, -f], [l_, t, -f], [r_, t, -f], [r_, b, -f]])
    corners_cam = np.vstack((n_corners, f_corners))
    corners_cam_homo = np.hstack((corners_cam, np.ones((corners_cam.shape[0], 1))))
    corners_world_homo = np.dot(corners_cam_homo, transform_mat.T)
    
    return corners_world_homo

def select_frame_pairs(file_path, min_overlap=0.20, max_overlap=0.60):
    """
    Reads a JSON file to get camera and frame information, then calculates
    and filters frame pairs based on their frustum overlap. 
    It does this for contiguous 10 contiguous frames as 
    avialblle clipping the last and first 10 frames.
    
    Args:
    - file_path (str): The path to the JSON file.
    - min_overlap (float): The minimum acceptable frustum overlap ratio.
    - max_overlap (float): The maximum acceptable frustum overlap ratio.
    
    Returns:
    - frame_pairs (dict): Pairs of frames with acceptable overlap.
    """
    R = 10
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    camera = data['camera']
    fx, fy, cx, cy = camera['params'][:4]
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
    
    points = data['points']
    z_coords = [point[2] for point in points]
    n, f = min(z_coords), max(z_coords)
    
    images = data['images']
    frame_pairs = defaultdict(list)
    
    frustums = {}
    for frame_name, pose in images.items():
        frustums[frame_name] = calculate_frustum(pose, K, camera, n, f)
    
    sorted_frame_names = sorted(images.keys())
    
    for i in tqdm(range(20, len(sorted_frame_names) - 20), desc="Comparing frames"):
        start_index = i - R
        end_index = i + R
        
        for j in range(start_index, end_index):
            if j == i: continue
            frame1_name = sorted_frame_names[i]
            frame2_name = sorted_frame_names[j]
            frustum1 = frustums[frame1_name]
            frustum2 = frustums[frame2_name]
            overlap = calculate_frustum_overlap(frustum1, frustum2, K)  
            
            if min_overlap <= overlap <= max_overlap:
                frame_pairs[frame1_name].append(frame2_name)
    
    return frame_pairs

def process_json_file(file_name):
    file_path = os.path.join(json_data_dir, file_name)
    frame_pairs_dict = select_frame_pairs(file_path)
    
    pair_file_name = f"{os.path.splitext(file_name)[0]}_pairs.json"
    pair_file_path = os.path.join(frame_pairs_dir, pair_file_name)
    
    frame_pairs_list = [(k, v) for k, vs in frame_pairs_dict.items() for v in vs]
    
    with open(pair_file_path, 'w') as f:
        json.dump(frame_pairs_list, f)

if __name__ == "__main__":
    json_data_dir = './JSON_DATA'
    frame_pairs_dir = './frame_pairs'

    if not os.path.exists(frame_pairs_dir):
        os.makedirs(frame_pairs_dir)

    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(process_json_file, os.listdir(json_data_dir)), total=len(os.listdir(json_data_dir))))

