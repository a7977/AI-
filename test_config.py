# test_config.py
"""测试配置文件"""


class TestConfig:
    # 浏览器配置
    BROWSER = "edge"
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 15

    # 应用URL
    BASE_URL = "http://localhost:8000"

    # 测试数据
    TEST_USER = "user_1"  # 测试用户

    # 截图配置
    SCREENSHOT_DIR = "./test_screenshots/"

    # 测试模式
    HEADLESS = False  # 是否无头模式运行