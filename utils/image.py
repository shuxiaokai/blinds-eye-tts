import requests
import progressbar as pb
import os
import cv2
import imageio
from imutils import paths
import numpy as np

def get_frames(video_file, save_dir=None, save_prefix='', ext='jpg'):

    video = cv2.VideoCapture(video_file)

    if not video.isOpened():

        print("[ERROR] Could not open video file ", video_file)
        video.release()
        return

    frames = []
    
    frame_count = 0

    while video.isOpened():

        status, frame = video.read()

        if not status:
            break
        
        frames.append(frame)

        if save_dir:

            frame_count += 1
            
            out_file = save_dir + os.path.sep + save_prefix + \
                        'frame_' + str(frame_count) + '.' + ext

            print('[INFO] Writing file to .. ', out_file)

            cv2.imwrite(out_file, frame)
            
    video.release()

    return frames


def animate(src, gif_name, reshape=None, fps=25):

    if not isinstance(src, list):

        if os.path.isdir(src):

            src = list(paths.list_images(src))

            for idx, image in enumerate(src):
                src[idx] = cv2.imread(image)

    if reshape:

        for idx, image in enumerate(src):
            src[idx] = cv2.resize(image, reshape)

    for idx, image in enumerate(src):
            src[idx] = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    src = np.array(src)
    
    imageio.mimsave(gif_name, src, fps=fps)