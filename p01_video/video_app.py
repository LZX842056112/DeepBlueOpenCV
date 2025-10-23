import cv2
import gradio as gr
import numpy as np
import threading
import time
import os
from datetime import datetime

class VideoProcessor:
    def __init__(self):
        self.camera = None
        self.is_recording = False
        self.video_writer = None
        self.current_frame = None
        self.recording_thread = None
        
    def start_camera(self, camera_index=0):
        """启动摄像头"""
        try:
            if self.camera is not None:
                self.camera.release()
            
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                return None, "无法打开摄像头，请检查摄像头连接"
            
            # 设置摄像头参数
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            return self.camera, "摄像头启动成功"
        except Exception as e:
            return None, f"摄像头启动失败: {str(e)}"
    
    def get_frame(self):
        """获取摄像头帧"""
        if self.camera is None or not self.camera.isOpened():
            return None
        
        ret, frame = self.camera.read()
        if ret:
            # 转换BGR到RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame = frame
            return frame_rgb
        return None
    
    def start_recording(self, filename=None):
        """开始录制视频"""
        if self.camera is None or not self.camera.isOpened():
            return "请先启动摄像头"
        
        if self.is_recording:
            return "已经在录制中"
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recorded_video_{timestamp}.avi"
        
        # 获取视频参数
        frame_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.camera.get(cv2.CAP_PROP_FPS))
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
        
        if not self.video_writer.isOpened():
            return f"无法创建视频文件: {filename}"
        
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.recording_thread.start()
        
        return f"开始录制: {filename}"
    
    def _recording_loop(self):
        """录制循环"""
        while self.is_recording and self.camera is not None and self.camera.isOpened():
            if self.current_frame is not None:
                self.video_writer.write(self.current_frame)
            time.sleep(0.03)  # 约30fps
    
    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return "当前没有在录制"
        
        self.is_recording = False
        if self.recording_thread is not None:
            self.recording_thread.join()
        
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        
        return "录制已停止"
    
    def release_camera(self):
        """释放摄像头资源"""
        if self.is_recording:
            self.stop_recording()
        
        if self.camera is not None:
            self.camera.release()
            self.camera = None
    
    def read_video_file(self, video_path):
        """读取视频文件并返回帧"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None, f"无法打开视频文件: {video_path}"
            
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            
            cap.release()
            return frames, f"成功读取视频，共 {len(frames)} 帧"
        except Exception as e:
            return None, f"读取视频文件失败: {str(e)}"

# 创建视频处理器实例
video_processor = VideoProcessor()

def camera_interface(camera_index):
    """摄像头界面"""
    camera, message = video_processor.start_camera(camera_index)
    if camera is None:
        return None, message
    
    frame = video_processor.get_frame()
    return frame, message

def start_recording_interface(filename):
    """开始录制界面"""
    return video_processor.start_recording(filename)

def stop_recording_interface():
    """停止录制界面"""
    return video_processor.stop_recording()

def video_playback_interface(video_file):
    """视频播放界面"""
    if video_file is None:
        return None, "请选择视频文件"
    
    frames, message = video_processor.read_video_file(video_file.name)
    if frames is None:
        return None, message
    
    # 返回第一帧作为预览
    return frames[0], message

def create_gradio_interface():
    """创建Gradio界面"""
    with gr.Blocks(title="视频处理应用", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎥 视频处理应用")
        gr.Markdown("使用OpenCV和Gradio实现的视频获取、录制和播放功能")
        
        with gr.Tab("摄像头控制"):
            with gr.Row():
                with gr.Column():
                    camera_index = gr.Number(value=0, label="摄像头索引", precision=0)
                    start_camera_btn = gr.Button("启动摄像头", variant="primary")
                    stop_camera_btn = gr.Button("停止摄像头", variant="secondary")
                
                with gr.Column():
                    camera_output = gr.Image(label="摄像头画面")
                    camera_status = gr.Textbox(label="状态", interactive=False)
            
            start_camera_btn.click(
                fn=camera_interface,
                inputs=[camera_index],
                outputs=[camera_output, camera_status]
            )
            
            stop_camera_btn.click(
                fn=lambda: (None, "摄像头已停止"),
                outputs=[camera_output, camera_status]
            )
        
        with gr.Tab("视频录制"):
            with gr.Row():
                with gr.Column():
                    filename_input = gr.Textbox(
                        label="文件名（可选）",
                        placeholder="留空将自动生成文件名",
                        value=""
                    )
                    start_record_btn = gr.Button("开始录制", variant="primary")
                    stop_record_btn = gr.Button("停止录制", variant="secondary")
                
                with gr.Column():
                    record_status = gr.Textbox(label="录制状态", interactive=False)
            
            start_record_btn.click(
                fn=start_recording_interface,
                inputs=[filename_input],
                outputs=[record_status]
            )
            
            stop_record_btn.click(
                fn=stop_recording_interface,
                outputs=[record_status]
            )
        
        with gr.Tab("视频播放"):
            with gr.Row():
                with gr.Column():
                    video_input = gr.File(
                        label="选择视频文件",
                        file_types=[".mp4", ".avi", ".mov", ".mkv"]
                    )
                    play_video_btn = gr.Button("播放视频", variant="primary")
                
                with gr.Column():
                    video_output = gr.Image(label="视频画面")
                    video_status = gr.Textbox(label="视频信息", interactive=False)
            
            play_video_btn.click(
                fn=video_playback_interface,
                inputs=[video_input],
                outputs=[video_output, video_status]
            )
        
        # 实时更新摄像头画面
        demo.load(
            fn=lambda: None,
            outputs=None,
            js="""
            () => {
                setInterval(() => {
                    if (document.querySelector('[data-testid="image"]')) {
                        document.querySelector('[data-testid="start-camera"]').click();
                    }
                }, 100);
            }
            """
        )
    
    return demo

if __name__ == "__main__":
    # 创建界面并启动
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7864,
        share=False,
        inbrowser=True
    )
