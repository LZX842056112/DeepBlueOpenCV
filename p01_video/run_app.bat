@echo off
chcp 65001 >nul
echo ================================
echo   视频处理应用启动脚本
echo ================================
echo.
echo 正在检查Python环境...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo 正在检查依赖包...
pip list | findstr "opencv-python" >nul
if %errorlevel% neq 0 (
    echo 安装OpenCV...
    pip install opencv-python
)

pip list | findstr "gradio" >nul
if %errorlevel% neq 0 (
    echo 安装Gradio...
    pip install gradio
)

pip list | findstr "numpy" >nul
if %errorlevel% neq 0 (
    echo 安装NumPy...
    pip install numpy
)

echo.
echo ================================
echo 选择要运行的版本:
echo 1. 基础版本 (video_app.py)
echo 2. 改进版本 (improved_video_app.py) - 推荐
echo 3. 退出
echo ================================
set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" (
    echo 启动基础版本...
    python video_app.py
) else if "%choice%"=="2" (
    echo 启动改进版本...
    python improved_video_app.py
) else if "%choice%"=="3" (
    echo 退出...
) else (
    echo 无效选择，退出...
)

pause
