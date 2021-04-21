# Generated by Selenium IDE
import subprocess
from collections import Counter
from urllib.parse import quote_plus

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config import *
from log import logger, color
from util import async_message_box
from version import now_version


# 在github action环境下登录异常
class GithubActionLoginException(Exception):
    pass


class LoginResult(ConfigInterface):
    def __init__(self, uin="", skey="", openid="", p_skey="", vuserid="", qc_openid="", qc_k="", apps_p_skey="", xinyue_openid="", xinyue_access_token=""):
        super().__init__()
        # 使用炎炎夏日活动界面得到
        self.uin = uin
        self.skey = skey
        # 登录QQ空间得到
        self.p_skey = p_skey
        # 使用心悦活动界面得到
        self.openid = openid
        # 使用腾讯视频相关页面得到
        self.vuserid = vuserid
        # 登录电脑管家页面得到
        self.qc_openid = qc_openid
        self.qc_k = qc_k
        # 分享用p_skey
        self.apps_p_skey = apps_p_skey
        # 心悦相关信息
        self.xinyue_openid = xinyue_openid
        self.xinyue_access_token = xinyue_access_token


class QQLogin():
    login_type_auto_login = "账密自动登录"
    login_type_qr_login = "扫码登录"

    login_mode_normal = "normal"
    login_mode_xinyue = "xinyue"
    login_mode_qzone = "qzone"
    login_mode_guanjia = "guanjia"
    login_mode_wegame = "wegame"

    bandizip_executable_path = os.path.realpath("./bandizip_portable/bz.exe")
    chrome_major_version = 89

    default_window_width = 390
    default_window_height = 360

    def __init__(self, common_config):
        self.cfg = common_config  # type: CommonConfig
        self.driver = None  # type: WebDriver
        self.window_title = ""
        self.time_start_login = datetime.datetime.now()

    def prepare_chrome(self, ctx, login_type, login_url):
        logger.info(color("fg_bold_cyan") + f"{self.name} 正在初始化chrome driver（版本为{self.get_chrome_major_version()}），用以进行【{ctx}】相关操作")
        caps = DesiredCapabilities().CHROME
        # caps["pageLoadStrategy"] = "normal"  #  Waits for full page load
        caps["pageLoadStrategy"] = "none"  # Do not wait for full page load

        options = Options()
        options.add_argument(f"window-size={self.default_window_width},{self.default_window_height}")
        options.add_argument(f"app={login_url}")
        # 设置静音
        options.add_argument("--mute-audio")
        if not self.cfg._debug_show_chrome_logs:
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
            selenium_logger.setLevel(logging.WARNING)
            # 使用Selenium期间将urllib的日志关闭
            urllib_logger = logging.getLogger('urllib3.connectionpool')
            urllib_logger.setLevel(logging.WARNING)
        if self.cfg.run_in_headless_mode:
            if login_type == self.login_type_auto_login:
                logger.warning(f"{self.name} 已配置在自动登录模式时使用headless模式运行chrome")
                options.headless = True
            else:
                logger.warning(f"{self.name} 扫码登录模式不使用headless模式")

        inited = False

        try:
            if not self.cfg.force_use_portable_chrome:
                # 如果未强制使用便携版chrome，则首先尝试使用系统安装的chrome
                self.driver = webdriver.Chrome(executable_path=self.chrome_driver_executable_path(), desired_capabilities=caps, options=options)
                logger.info(f"{self.name} 使用自带chrome")
                inited = True
        except:
            pass

        if not inited:
            # 如果找不到，则尝试使用打包的便携版chrome
            # 先判定本地是否有便携版压缩包，若无则提示去网盘下载
            if not os.path.isfile(self.chrome_binary_7z()):
                msg = (
                    "================ 这一段是问题描述 ================\n"
                    "当前电脑未发现{version}版本chrome浏览器版本，且当前目录无便携版chrome浏览器的压缩包({zip_name})\n"
                    "\n"
                    "================ 这一段是解决方法 ================\n"
                    "如果不想影响系统浏览器，请在稍后打开的网盘页面中下载[{zip_name}]，并放到小助手的exe所在目录（注意：是把这个压缩包原原本本地放到这个目录里，而不是解压后再放过来！！！），然后重新打开程序~\n"
                    "如果愿意装一个浏览器，请在稍后打开的网盘页面中下载{installer_name}，下载完成后双击安装即可\n"
                    "(一定要看清版本，如果发现网盘里的便携版和安装版版本都比提示里的高（比如这里提示87，网盘里显示89），建议直接下个最新的小助手压缩包，解压后把配置文件复制过去~)\n"
                    "\n"
                    "================ 这一段是补充说明 ================\n"
                    "1. 如果之前版本已经下载过这个文件，可以直接去之前版本复制过来~不需要再下载一次~\n"
                    "2. 如果之前一直都运行的好好的，今天突然不行了，可能是以下原因\n"
                    "2.1 系统安装的chrome自动升级到新版本了，当前小助手使用的驱动不支持该版本。解决办法：下载当前版本小助手对应版本的便携版chrome\n"
                    "2.2 新版小助手升级了驱动，当前系统安装的chrome或便携版chrome的版本太低了。解决办法：升级新版本chrome或下载新版本的便携版chrome\n"
                    "\n"
                    "------- 如果这样还有人进群问，将直接踢出群聊 -------\n"
                ).format(zip_name=os.path.basename(self.chrome_binary_7z()), installer_name=self.chrome_installer_name(), version=self.get_chrome_major_version())
                async_message_box(msg, f"你没有{self.get_chrome_major_version()}版本的chrome浏览器，需要安装完整版或下载便携版", icon=win32con.MB_ICONERROR, open_url="https://fzls.lanzous.com/s/djc-tools")
                os.system("PAUSE")
                exit(-1)

            # 先判断便携版chrome是否已解压
            if not os.path.isdir(self.chrome_binary_directory()):
                logger.info(f"{self.name} 自动解压便携版chrome到当前目录")
                subprocess.call([self.bandizip_executable_path, "x", "-target:auto", self.chrome_binary_7z()])

            # 然后使用本地的chrome来初始化driver对象
            options.binary_location = self.chrome_binary_location()
            # you may need some other options
            options.add_argument('--no-sandbox')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--no-first-run')
            self.driver = webdriver.Chrome(executable_path=self.chrome_driver_executable_path(), desired_capabilities=caps, options=options)
            logger.info(f"{self.name} 使用便携版chrome")

        self.cookies = self.driver.get_cookies()

    def destroy_chrome(self):
        logger.info(f"{self.name} 释放chrome实例")
        if self.driver is not None:
            # 最小化网页
            self.driver.minimize_window()
            threading.Thread(target=self.driver.quit, daemon=True).start()

        # 使用Selenium结束将日志级别改回去
        urllib_logger = logging.getLogger('urllib3.connectionpool')
        urllib_logger.setLevel(logger.level)

    def extract_portable_chrome_ahead(self):
        """
        若存在便携版压缩包，且未解压，则预先解压缩
        主要用于处理多进程模式下，可能多个进程同时尝试解压导致的问题
        :return:
        """
        if os.path.isfile(self.chrome_binary_7z()) and not os.path.isdir(self.chrome_binary_directory()):
            logger.info("预先在主进程自动解压便携版chrome到当前目录，避免后续多进程同时尝试解压")
            subprocess.call([self.bandizip_executable_path, "x", "-target:auto", self.chrome_binary_7z()])

    def chrome_driver_executable_path(self):
        return os.path.realpath(f"./chromedriver_{self.get_chrome_major_version()}.exe")

    def chrome_binary_7z(self):
        return os.path.realpath(f"./chrome_portable_{self.get_chrome_major_version()}.7z")

    def chrome_binary_directory(self):
        return os.path.realpath(f"./chrome_portable_{self.get_chrome_major_version()}")

    def chrome_binary_location(self):
        return os.path.realpath(f"./chrome_portable_{self.get_chrome_major_version()}/chrome.exe")

    def chrome_installer_name(self):
        return f"Chrome_{self.get_chrome_major_version()}.(小版本号)_普通安装包_非便携版.exe"

    def get_chrome_major_version(self):
        if self.cfg is None or self.cfg.force_use_chrome_major_version == 0:
            return self.chrome_major_version
        else:
            return self.cfg.force_use_chrome_major_version

    def login(self, account, password, login_mode="normal", name=""):
        """
        自动登录指定账号，并返回登陆后的cookie中包含的uin、skey数据
        :param account: 账号
        :param password: 密码
        :rtype: LoginResult
        """
        self.name = name
        self.window_title = f"将登录 {name}({account}) - {login_mode}"
        logger.info(f"{name} 即将开始自动登录，无需任何手动操作，等待其完成即可")
        logger.info(f"{name} 如果出现报错，可以尝试调高相关超时时间然后重新执行脚本")

        def login_with_account_and_password():
            logger.info(color("bold_green") + f"{name} 当前为自动登录模式，请不要手动操作网页，否则可能会导致登录流程失败")

            # 切换到自动登录界面
            logger.info(f"{name} 等待#switcher_plogin加载完毕")
            time.sleep(self.cfg.login.open_url_wait_time)
            WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.ID, 'switcher_plogin')))

            # 选择密码登录
            self.driver.find_element(By.ID, "switcher_plogin").click()

            # 输入账号
            self.driver.find_element(By.ID, "u").send_keys(account)
            # 输入密码
            self.driver.find_element(By.ID, "p").send_keys(password)

            logger.info(f"{name} 等待一会，确保登录键可以点击")
            time.sleep(3)

            # 发送登录请求
            self.driver.find_element(By.ID, "login_button").click()

            # 尝试自动处理验证码
            self.try_auto_resolve_captcha()

        return self._login(self.login_type_auto_login, login_action_fn=login_with_account_and_password, login_mode=login_mode)

    def qr_login(self, login_mode="normal", name=""):
        """
        二维码登录，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """
        logger.info("即将开始扫码登录，请在弹出的网页中扫码登录~")
        self.name = name
        self.window_title = f"请扫码 {name} - {login_mode}"

        def login_with_qr_code():
            logger.info(color("bold_yellow") + f"请在{self.cfg.login.login_timeout}s内完成扫码登录操作或快捷登录操作")

        return self._login(self.login_type_qr_login, login_action_fn=login_with_qr_code, login_mode=login_mode)

    def _login(self, login_type, login_action_fn=None, login_mode="normal"):
        # 结合历史数据和配置，计算各轮重试等待的时间
        login_retry_key = "login_retry_key"
        db = load_db()
        login_retry_data = db.get(login_retry_key, {
            "recommended_first_retry_timeout": 0,
            "history_success_timeouts": [],
        })

        actual_retry_count = self.cfg.login.max_retry_count - 1

        retry_timeouts = []
        if actual_retry_count == 1:
            retry_timeouts = [self.cfg.login.retry_wait_time]
        elif actual_retry_count > 1:
            # 默认重试时间为按时长等分递增
            retry_timeouts = list([int(idx / actual_retry_count * self.cfg.login.retry_wait_time) for idx in range_from_one(actual_retry_count)])
            if login_retry_data['recommended_first_retry_timeout'] != 0:
                # 如果有历史成功数据，则以推荐首次重试时间为第一次重试的时间，后续重试次数则等分递增
                retry_timeouts = [login_retry_data["recommended_first_retry_timeout"]]
                remaining_retry_count = actual_retry_count - 1
                retry_timeouts.extend(list([int(idx / (remaining_retry_count) * self.cfg.login.retry_wait_time) for idx in range_from_one(remaining_retry_count)]))

        for idx in range_from_one(self.cfg.login.max_retry_count):
            self.login_mode = login_mode

            # note: 如果get_login_url的surl变更，代码中确认登录完成的地方也要一起改
            login_fn, suffix, login_url = {
                self.login_mode_normal: (
                    self._login_real,
                    "",
                    self.get_login_url(21000127, 8, "https://dnf.qq.com/"),
                ),
                self.login_mode_xinyue: (
                    self._login_xinyue_real,
                    "心悦",
                    "https://xinyue.qq.com/act/a20210317dnf/index_pc.html",
                ),
                self.login_mode_qzone: (
                    self._login_qzone,
                    "QQ空间业务（如抽卡等需要用到）（不启用QQ空间系活动就不会触发本类型的登录，完整列表参见示例配置）",
                    self.get_login_url(15000103, 5, "https://act.qzone.qq.com/"),
                ),
                self.login_mode_guanjia: (
                    self._login_guanjia,
                    "电脑管家（如电脑管家蚊子腿需要用到，完整列表参见示例配置）",
                    "http://guanjia.qq.com/act/cop/20210127dnf/pc/",
                ),
                self.login_mode_wegame: (
                    self._login_wegame,
                    "wegame（获取wegame相关api需要用到）",
                    self.get_login_url(1600001063, 733, "https://www.wegame.com.cn/"),
                ),
            }[login_mode]

            ctx = f"{login_type}-{suffix}"

            login_exception = None

            try:
                if idx > 1:
                    logger.info(color("bold_cyan") + f"已经是第{idx}次登陆，说明可能出现某些问题，将关闭隐藏浏览器选项，方便观察出现什么问题")
                    self.cfg.run_in_headless_mode = False

                self.prepare_chrome(ctx, login_type, login_url)

                return login_fn(ctx, login_action_fn=login_action_fn)
            except Exception as e:
                login_exception = e
            finally:
                login_result = color("bold_green") + "登录成功"
                if login_exception is not None:
                    login_result = color("bold_cyan") + "登录失败"

                used_time = datetime.datetime.now() - self.time_start_login
                logger.info("")
                logger.info(f"[{login_result}] " + color("bold_yellow") + f"{self.name} 第{idx}/{self.cfg.login.max_retry_count}次 {ctx} 共耗时为 {used_time}")
                logger.info("")
                self.destroy_chrome()

                if login_exception is not None:
                    # 登陆失败
                    lc = self.cfg.login

                    msg = f"{self.name} 第{idx}/{lc.max_retry_count}次尝试登录出错"
                    if idx < lc.max_retry_count:
                        # 每次等待时长线性递增
                        wait_time = retry_timeouts[idx - 1]
                        msg += f"，等待{wait_time}秒后重试"
                        msg += f"\n\t当前登录重试等待时间序列：{retry_timeouts}"
                        msg += f"\n\t根据历史数据得出的推荐重试等待时间：{login_retry_data['recommended_first_retry_timeout']}"
                        if use_by_myself():
                            msg += f"\n\t(仅我可见)历史重试成功等待时间列表：{login_retry_data['history_success_timeouts']}"
                        logger.exception(msg, exc_info=login_exception)
                        count_down(f"{truncate(self.name, 20):20s} 重试", wait_time)
                    else:
                        logger.exception(msg, exc_info=login_exception)
                else:
                    # 登陆成功
                    if idx > 1:
                        # 第idx-1次的重试成功了，尝试更新历史数据
                        success_timeout = retry_timeouts[idx - 2]
                        if login_retry_data['recommended_first_retry_timeout'] == 0:
                            login_retry_data['recommended_first_retry_timeout'] = success_timeout
                        else:
                            cr = self.cfg.login.recommended_retry_wait_time_change_rate
                            login_retry_data['recommended_first_retry_timeout'] = int((1 - cr) * login_retry_data['recommended_first_retry_timeout'] + cr * success_timeout)
                        login_retry_data['history_success_timeouts'].append(success_timeout)

                        db[login_retry_key] = login_retry_data
                        save_db(db)

                        if use_by_myself():
                            logger.info(f"(仅我可见){self.name} 重试{idx - 1}次后成功登录，本次重试等待时间为{success_timeout}，当前历史重试数据为{login_retry_data}")

        # 能走到这里说明登录失败了，大概率是网络不行
        logger.warning(color("bold_yellow") + (
            f"已经尝试登录 {self.name} {self.cfg.login.max_retry_count}次，均已失败，大概率是网络有问题\n"
            "建议依次尝试下列措施\n"
            "1. 重新打开程序\n"
            "2. 重启电脑\n"
            "3. 更换dns，如谷歌、阿里、腾讯、百度的dns，具体更换方法请百度\n"
            "4. 重装网卡驱动\n"
            "5. 换个网络环境\n"
            "6. 换台电脑\n"
        ))
        if login_mode == self.login_mode_guanjia:
            logger.warning(color("bold_cyan") + "如果一直卡在管家登录流程，可能是你网不行，建议多试几次，真不行就去配置工具关闭管家活动的开关（不是关闭这个登录页面）~")

        if is_run_in_github_action():
            # github action 环境下特殊处理
            raise GithubActionLoginException()

        raise Exception("网络很有可能有问题（备注：访问其他网页没问题不代表访问这个网页也没问题-。-）")

    def _login_real(self, login_type, login_action_fn=None):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """
        s_url = "https://dnf.qq.com/"

        def switch_to_login_frame_fn():
            if self.need_reopen_url(login_type):
                self.get_switch_to_login_frame_fn(21000127, 8, s_url)

        def assert_login_finished_fn():
            logger.info(f"{self.name} 请等待网页切换为目标网页，则说明已经登录完成了，最大等待时长为{self.cfg.login.login_finished_timeout}")
            WebDriverWait(self.driver, self.cfg.login.login_finished_timeout).until(expected_conditions.url_to_be(s_url))

        self._login_common(login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn)

        # 从cookie中获取uin和skey
        return LoginResult(uin=self.get_cookie("uin"), skey=self.get_cookie("skey"),
                           p_skey=self.get_cookie("p_skey"), vuserid=self.get_cookie("vuserid"),
                           apps_p_skey=self.get_cookie("apps_p_skey"),
                           )

    def _login_qzone(self, login_type, login_action_fn=None):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """
        s_url = "https://act.qzone.qq.com/"

        def switch_to_login_frame_fn():
            if self.need_reopen_url(login_type):
                self.get_switch_to_login_frame_fn(15000103, 5, s_url)

        def assert_login_finished_fn():
            logger.info(f"{self.name} 请等待网页切换为目标网页，则说明已经登录完成了，最大等待时长为{self.cfg.login.login_finished_timeout}")
            WebDriverWait(self.driver, self.cfg.login.login_finished_timeout).until(expected_conditions.url_to_be(s_url))

        self._login_common(login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn)

        # 从cookie中获取uin和skey
        return LoginResult(p_skey=self.get_cookie("p_skey"),
                           uin=self.get_cookie("uin"), skey=self.get_cookie("skey"), vuserid=self.get_cookie("vuserid"),
                           apps_p_skey=self.get_cookie("apps_p_skey"),
                           )

    def _login_guanjia(self, login_type, login_action_fn=None):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """

        def switch_to_login_frame_fn():
            if self.need_reopen_url(login_type):
                logger.info("打开活动界面")
                self.open_url_on_start("http://guanjia.qq.com/act/cop/20210127dnf/pc/")

            self.set_window_size()

            logger.info("等待登录按钮#dologin出来，确保加载完成")
            WebDriverWait(self.driver, self.cfg.login.load_page_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "dologin")))

            logger.info("等待5秒，确保加载完成")
            time.sleep(5)

            logger.info("点击登录按钮")
            self.driver.find_element(By.ID, "dologin").click()

            logger.info("等待#login_ifr显示出来并切换")
            WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "login_ifr")))
            loginIframe = self.driver.find_element_by_id("login_ifr")
            self.driver.switch_to.frame(loginIframe)

            logger.info("等待#login_ifr#ptlogin_iframe加载完毕并切换")
            WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "ptlogin_iframe")))
            ptlogin_iframe = self.driver.find_element_by_id("ptlogin_iframe")
            self.driver.switch_to.frame(ptlogin_iframe)

        def assert_login_finished_fn():
            logger.info(f"{self.name} 请等待#logined的div可见，则说明已经登录完成了，最大等待时长为{self.cfg.login.login_finished_timeout}")
            WebDriverWait(self.driver, self.cfg.login.login_finished_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "logined")))

        self._login_common(login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn)

        # 从cookie中获取uin和skey
        return LoginResult(qc_openid=self.get_cookie("__qc__openid"), qc_k=self.get_cookie("__qc__k"),
                           uin=self.get_cookie("uin"), skey=self.get_cookie("skey"), p_skey=self.get_cookie("p_skey"), vuserid=self.get_cookie("vuserid"))

    def _login_wegame(self, login_type, login_action_fn=None):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """
        s_url = "https://www.wegame.com.cn/"

        def switch_to_login_frame_fn():
            if self.need_reopen_url(login_type):
                self.get_switch_to_login_frame_fn(1600001063, 733, s_url)

        def assert_login_finished_fn():
            logger.info(f"{self.name} 请等待网页切换为目标网页，则说明已经登录完成了，最大等待时长为{self.cfg.login.login_finished_timeout}")
            WebDriverWait(self.driver, self.cfg.login.login_finished_timeout).until(expected_conditions.url_to_be(s_url))

        self._login_common(login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn)

        # 从cookie中获取uin和skey
        return LoginResult(uin=self.get_cookie("uin"), skey=self.get_cookie("skey"), p_skey=self.get_cookie("p_skey"))

    def _login_xinyue_real(self, login_type, login_action_fn=None):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """

        def switch_to_login_frame_fn():
            if self.need_reopen_url(login_type):
                logger.info("打开活动界面")
                self.open_url_on_start("https://xinyue.qq.com/act/a20210317dnf/index_pc.html")

            self.set_window_size()

            logger.info("等待#loginframe加载完毕并切换")
            WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "loginframe")))
            login_frame = self.driver.find_element_by_class_name("loginframe")
            self.driver.switch_to.frame(login_frame)

            logger.info("等待#loginframe#ptlogin_iframe加载完毕并切换")
            WebDriverWait(self.driver, self.cfg.login.load_login_iframe_timeout).until(expected_conditions.visibility_of_element_located((By.ID, "ptlogin_iframe")))
            ptlogin_iframe = self.driver.find_element_by_id("ptlogin_iframe")
            self.driver.switch_to.frame(ptlogin_iframe)

        def assert_login_finished_fn():
            logger.info(f"{self.name} 请等待#btn_wxqclogin可见，则说明已经登录完成了，最大等待时长为{self.cfg.login.login_finished_timeout}")
            WebDriverWait(self.driver, self.cfg.login.login_finished_timeout).until(expected_conditions.invisibility_of_element_located((By.ID, "btn_wxqclogin")))

            logger.info("等待1s，确认获取openid的请求完成")
            time.sleep(1)

            # 确保openid已设置
            for t in range(1, 3 + 1):
                if self.driver.get_cookie('openid') is None:
                    logger.info(f"第{t}/3未在心悦的cookie中找到openid，等一秒再试")
                    time.sleep(1)
                    continue
                break

        self._login_common(login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn)

        # 从cookie中获取openid
        return LoginResult(openid=self.get_cookie("openid"), xinyue_openid=self.get_cookie("xinyue_openid"), xinyue_access_token=self.get_cookie("xinyue_access_token"))

    def get_switch_to_login_frame_fn(self, appid, daid, s_url, style=34, theme=2):
        # 参数：appid  daid
        # 21000127      8       普通游戏活动        https://dnf.qq.com/
        # 15000103      5       qq空间             https://act.qzone.qq.com/
        # 716027609     383     安全管家            https://guanjia.qq.com/
        # 1600001063    733     wegame             https://www.wegame.com.cn/
        # 716027609     383     心悦战场            https://xinyue.qq.com/
        # 21000115      8       腾讯游戏/移动游戏    https://dnf.qq.com/
        # 532001604     ?       腾讯视频            https://film.qq.com/

        # 参数：s_url
        # 登陆完毕后要跳转的网页

        # 参数：style
        # 仅二维码 样式一（QQ邮箱设备锁）：30
        # 二维码/快捷/密码 样式一（整个页面-与之前的兼容（其实就是原来点登录的弹窗））：0/11-15/17/19-23/32-33/40
        # 二维码/快捷/密码 样式二（限定大小）：25
        # 二维码/快捷/密码 样式三（限定大小-格式美化）：34 re: 选用
        # 二维码/快捷/密码 样式四（居中-移动端风格-需要在手机上，且安装手机QQ后才可以）：35/42

        # 参数：theme
        # 绿色风格：1
        # 蓝色风格：2 re: 选用
        logger.info("打开登录界面")
        login_url = self.get_login_url(appid, daid, s_url, style, theme)
        self.open_url_on_start(login_url)

    def get_login_url(self, appid, daid, s_url, style=34, theme=2):
        return f"https://xui.ptlogin2.qq.com/cgi-bin/xlogin?appid={appid}&daid={daid}&s_url={quote_plus(s_url)}&style={style}&theme={theme}&target=self"

    def _login_common(self, login_type, switch_to_login_frame_fn, assert_login_finished_fn, login_action_fn=None):
        """
        通用登录逻辑，并返回登陆后的cookie中包含的uin、skey数据
        :rtype: LoginResult
        """
        switch_to_login_frame_fn()

        self.driver.execute_script(f"document.title = '{self.window_title}'")

        # 实际登录的逻辑，不同方式的处理不同，这里调用外部传入的函数
        logger.info(f"{self.name} 开始{login_type}流程")
        if login_action_fn is not None:
            login_action_fn()

        logger.info(f"{self.name} 等待登录完成（也就是#loginIframe#login登录框消失）")
        # 出验证码的时候，下面这个操作可能会报错 'target frame detached\n(Session info: chrome=87.0.4280.88)'
        # 这时候等待一下好像就行了
        max_try = 2
        for i in range(max_try):
            idx = i + 1
            try:
                wait_time = int(self.cfg.login.login_timeout * idx / max_try)
                logger.info(f"[{idx}/{max_try}] {self.name} 尝试等待登录按钮消失~ 最大等待 {wait_time} 秒")
                WebDriverWait(self.driver, wait_time).until(expected_conditions.invisibility_of_element_located((By.ID, "login")))
                break
            except Exception as e:
                logger.error(f"[{idx}/{max_try}] {self.name} 出错了，等待两秒再重试。" +
                             color("bold_yellow") + "也许是网络有问题/出现短信验证码/账号密码不匹配导致，若隐藏了浏览器，请取消隐藏再打开，确认到底是什么问题",
                             exc_info=e)
                if idx < max_try:
                    time.sleep(2)

        logger.info(f"{self.name} 回到主iframe")
        self.driver.switch_to.default_content()

        assert_login_finished_fn()

        logger.info(f"{self.name} 登录完成")

        self.cookies = self.driver.get_cookies()

        if self.login_mode in [self.login_mode_normal, self.login_mode_qzone]:
            self.fetch_qq_video_vuserid()
        if self.login_mode in [self.login_mode_normal]:
            self.fetch_apps_p_skey()
        if self.login_mode in [self.login_mode_xinyue]:
            self.fetch_xinyue_openid_access_token()

        return

    def fetch_qq_video_vuserid(self):
        logger.info(f"{self.name} 转到qq视频界面，从而可以获取vuserid，用于腾讯视频的蚊子腿")
        self.driver.get("https://m.film.qq.com/magic-act/110254/index.html")
        for i in range(5):
            vuserid = self.driver.get_cookie('vuserid')
            if vuserid is not None:
                break
            time.sleep(1)
        self.add_cookie('vuserid', self.driver.get_cookie('vuserid'))

    def fetch_apps_p_skey(self):
        logger.info(f"{self.name} 跳转到apps.game.qq.com，用于获取该域名下的p_skey，用于部分分享功能")
        self.driver.get("https://apps.game.qq.com/")
        time.sleep(1)
        for i in range(5):
            p_skey = self.driver.get_cookie('p_skey')
            if p_skey is not None:
                break
            time.sleep(1)
        self.add_cookie('apps_p_skey', self.driver.get_cookie('p_skey'))

    def fetch_xinyue_openid_access_token(self):
        logger.info(f"{self.name} 跳转到xinyue.qq.com，用于获取该域名下的openid和access_token，用于心悦相关操作")
        self.driver.get("https://xinyue.qq.com/")
        time.sleep(1)
        for i in range(5):
            openid = self.driver.get_cookie('openid')
            access_token = self.driver.get_cookie('access_token')
            if openid is not None and access_token is not None:
                break
            time.sleep(1)
        self.add_cookie('xinyue_openid', self.driver.get_cookie('openid'))
        self.add_cookie('xinyue_access_token', self.driver.get_cookie('access_token'))

    def try_auto_resolve_captcha(self):
        try:
            self._try_auto_resolve_captcha()
        except Exception as e:
            msg = f"ver {now_version} {self.name} 自动处理验证失败了，出现未捕获的异常，请加群743671885反馈或自行解决。请手动进行处理验证码"
            logger.exception(color("fg_bold_red") + msg, exc_info=e)
            logger.warning(color("fg_bold_cyan") + "如果稳定报错，不妨打开网盘，看看是否有新版本修复了这个问题~")
            logger.warning(color("fg_bold_cyan") + "链接：https://fzls.lanzous.com/s/djc-helper")

    def _try_auto_resolve_captcha(self):
        if not self.cfg.login.auto_resolve_captcha:
            logger.info(f"{self.name} 未启用自动处理拖拽验证码的功能")
            return

        if self.cfg.login.move_captcha_delta_width_rate <= 0:
            logger.info(f"{self.name} 未设置每次尝试的偏移值，跳过自动拖拽验证码")
            return

        captcha_try_count = 0
        success_xoffset = 0
        history_key = 'history_captcha_succes_data'
        db = load_db()
        history_captcha_succes_data = db.get(history_key, {})
        try:
            WebDriverWait(self.driver, self.cfg.login.open_url_wait_time).until(expected_conditions.visibility_of_element_located((By.ID, "tcaptcha_iframe")))
            tcaptcha_iframe = self.driver.find_element_by_id("tcaptcha_iframe")
            self.driver.switch_to.frame(tcaptcha_iframe)

            logger.info(color("bold_green") + f"{self.name} 检测到了滑动验证码，将开始自动处理。（若验证码完毕会出现短信验证，请去配置文件关闭本功能，目前暂不支持带短信验证的情况）")

            try:
                WebDriverWait(self.driver, self.cfg.login.open_url_wait_time).until(expected_conditions.visibility_of_element_located((By.ID, "slide")))
                WebDriverWait(self.driver, self.cfg.login.open_url_wait_time).until(expected_conditions.visibility_of_element_located((By.ID, "slideBlock")))
                WebDriverWait(self.driver, self.cfg.login.open_url_wait_time).until(expected_conditions.visibility_of_element_located((By.ID, "tcaptcha_drag_button")))
            except Exception as e:
                logger.warning(f"{self.name} 等待验证码相关元素出现失败了,将按照默认宽度进行操作", exc_info=e)

            drag_tarck_width = self.driver.find_element_by_id('slide').size['width'] or 280  # 进度条轨道宽度
            drag_block_width = self.driver.find_element_by_id('slideBlock').size['width'] or 56  # 缺失方块宽度
            delta_width = int(drag_block_width * self.cfg.login.move_captcha_delta_width_rate) or 11  # 每次尝试多移动该宽度

            drag_button = self.driver.find_element_by_id('tcaptcha_drag_button')  # 进度条按钮

            # 根据经验，缺失验证码大部分时候出现在右侧，所以从右侧开始尝试
            xoffsets = []
            init_offset = drag_tarck_width - drag_block_width - delta_width
            if len(history_captcha_succes_data) != 0:
                # 若有则取其中最频繁的前几个作为优先尝试项
                mostCommon = Counter(history_captcha_succes_data).most_common()
                logger.info(f"{self.name} 根据本地记录数据，过去运行中成功解锁次数最多的偏移值为：{mostCommon}，将首先尝试他们")
                for xoffset, success_count in mostCommon:
                    xoffsets.append(int(xoffset))
            else:
                # 没有历史数据，只能取默认经验值了
                # 有几个位置经常出现，如2/4和3/4个滑块处，优先尝试
                xoffsets.append(init_offset - 2 * (drag_block_width // 4))
                xoffsets.append(init_offset - 3 * (drag_block_width // 4))

            logger.info(
                color("bold_green") +
                f"{self.name} 验证码相关信息：轨道宽度为{drag_tarck_width}，滑块宽度为{drag_block_width}，偏移递增量为{delta_width}({self.cfg.login.move_captcha_delta_width_rate:.2f}倍滑块宽度)"
            )

            # 将普通序列放入其中
            xoffset = init_offset
            while xoffset > 0:
                xoffsets.append(xoffset)
                xoffset -= delta_width

            wait_time = 1

            logger.info(f"{self.name} 先release滑块一次，以避免首次必定失败的问题")
            ActionChains(self.driver).release(on_element=drag_button).perform()
            time.sleep(wait_time)

            logger.info(color("bold_green") + f"{self.name} 开始拖拽验证码，将依次尝试下列偏移量:\n{xoffsets}")
            for xoffset in xoffsets:
                ActionChains(self.driver).click_and_hold(on_element=drag_button).perform()  # 左键按下
                time.sleep(0.5)
                ActionChains(self.driver).move_by_offset(xoffset=xoffset, yoffset=0).perform()  # 将滑块向右滑动指定距离
                time.sleep(0.5)
                ActionChains(self.driver).release(on_element=drag_button).perform()  # 左键放下，完成一次验证尝试
                time.sleep(0.5)

                captcha_try_count += 1
                success_xoffset = xoffset
                distance_rate = (init_offset - xoffset) / drag_block_width
                logger.info(f"{self.name} 尝试第{captcha_try_count}次拖拽验证码，本次尝试偏移量为{xoffset}，距离右侧初始尝试位置({init_offset})距离相当于{distance_rate:.2f}个滑块宽度(若失败将等待{wait_time}秒)")

                time.sleep(wait_time)

            self.driver.switch_to.parent_frame()
        except StaleElementReferenceException as e:
            logger.info(f"{self.name} 成功完成了拖拽验证码操作，总计尝试次数为{captcha_try_count}")
            # 更新历史数据
            success_key = str(success_xoffset)  # 因为json只支持str作为key，所以需要强转一下，使用时再转回int
            if success_key not in history_captcha_succes_data:
                history_captcha_succes_data[success_key] = 0
            history_captcha_succes_data[success_key] += 1
            db[history_key] = history_captcha_succes_data
            save_db(db)
        except TimeoutException as e:
            logger.info(f"{self.name} 看上去没有出现验证码")

    def set_window_size(self):
        logger.info("浏览器设为1936x1056")
        self.driver.set_window_size(1936, 1056)

    def add_cookies(self, cookies):
        to_add = []
        for cookie in cookies:
            if self.get_cookie(cookie['name']) == "":
                to_add.append(cookie)

        self.cookies.extend(to_add)

    def add_cookie(self, new_name, cookie):
        if cookie is None:
            return

        cookie['name'] = new_name
        self.cookies.append(cookie)
        logger.warning(f"{self.name} add_cookie {cookie['domain']} {cookie['name']} {cookie['value']}")

    def get_cookie(self, name):
        for cookie in self.cookies:
            if cookie['name'] == name:
                return cookie['value']
        return ''

    def print_cookie(self):
        for cookie in self.cookies:
            domain, name, value = cookie['domain'], cookie['name'], cookie['value']
            print(f"{domain:20s} {name:20s} {cookie}")

    def open_url_on_start(self, url):
        chrome_default_url = 'data:,'
        while True:
            self.driver.get(url)
            # 等待一会，确保地址栏url变量已变更
            time.sleep(0.1)
            if self.driver.current_url != chrome_default_url:
                break

            logger.info(f"尝试打开网页({url})，但似乎指令未生效，当前地址栏仍为{chrome_default_url}，等待{self.cfg.retry.retry_wait_time}秒后重试")
            time.sleep(self.cfg.retry.retry_wait_time)

    def need_reopen_url(self, login_type):
        return self.login_type_auto_login in login_type and self.cfg.run_in_headless_mode


def do_login(common_cfg, account: AccountConfig):
    acc = account.account_info
    ql = QQLogin(common_cfg)

    lr = ql.login(acc.account, acc.password, login_mode=ql.login_mode_normal, name=account.name)
    # lr = ql.qr_login(login_mode=mode, name=account.name)
    logger.info(color("bold_green") + f"{account.name}登录结果为： {lr}")


if __name__ == '__main__':
    # 读取配置信息
    load_config("config.toml", "config.toml.local")
    cfg = config()

    RUN_PARALLEL = False

    if RUN_PARALLEL:
        from multiprocessing import Pool, cpu_count, freeze_support

        freeze_support()

        with Pool(len(cfg.account_configs)) as pool:
            pool.starmap(do_login, [(cfg.common, account) for account in cfg.account_configs])

            logger.info("全部账号登录完毕")
    else:
        cfg.common.force_use_portable_chrome = True
        cfg.common.run_in_headless_mode = False

        ql = QQLogin(cfg.common)
        idx = 1
        account = cfg.account_configs[idx - 1]
        acc = account.account_info
        logger.warning(f"测试账号 {account.name} 的登录情况")


        def run_test(mode):
            lr = ql.login(acc.account, acc.password, login_mode=mode, name=account.name)
            # lr = ql.qr_login(login_mode=mode, name=account.name)
            logger.info(color("bold_green") + f"{lr}")


        test_all = False

        if not test_all:
            run_test(ql.login_mode_normal)
        else:
            for attr in dir(ql):
                if not attr.startswith("login_mode_"):
                    continue

                mode = getattr(ql, attr)

                logger.info(f"开始测试登录模式 {mode}，请按任意键开始测试")
                input()

                run_test(mode)
