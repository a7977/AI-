import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path


def start_system():
    """启动整个系统"""
    print("🚀 启动个性化广告推荐系统")
    print("=" * 50)

    # 启动后端
    print("🔧 启动后端服务器...")
    backend_process = subprocess.Popen(
        [sys.executable, "api_server.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # 等待后端启动
    print("⏳ 等待后端启动...")
    time.sleep(5)

    # 启动前端
    print("🎨 启动前端服务器...")
    frontend_dir = Path(__file__).parent / "frontend"
    if frontend_dir.exists():
        os.chdir(frontend_dir)
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "http.server", "3000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        os.chdir("..")  # 回到项目根目录
    else:
        print("❌ 前端目录不存在")
        frontend_process = None

    # 打开浏览器
    print("🌐 打开浏览器...")
    time.sleep(2)
    webbrowser.open("http://localhost:3000")

    # 显示信息
    print("\n🎯 系统启动完成!")
    print("=" * 50)
    print("📚 访问地址:")
    print("   前端界面: http://localhost:3000")
    print("   API文档: http://localhost:8000/docs")
    print("\n🛑 停止系统: 按 Ctrl+C")
    print("=" * 50)

    try:
        # 等待进程
        if frontend_process:
            frontend_process.wait()
        else:
            backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 停止系统...")
        if frontend_process:
            frontend_process.terminate()
        backend_process.terminate()
        print("✅ 系统已停止")


if __name__ == "__main__":
    start_system()