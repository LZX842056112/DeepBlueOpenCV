import cv2 as cv
import gradio as gr  # 用于设置前端界面
import numpy as np
import threading     # 导入线程模块
import time
import os
from datetime import datetime


class ImprovedVideoProcessor:
    """视频处理"""
    def __init__(self):
        self.camera = None            # 摄像头对象
        self.is_recording = False     # 录制状态标志
        self.video_writer = None      # 视频写入器
        self.current_frame = None     # 当前帧缓存
        self.recording_thread = None  # 录制线程
        self.camera_thread = None     # 摄像头线程
        self.camera_running = False   # 摄像头运行状态
        
    def start_camera(self, camera_index=0):
        """启动摄像头
        :param camera_index=0: 默认摄像头"""
        try:
            # 检查是否已有摄像头实例在运行；如果有，先释放现有资源，避免冲突
            if self.camera is not None:
                self.release_camera()
            
            # 创建 VideoCapture 对象
            self.camera = cv.VideoCapture(camera_index)
            # 检查摄像头是否成功打开，失败则返回错误信息
            if not self.camera.isOpened():
                return False, "无法打开摄像头，请检查摄像头连接"
            
            # 设置摄像头参数（分辨率: 640×480像素，帧率: 30帧/秒）
            self.camera.set(cv.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv.CAP_PROP_FPS, 30)
            
            # 设置运行标志
            self.camera_running = True
            # 启动摄像头线程，执行 _camera_loop 方法
            self.camera_thread = threading.Thread(target=self._camera_loop)
            # 设置为守护线程，主程序退出时自动结束
            self.camera_thread.daemon = True
            # 启动线程开始持续获取帧
            self.camera_thread.start()
            
            # 成功时返回：操作成功状态，成功消息字符串
            return True, "摄像头启动成功"
        except Exception as e:
            # 捕获所有可能的异常，返回包含具体错误信息的失败状态
            return False, f"摄像头启动失败: {str(e)}"
    
    def _camera_loop(self):
        """摄像头循环，持续获取帧"""
        # self.camera_running：程序控制的运行标志
        # self.camera is not None：确保摄像头对象存在
        # self.camera.isOpened()：确保硬件连接正常
        while self.camera_running and self.camera is not None and self.camera.isOpened():
            # camera.read()：从摄像头读取一帧
            # ret：布尔值，表示读取是否成功
            # frame：成功时包含图像数据，失败时为 None
            ret, frame = self.camera.read()
            # 只有读取成功时才更新当前帧
            if ret:
                self.current_frame = frame
            # 通过睡眠时间控制循环频率，1 ÷ 0.03 ≈ 33.3 帧/秒
            time.sleep(0.03)

    def get_frame(self):
        """获取当前帧"""
        # 有有效帧时：返回转换后的 RGB 帧
        if self.current_frame is not None:
            # 颜色空间转换：转换 BGR 到 RGB
            frame_rgb = cv.cvtColor(self.current_frame, cv.COLOR_BGR2RGB)
            return frame_rgb
        # 无有效帧时：返回 None（避免程序崩溃）
        return None
    
    def start_recording(self, filename=None):
        """开始录制视频
        用于启动视频录制功能，创建视频文件并在后台线程中持续写入摄像头帧。"""
        # 检查摄像头是否已启动
        if self.camera is None or not self.camera_running:
            return "请先启动摄像头"
        
        # 检查是否已经在录制中，避免重复录制
        if self.is_recording:
            return "已经在录制中"
        
        # 文件名处理
        if filename is None or filename.strip() == "":
            # 时间戳格式：年月日_时分秒
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 自动命名：使用时间戳格式 recorded_video_20231201_143052.avi
            filename = f"recorded_video_{timestamp}.avi"
        else:
            # 格式保证：确保文件扩展名为 .avi
            if not filename.endswith('.avi'):
                filename += '.avi'
        
        # 从摄像头获取录制参数：帧宽度和高度，帧率
        frame_width = int(self.camera.get(cv.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.camera.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.camera.get(cv.CAP_PROP_FPS))
        
        # 创建视频写入器
        # 视频编码器设置：
        # - FourCC编码：XVID 是一种常用的 MPEG-4 视频编码
        # - *'XVID'：'X' 'V' 'I' 'D'
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        # 参数传递：文件名、编码器、帧率、分辨率
        self.video_writer = cv.VideoWriter(filename, fourcc, fps, (frame_width, frame_height))
        
        # 创建验证：检查视频写入器是否成功初始化
        if not self.video_writer.isOpened():
            return f"无法创建视频文件: {filename}"
        
        # 多线程录制
        # 状态标志：启动录制状态
        self.is_recording = True
        # 后台线程：创建线程执行 _recording_loop 方法
        self.recording_thread = threading.Thread(target=self._recording_loop)
        # 守护线程：daemon=True 确保主程序退出时自动结束录制
        self.recording_thread.daemon = True
        # 启动录制线程
        self.recording_thread.start()
        
        # 返回包含实际使用文件名的成功消息
        return f"开始录制: {filename}"
    
    def _recording_loop(self):
        """录制循环"""
        # self.is_recording：主控制标志，由 stop_recording() 方法设置为 False
        # self.camera_running：确保摄像头仍在运行
        # self.current_frame is not None：确保有有效的帧数据可写入
        while self.is_recording and self.camera_running and self.current_frame is not None:
            # 持续写入：将当前摄像头帧写入视频文件
            self.video_writer.write(self.current_frame)
            time.sleep(0.03)  # 约 30 fps
    
    def stop_recording(self):
        """停止录制"""
        # 防止重复停止操作
        if not self.is_recording:
            return "当前没有在录制"
        
        # 停止录制循环
        # 设置标志：is_recording = False 使录制循环退出
        self.is_recording = False
        if self.recording_thread is not None:
            # 线程等待：join(timeout=1.0) 等待录制线程安全结束
            # 超时保护：1秒超时防止线程卡死
            self.recording_thread.join(timeout=1.0)
        
        # 释放资源
        if self.video_writer is not None:
            # 释放写入器：release() 方法确保视频文件正确关闭
            self.video_writer.release()
            # 置空引用：防止内存泄漏和重复释放
            # 文件完整性：确保录制的视频文件可以正常播放
            self.video_writer = None
        
        # 提供操作完成的状态反馈
        return "录制已停止"
    
    def release_camera(self):
        """释放摄像头资源"""
        # 设置全局运行标志为 False，使 _camera_loop 循环在下次迭代时自动退出
        self.camera_running = False
        # 检查是否正在录制视频
        if self.is_recording:
            # 确保视频文件正确关闭，避免录制过程中断导致文件损坏
            self.stop_recording()

        # 检查摄像头线程是否存在
        if self.camera_thread is not None:
            # 等待线程结束，最多等待 1 秒，防止线程卡死导致程序无法退出
            self.camera_thread.join(timeout=1.0)
        
        # 资源清理
        if self.camera is not None:
            # 释放摄像头硬件占用
            self.camera.release()
            # 清除对象引用，帮助垃圾回收，让其他程序可以访问摄像头设备
            self.camera = None
    
    def read_video_file(self, video_path):
        """读取视频文件并返回所有帧"""
        try:
            # 创建视频捕获对象
            cap = cv.VideoCapture(video_path)
            # 检查文件是否成功打开失败（原因可能包括：文件不存在、文件路径错误、格式不支持、文件损坏）
            if not cap.isOpened():
                return None, f"无法打开视频文件: {video_path}"
            
            # 读取所有帧的循环
            frames = []
            while True:
                # 读取单帧
                # frame：成功时包含图像数据（BGR格式），失败时为 None
                ret, frame = cap.read()
                # 退出时机：视频文件结束（EOF）、读取错误发生、视频流中断
                if not ret:
                    break
                # 颜色空间转换
                frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                # 将所有帧存储在列表中
                frames.append(frame_rgb)

            # 释放资源：关闭视频文件
            cap.release()
            # 返回结果：所有帧的列表、包含帧数统计的成功消息
            return frames, f"成功读取视频，共 {len(frames)} 帧"
        except Exception as e:
            # 返回统一的错误格式：(None, 错误消息)
            return None, f"读取视频文件失败: {str(e)}"
    
    def get_video_info(self, video_path):
        """获取视频文件信息
        提取视频文件的元数据信息，包括分辨率、帧率、时长等关键参数"""
        try:
            # 打开视频文件
            cap = cv.VideoCapture(video_path)
            # 如果打开失败（文件不存在、格式不支持等），直接返回 None
            if not cap.isOpened():
                return None
            
            # 提取视频属性
            width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))        # 帧宽度
            height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))      # 帧高度
            fps = cap.get(cv.CAP_PROP_FPS)                       # 帧率（帧/秒）
            frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))  # 总帧数
            duration = frame_count / fps if fps > 0 else 0        # 视频时长（秒） = 总帧数 ÷ 帧率
            
            # 资源清理
            cap.release()
            
            # 返回结构化的视频信息
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration
            }
        # 发生任何错误时返回 None
        except Exception as e:
            return None

# 创建视频处理器实例
video_processor = ImprovedVideoProcessor()

def camera_interface(camera_index):
    """摄像头界面
    启动摄像头并获取第一帧用于预览"""
    # 启动摄像头
    # True, "摄像头启动成功"
    # False, f"摄像头启动失败: {str(e)}"
    success, message = video_processor.start_camera(int(camera_index))
    # 错误处理：如果启动失败，立即返回错误信息
    if not success:
        return None, message
    
    # 等待第一帧
    # 0.1秒的延迟确保有可用的帧数据
    time.sleep(0.1)
    # 获取预览帧
    frame = video_processor.get_frame()
    # 返回结果：
    # 成功：返回 (第一帧图像, "摄像头启动成功")
    # 失败：返回 (None, 错误消息)
    return frame, message

def get_camera_frame():
    """获取摄像头帧（用于实时更新）"""
    frame = video_processor.get_frame()
    return frame

def start_recording_interface(filename):
    """开始录制界面"""
    return video_processor.start_recording(filename)

def stop_recording_interface():
    """停止录制界面"""
    return video_processor.stop_recording()

def video_playback_interface(video_file):
    """视频播放界面
    负责处理视频文件的读取、信息提取和预览"""
    # 确保用户已选择视频文件，如果未选择，返回提示信息
    if video_file is None:
        return None, "请选择视频文件", ""
    
    # 获取视频信息
    video_info = video_processor.get_video_info(video_file.name)
    # 信息格式化
    if video_info:
        info_text = f"分辨率: {video_info['width']}x{video_info['height']}\n"
        info_text += f"帧率: {video_info['fps']:.2f} FPS\n"
        info_text += f"总帧数: {video_info['frame_count']}\n"
        info_text += f"时长: {video_info['duration']:.2f} 秒"
    else:
        info_text = "无法获取视频信息"
    
    # 读取整个视频的所有帧到内存
    # frames, f"成功读取视频，共 {len(frames)} 帧"
    # None, f"读取视频文件失败: {str(e)}"
    frames, message = video_processor.read_video_file(video_file.name)
    # 处理读取失败的情况，即使视频信息获取成功，也可能读取失败（文件损坏等）
    if frames is None:
        return None, message, info_text
    
    # 返回第一帧作为预览
    return frames[0], message, info_text

def create_improved_gradio_interface():
    """创建改进的 Gradio 界面
    创建了一个包含三个主要功能模块的 Web 界面：摄像头控制、视频录制和视频播放"""
    with gr.Blocks(title="视频处理应用", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎥 视频处理应用")
        gr.Markdown("使用OpenCV和Gradio实现的视频获取、录制和播放功能")
        
        # 标签页 1
        with gr.Tab("📷 摄像头控制"):
            with gr.Row():
                # 左侧控制面板
                with gr.Column():
                    camera_index = gr.Number(
                        value=0,      # 数字输入
                        label="摄像头索引", 
                        precision=0,  # 只接受整数值
                        info="通常0是默认摄像头，1是外接摄像头"
                    )
                    with gr.Row():
                        # 主要按钮（突出显示）
                        start_camera_btn = gr.Button("启动摄像头", variant="primary")
                        # 次要按钮
                        stop_camera_btn = gr.Button("停止摄像头", variant="secondary")

                # 右侧显示面板
                with gr.Column():
                    camera_output = gr.Image(
                        label="摄像头实时画面",
                        streaming=True
                    )
                    camera_status = gr.Textbox(label="状态", interactive=False)
            
            # 启动：调用 camera_interface，传入摄像头索引
            start_camera_btn.click(
                fn=camera_interface,                    # 点击按钮时调用的函数
                                                        # - 成功：返回 (第一帧图像, "摄像头启动成功")
                                                        # - 失败：返回 (None, 错误消息)
                inputs=[camera_index],                  # 输入参数列表，这里传入摄像头索引值
                outputs=[camera_output, camera_status]  # 输出组件列表，更新图像显示和状态文本
            )
            
            # 停止：使用 lambda 函数释放摄像头并清空显示
            stop_camera_btn.click(
                # video_processor.release_camera() 执行（返回 None）
                # None or (None, "摄像头已停止") → 返回元组 (None, "摄像头已停止")
                fn=lambda: video_processor.release_camera() or (None, "摄像头已停止"),
                # 用 None 清空图像显示，用"摄像头已停止"更新状态文本
                outputs=[camera_output, camera_status]
            )
            
            # 实时更新摄像头画面
            # 注意：Gradio 5.x 版本移除了 every 参数，需要手动处理实时更新
            # 主要是为了 简化组件 API 并 提升框架的稳定性和性能

        # 标签页 2
        with gr.Tab("🎬 视频录制"):
            with gr.Row():
                # 录制控制区
                with gr.Column():
                    filename_input = gr.Textbox(
                        label="文件名（可选）",
                        placeholder="留空将自动生成文件名，格式为 .avi",
                        value=""
                    )
                    with gr.Row():
                        start_record_btn = gr.Button("开始录制", variant="primary")
                        stop_record_btn = gr.Button("停止录制", variant="secondary")

                # 状态和信息区
                with gr.Column():
                    record_status = gr.Textbox(label="录制状态", interactive=False)
                    gr.Markdown("### 录制说明")
                    gr.Markdown("""
                    - 请先启动摄像头再开始录制
                    - 录制的视频将保存为AVI格式
                    - 文件名留空将自动生成带时间戳的文件名
                    - 录制过程中可以实时查看摄像头画面
                    """)
            
            # 开始录制按钮
            start_record_btn.click(
                fn=start_recording_interface,  # 点击按钮时调用的函数，返回：f"开始录制: {filename}"等录制状态消息字符串
                inputs=[filename_input],       # 输入参数，传入用户输入的文件名
                outputs=[record_status]        # 输出组件，只更新录制状态文本框
            )
            
            # 停止录制按钮
            stop_record_btn.click(
                fn=stop_recording_interface,  # 点击按钮时调用的函数，返回："录制已停止"等
                outputs=[record_status]
            )

        # 标签页 3
        with gr.Tab("📹 视频播放"):
            with gr.Row():
                # 文件选择区
                with gr.Column():
                    video_input = gr.File(
                        label="选择视频文件",
                        file_types=[".mp4", ".avi", ".mov", ".mkv", ".wmv"]
                    )
                    play_video_btn = gr.Button("播放视频", variant="primary")
                
                # 视频预览和信息区
                with gr.Column():
                    video_output = gr.Image(label="视频画面预览")
                    video_status = gr.Textbox(label="视频信息", interactive=False)
                    video_info = gr.Textbox(label="视频详细信息", interactive=False, lines=4)
            
            play_video_btn.click(
                fn=video_playback_interface,  # 点击按钮时调用的函数，返回：第一帧 frames[0], message, info_text
                inputs=[video_input],         # 输入参数，传入用户选择的视频文件
                outputs=[video_output, video_status, video_info]  # 输出三个组件，分别更新图像预览、状态信息和详细视频信息
            )

        # 标签页 4
        with gr.Tab("ℹ️ 使用说明"):
            gr.Markdown("""
            ## 使用说明
            
            ### 摄像头控制
            1. 选择摄像头索引（通常0是默认摄像头）
            2. 点击"启动摄像头"开始实时预览
            3. 点击"停止摄像头"释放资源
            
            ### 视频录制
            1. 确保摄像头已启动
            2. 输入文件名（可选，留空自动生成）
            3. 点击"开始录制"开始录制视频
            4. 点击"停止录制"结束录制
            
            ### 视频播放
            1. 选择本地视频文件
            2. 点击"播放视频"查看视频信息和预览
            
            ### 支持的视频格式
            - MP4, AVI, MOV, MKV, WMV
            
            ### 注意事项
            - 确保摄像头设备正常工作
            - 录制前检查存储空间
            - 不同摄像头可能需要不同的索引号
            """)

    # 返回构建好的 Gradio 界面对象
    return demo


if __name__ == "__main__":
    # 创建 Gradio 界面
    demo = create_improved_gradio_interface()
    
    try:
        # 启动 Gradio 界面
        demo.launch(
            server_name="0.0.0.0",  # 本机 + 局域网内其他设备都可以访问；"127.0.0.1" 或 "localhost"：只能本机访问
            server_port=7863,       # 指定端口；如果出现端口冲突，将端口号加 1 即可
            share=False,            # 本地开发时通常设为 False，生产分享时设为 True
            inbrowser=True,         # 启动服务器后自动在默认浏览器中打开应用
            show_error=True         # 在浏览器中显示详细的错误信息（开发调试：便于快速定位和修复问题）
                                    # 生产环境：通常设为 False，避免暴露敏感信息
        )
    except Exception as e:
        print(f"启动失败: {e}")
    finally:
        # 确保释放资源
        video_processor.release_camera()
