# utils/video_utils.py

import supervision as sv


def get_video(video_path):
    video_info = sv.VideoInfo.from_video_path(video_path)
    frames = sv.get_video_frames_generator(video_path)
    return video_info, frames


def get_video_writer(output_path, video_info):
    return sv.VideoSink(output_path, video_info)