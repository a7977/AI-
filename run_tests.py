# run_tests.py
"""测试运行脚本"""

import os
import sys
from datetime import datetime


def setup_test_environment():
    """设置测试环境"""
    print("设置测试环境...")

    # 创建截图目录
    screenshot_dir = "./test_screenshots/"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
        print(f"创建截图目录: {screenshot_dir}")

    # 检查ChromeDriver
    try:
        from selenium import webdriver
        driver = webdriver.Edge()
        driver.quit()
        print("ChromeDriver 可用")
    except Exception as e:
        print(f"ChromeDriver 问题: {e}")
        return False

    return True


def main():
    """主运行函数"""
    print("个性化广告推荐系统 - UI自动化测试")
    print("=" * 60)

    # 记录开始时间
    start_time = datetime.now()
    print(f"测试开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 设置环境
    if not setup_test_environment():
        print("测试环境设置失败，退出测试")
        return

    # 运行测试
    from test_ui_functionality import run_tests
    result = run_tests()

    # 记录结束时间
    end_time = datetime.now()
    duration = end_time - start_time

    print(f"测试结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总耗时: {duration}")

    # 返回退出码
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()