# test_ui_functionality.py
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class AdRecommendationSystemUITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """测试类初始化 - 启动浏览器"""
        print("启动浏览器...")
        cls.driver = webdriver.Edge()
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "http://localhost:3000"  # 系统运行的本地端口

    def setUp(self):
        """每个测试用例前的准备工作"""
        self.driver.get(self.base_url)
        time.sleep(2)  # 等待页面加载

    def test_01_system_initialization(self):
        """测试1: 系统初始化加载"""
        print("测试系统初始化...")

        # 检查页面标题
        self.assertIn("个性化广告推荐系统", self.driver.title)

        # 检查导航栏
        nav_logo = self.driver.find_element(By.CLASS_NAME, "nav-logo")
        self.assertIsNotNone(nav_logo)

        # 检查统计卡片是否加载
        stat_cards = self.driver.find_elements(By.CLASS_NAME, "stat-card")
        self.assertGreaterEqual(len(stat_cards), 4)

        # 检查用户数量显示
        user_count = self.driver.find_element(By.ID, "user-count")
        self.assertIsNotNone(user_count.text)

        print("系统初始化测试通过")

    def test_02_navigation_functionality(self):
        """测试2: 导航功能"""
        print("测试导航功能...")

        # 获取所有导航链接
        nav_links = self.driver.find_elements(By.CLASS_NAME, "nav-link")
        self.assertEqual(len(nav_links), 3)

        # 测试控制台导航
        dashboard_link = self.driver.find_element(By.XPATH, "//a[@href='#dashboard']")
        dashboard_link.click()
        time.sleep(1)

        dashboard_section = self.driver.find_element(By.ID, "dashboard")
        self.assertTrue("active" in dashboard_section.get_attribute("class"))

        # 测试推荐管理导航
        recommendations_link = self.driver.find_element(By.XPATH, "//a[@href='#recommendations']")
        recommendations_link.click()
        time.sleep(1)

        recommendations_section = self.driver.find_element(By.ID, "recommendations")
        self.assertTrue("active" in recommendations_section.get_attribute("class"))

        # 测试数据分析导航
        analytics_link = self.driver.find_element(By.XPATH, "//a[@href='#analytics']")
        analytics_link.click()
        time.sleep(1)

        analytics_section = self.driver.find_element(By.ID, "analytics")
        self.assertTrue("active" in analytics_section.get_attribute("class"))

        print("导航功能测试通过")

    def test_03_user_selection_and_recommendations(self):
        """测试3: 用户选择和推荐功能"""
        print("测试用户选择和推荐功能...")

        # 确保在控制台页面
        dashboard_link = self.driver.find_element(By.XPATH, "//a[@href='#dashboard']")
        dashboard_link.click()
        time.sleep(1)

        # 查找用户选择器
        user_select = self.wait.until(
            EC.presence_of_element_located((By.ID, "userSelect"))
        )

        # 检查是否有用户选项
        user_options = user_select.find_elements(By.TAG_NAME, "option")
        self.assertGreater(len(user_options), 1)  # 至少有一个"选择用户..."选项

        # 如果有用户数据，选择第一个用户
        if len(user_options) > 1:
            # 选择第一个真实用户（跳过"选择用户..."选项）
            user_select.click()
            user_options[1].click()  # 选择第一个用户

            # 检查获取推荐按钮是否启用
            get_recommendations_btn = self.driver.find_element(By.ID, "getRecommendations")
            self.assertFalse(get_recommendations_btn.get_attribute("disabled"))

            # 点击获取推荐按钮
            get_recommendations_btn.click()
            time.sleep(3)  # 等待推荐加载

            # 检查推荐结果区域
            recommendation_results = self.driver.find_element(By.ID, "recommendationResults")
            self.assertIsNotNone(recommendation_results)

            # 检查是否有推荐卡片加载
            ad_cards = recommendation_results.find_elements(By.CLASS_NAME, "ad-card")
            if ad_cards:
                # 如果有推荐卡片，测试交互按钮
                click_buttons = recommendation_results.find_elements(
                    By.XPATH, ".//button[contains(text(), '模拟点击')]"
                )
                if click_buttons:
                    # 测试模拟点击功能
                    click_buttons[0].click()
                    time.sleep(1)

        print("用户选择和推荐功能测试通过")

    def test_04_management_sections(self):
        """测试4: 管理页面功能"""
        print("测试管理页面功能...")

        # 导航到推荐管理页面
        recommendations_link = self.driver.find_element(By.XPATH, "//a[@href='#recommendations']")
        recommendations_link.click()
        time.sleep(2)

        # 检查用户管理区域
        user_list = self.driver.find_element(By.ID, "userList")
        self.assertIsNotNone(user_list)

        # 检查广告管理区域
        ad_list = self.driver.find_element(By.ID, "adList")
        self.assertIsNotNone(ad_list)

        # 测试用户操作按钮（如果存在用户）
        user_items = user_list.find_elements(By.CLASS_NAME, "user-item")
        if user_items:
            # 查找查看推荐按钮
            recommendation_buttons = user_list.find_elements(
                By.XPATH, ".//button[contains(text(), '查看推荐')]"
            )
            if recommendation_buttons:
                recommendation_buttons[0].click()
                time.sleep(2)

                # 验证是否跳转回控制台
                dashboard_section = self.driver.find_element(By.ID, "dashboard")
                self.assertTrue("active" in dashboard_section.get_attribute("class"))

        print("管理页面功能测试通过")

    def test_05_interaction_modal_functionality(self):
        """测试5: 交互模态框功能"""
        print("测试交互模态框功能...")

        # 先获取一些推荐
        self.driver.get(self.base_url)
        time.sleep(2)

        dashboard_link = self.driver.find_element(By.XPATH, "//a[@href='#dashboard']")
        dashboard_link.click()
        time.sleep(1)

        user_select = self.driver.find_element(By.ID, "userSelect")
        user_options = user_select.find_elements(By.TAG_NAME, "option")

        if len(user_options) > 1:
            user_select.click()
            user_options[1].click()

            get_recommendations_btn = self.driver.find_element(By.ID, "getRecommendations")
            get_recommendations_btn.click()
            time.sleep(3)

            # 查找记录交互按钮
            recommendation_results = self.driver.find_element(By.ID, "recommendationResults")
            interaction_buttons = recommendation_results.find_elements(
                By.XPATH, ".//button[contains(text(), '记录交互')]"
            )

            if interaction_buttons:
                # 打开交互模态框
                interaction_buttons[0].click()
                time.sleep(1)

                # 检查模态框是否显示
                modal = self.driver.find_element(By.ID, "interactionModal")
                self.assertEqual(modal.value_of_css_property("display"), "block")

                # 检查表单字段
                user_field = self.driver.find_element(By.ID, "interactionUser")
                ad_field = self.driver.find_element(By.ID, "interactionAd")
                action_select = self.driver.find_element(By.ID, "interactionAction")

                self.assertTrue(user_field.get_attribute("readonly"))
                self.assertTrue(ad_field.get_attribute("readonly"))

                # 测试取消按钮
                cancel_btn = self.driver.find_element(By.ID, "cancelInteraction")
                cancel_btn.click()
                time.sleep(1)

                # 检查模态框是否关闭
                self.assertNotEqual(modal.value_of_css_property("display"), "block")

        print("交互模态框功能测试通过")

    def test_06_loading_states(self):
        """测试6: 加载状态测试"""
        print("测试加载状态...")

        # 检查加载覆盖层初始状态（应该隐藏）
        loading_overlay = self.driver.find_element(By.ID, "loading")
        self.assertEqual(loading_overlay.value_of_css_property("display"), "none")

        print("加载状态测试通过")

    def test_07_responsive_design(self):
        """测试7: 响应式设计基础测试"""
        print("测试响应式设计...")

        # 测试移动端尺寸
        self.driver.set_window_size(375, 667)  # iPhone 6/7/8尺寸
        time.sleep(1)

        # 检查导航栏在移动端的显示
        nav_container = self.driver.find_element(By.CLASS_NAME, "nav-container")
        self.assertIsNotNone(nav_container)

        # 恢复窗口大小
        self.driver.maximize_window()

        print("响应式设计测试通过")

    def test_08_error_handling(self):
        """测试8: 错误处理测试"""
        print("测试错误处理...")

        # 测试在没有选择用户时点击获取推荐按钮
        dashboard_link = self.driver.find_element(By.XPATH, "//a[@href='#dashboard']")
        dashboard_link.click()
        time.sleep(1)

        # 确保没有选择用户
        user_select = self.driver.find_element(By.ID, "userSelect")
        user_select.click()
        # 选择"选择用户..."选项（第一个选项）
        user_options = user_select.find_elements(By.TAG_NAME, "option")
        user_options[0].click()

        # 检查获取推荐按钮是否被禁用
        get_recommendations_btn = self.driver.find_element(By.ID, "getRecommendations")
        self.assertTrue(get_recommendations_btn.get_attribute("disabled"))

        print("错误处理测试通过")

    @classmethod
    def tearDownClass(cls):
        """测试类清理 - 关闭浏览器"""
        print("清理测试环境...")
        cls.driver.quit()
        print("测试完成，浏览器已关闭")


def run_tests():
    """运行测试套件"""
    # 创建测试套件
    suite = unittest.TestSuite()

    # 按顺序添加测试用例
    test_cases = [
        'test_01_system_initialization',
        'test_02_navigation_functionality',
        'test_03_user_selection_and_recommendations',
        'test_04_management_sections',
        'test_05_interaction_modal_functionality',
        'test_06_loading_states',
        'test_07_responsive_design',
        'test_08_error_handling'
    ]

    for test_case in test_cases:
        suite.addTest(AdRecommendationSystemUITest(test_case))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试总结
    print("\n" + "=" * 50)
    print("测试总结:")
    print(f"通过的测试: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败的测试: {len(result.failures)}")
    print(f"错误的测试: {len(result.errors)}")
    print("=" * 50)

    return result


if __name__ == "__main__":
    print("开始个性化广告推荐系统UI自动化测试")
    print("=" * 60)

    run_tests()