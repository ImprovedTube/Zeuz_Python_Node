# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
"""
    Created on May 15, 2016

    @author: Built_In_Automation Solutionz Inc.
    Name: Built In Functions - Selenium
    Description: Sequential Actions for controlling Web Browsers - All main Web Browsers supported on Linux/Windows/Mac
"""

#########################
#                       #
#        Modules        #
#                       #
#########################
import platform
import sys, os, time, inspect, shutil, subprocess, json
import socket
import requests
import psutil
from pathlib import Path
from datetime import datetime

from selenium.webdriver.chrome.service import Service
import re
sys.path.append("..")
from selenium import webdriver
if "linux" in platform.system().lower():
    from xvfbwrapper import Xvfb
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.opera import OperaDriverManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, WebDriverException,\
    SessionNotCreatedException, TimeoutException, NoSuchFrameException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
import selenium

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from Framework.Utilities import CommonUtil, ConfigModule
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
from Framework.Utilities.decorators import logger, deprecated
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)
from Framework.AI.NLP import binary_classification
from settings import temp_ini_file

#########################
#                       #
#    Global Variables   #
#                       #
#########################

MODULE_NAME = inspect.getmodulename(__file__)

temp_config = os.path.join(
    os.path.join(
        os.path.abspath(__file__).split("Framework")[0],
        os.path.join(
            "AutomationLog", ConfigModule.get_config_value("Advanced Options", "_file")
        ),
    )
)
temp_config = str(Path(os.path.abspath(__file__).split("Framework")[0])/"AutomationLog"/ConfigModule.get_config_value("Advanced Options", "_file"))
aiplugin_path = str(Path(os.path.abspath(__file__).split("Framework")[0])/"Apps"/"Web"/"aiplugin")
ai_recorder_path = str(Path(os.path.abspath(__file__).split("Framework")[0])/"Apps"/"Web"/"AI_Recorder")

# Disable WebdriverManager SSL verification.
os.environ['WDM_SSL_VERIFY'] = '0'

WebDriver_Wait = 1
WebDriver_Wait_Short = 1

current_driver_id = None
selenium_driver = None
selenium_details = {}
default_x, default_y = 1920, 1080
vdisplay = None

# JavaScript for collecting First Contentful Paint value.
JS_FCP = '''
return performance.getEntriesByName("first-contentful-paint")[0].startTime
'''

# JavaScript for collecting Largest Contentful Paint value.
JS_LCP = '''
var args = arguments;
const po = new PerformanceObserver(list => {
    const entries = list.getEntries();
    const entry = entries[entries.length - 1];
    // Process entry as the latest LCP candidate
    // LCP is accurate when the renderTime is available.
    // Try to avoid this being false by adding Timing-Allow-Origin headers!
    const accurateLCP = entry.renderTime ? true : false;
    // Use startTime as the LCP timestamp. It will be renderTime if available, or loadTime otherwise.
    const largestPaintTime = entry.startTime;
    // Send the LCP information for processing.

    console.log("[ZeuZ Node] Largest Contentful Paint: ", largestPaintTime);
    args[0](largestPaintTime);
});
po.observe({ type: 'largest-contentful-paint', buffered: true });
'''

# if Shared_Resources.Test_Shared_Variables('selenium_driver'): # Check if driver is already set in shared variables
#    selenium_driver = Shared_Resources.Get_Shared_Variables('selenium_driver') # Retreive appium driver

# Recall dependency, if not already set
dependency = None
if Shared_Resources.Test_Shared_Variables("dependency"):  # Check if driver is already set in shared variables
    dependency = Shared_Resources.Get_Shared_Variables("dependency")  # Retreive appium driver
else:
    raise ValueError("No dependency set - Cannot run")


@logger
def find_exe_in_path(exe):
    """ Search the path for an executable """

    try:
        path = os.getenv("PATH")  # Linux/Windows path

        if ";" in path:  # Windows delimiter
            dirs = path.split(";")
        elif ":" in path:  # Linux delimiter
            dirs = path.split(":")
        else:
            return "zeuz_failed"

        for directory in dirs:  # Try each directory
            filename = os.path.join(directory, exe)  # Create full path
            if os.path.isfile(filename):  # If it exists, return it and stop
                return filename

        # No matches
        return "zeuz_failed"

    except Exception:
        errMsg = "Error searching PATH"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def find_appium():
    """ Do our very best to find the appium executable """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Expected locations
    appium_list = [
        "/usr/bin/appium",
        os.path.join(str(os.getenv("HOME")), ".linuxbrew/bin/appium"),
        os.path.join(str(os.getenv("ProgramFiles")), "APPIUM", "Appium.exe"),
        os.path.join(
            str(os.getenv("USERPROFILE")), "AppData", "Roaming", "npm", "appium.cmd"
        ),
        os.path.join(str(os.getenv("ProgramFiles(x86)")), "APPIUM", "Appium.exe"),
    ]  # getenv() must be wrapped in str(), so it doesn't fail on other platforms

    # Try to find the appium executable
    appium_binary = ""

    for binary in appium_list:
        if os.path.exists(binary):
            appium_binary = binary
            break

    # Try to find the appium executable in the PATH variable
    if appium_binary == "":  # Didn't find where appium was installed
        CommonUtil.ExecLog(sModuleInfo, "Searching PATH for appium", 0)
        for exe in ("appium", "appium.exe", "appium.bat", "appium.cmd"):
            result = find_exe_in_path(exe)  # Get path and search for executable with in
            if result != "zeuz_failed":
                appium_binary = result
                break

    # Verify if we have the binary location
    if appium_binary == "":  # Didn't find where appium was installed
        CommonUtil.ExecLog(
            sModuleInfo, "Appium not found. Trying to locate via which", 0
        )
        try:
            appium_binary = subprocess.check_output(
                "which appium", encoding="utf-8", shell=True
            ).strip()
        except:
            pass

        if appium_binary == "":  # Didn't find where appium was installed
            appium_binary = "appium"  # Default filename of appium, assume in the PATH
            CommonUtil.ExecLog(
                sModuleInfo, "Appium still not found. Assuming it's in the PATH.", 2
            )
        else:
            CommonUtil.ExecLog(sModuleInfo, "Found appium: %s" % appium_binary, 1)
    else:  # Found appium's path
        CommonUtil.ExecLog(sModuleInfo, "Found appium: %s" % appium_binary, 1)

    return appium_binary


@logger
def start_appium_server():
    """Starts the external Appium server.

    Returns appium_port on success.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    appium_binary = find_appium()

    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    try:
        appium_port = 4723
        tries = 0
        while is_port_in_use(appium_port) and tries < 20:
            appium_port += 2

        if tries >= 20:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Failed to find a free port for running appium after 20 tries.",
                1,
            )
            return "zeuz_failed"

        try:
            appium_server = None
            if (
                sys.platform == "win32"
            ):  # We need to open appium in it's own command dos box on Windows
                cmd = (
                    'start "Appium Server" /wait /min cmd /c %s --allow-insecure chromedriver_autodownload -p %d'
                    % (appium_binary, appium_port)
                )  # Use start to execute and minimize, then cmd /c will remove the dos box when appium is killed
                appium_server = subprocess.Popen(
                    cmd, shell=True
                )  # Needs to run in a shell due to the execution command
            elif sys.platform == "darwin":
                appium_server = subprocess.Popen(
                    "%s --allow-insecure chromedriver_autodownload -p %s"
                    % (appium_binary, str(appium_port)),
                    shell=True,
                )
            elif sys.platform == "linux" or sys.platform == "linux2":
                appium_server = subprocess.Popen(
                    "%s --allow-insecure chromedriver_autodownload -p %s"
                    % (appium_binary, str(appium_port)),
                    shell=True,
                )
            else:
                try:

                    appium_binary_path = os.path.normpath(appium_binary)
                    appium_binary_path = os.path.abspath(
                        os.path.join(appium_binary_path, os.pardir)
                    )
                    env = {"PATH": str(appium_binary_path)}
                    appium_server = subprocess.Popen(
                        subprocess.Popen(
                            "%s --allow-insecure chromedriver_autodownload -p %s"
                            % (appium_binary, str(appium_port)),
                            shell=True,
                        ),
                        env=env,
                    )
                except:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Couldn't launch appium server, please do it manually by typing 'appium &' in the terminal",
                        2,
                    )
        except Exception as returncode:  # Couldn't run server
            return CommonUtil.Exception_Handler(
                sys.exc_info(),
                None,
                "Couldn't start Appium server. May not be installed, or not in your PATH: %s"
                % returncode,
            )

        # Wait for server to startup and return
        CommonUtil.ExecLog(
            sModuleInfo,
            "Waiting for server to start on port %d: %s" % (appium_port, appium_binary),
            0,
        )
        maxtime = time.time() + 10  # Maximum time to wait for appium server
        while True:  # Dynamically wait for appium to start by polling it
            if time.time() > maxtime:
                break  # Give up if max time was hit
            try:  # If this works, then stop waiting for appium
                r = requests.get(
                    "http://localhost:%d/sessions" % appium_port
                )  # Poll appium server
                if r.status_code:
                    break
            except:
                time.sleep(0.1) # sleep for 0.1 sec before retrying.

        if appium_server:
            CommonUtil.ExecLog(sModuleInfo, "Server started", 1)
            return appium_port
        else:
            CommonUtil.ExecLog(sModuleInfo, "Server failed to start", 3)
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error starting Appium server"
        )


@logger
def Open_Electron_App(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    global selenium_details
    global current_driver_id

    try:
        desktop_app_path = ""
        driver_id = ""
        for left, _, right in data_set:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if "windows" in left and platform.system() == "Windows":
                desktop_app_path = right.strip()
            elif "mac" in left and platform.system() == "Darwin":
                desktop_app_path = right.strip()
            elif "linux" in left and platform.system() == "Linux":
                desktop_app_path = right.strip()
            elif left == "driverid":
                driver_id = right.strip()

        if not desktop_app_path:
            CommonUtil.ExecLog(sModuleInfo, "You did not provide an Electron app path for %s OS" % platform.system(), 3)
            return "zeuz_failed"

        if not driver_id:
            driver_id = "default"

        desktop_app_path = CommonUtil.path_parser(desktop_app_path)
        electron_chrome_path = ConfigModule.get_config_value("Selenium_driver_paths", "electron_chrome_path")
        if not electron_chrome_path:
            electron_chrome_path = ChromeDriverManager().install()

        try:
            from selenium.webdriver.chrome.options import Options
            opts = Options()
            opts.binary_location = desktop_app_path
            selenium_driver = webdriver.Chrome(executable_path=electron_chrome_path, chrome_options=opts)
            selenium_driver.implicitly_wait(WebDriver_Wait)
            CommonUtil.ExecLog(sModuleInfo, "Started Electron App", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
        except SessionNotCreatedException as exc:
            try:
                major_version = exc.msg.split("\n")[1].split("is ", 1)[1].split(".")[0]
                specific_version = requests.get("https://chromedriver.storage.googleapis.com/LATEST_RELEASE_" + major_version).text
                electron_chrome_path = ChromeDriverManager(version=specific_version).install()
                ConfigModule.add_config_value("Selenium_driver_paths", "electron_chrome_path", electron_chrome_path)
                from selenium.webdriver.chrome.options import Options
                opts = Options()
                opts.binary_location = desktop_app_path
                selenium_driver = webdriver.Chrome(executable_path=electron_chrome_path, chrome_options=opts)
                selenium_driver.implicitly_wait(WebDriver_Wait)
                CommonUtil.ExecLog(sModuleInfo, "Started Electron App", 1)
                Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
                CommonUtil.teardown = True
                CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            except:
                CommonUtil.ExecLog(sModuleInfo, "To start an Electron app, you need to download a ChromeDriver with the version that your Electron app supports.\n" +
                   "Visit this link to download specific version of Chrome driver: https://chromedriver.chromium.org/downloads\n" +
                   'Then add the path of the ChromeDriver path into Framework/settings.conf file "Selenium_driver_paths" section with "electron_chrome_path" name', 3)
                return "zeuz_failed"
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info())

        if driver_id in selenium_details:
            pass    # we need to decide later based on the situation
        else:
            selenium_details[driver_id] = {"driver": selenium_driver}
        current_driver_id = driver_id
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def get_performance_metrics(dataset):
    try:
        label = driver_id = ""
        for left, mid, right in dataset:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "driverid":
                driver_id = right.strip()
            elif left == "getperformancemetrics":
                var_name = right.strip()
            elif left == "label":
                label = right.strip()

        if not driver_id:
            driver_id = current_driver_id

        # from selenium.webdriver.common.devtools.v101.performance import enable, disable, get_metrics
        # from selenium.webdriver.chrome.webdriver import ChromiumDriver
        # time.sleep(5)

        perf_json_data = collect_browser_metrics(driver_id, label if label else CommonUtil.previous_action_name)
        Shared_Resources.Set_Shared_Variables(var_name, perf_json_data)
        return "passed"
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def use_xvfb_or_headless(callback):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    if platform.system() == "Linux":
        try:
            global vdisplay
            vdisplay = Xvfb(width=1920, height=1080, colordepth=16)
            vdisplay.start()
        except:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Failed to initialize xvfb. "
                "Perhaps xvfb is not installed?\n"
                "For apt-get: `sudo apt-get install xvfb`\n"
                "For yum: `sudo yum install xvfb`.\n"
                "Falling back to headless mode.",
                2,
            )
            callback()
    else:
        callback()


def set_extension_variables():
    try:
        url = ConfigModule.get_config_value("Authentication", "server_address").strip()
        apiKey = ConfigModule.get_config_value("Authentication", "api-key").strip()
        jwtKey = CommonUtil.jwt_token.strip()
        with open(Path(aiplugin_path) / "data.json", "w") as file:
            json.dump({
              "zeuz_url": url,
              "zeuz_key": apiKey
            }, file, indent=4)

    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Could not load inspector extension")

    try:
        with open(Path(ai_recorder_path) / "background" / "data.json", "w") as file:
            metaData = {
                "testNo": CommonUtil.current_tc_no,
                "testName": CommonUtil.current_tc_name,
                "stepNo": CommonUtil.current_step_sequence,
                "stepName": CommonUtil.current_step_name,
                "url": url,
                "apiKey": apiKey,
                "jwtKey": jwtKey,
            }
            json.dump(metaData, file, indent=4)
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Could not load recorder extension")


def browser_process_status(browser:str):
    list_process_command = ['tasklist']
    seacrh_command = ['findstr', f'{browser}.exe']

    list_process = subprocess.Popen(list_process_command, stdout=subprocess.PIPE)
    search_process = subprocess.Popen(seacrh_command, stdin=list_process.stdout, stdout=subprocess.PIPE, text=True)

    output,_ = search_process.communicate()

    if output:
        return True
    else:
        return False

initial_download_folder = None
@logger
def Open_Browser(dependency, window_size_X=None, window_size_Y=None, capability=None, browser_options=None, profile_options=None):
    """ Launch browser and create instance """

    global selenium_driver
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        browser = dependency["Browser"]
    except Exception:
        ErrorMessage = (
            "Dependency not set for browser. Please set the Apply Filter value to YES."
        )
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

    remote_host = None
    remote_browser_version = None
    if Shared_Resources.Test_Shared_Variables('run_time_params'): # Look for remote config in runtime params
        run_time_params = Shared_Resources.Get_Shared_Variables('run_time_params')
        remote_config = run_time_params.get("remote_config")
        if(remote_config):
            remote_host = remote_config.get('host')
            remote_browser_version = remote_config.get('browser_version')
            if(remote_host):
                try:
                    if requests.get(remote_host).status_code != 200:
                        remote_host = None
                except requests.exceptions.RequestException as e:
                    remote_host = None
                if remote_host == None:
                    CommonUtil.ExecLog(
                    sModuleInfo, "Remote host: %s is not up. Running the browser locally " % remote_config.get('host'), 3
                )
    
    is_browserstack = 'browserstack' in browser
    if is_browserstack:
        try:
            browerstack_config = json.loads(browser)
            browser = 'browserstack'
            remote_host = browerstack_config['remote_host']
            desired_cap = browerstack_config['desired_cap']
            remote_desired_cap = {
                'bstack:options' : {
                "os" : desired_cap["os"],
                "osVersion" : desired_cap['os_version'],
                "browserVersion" : desired_cap['browser_version'],
                "local" : "false",
                "seleniumVersion" : "4.8.0",
                },
                "browserName" : desired_cap['browser'],
                }
        except ValueError as e:
            is_browserstack = False
            CommonUtil.ExecLog(
                    sModuleInfo, "Unable to parse browserstack config. Running the browser locally", 3
                )

    try:
        CommonUtil.teardown = True
        browser = browser.lower().strip() 
        import selenium
        selenium_version = selenium.__version__

        kill_process = False

        browser_map = {
            "microsoft edge chromium": 'msedge',
            "chrome": "chrome",
            "firefox": "firefox",
            "chromeheadless": "chrome",
            "firefoxheadless": "firefox",
            "edgechromiumheadless": "msedge",
        }

        if profile_options:
            if browser.strip().lower() in browser_map.keys():
                browser_short_form = browser_map[browser] 
                process_status = browser_process_status(browser_short_form)
                for options in profile_options:
                    if options[0] == "autokillforprofile" and options[1] == "True":
                        kill_process = True

                if process_status == True and kill_process == False:
                    err_msg = f'''
                    Please close all the {browser} browser instance.
                    Or, use the following optional parameter to do it automatically:
                    ( auto kill for profile | browser option | True )
                    '''
                    CommonUtil.ExecLog(
                        sModuleInfo, err_msg, 3
                    )
                    raise Exception
                elif process_status == True and kill_process == True:
                    task_kill_command = ['taskkill', '/IM', f'{browser_short_form}.exe', '/F']
                    task_kill_process = subprocess.Popen(task_kill_command, stdout=subprocess.PIPE, text=True)
                    kill_output,err = task_kill_process.communicate()
                    kill_output_status = kill_output.split()[0]
                    if kill_output_status == "SUCCESS:":
                        CommonUtil.ExecLog(
                            sModuleInfo, f"Successfully terminated all the {browser_short_form}.exe processes", 1
                        )
                    else:
                        CommonUtil.ExecLog(
                            sModuleInfo, f"Could not terminate the {browser_short_form}.exe processes", 3
                        )
            else:
                CommonUtil.ExecLog(
                        sModuleInfo, f"ZeuZ does not support browser profile for {browser} browser", 3
                    )
                raise Exception
                
        if browser in ("ios",):
            # Finds the appium binary and starts the server.
            appium_port = start_appium_server()

            if appium_port == "zeuz_failed":
                return "zeuz_failed"

            if browser == "android":
                capabilities = {
                    "platformName": "Android",
                    "automationName": "UIAutomator2",
                    "browserName": "Chrome"

                    # Platform specific details may later be fetched from the device
                    # list sent by zeuz server.
                    # "platformVersion": "9.0",
                    # "deviceName": "Android Emulator",
                }
            elif browser == "ios":
                capabilities = {
                    "platformName": "iOS",
                    "automationName": "XCUITest",
                    "browserName": "Safari"

                    # Platform specific details may later be fetched from the device
                    # list sent by zeuz server.
                }

            from appium import webdriver as appiumdriver

            selenium_driver = appiumdriver.Remote("http://localhost:%d" % appium_port, capabilities)
            selenium_driver.implicitly_wait(WebDriver_Wait)

        elif browser in ("android", "chrome", "chromeheadless"):
            from selenium.webdriver.chrome.options import Options
            chrome_path = ConfigModule.get_config_value("Selenium_driver_paths", "chrome_path")
            try:
                if not chrome_path:
                    chrome_path = ChromeDriverManager().install()
                    ConfigModule.add_config_value("Selenium_driver_paths", "chrome_path", chrome_path)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Unable to download chromedriver using ChromedriverManager", 2)
            options = Options()

            if remote_browser_version:
                options.set_capability("browserVersion",remote_browser_version)
            # capability
            if capability:
                for key, value in capability.items():
                    # options.set_capability('unhandledPromptBehavior', 'ignore')
                    options.set_capability(key, value)

            # argument
            if not browser_options:
                options.add_argument("--no-sandbox")
                # options.add_argument("--disable-extensions")
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--zeuz_pid_finder')
                options.add_argument('--allow-running-insecure-content')    # This is for running extension on a http server to call a https request

            # Todo: profile, add_argument => open_browser
            _prefs = {}
            if browser_options:
                for left, right in browser_options:
                    if left in ("addargument", "addarguments"):
                        options.add_argument(right.strip())
                        print(left, right)

                    elif left in ("addextension", "addextensions"):
                        options.add_extension(CommonUtil.path_parser(right.strip()))
                    elif left in ("addexperimentaloption"):
                        if "prefs" in right:
                            _prefs = right["prefs"]
                        else:
                            options.add_experimental_option(list(right.items())[0][0], list(right.items())[0][1])

            if profile_options:
                for left, right in profile_options:
                    if left in ("addargument", "addarguments"):
                        options.add_argument(right.strip())
                        print(left, right)

            if browser == "android":
                mobile_emulation = {"deviceName": "Pixel 2 XL"}
                options.add_experimental_option("mobileEmulation", mobile_emulation)
            else:
                options.add_experimental_option("useAutomationExtension", False)

                # On Debug run open inspector with credentials
                if CommonUtil.debug_status and ConfigModule.get_config_value("Inspector", "ai_plugin").strip().lower() in ("true", "on", "enable", "yes", "on_debug"):
                    set_extension_variables()
                    options.add_argument(f"load-extension={aiplugin_path},{ai_recorder_path}")
                    # options.add_argument(f"load-extension={ai_recorder_path}")

            if "chromeheadless" in browser:
                def chromeheadless():
                    options.add_argument(
                        "--headless=new"
                    )
                use_xvfb_or_headless(chromeheadless)

            global initial_download_folder
            initial_download_folder = download_dir = ConfigModule.get_config_value("sectionOne", "initial_download_folder", temp_config)
            prefs = {
                "profile.default_content_settings.popups": 0,
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                'safebrowsing.enabled': 'false'
            }
            for key in _prefs:
                prefs[key] = _prefs[key]
            options.add_experimental_option('prefs', prefs)

            if remote_host:
                selenium_driver = webdriver.Remote(
                    command_executor= remote_host + "wd/hub",
                    options=options,
                )
            else:
                import selenium
                from distutils.version import StrictVersion

                required_version = StrictVersion('4.10.0')
                installed_version = StrictVersion(selenium.__version__)

                if installed_version >= required_version:
                    service = Service()
                    if installed_version == required_version:
                        service.path = chrome_path
                    selenium_driver = webdriver.Chrome(
                        service=service,
                        options=options,
                    )
                else:
                    d = DesiredCapabilities.CHROME
                    d["loggingPrefs"] = {"browser": "ALL"}
                    d['goog:loggingPrefs'] = {'performance': 'ALL'}
                    selenium_driver = webdriver.Chrome(
                        executable_path=chrome_path,
                        chrome_options=options,
                        desired_capabilities=d
                    )

            selenium_driver.implicitly_wait(WebDriver_Wait)
            if not window_size_X and not window_size_Y:
                selenium_driver.set_window_size(default_x, default_y)
                selenium_driver.maximize_window()
            else:
                if not window_size_X:
                    window_size_X = 1000
                if not window_size_Y:
                    window_size_Y = 1000
                selenium_driver.set_window_size(window_size_X, window_size_Y)
            CommonUtil.ExecLog(sModuleInfo, "Started Chrome Browser", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"

        elif browser in ("firefox", "firefoxheadless"):
            firefox_path = ConfigModule.get_config_value("Selenium_driver_paths", "firefox_path")
            if not firefox_path:
                firefox_path = GeckoDriverManager().install()
                ConfigModule.add_config_value("Selenium_driver_paths", "firefox_path", firefox_path)
            from sys import platform as _platform
            from selenium.webdriver.firefox.options import Options
            options = Options()

            if profile_options:
                for left, right in profile_options:
                    if left in ("addargument", "addarguments"):
                        options.add_argument(right.strip())
                        print(left, right)

            if remote_browser_version:
                options.set_capability("browserVersion",remote_browser_version)

            if "headless" in browser:
                #firefox headless mode needs add_argument
                options.add_argument("-headless")
                
                '''
                # commenting out as this is not working.  Make sure 
                # whoever implemented this it is tested with latest firefox version
                def firefoxheadless():
                    options.headless = True
                use_xvfb_or_headless(firefoxheadless)
                '''

            if _platform == "win32":
                try:
                    import winreg
                except ImportError:
                    import _winreg as winreg
                handle = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
                )
                num_values = winreg.QueryInfoKey(handle)[1]
                path = False
                for i in range(num_values):
                    path = winreg.EnumValue(handle, i)
                    if path != False:
                        Firefox_path = path[1]
                        binary = FirefoxBinary(Firefox_path)
                        break

            profile = webdriver.FirefoxProfile()
            initial_download_folder = download_dir = ConfigModule.get_config_value("sectionOne", "initial_download_folder", temp_config)
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            profile.set_preference("browser.download.dir", download_dir)
            #text/plain;charset=UTF-8
            # Allowing txt, pdf, xlsx, xml, csv, zip files to be directly downloaded without save prompt
            apps = "application/pdf;text/plain;application/text;text/xml;application/xml;application/xlsx;application/csv;application/zip"
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", apps)
            profile.accept_untrusted_certs = True
            if(remote_host):
                capabilities = webdriver.DesiredCapabilities().FIREFOX
                capabilities['acceptSslCerts'] = True
                selenium_driver = webdriver.Remote(
                    command_executor= remote_host + "wd/hub",
                    options=options,
                    desired_capabilities=capabilities,
                    browser_profile=profile
                )
            else:
                if selenium_version.startswith('4.'):
                    service = Service(firefox_path)
                    selenium_driver = webdriver.Firefox(
                        service=service,
                        options=options,
                    )
                elif selenium_version.startswith('3.'):
                    capabilities = webdriver.DesiredCapabilities().FIREFOX
                    capabilities['acceptSslCerts'] = True
                    selenium_driver = webdriver.Firefox(
                        executable_path=firefox_path,
                        capabilities=capabilities,
                        options=options,
                        firefox_profile=profile
                    )
                else:
                    print("Please update selenium & rerun node_cli file again.")

            selenium_driver.implicitly_wait(WebDriver_Wait)
            if not window_size_X and not window_size_Y:
                selenium_driver.set_window_size(default_x, default_y)
                selenium_driver.maximize_window()
            else:
                if window_size_X is None:
                    window_size_X = 1000
                if window_size_Y is None:
                    window_size_Y = 1000
                selenium_driver.set_window_size(window_size_X, window_size_Y)
            CommonUtil.ExecLog(sModuleInfo, "Started Firefox Browser", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"

        elif browser in ("microsoft edge chromium", "edgechromiumheadless"):
            edge_path = ConfigModule.get_config_value("Selenium_driver_paths", "edge_path")
            if not edge_path:
                edge_path = EdgeChromiumDriverManager().install()
                ConfigModule.add_config_value("Selenium_driver_paths", "edge_path", edge_path)

            """We are using a Custom module from Microsoft which inherits Selenium class and provides additional supports which we need.
            Since this module inherits Selenium module so all updates will be inherited as well
            """
            from Framework.edge_module.msedge.selenium_tools import EdgeOptions, Edge
            initial_download_folder = download_dir = ConfigModule.get_config_value("sectionOne", "initial_download_folder", temp_config)
            options = webdriver.EdgeOptions()

            if remote_browser_version:
                options.set_capability("browserVersion",remote_browser_version)

            options.use_chromium = True

            if profile_options:
                for left, right in profile_options:
                    if left in ("addargument", "addarguments"):
                        options.add_argument(right.strip())
                        print(left, right)

            if "headless" in browser:
                def edgeheadless():
                    options.headless = True
                use_xvfb_or_headless(edgeheadless)

            options.add_experimental_option("prefs", {"download.default_directory": download_dir})
            options.add_argument('--zeuz_pid_finder')
            options.add_argument("--no-sandbox")
            # options.add_argument("--disable-extensions")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--allow-running-insecure-content')    # This is for running extension on a http server to call a https request
            if CommonUtil.debug_status and ConfigModule.get_config_value("Inspector", "ai_plugin").strip().lower() in ("true", "on", "enable", "yes", "on_debug"):
                set_extension_variables()
                options.add_argument(f"load-extension={aiplugin_path},{ai_recorder_path}")
            if(remote_host):
                capabilities = webdriver.EdgeOptions().capabilities
                capabilities['acceptSslCerts'] = True
                selenium_driver = webdriver.Remote(
                    command_executor= remote_host + "wd/hub",
                    options=options,
                    desired_capabilities=capabilities
                )
            else:
                if selenium_version.startswith('4.'):
                    selenium_driver = webdriver.Edge(
                        options=options,
                    )
                elif selenium_version.startswith('3.'):
                    capabilities = webdriver.EdgeOptions().capabilities
                    capabilities['acceptSslCerts'] = True
                    selenium_driver = Edge(
                        executable_path=edge_path,
                        options=options,
                        capabilities=capabilities
                    )
                else:
                    print("Please update selenium & rerun node_cli file again.")

            selenium_driver.implicitly_wait(WebDriver_Wait)
            if not window_size_X and not window_size_Y:
                selenium_driver.set_window_size(default_x, default_y)
                selenium_driver.maximize_window()
            else:
                if not window_size_X:
                    window_size_X = 1000
                if not window_size_Y:
                    window_size_Y = 1000
                selenium_driver.set_window_size(window_size_X, window_size_Y)
            CommonUtil.ExecLog(sModuleInfo, "Started Microsoft Edge Browser", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"

        elif browser == "opera":
            opera_path = ConfigModule.get_config_value("Selenium_driver_paths", "opera_path")
            if not opera_path:
                opera_path = OperaDriverManager().install()
                ConfigModule.add_config_value("Selenium_driver_paths", "opera_path", opera_path)
            capabilities = webdriver.DesiredCapabilities().OPERA
            capabilities['acceptSslCerts'] = True

            from selenium.webdriver.opera.options import Options
            options = Options()
            options.add_argument("--zeuz_pid_finder")
            initial_download_folder = download_dir = ConfigModule.get_config_value("sectionOne", "initial_download_folder", temp_config)
            options.add_experimental_option("prefs", {"download.default_directory": download_dir})  # This does not work
            # options.binary_location = r'C:\Users\ASUS\AppData\Local\Programs\Opera\launcher.exe'  # This might be needed

            selenium_driver = webdriver.Opera(executable_path=opera_path, desired_capabilities=capabilities, options=options)
            selenium_driver.implicitly_wait(WebDriver_Wait)
            if not window_size_X and not window_size_Y:
                selenium_driver.set_window_size(default_x, default_y)
                selenium_driver.maximize_window()
            else:
                if not window_size_X:
                    window_size_X = 1000
                if not window_size_Y:
                    window_size_Y = 1000
                selenium_driver.set_window_size(window_size_X, window_size_Y)
            CommonUtil.ExecLog(sModuleInfo, "Started Opera Browser", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"

        elif browser == "ie":
            ie_path = ConfigModule.get_config_value("Selenium_driver_paths", "ie_path")
            if not ie_path:
                ie_path = IEDriverManager().install()
                ConfigModule.add_config_value("Selenium_driver_paths", "ie_path", ie_path)
            capabilities = webdriver.DesiredCapabilities().INTERNETEXPLORER
            # capabilities['acceptSslCerts'] = True     # It does not work for internet explorer
            selenium_driver = webdriver.Ie(executable_path=ie_path, capabilities=capabilities)
            selenium_driver.implicitly_wait(WebDriver_Wait)
            if not window_size_X and not window_size_Y:
                selenium_driver.set_window_size(default_x, default_y)
                selenium_driver.maximize_window()
            else:
                if not window_size_X:
                    window_size_X = 1000
                if not window_size_Y:
                    window_size_Y = 1000
                selenium_driver.set_window_size(window_size_X, window_size_Y)
            CommonUtil.ExecLog(sModuleInfo, "Started Internet Explorer Browser", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"

        elif "safari" in browser:
            CommonUtil.ExecLog(sModuleInfo, "Restart computer after following ... https://developer.apple.com/documentation/webkit/testing_with_webdriver_in_safari ", 1)
            '''
            os.environ["SELENIUM_SERVER_JAR"] = (
                    os.sys.prefix
                    + os.sep
                    + "Scripts"
                    + os.sep
                    + "selenium-server-standalone-2.45.0.jar"
            )'''

            desired_capabilities = DesiredCapabilities.SAFARI

            if "ios" in browser:
                desired_capabilities["platformName"] = "ios"

                if "simulator" in browser:
                    desired_capabilities["safari:useSimulator"] = True

            selenium_driver = webdriver.Safari(desired_capabilities=desired_capabilities)
            selenium_driver.implicitly_wait(WebDriver_Wait)
            if not window_size_X and not window_size_Y:
                selenium_driver.set_window_size(default_x, default_y)
                selenium_driver.maximize_window()
            else:
                if not window_size_X:
                    window_size_X = 1000
                if not window_size_Y:
                    window_size_Y = 1000
                selenium_driver.set_window_size(window_size_X, window_size_Y)
            CommonUtil.ExecLog(sModuleInfo, "Started Safari Browser", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"
        elif 'browserstack' in browser:
            selenium_driver = webdriver.Remote(
                command_executor= remote_host,
                desired_capabilities=remote_desired_cap)
            selenium_driver.implicitly_wait(WebDriver_Wait)
            if not window_size_X and not window_size_Y:
                selenium_driver.set_window_size(default_x, default_y)
                selenium_driver.maximize_window()
            else:
                if not window_size_X:
                    window_size_X = 1000
                if not window_size_Y:
                    window_size_Y = 1000
                selenium_driver.set_window_size(window_size_X, window_size_Y)
            CommonUtil.ExecLog(sModuleInfo, f"Started {remote_desired_cap['browserName']} on Browserstack", 1)
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            CommonUtil.set_screenshot_vars(Shared_Resources.Shared_Variable_Export())
            return "passed"

        else:
            CommonUtil.ExecLog(
                sModuleInfo, "You did not select a valid browser: %s" % browser, 3
            )
            return "zeuz_failed"
        # time.sleep(3)

    except SessionNotCreatedException as exc:
        if "This version" in exc.msg and "only supports" in exc.msg and not installed_version >= required_version:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Couldn't open the browser because the webdriver is backdated. Trying again after updating webdriver",
                2
            )
            if browser in ("android", "chrome", "chromeheadless"):
                ConfigModule.add_config_value("Selenium_driver_paths", "chrome_path", ChromeDriverManager().install())
            elif browser in ("firefox", "firefoxheadless"):
                ConfigModule.add_config_value("Selenium_driver_paths", "firefox_path", GeckoDriverManager().install())
            elif browser in ("microsoft edge chromium", "EdgeChromiumHeadless"):
                ConfigModule.add_config_value("Selenium_driver_paths", "edge_path", EdgeChromiumDriverManager().install())
            elif browser == "opera":
                ConfigModule.add_config_value("Selenium_driver_paths", "opera_path", OperaDriverManager().install())
            elif browser == "ie":
                ConfigModule.add_config_value("Selenium_driver_paths", "ie_path", IEDriverManager().install())
            Open_Browser(dependency, window_size_X, window_size_Y)
        else:
            return CommonUtil.Exception_Handler(sys.exc_info())

    except WebDriverException as exc:
        if "needs to be in PATH" in exc.msg and not installed_version >= required_version:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Couldn't open the browser because the webdriver is not installed. Trying again after installing webdriver",
                2
            )
            if browser in ("chrome", "chromeheadless"):
                ConfigModule.add_config_value("Selenium_driver_paths", "chrome_path", ChromeDriverManager().install())
            elif browser in ("firefox", "firefoxheadless"):
                ConfigModule.add_config_value("Selenium_driver_paths", "firefox_path", GeckoDriverManager().install())
            elif browser in ("microsoft edge chromium", "EdgeChromiumHeadless"):
                ConfigModule.add_config_value("Selenium_driver_paths", "edge_path", EdgeChromiumDriverManager().install())
            elif browser == "opera":
                ConfigModule.add_config_value("Selenium_driver_paths", "opera_path", OperaDriverManager().install())
            elif browser == "ie":
                ConfigModule.add_config_value("Selenium_driver_paths", "ie_path", IEDriverManager().install())
            Open_Browser(dependency, window_size_X, window_size_Y)
        else:
            return CommonUtil.Exception_Handler(sys.exc_info())

    except Exception:
        CommonUtil.teardown = False
        return CommonUtil.Exception_Handler(sys.exc_info())


@deprecated
@logger
def Open_Browser_Wrapper(step_data):
    """ Temporary wrapper for open_browser() until that function can be updated to use only data_set """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        global dependency
        # Get the dependency again in case it was missed
        if Shared_Resources.Test_Shared_Variables("dependency"):  # Check if driver is already set in shared variables
            dependency = Shared_Resources.Get_Shared_Variables("dependency")  # Retrieve selenium driver

        cmd = step_data[0][2]  # Expected "open" or "close" for current method. May contain other strings for old method of Field="open browser"
        if cmd.lower().strip() == "close":  # User issued close command
            try:
                selenium_driver.close()
            except:
                pass
            return "passed"
        else:  # User issued "open" command or used old method of "open browser"
            return Open_Browser(dependency)
    except Exception:
        ErrorMessage = "failed to open browser"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

@logger
def Open_Empty_Browser(step_data):
    """Open Empty Browser.

       Args:
       data_set:
       open browser       | selenium action    | open

       Returns:
       "passed" if browser open is successful.
       "zeuz_failed" otherwise.
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    window_size_X = ConfigModule.get_config_value("", "window_size_x")
    window_size_Y = ConfigModule.get_config_value("", "window_size_y")
    # Open browser and create driver if user has not already done so
    global dependency
    global selenium_driver
    global selenium_details
    global current_driver_id

    if Shared_Resources.Test_Shared_Variables("dependency"):
        dependency = Shared_Resources.Get_Shared_Variables("dependency")
    else:
        raise ValueError("No dependency set - Cannot run")

    try:
        driver_id = ""
        for left, mid, right in step_data:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "driverid":
                driver_id = right.strip()

        if not driver_id:
            driver_id = "default"

        browser_map = {
            "Microsoft Edge Chromium": 'msedge',
            "Chrome": "chrome",
            "FireFox": "firefox",
            "Opera": "opera",
            "ChromeHeadless": "chrome",
            "FirefoxHeadless": "firefox",
            "EdgeChromiumHeadless": "msedge",
        }

        if driver_id not in selenium_details or selenium_details[driver_id]["driver"].capabilities["browserName"].strip().lower() != browser_map[dependency["Browser"]]:
            if driver_id in selenium_details and selenium_details[driver_id]["driver"].capabilities["browserName"].strip().lower() != browser_map[dependency["Browser"]]:
                Tear_Down_Selenium()    # If dependency is changed then teardown and relaunch selenium driver
            CommonUtil.ExecLog(sModuleInfo, "Browser not previously opened, doing so now", 1)
            if window_size_X == "None" and window_size_Y == "None":
                result = Open_Browser(dependency)
            elif window_size_X == "None":
                result = Open_Browser(dependency, window_size_Y)
            elif window_size_Y == "None":
                result = Open_Browser(dependency, window_size_X)
            else:
                result = Open_Browser(dependency, window_size_X, window_size_Y)

            if result == "zeuz_failed":
                return "zeuz_failed"

            selenium_details[driver_id] = {"driver": Shared_Resources.Get_Shared_Variables("selenium_driver")}

        else:
            selenium_driver = selenium_details[driver_id]["driver"]
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)

        return "passed"
    except Exception:
        ErrorMessage = "failed to open browser"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

@logger
def Go_To_Link(step_data, page_title=False):
    # this function needs work with validating page title.  We need to check if user entered any title.
    # if not then we don't do the validation
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    window_size_X = ConfigModule.get_config_value("", "window_size_x")
    window_size_Y = ConfigModule.get_config_value("", "window_size_y")

    # default capabilities
    capabilities = {"unhandledPromptBehavior": "ignore"}

    # options for add_argument or add_extension etc
    browser_options = []
    profile_options = []

    # Open browser and create driver if user has not already done so
    global dependency
    global selenium_driver
    global selenium_details
    global current_driver_id
    if Shared_Resources.Test_Shared_Variables("dependency"):
        dependency = Shared_Resources.Get_Shared_Variables("dependency")
    else:
        raise ValueError("No dependency set - Cannot run")

    page_load_timeout_sec = 120

    try:
        driver_id = ""
        for left, mid, right in step_data:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "gotolink":
                web_link = right.strip()
            elif left == "driverid":
                driver_id = right.strip()
            elif left == "waittimetoappearelement":
                Shared_Resources.Set_Shared_Variables("element_wait", float(right.strip()))
            elif left == "waittimetopageload":
                page_load_timeout_sec = int(right.strip())
            # checks for capabilities and modifies them by the given step_data
            elif mid.strip().lower() == "shared capability":
                if left.strip().lower() in ("promptbehavior", "alertbehavior"):
                    if right.strip().lower() in ("accept", "yes", "ok"):
                        capabilities["unhandledPromptBehavior"] = "accept"

                    elif right.strip().lower() in ("dismiss", "no", "cancel"):
                        capabilities["unhandledPromptBehavior"] = "dismiss"

                else:
                    # any other shared capabilities can be added from the selenium document
                    capabilities[left.strip()] = right.strip()

            # Todo: profile, argument, extension, chrome option => go_to_link
            elif mid.strip().lower() in ("chrome option", "chrome options") and dependency["Browser"].lower() == "chrome":
                browser_options.append([left, right.strip()])
            elif mid.strip().lower() in ("chrome experimental option", "chrome experimental options") and dependency["Browser"].lower() == "chrome":
                browser_options.append(["addexperimentaloption", {left.strip():CommonUtil.parse_value_into_object(right.strip())}])
            elif mid.strip().lower() in ("profile option", "profile options"):
                profile_options.append([left, right.strip()])

        if browser_options:
            CommonUtil.ExecLog(sModuleInfo, f"Got these browser_options\n{browser_options}", 1)

        if not driver_id:
            driver_id = "default"

        browser_map = {
            "Microsoft Edge Chromium": 'msedge',
            "Chrome": "chrome",
            "FireFox": "firefox",
            "Opera": "opera",
            "ChromeHeadless": "chrome",
            "FirefoxHeadless": "firefox",
            "EdgeChromiumHeadless": "msedge",
        }

        
        is_browserstack = 'browserstack' in dependency["Browser"]
        if is_browserstack and driver_id in selenium_details:
            selenium_driver = selenium_details[driver_id]["driver"]
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)

        elif driver_id not in selenium_details or selenium_details[driver_id]["driver"].capabilities["browserName"].strip().lower() != browser_map[dependency["Browser"]]:
            if driver_id in selenium_details and selenium_details[driver_id]["driver"].capabilities["browserName"].strip().lower() != browser_map[dependency["Browser"]]:
                Tear_Down_Selenium()    # If dependency is changed then teardown and relaunch selenium driver
            CommonUtil.ExecLog(sModuleInfo, "Browser not previously opened, doing so now", 1)
            if window_size_X == "None" and window_size_Y == "None":
                result = Open_Browser(dependency, capability=capabilities, browser_options=browser_options, profile_options=profile_options)
            elif window_size_X == "None":
                result = Open_Browser(dependency, window_size_Y, capability=capabilities, browser_options=browser_options, profile_options=profile_options)
            elif window_size_Y == "None":
                result = Open_Browser(dependency, window_size_X, capability=capabilities, browser_options=browser_options, profile_options=profile_options)
            else:
                result = Open_Browser(dependency, window_size_X, window_size_Y, capability=capabilities, browser_options=browser_options, profile_options=profile_options)

            if result == "zeuz_failed":
                return "zeuz_failed"

            selenium_details[driver_id] = {"driver": Shared_Resources.Get_Shared_Variables("selenium_driver")}
            if selenium_driver.capabilities["browserName"].strip().lower() in ("chrome", "msedge"):
                try:
                    selenium_driver.execute_cdp_cmd("Performance.enable", {})
                except:
                    CommonUtil.ExecLog(
                        sModuleInfo, "Unable to execute cdp command - Performance.enable", 3
                    )

        else:
            selenium_driver = selenium_details[driver_id]["driver"]
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
        current_driver_id = driver_id
    except Exception:
        ErrorMessage = "failed to open browser"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

    # Set timeout
    selenium_driver.set_page_load_timeout(page_load_timeout_sec)

    # Open URL in browser
    try:
        try:
            selenium_driver.get(web_link)
        except TimeoutException as e:
            CommonUtil.ExecLog(sModuleInfo, "Maximum page load time reached. Loading and proceeding", 2)

        selenium_driver.implicitly_wait(0.5)  # Wait for page to load
        CommonUtil.ExecLog(sModuleInfo, "Successfully opened your link with driver_id='%s': %s" % (driver_id, web_link), 1)
    except WebDriverException as e:
        browser = selenium_driver.capabilities["browserName"].strip().lower()
        if (browser in ("chrome", "msedge", "opera") and e.msg.lower().startswith("chrome not reachable")) or (browser == "firefox" and e.msg.lower().startswith("tried to run command without establishing a connection")):
            CommonUtil.ExecLog(sModuleInfo, "Browser not found. trying to restart the browser", 2)
            # If the browser is closed but selenium instance is on, relaunch selenium_driver
            if Shared_Resources.Test_Shared_Variables("dependency"):
                dependency = Shared_Resources.Get_Shared_Variables("dependency")
            else:
                return CommonUtil.Exception_Handler(sys.exc_info())
            if window_size_X == "None" and window_size_Y == "None":
                result = Open_Browser(dependency, capability=capabilities, browser_options=browser_options, profile_options=profile_options)
            elif window_size_X == "None":
                result = Open_Browser(dependency, window_size_Y, capability=capabilities, browser_options=browser_options, profile_options=profile_options)
            elif window_size_Y == "None":
                result = Open_Browser(dependency, window_size_X, capability=capabilities, browser_options=browser_options, profile_options=profile_options)
            else:
                result = Open_Browser(dependency, window_size_X, window_size_Y, capability=capabilities, browser_options=browser_options, profile_options=profile_options)
        else:
            result = "zeuz_failed"

        if result == "zeuz_failed":
            ErrorMessage = "failed to open your link with driver_id='%s: %s" % (driver_id, web_link)
            return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)
        try:
            selenium_details[driver_id] = {"driver": Shared_Resources.Get_Shared_Variables("selenium_driver")}
            selenium_driver.get(web_link)
            selenium_driver.implicitly_wait(0.5)
            CommonUtil.ExecLog(sModuleInfo, "Successfully opened your link with driver_id='%s': %s" % (driver_id, web_link), 1)
        except Exception:
            ErrorMessage = "failed to open your link: %s" % (web_link)
            return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)
    except Exception:
        ErrorMessage = "failed to open your link: %s" % (web_link)
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)

    # collect_browser_metrics(current_driver_id, CommonUtil.current_action_name)
    return "passed"


def collect_browser_metrics(driver_id, label):
    # Collect custom performance metrics
    try:
        if selenium_driver.capabilities["browserName"].strip().lower() not in ("chrome", "msedge"):
            return {}

        metrics = selenium_driver.execute_cdp_cmd('Performance.getMetrics', {})
        metrics_dict = {}
        # FCP - First Contentful Paint
        try: metrics_dict["first_contentful_paint"] = selenium_driver.execute_script(JS_FCP)
        except: metrics_dict["first_contentful_paint"] = 0
        # LCP - Largest Contenful Paint
        try: metrics_dict["largest_contentful_paint"] = selenium_driver.execute_async_script(JS_LCP)
        except: metrics_dict["largest_contentful_paint"] = 0
        metrics_dict.update({data["name"]: data["value"] for data in metrics["metrics"]})

        # Collect identifying information
        metrics_dict["label"] = label
        metrics_dict["tc_id"] = CommonUtil.current_tc_no
        metrics_dict["step_name"] = CommonUtil.current_step_name
        metrics_dict["step_sequence"] = CommonUtil.current_step_sequence
        metrics_dict["step_id"] = CommonUtil.current_step_id
        metrics_dict["time_stamp"] = CommonUtil.get_timestamp()

        if driver_id not in CommonUtil.browser_perf:
            CommonUtil.browser_perf[driver_id] = [metrics_dict]
        else:
            CommonUtil.browser_perf[driver_id].append(metrics_dict)

            # CommonUtil.prettify(key="metrics", val=metrics_dict)
        return metrics_dict
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())



@logger
def Handle_Browser_Alert(step_data):
    # accepts browser alert
    """
    wait           optional parameter  5.0
    handle alert   selenium action     get text = my_variable
    handle alert   selenium action     send text = my text to send to alert
    handle alert   selenium action     accept, pass, yes, ok (any of these would work)
    handle alert   selenium action     reject, fail, no, cancel (any of these would work)
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    wait = 5.0
    choice, choice_lower = "", ""
    try:
        for left, mid, right in step_data:
            left = left.lower()
            if "handle alert" in left:
                choice = right
                choice_lower = right.strip().lower()
            elif "wait" in left:
                wait = float(right.strip())

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Failed to parse data", 3)
        return "zeuz_failed"

    try:
        CommonUtil.ExecLog("", "Waiting %s seconds max for the alert box to appear" % str(wait), 1)
        WebDriverWait(selenium_driver, wait).until(EC.alert_is_present())
        time.sleep(2)
    except TimeoutException:
        CommonUtil.ExecLog(sModuleInfo, "Waited %s seconds but no alert box appeared" % str(wait), 3)
        return "zeuz_failed"

    try:
        if choice_lower in ("accept", "pass", "yes", "ok"):
            Alert(selenium_driver).accept()
            CommonUtil.ExecLog(sModuleInfo, "Browser alert accepted", 1)
            return "passed"

        elif choice_lower in ("reject", "decline", "dismiss", "fail", "no", "cancel"):
            Alert(selenium_driver).dismiss()
            CommonUtil.ExecLog(sModuleInfo, "Browser alert rejected", 1)
            return "passed"

        elif choice_lower.replace(" ", "").replace("_", "").startswith("gettext"):
            alert_text = Alert(selenium_driver).text
            Alert(selenium_driver).accept()
            variable_name = (choice.split("="))[1].strip()
            return Shared_Resources.Set_Shared_Variables(variable_name, alert_text)

        elif choice_lower.replace(" ", "").replace("_", "").startswith("sendtext"):
            text_to_send = (choice.split("="))[1].strip()
            Alert(selenium_driver).send_keys(text_to_send)
            Alert(selenium_driver).accept()
            return "passed"

        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Wrong Step Data. The following are valid data --\n" +
                "1. (handle alert, selenium action, ok)" +
                "2. (handle alert, selenium action, cancel)" +
                "3. (handle alert, selenium action, get text = var_name)" +
                "4. (handle alert, selenium action, send text = some text)",
                3,
            )
            return "zeuz_failed"

    except Exception:
        ErrorMessage = "Failed to handle alert"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, ErrorMessage)


@logger
@deprecated
def Initialize_List(data_set):
    """ Temporary wrapper until we can convert everything to use just data_set and not need the extra [] """
    return Shared_Resources.Initialize_List([data_set])


@logger
def save_screenshot(driver, path):
    """
    Take the screenshot of the whole web page
    :param driver: selenium driver
    :param path: where to save the screenshot
    :return: None
    """
    # Ref: https://stackoverflow.com/a/52572919
    import time

    original_size = driver.get_window_size()
    required_width = driver.execute_script(
        "return document.body.parentNode.scrollWidth"
    )
    required_height = driver.execute_script(
        "return document.body.parentNode.scrollHeight"
    )
    driver.set_window_size(required_width, required_height)
    time.sleep(2)
    # driver.save_screenshot(path)  # has scrollbar
    driver.find_element("xpath","//body").screenshot(path)  # avoids scrollbar
    time.sleep(2)
    driver.set_window_size(original_size["width"], original_size["height"])


@logger
def take_screenshot_selenium(data_set):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    try:
        filename_format = "%Y_%m_%d_%H-%M-%S"
        fullscreen = False

        for left, mid, right in data_set:
            if "take screenshot web" in left:
                if "default" not in right:
                    filename_format = right.strip()
            if "fullscreen" in left:
                fullscreen = right.lower().strip() == "true"

        screenshot_folder = ConfigModule.get_config_value(
            "sectionOne", "screen_capture_folder", temp_config
        )
        filename = time.strftime(filename_format) + ".png"
        screenshot_path = str(Path(screenshot_folder) / Path(filename))

        if fullscreen:
            save_screenshot(selenium_driver, screenshot_path)
        else:
            selenium_driver.save_screenshot(screenshot_path)

        # Save the screenshot's name into a variable
        Shared_Resources.Set_Shared_Variables("zeuz_screenshot", filename)
    except Exception:
        errMsg = "Failed to take screenshot"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

def Change_Attribute_Value(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        change_value = ""
        attribute_name = ""
        global selenium_driver
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"
        for left, mid, right in step_data:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if "input parameter" in mid:
                attribute_name = left
                change_value = right

        selenium_driver.execute_script(f"arguments[0].{attribute_name} = `{change_value}`;", Element)
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of the attribute to: %s" % change_value, 1)
        return "passed"
    except Exception:
        errMsg = "Could not find your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)

# Method to enter texts in a text box; step data passed on by the user
@logger
def Enter_Text_In_Text_Box(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        delay = 0
        text_value = ""
        use_js = False
        clear = True
        global selenium_driver
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"
        for left, mid, right in step_data:
            mid = mid.strip().lower()
            left = left.strip().lower()
            if mid == "action":
                text_value = right
            elif left == "delay":
                delay = float(right.strip())
            elif left == "use js":
                use_js = right.strip().lower() in ("true", "yes", "1")
            elif left == "clear":
                clear = False if right.strip().lower() in ("no", "false") else True
        if use_js:  # Use js will automatically clear the field and then enter text
            try:
                selenium_driver.execute_script("arguments[0].click();", Element)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Entering text without clicking the element", 2)
            # Fill up the value.
            selenium_driver.execute_script(f"arguments[0].value = `{text_value}`;", Element)
            # Sometimes text field becomes unclickable after entering text?
            selenium_driver.execute_script("arguments[0].click();", Element)
        else:
            try:
                Element = handle_clickability_and_click(step_data, Element)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Entering text without clicking the element", 2)
            if clear:
                # Element.clear()
                # Safari Keys are extremely slow and not working
                if selenium_driver.desired_capabilities['browserName'] == "Safari":
                    Element.clear()
                else:
                    if sys.platform == "darwin":
                        Element.send_keys(Keys.COMMAND, "a")
                    else:
                        Element.send_keys(Keys.CONTROL, "a")
                    Element.send_keys(Keys.DELETE)
                    try:
                        Element.clear() #some cases it works .. so adding it here just incase
                    except:
                        pass
            if delay == 0:
                Element.send_keys(text_value)
            else:
                for c in text_value:
                    Element.send_keys(c)
                    time.sleep(delay)
            try:
                Element.click()
            except:  # sometimes text field can be unclickable after entering text
                pass
        CommonUtil.ExecLog(sModuleInfo, "Successfully set the value of to text to: %s" % text_value, 1)
        return "passed"
    except Exception:
        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def Keystroke_For_Element(data_set):
    """ Send a key stroke or string to an element or wherever the cursor is located """
    # Keystroke Keys: Any key. Eg: Tab, Escape, etc
    # Keystroke Chars: Any string. Eg: The quick brown...
    # If no element parameter is provided, it will enter the keystroke wherever the cursor is located

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    # Parse the data set
    try:
        stype = ""  # keys/chars
        get_element = False  # Use element
        key_count = 1  # Default number of button presses
        for row in data_set:
            if row[1] == "action":
                if row[0] == "keystroke keys":  # Keypress
                    stype = "keys"
                    keystroke_value = row[2]
                    if "," in keystroke_value:  # If user supplied a number of presses
                        keystroke_value.replace(" ", "")
                        keystroke_value, key_count = keystroke_value.split(
                            ","
                        )  # Save keypress and count
                        key_count = int(key_count)
                elif row[0] == "keystroke chars":  # String
                    stype = "chars"
                    keystroke_value = row[2]
            elif row[1] == "element parameter":
                get_element = True

        if stype == "":
            CommonUtil.ExecLog(sModuleInfo, "Field contains incorrect data", 3)
            return "zeuz_failed"

    except:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error parsing data set"
        )

    # Get the element, or if none provided, create action chains for keystroke insertion without an element
    if get_element:
        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Failed to locate element", 3)
            return "zeuz_failed"
    else:
        Element = ActionChains(selenium_driver)

    # Insert keystroke
    try:
        if stype == "keys":
            # Requires: python-selenium v3.1+, geckodriver v0.15.0+
            keystroke_value = keystroke_value.upper().replace("CTRL", "CONTROL")
            if "+" in keystroke_value:
                hotkey_list = keystroke_value.split("+")
                for i in range(len(hotkey_list)):
                    if hotkey_list[i] in list(dict(Keys.__dict__).keys())[2:-2]:
                        Element.key_down(getattr(Keys, hotkey_list[i]))
                    else:
                        Element.key_down(hotkey_list[i])
                for i in range(len(hotkey_list)).__reversed__():
                    if hotkey_list[i] in list(dict(Keys.__dict__).keys())[2:-2]:
                        Element.key_up(getattr(Keys, hotkey_list[i]))
                    else:
                        Element.key_up(hotkey_list[i])
                Element.perform()
                result = "passed"

            else:
                get_keystroke_value = getattr(Keys, keystroke_value)  # Create an object for the keystroke
                result = Element.send_keys(get_keystroke_value * key_count)  # Prepare keystroke for sending if Actions, or send if Element
                if not get_element:
                    Element.perform()  # Send keystroke
        else:
            result = Element.send_keys(keystroke_value)
            if not get_element:
                Element.perform()
    except:
        return CommonUtil.Exception_Handler(
            sys.exc_info(),
            None,
            "Error sending keystroke %s: %s" % (stype, keystroke_value),
        )

    # Test result
    if result not in failed_tag_list:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Successfully sent %s: %s %d times" % (stype, keystroke_value, key_count),
            1,
        )
        return "passed"
    else:
        CommonUtil.ExecLog(
            sModuleInfo,
            "Error sending keystroke %s: %s %d times"
            % (stype, keystroke_value, key_count),
            3,
        )
        return "zeuz_failed"


@logger
def execute_javascript(data_set):
    """Executes the JavaScript code.

    Args:
        data_set:
          id/class/etc       | element parameter  | button_id     ; optional row
          variable           | optional parameter | var_name      ; store result into variable
          execute javascript | selenium action    | js_code_here  ; example: $elem.click();

    Returns:
        "passed" if the given script execution is successful.
        "zeuz_failed" otherwise.
    """

    try:
        Element = False
        var_name = None
        script_to_exec = None

        for left, mid, right in data_set:
            left = left.lower().strip()
            mid = mid.lower().strip()
            right = right.strip()

            if "element parameter" in mid:
                Element = True
            if "variable" == left:
                var_name = right
            if "javascript" in left:
                script_to_exec = right

        # Element parameter is provided to use Zeuz Node's element finding approach.
        if Element:
            Element = LocateElement.Get_Element(data_set, selenium_driver)
            # Replace "$elem" with "arguments[0]". For convenience only.
            script_to_exec = script_to_exec.replace("$elem", "arguments[0]")
            # Execute the script.
            result = selenium_driver.execute_script(script_to_exec, Element)
        else:
            result = selenium_driver.execute_script(script_to_exec, None)

        if var_name:
            return Shared_Resources.Set_Shared_Variables(var_name, result)
        else:
            return "passed"
    except Exception:
        errMsg = "Make sure element parameter is provided in the action."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


def handle_clickability_and_click(dataset, Element:selenium.webdriver.remote.webelement.WebElement):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    wait_clickable = Shared_Resources.Get_Shared_Variables("element_wait")
    # for left, mid, right in dataset:
    #     if mid.strip().lower() == "option":
    #         left = left.strip().lower()
    #         if "wait" in left and "clickable" in left:
    #             wait_clickable = int(right.strip())
    # if not wait_clickable:
    #     Element.click()     # no need of try except here. we need to return the exact exception upto this point
    # else:
    log_flag = True
    log_flag2 = True
    first = True
    start = time.perf_counter()
    stale_i = 0
    while True:
        try:
            Element.click()
            if not first:
                CommonUtil.ExecLog(sModuleInfo, "Element has become clickable after %s seconds" % round(time.perf_counter() - start, 2), 2)
            return Element
        except ElementClickInterceptedException:
            first = False
            if log_flag:
                CommonUtil.ExecLog(sModuleInfo, "Click is Intercepted. Waiting %s seconds max for the element to become clickable" % wait_clickable, 2)
                log_flag = False
        except StaleElementReferenceException:
            first = False
            if log_flag2:
                CommonUtil.ExecLog(sModuleInfo, "Element is stale. Waiting %s seconds max for the element to become clickable" % wait_clickable, 2)
                log_flag2 = False
            Element = LocateElement.Get_Element(dataset, selenium_driver)  # Element may need to be relocated in stale
            if stale_i == 0:
                stale_i += 1
                continue
        if time.perf_counter() > start + wait_clickable:
            raise Exception     # not StaleElementReferenceException. we don't want js to perform click

# Method to click on element; step data passed on by the user
@logger
def Click_Element(data_set, retry=0):
    """ Click using element or location """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    use_js = False  # Use js to click on element?
    try:
        location = ""
        for row in data_set:
            if row[0] == "offset" and row[1] == "optional parameter":
                location = row[2]  # Save shared variable name, or coordinates if entered directory in step data
            if "use js" in row[0].lower():
                use_js = row[2].strip().lower() in ("true", "yes", "1")
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return "zeuz_failed"
    if location == "":
        try:
            if use_js:
                # Click on element.
                selenium_driver.execute_script("arguments[0].click();", Element)
            else:
                handle_clickability_and_click(data_set, Element)

            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
            return "passed"

        except ElementClickInterceptedException:
            try:
                selenium_driver.execute_script("arguments[0].click();", Element)
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Your element is overlapped with another sibling element. Clicked the element successfully by executing JavaScript",
                    2
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not click and hold your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        except StaleElementReferenceException:
            if retry == 5:
                CommonUtil.ExecLog(sModuleInfo, "Could not perform click because javascript of the element is not fully loaded", 3)
                return "zeuz_failed"
            CommonUtil.ExecLog("", "Javascript of the element is not fully loaded. Trying again after 1 second delay", 2)
            time.sleep(1)
            return Click_Element(data_set, retry + 1)

        except Exception:
            try:
                element_attributes = Element.get_attribute("outerHTML")
                CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                errMsg = "Could not click and hold your element."
                return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
            except:
                return CommonUtil.Exception_Handler(sys.exc_info())

    # Click using location
    else:
        try:
            location = location.replace(" ", "")
            location = location.split(",")
            x = float(location[0])
            y = float(location[1])

            height_width = Element.size

            ele_width = int((height_width)["width"])
            ele_height = int((height_width)["height"])

            total_x_offset = int((ele_width // 2) * (x / 100))
            total_y_offset = int((ele_height // 2) * (y / 100))

            # Click coordinates
            actions = ActionChains(selenium_driver)  # Create actions object
            actions.move_to_element_with_offset(Element, total_x_offset, total_y_offset)  # Move to coordinates (referrenced by body at 0,0)
            actions.click()  # Click action
            actions.perform()  # Perform all actions

            CommonUtil.ExecLog(sModuleInfo, "Click on location successful", 1)
            return "passed"
        except Exception:
            return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error clicking location")


@logger
def Click_and_Download(data_set):
    """ Click and download attachments from web and save it to specific destinations"""
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    if selenium_driver.capabilities["browserName"].strip().lower() not in ("chrome", "msedge", "firefox"):
        CommonUtil.ExecLog(sModuleInfo, "This action was made for Chrome, MS Edge and Firefox. Other browsers won't download files in Zeuz_Download_Folder", 2)

    #Todo:
    # 1. For other browsers than ("chrome", "msedge", "firefox") copy the New files generated in Downloads directory and move them to zeuz_download_folder

    wait_download = 20
    filepath = ""
    automate_firefox = False
    try:
        click_dataset = []
        for left, mid, right in data_set:
            l = left.replace(" ", "").replace("_", "").lower()
            if l == "waitfordownload":
                wait_download = float(right.strip())
            elif l in ("folderpath", "directory", "filepath", "file", "folder") and mid.strip().lower() in ("optional parameter"):
                filepath = right.strip()
                filepath = CommonUtil.path_parser(filepath)
            elif l == "automatefirefoxsavewindow" and mid.strip().lower() in ("optional parameter"):
                automate_firefox = right.strip().lower() in ("accept", "yes", "ok", "true")
            else:
                click_dataset.append((left, mid, right))

            # On next improvement user will have option to tell the filename and only that filename will be copied from
            # the initial download directory
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    try:
        if Click_Element(click_dataset) == "zeuz_failed":
            return "zeuz_failed"
        if selenium_driver.capabilities["browserName"].strip().lower() == "firefox" and automate_firefox:
            if platform.system() == "Windows":
                try:
                    from Framework.Built_In_Automation.Desktop.Windows.BuiltInFunctions import Click_Element as win_Click_Element, wait_for_element
                    pid = str(selenium_driver.capabilities["moz:processID"])
                    window_ds = ("window pid", "element parameter", pid)
                    wait_ds = [
                        window_ds,
                        ("Name", "element parameter", "Save File"),
                        ("LocalizedControlType", "element parameter", "radio button"),
                        ("wait to appear", "windows action", "10"),
                    ]
                    CommonUtil.ExecLog(sModuleInfo, "Checking if any Save window is opened", 1)
                    if wait_for_element(wait_ds) == "zeuz_failed":
                        CommonUtil.ExecLog(sModuleInfo, "No Save window is found. Continuing...", 1)
                    else:
                        save_click_ds = [
                            window_ds,
                            ("Name", "element parameter", "Save File"),
                            ("LocalizedControlType", "element parameter", "radio button"),
                            ("click", "windows action", "click"),
                        ]
                        if win_Click_Element(save_click_ds) == "zeuz_failed":
                            CommonUtil.ExecLog(sModuleInfo, "Could not click Save Button. Switching to GUI method", 2)
                            import pyautogui
                            pyautogui.hotkey("down")
                            pyautogui.hotkey("enter")

                        else:
                            # remember_choice_ds = [
                            #     window_ds,
                            #     ("wait", "optional parameter", "5"),
                            #     ("*Name", "element parameter", "Do this automatically"),
                            #     ("LocalizedControlType", "element parameter", "check box"),
                            #     ("click", "windows action", "click"),
                            # ]
                            # if win_Click_Element(remember_choice_ds) == "zeuz_failed":
                            #     CommonUtil.ExecLog(sModuleInfo, "Could not click remember choice Button", 2)
                            ok_ds = [
                                window_ds,
                                ("Name", "element parameter", "OK"),
                                ("LocalizedControlType", "element parameter", "button"),
                                ("click", "windows action", "click"),
                            ]
                            if win_Click_Element(ok_ds) == "zeuz_failed":
                                CommonUtil.ExecLog(sModuleInfo, "Could not find the OK button. Switching to GUI method (pressing Enter)", 2)
                                import pyautogui
                                pyautogui.hotkey("enter")
                except:
                    CommonUtil.ExecLog(sModuleInfo, "Could not check if any save window was opened. Continuing...", 2)

            else:
                # Todo: Test this on Mac and Linux
                import pyautogui
                pyautogui.hotkey("down")
                pyautogui.hotkey("enter")

        if selenium_driver.capabilities["browserName"].strip().lower() in ("chrome", "msedge", "firefox"):
            CommonUtil.ExecLog(sModuleInfo, "Download started. Will wait max %s seconds..." % wait_download, 1)
            s = time.perf_counter()
            if selenium_driver.capabilities["browserName"].strip().lower() == "firefox":
                ext = ".part"
            elif selenium_driver.capabilities["browserName"].strip().lower() == "opera":
                ext = ".opera"
            else:
                ext = ".crdownload"
            e = 0
            while True:
                try:
                    ld = os.listdir(initial_download_folder)
                    if all([len(ld) > 0, all([not i.endswith(".tmp") and not i.endswith(ext) for i in ld])]):
                        CommonUtil.ExecLog(sModuleInfo, "Download Finished in %s seconds" % round(time.perf_counter()-s, 2), 1)
                        break
                    if s + wait_download < time.perf_counter():
                        CommonUtil.ExecLog(sModuleInfo, "Could not finish download within %s seconds. You can increase the amount of seconds with (wait for download, optional parameter, 60)" % wait_download, 2)
                        break
                except:
                    CommonUtil.Exception_Handler(sys.exc_info())
                    time.sleep(2)
                    e += 1
                    if e == 3: break
        else:
            time.sleep(2)
        time.sleep(3)

        if filepath:
            # filepath = Shared_Resources.Get_Shared_Variables("zeuz_download_folder")
            source_folder = initial_download_folder
            all_source_dir = [os.path.join(source_folder, f) for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
            new_path = filepath
            for file_to_be_moved in all_source_dir:
                file_name = Path(file_to_be_moved).name
                if "." not in os.path.basename(new_path) and not os.path.exists(new_path):
                    # if the path is a directory and does not exist then create the directory
                    Path(new_path).mkdir(parents=True, exist_ok=True)
                elif "." in os.path.basename(new_path) and not os.path.exists(new_path):
                    # if the path is a filepath and the directory does not exist then create the directory
                    Path(os.path.dirname(new_path)).mkdir(parents=True, exist_ok=True)
                shutil.move(file_to_be_moved, new_path)

                # after performing shutil.move() we have to check that if the file with new name exists in correct location.
                # if the file exists in correct position then return passed
                # if the file doesn't exist in correct position then return failed
                if "." not in os.path.basename(new_path):
                    file_path_for_check_after_move = os.path.join(new_path, file_name)
                    if os.path.isfile(file_path_for_check_after_move):
                        CommonUtil.ExecLog(sModuleInfo, "File '%s' is moved to '%s'" % (file_name, file_path_for_check_after_move), 1)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "File failed to move", 3)
                        return "zeuz_failed"
                else:
                    if os.path.isfile(new_path):
                        CommonUtil.ExecLog(sModuleInfo, "File '%s' is moved to '%s'" % (file_name, new_path), 1)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "File failed to move", 3)
                        return "zeuz_failed"
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Mouse_Click_Element(data_set):
    """
    This funciton will move the mouse to the element and then perform a physical mouse click

    element_prop        element parameter          element_value
    mouse click        selenium action            click



    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    # Click using elemen
    CommonUtil.ExecLog(sModuleInfo, "Looking for element", 0)
    # Get element object
    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return "zeuz_failed"
    # Get element location

    # Get element size
    try:
        size_ele = (
            Element.size
        )  # Retreive the dictionary containing the x,y location coordinates
        if size_ele in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not get element location", 3)
            return "zeuz_failed"
        # Find center of the element. We will use offset
        width = (size_ele["width"]) / 2
        height = (size_ele["height"]) / 2
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error retrieving element location"
        )
    try:
        actions = ActionChains(selenium_driver)
        actions.move_to_element_with_offset(Element, width, height).click().perform()
        CommonUtil.ExecLog(sModuleInfo, "Successfully clicked the element", 1)
        return "passed"
    except Exception:

        errMsg = "Could not select/click your element."
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


# Method to click and hold on element; step data passed on by the user
@logger
def Click_and_Text(data_set):
    """ Click and enter text specially for dropdown box"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        data_set_to = []
        data_set_to2 = []

        for row in data_set:
            if row[0] == "click and enter text" and row[1] == "action":
                row[2].lower()
                data_set_to2.append(("keystroke chars", "action", row[2]))

            elif row[1] == "element parameter":
                data_set_to.append(row)
        Click_Element(data_set_to)

        Keystroke_For_Element(data_set_to2)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Click_and_Hold_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element != "zeuz_failed":
            try:
                click_and_hold = ActionChains(selenium_driver).click_and_hold(Element)
                click_and_hold.perform()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully clicked and held the element with given parameters and values",
                    1,
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not click and hold your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to right click on element; step data passed on by the user
@logger
def Context_Click_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element != "zeuz_failed":
            try:
                context_click = ActionChains(selenium_driver).context_click(Element)
                context_click.perform()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully right clicked the element with given parameters and values",
                    1,
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not click and hold your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to double click on element; step data passed on by the user
@logger
def Double_Click_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element != "zeuz_failed":
            try:
                double_click = ActionChains(selenium_driver).double_click(Element)
                double_click.perform()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully double clicked the element with given parameters and values",
                    1,
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not click and hold your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to move to middle of the element; step data passed on by the user
@logger
def Move_To_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element != "zeuz_failed":
            try:
                move = ActionChains(selenium_driver).move_to_element(Element).perform()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully moved to the middle of the element with given parameters and values",
                    1,
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not click and hold your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to hover over element; step data passed on by the user
@logger
def Hover_Over_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element != "zeuz_failed":
            try:
                hov = ActionChains(selenium_driver).move_to_element(Element)
                hov.perform()
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Successfully hovered over the element with given parameters and values",
                    1,
                )
                return "passed"
            except Exception:
                try:
                    element_attributes = Element.get_attribute("outerHTML")
                    CommonUtil.ExecLog(sModuleInfo, "Element Attributes: %s" % (element_attributes), 3)
                    errMsg = "Could not select/hover your element."
                    return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                except:
                    return CommonUtil.Exception_Handler(sys.exc_info())
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def get_location_of_element(data_set):
    """ Returns the x,y location of an element """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    # Parse data set
    try:
        shared_var = ""
        for row in data_set:
            if row[1] == "action":
                shared_var = row[2]  # Save the shared variable name

        if shared_var == "":
            CommonUtil.ExecLog(
                sModuleInfo, "Shared variable name missing from Value on action row", 3
            )
            return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error parsing data set"
        )

    # Get element object
    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element in failed_tag_list:
        CommonUtil.ExecLog(sModuleInfo, "Could not find element", 3)
        return "zeuz_failed"

    # Get element location
    try:
        location = (
            Element.location
        )  # Retreive the dictionary containing the x,y location coordinates
        if location in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not get element location", 3)
            return "zeuz_failed"

        # Save location as string, in preparation for the shared variable
        x = str(location["x"])
        y = str(location["y"])
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error retrieving element location"
        )

    # Save location in shared variable
    Shared_Resources.Set_Shared_Variables(shared_var, "%s,%s" % (x, y))
    return "passed"


@logger
def Save_Attribute(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        variable_name = None
        new_ds = []
        for each_step_data_item in step_data:
            if "save parameter" == each_step_data_item[1].strip().lower():
                variable_name = each_step_data_item[2].strip()
                attribute_name = each_step_data_item[0].strip().lower()
            else:
                new_ds.append(each_step_data_item)

        if variable_name is None:
            CommonUtil.ExecLog(sModuleInfo, "Variable name should be mentioned. Example: (text, save parameter, var_name)", 3)
            return "zeuz_failed"

        Element = LocateElement.Get_Element(new_ds, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"

        elif attribute_name == "text":
            attribute_value = Element.text
        elif attribute_name == "tag":
            attribute_value = Element.tag_name
        elif attribute_name == "checked":
            attribute_value = Element.is_selected()
        else:
            attribute_value = Element.get_attribute(attribute_name)

        result = Shared_Resources.Set_Shared_Variables(variable_name, attribute_value)
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Value of Variable '%s' could not be saved!!!" % variable_name,
                3,
            )
            return "zeuz_failed"
        else:
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Search for element on new page after a particular time-out duration entered by the user through step-data
@logger
def Wait_For_New_Element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        wait_for_element_to_disappear = False
        for each in step_data:
            if each[1] == "action":
                timeout_duration = int(each[2])
                if each[0] == "wait disable":
                    wait_for_element_to_disappear = True
        start_time = time.time()
        interval = 1
        for i in range(timeout_duration):
            time.sleep(time.time() + i * interval - start_time)
            Element = LocateElement.Get_Element(step_data, selenium_driver)
            if wait_for_element_to_disappear == False:
                if Element == "zeuz_failed":
                    continue
                else:
                    return "passed"
            else:
                if Element == "zeuz_failed":
                    return "passed"
                else:
                    continue
        if wait_for_element_to_disappear == False:
            CommonUtil.ExecLog(
                sModuleInfo, "Waited for %s seconds but couldnt locate your element", 3
            )
        else:
            CommonUtil.ExecLog(
                sModuleInfo, "Waited for %s seconds but your element still exists", 3
            )
        return "zeuz_failed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Validating text from an element given information regarding the expected text
@logger
def Compare_Lists(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        return Shared_Resources.Compare_Lists([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Validating text from an element given information regarding the expected text
@logger
def Compare_Variables(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        return Shared_Resources.Compare_Variables([step_data])
    except:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Inserting a field into a list of shared variables
@logger
def Insert_Into_List(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        if len(step_data) == 1:  # will have to test #saving direct input string data
            list_name = ""
            key = ""
            value = ""
            full_input_key_value_name = ""

            for each_step_data_item in step_data:
                if each_step_data_item[1] == "action":
                    full_input_key_value_name = each_step_data_item[2]

            temp_list = full_input_key_value_name.split(",")
            if len(temp_list) == 1:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Value must contain more than one item, and must be comma separated",
                    3,
                )
                return "zeuz_failed"
            else:
                list_name = temp_list[0].split(":")[1].strip()
                key = temp_list[1].split(":")[1].strip()
                value = temp_list[2].split(":")[1].strip()

            result = Shared_Resources.Set_List_Shared_Variables(list_name, key, value)
            if result in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "In list '%s' Value of Variable '%s' could not be saved!!!"
                    % (list_name, key),
                    3,
                )
                return "zeuz_failed"
            else:
                Shared_Resources.Show_All_Shared_Variables()
                return "passed"

        else:
            Element = LocateElement.Get_Element(step_data, selenium_driver)
            if Element == "zeuz_failed":
                CommonUtil.ExecLog(
                    sModuleInfo, "Unable to locate your element with given data.", 3
                )
                return "zeuz_failed"
            list_name = ""
            key = ""
            for each_step_data_item in step_data:
                if each_step_data_item[1] == "action":
                    key = each_step_data_item[2]
            # get list name from full input_string
            temp_list = key.split(",")
            if len(temp_list) == 1:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Value must contain more than one item, and must be comma separated",
                    3,
                )
                return "zeuz_failed"
            else:
                list_name = str(temp_list[0]).split(":")[1].strip()
                key = str(temp_list[1]).strip()

            # get text from selenium element
            list_of_element_text = Element.text.split("\n")
            visible_list_of_element_text = ""
            for each_text_item in list_of_element_text:
                if each_text_item != "":
                    visible_list_of_element_text += each_text_item
            # save text in the list of shared variables in CommonUtil
            result = Shared_Resources.Set_List_Shared_Variables(
                list_name, key, visible_list_of_element_text
            )
            if result in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "In list '%s' Value of Variable '%s' could not be saved!!!"
                    % (list_name, key),
                    3,
                )
                return "zeuz_failed"
            else:
                Shared_Resources.Show_All_Shared_Variables()
                return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Validating text from an element given information regarding the expected text
@logger
def Save_Text(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
        for each_step_data_item in step_data:
            if each_step_data_item[1] == "action":
                variable_name = each_step_data_item[2]
        list_of_element_text = Element.text.split("\n")
        visible_list_of_element_text = ""
        for each_text_item in list_of_element_text:
            if each_text_item != "":
                visible_list_of_element_text += each_text_item
        result = Shared_Resources.Set_Shared_Variables(
            variable_name, visible_list_of_element_text
        )
        if result in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Value of Variable '%s' could not be saved!!!" % variable_name,
                3,
            )
            return "zeuz_failed"
        else:
            Shared_Resources.Show_All_Shared_Variables()
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def save_attribute_values_in_list(step_data):
    """
    This action will expect users to provide a parent element under which they are expecting
    to collect multiple objects.  Users can provide certain constrain to search their elements
    Sample data:

    aria-label                       element parameter      Calendar

    attributes                       target parameter       data-automation="productItemName",
                                                            class="S58f2saa25a3w1",
                                                            return="text",
                                                            return_contains="128GB",
                                                            return_does_not_contain="Windows 10",
                                                            return_does_not_contain="Linux"

    attributes                       target parameter       class="productPricingContainer_3gTS3",
                                                            return="text",
                                                            return_does_not_contain="99.99"

    save attribute values in list    selenium action        list_name

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        # this is the parent object.  If the user wants to search the entire page, they can
        # provide tag = html
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

        all_elements = []
        target_index = 0
        target = []
        paired = True

        try:
            for left, mid, right in step_data:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.strip()
                if "target parameter" in mid:
                    target.append([[], [], [], []])
                    temp = right.strip(",").split(",")
                    data = []
                    for each in temp:
                        data.append(each.strip().split("="))
                    for i in range(len(data)):
                        for j in range(len(data[i])):
                            data[i][j] = data[i][j].strip()
                            if j == 1:
                                data[i][j] = data[i][j].strip('"')  # dont add another strip here. dont need to strip inside quotation mark

                    for Left, Right in data:
                        if Left == "return":
                            target[target_index][1] = Right
                        elif Left == "return_contains":
                            target[target_index][2].append(Right)
                        elif Left == "return_does_not_contain":
                            target[target_index][3].append(Right)   
                        elif Left.replace(" ", "").replace("_", "") in ("allowhidden", "allowdisable"):
                            target[target_index][0].append(("allow hidden", "optional parameter", Right))
                        else:
                            target[target_index][0].append((Left, "element parameter", Right))

                    target_index = target_index + 1
                elif left == "save attribute values in list":
                    variable_name = right
                elif left == "paired":
                    paired = False if right.lower() == "no" else True

        except:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to parse data. Please write data in correct format", 3
            )
            return "zeuz_failed"

        for each in target:
            all_elements.append(LocateElement.Get_Element(each[0], Element, return_all_elements=True))

        variable_value_size = 0
        for each in all_elements:
            variable_value_size = max(variable_value_size, len(each))

        variable_value = []
        for i in range(variable_value_size):
            variable_value.append([])

        i = 0
        for each in all_elements:
            search_by_attribute = target[i][1]
            j = 0
            for elem in each:
                if search_by_attribute == "text":
                    Attribute_value = elem.text
                elif search_by_attribute == 'tag':
                    Attribute_value = elem.tag_name
                elif search_by_attribute == "checked":
                    Attribute_value = str(elem.is_selected())
                else:
                    Attribute_value = elem.get_attribute(search_by_attribute)
                try:
                    for search_contain in target[i][2]:
                        if not isinstance(search_contain, type(Attribute_value)) or search_contain in Attribute_value or len(search_contain) == 0:
                            break
                    else:
                        if target[i][2]:
                            Attribute_value = None

                    for search_doesnt_contain in target[i][3]:
                        if isinstance(search_doesnt_contain, type(Attribute_value)) and search_doesnt_contain in Attribute_value and len(search_doesnt_contain) != 0:
                            Attribute_value = None
                except:
                    CommonUtil.ExecLog(
                        sModuleInfo, "Couldn't search by return_contains and return_does_not_contain", 2
                    )
                variable_value[j].append(Attribute_value)
                j = j + 1
            i = i + 1
        if target_index == 1:
            variable_value = list(map(list, zip(*variable_value)))[0]
        elif not paired:
            variable_value = list(map(list, zip(*variable_value)))

        return Shared_Resources.Set_Shared_Variables(variable_name, variable_value)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Extract_Table_Data(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
            return "zeuz_failed"
        if Element.tag_name != "tbody":
            CommonUtil.ExecLog(sModuleInfo, 'Tag name of the Element is not "tbody"', 2)
        _row = ""
        _column = ""
        try:
            for left, mid, right in step_data:
                left = left.strip().lower()
                right = right.strip()
                mid = mid.strip().lower()
                if left == "extract table data":
                    variable_name = right
                elif "row" in left and mid == "optional parameter":
                    _row = right.replace(" ", "")
                elif "column" in left and mid == "optional parameter":
                    _column = right.replace(" ", "")


        except:
            CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Please write data in correct format", 3)
            return "zeuz_failed"

        variable_value = []
        all_tr = Element.find_elements("tag name", "tr")
        for row in all_tr:
            all_td = row.find_elements("tag name", "td")
            td_data = []
            for td in all_td:
                text_data = td.get_property("textContent").strip()
                td_data.append(text_data)
            variable_value.append(td_data)
        if _row and "," not in _row and "-" not in _row:
            try:
                int(_row)
                variable_value = [variable_value[int(_row)]]
            except:
                variable_value = eval("variable_value[%s]" % _row)
        if _column and "," not in _column and "-" not in _column:
            try:
                int(_column)
                variable_value = [[i[int(_column)]] for i in variable_value]
            except:
                variable_value = [eval("i[%s]" % _column) for i in variable_value]

        return Shared_Resources.Set_Shared_Variables(variable_name, variable_value)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def save_web_elements_in_list(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        has_element = False
        all_elements = []
        target_index = 0
        target = []
        # paired = True
        try:
            for left, mid, right in step_data:
                left = left.strip().lower()
                mid = mid.strip().lower()
                right = right.strip()
                if not has_element and mid in ("element parameter", "parent parameter", "unique parameter", "child parameter", "sibling parameter"):
                    has_element = True
                elif "target parameter" in mid:
                    target.append([[], [], [], []])
                    temp = right.strip(",").split(",")
                    data = []
                    for each in temp:
                        if each.strip("\n").startswith("return_contains"):
                            data.append(["return_contains", each.split("return_contains")[1].strip()[1:-1].split("=")])
                        elif each.strip("\n").startswith("return_does_not_contain"):
                            data.append(["return_does_not_contain", each.split("return_does_not_contain")[1].strip()[1:-1].split("=")])
                        else:
                            data.append(each.strip().split("="))
                    for i in range(len(data)):
                        for j in range(len(data[i])):
                            if isinstance(data[i][j], str):
                                data[i][j] = data[i][j].strip()
                            if j == 1:
                                if isinstance(data[i][j], list):
                                    data[i][j][0], data[i][j][1] = data[i][j][0].strip().strip('"'), data[i][j][1].strip().strip('"')
                                elif isinstance(data[i][j], str):
                                    data[i][j] = data[i][j].strip('"')  # dont add another strip here. dont need to strip inside quotation mark

                    for Left, Right in data:
                        if Left == "return_contains":
                            target[target_index][2].append(Right)
                        elif Left == "return_does_not_contain":
                            target[target_index][3].append(Right)
                        else:
                            target[target_index][0].append((Left, 'element parameter', Right))

                    target_index = target_index + 1
                elif left == "save web elements in list":
                    variable_name = right
                # elif left == "paired":
                #     paired = False if right.lower() == "no" else True

            if has_element:
                Element = LocateElement.Get_Element(step_data, selenium_driver)
                if Element == "zeuz_failed":
                    CommonUtil.ExecLog(sModuleInfo, "Unable to locate your element with given data.", 3)
                    return "zeuz_failed"
            else:
                Element = selenium_driver
        except:
            CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Please write data in correct format", 3)
            return "zeuz_failed"

        for each in target:
            all_elements.append(LocateElement.Get_Element(each[0], Element, return_all_elements=True))

        cnt = 0
        while cnt < target_index:
            if target[cnt][2]:
                count, to_del = 0, []
                for elem in all_elements[cnt]:
                    for each in target[cnt][2]:
                        if each[0] == "text" and each[1] in elem.text:
                            break
                    else:
                        for each in target[cnt][2]:
                            if each[0] == "tag" and each[1] in elem.tag_name:
                                break
                        else:
                            for each in target[cnt][2]:
                                if each[0] not in ("text", "tag") and elem.get_attribute(each[0]) is None:
                                    break
                            else:
                                for each in target[cnt][2]:
                                    if each[0] not in ("text", "tag") and each[1] in elem.get_attribute(each[0]):
                                        break
                                else:
                                    to_del.append(count)
                    count += 1
                all_elements[cnt] = CommonUtil.Delete_from_list(all_elements[cnt], to_del)
                # Using this function to delete in O(N) complexity
            if target[cnt][3]:
                count, to_del = 0, []
                for elem in all_elements[cnt]:
                    for each in target[cnt][3]:
                        if each[0] == "text" and each[1] in elem.text:
                            to_del.append(count)
                            break
                    else:
                        for each in target[cnt][3]:
                            if each[0] == "tag" and each[1] in elem.tag_name:
                                to_del.append(count)
                                break
                        else:
                            for each in target[cnt][3]:
                                if each[0] not in ("text", "tag") and elem.get_attribute(each[0]) is None:
                                    to_del.append(count)
                                    break
                            else:
                                for each in target[cnt][3]:
                                    if each[0] not in ("text", "tag") and each[1] in elem.get_attribute(each[0]):
                                        to_del.append(count)
                                        break

                    count += 1
                all_elements[cnt] = CommonUtil.Delete_from_list(all_elements[cnt], to_del)

            cnt += 1

        if target_index == 1:
            return Shared_Resources.Set_Shared_Variables(variable_name, all_elements[0])
        else:
            return Shared_Resources.Set_Shared_Variables(variable_name, all_elements)

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Validating text from an element given information regarding the expected text
@logger
def Validate_Text(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        ignore_case = False
        zeuz_ai = None
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"
        for each_step_data_item in step_data:
            if each_step_data_item[1] == "action":
                expected_text_data = each_step_data_item[2]
                validation_type = each_step_data_item[0]
            elif each_step_data_item[1].strip().lower() in ("optional parameter") and each_step_data_item[0] == "ignore case":
                ignore_case = True if each_step_data_item[2].strip().lower() in ("yes", "true", "ok") else False
            elif each_step_data_item[1].strip().lower() == "text classifier offset":
                zeuz_ai = [each_step_data_item[0].strip(), float(each_step_data_item[2])]
        # expected_text_data = step_data[0][len(step_data[0]) - 1][2]
        if ignore_case:
            expected_text_data = expected_text_data.lower()
            list_of_element_text = Element.text.lower().split("\n")
        else:
            list_of_element_text = Element.text.split("\n")
        visible_list_of_element_text = []
        for each_text_item in list_of_element_text:
            if each_text_item != "":
                visible_list_of_element_text.append(each_text_item)

        # if step_data[0][len(step_data[0])-1][0] == "validate partial text":
        if zeuz_ai is not None:
            """{
                "binary_classification":{
                    "expected_category":"success",
                    "confidence": 0.7
                }
             }
             """
            message = " ".join(visible_list_of_element_text)
            labels = [zeuz_ai[0]]
            confidence = zeuz_ai[1]
            return binary_classification(message, labels, confidence)["status"]

        elif validation_type == "validate partial text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
            CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
            for each_actual_text_data_item in actual_text_data:
                if expected_text_data in each_actual_text_data_item:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "The text has been validated by a partial match.",
                        1,
                    )
                    return "passed"
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to validate using partial match.", 3
            )
            return "zeuz_failed"
        # if step_data[0][len(step_data[0])-1][0] == "validate full text":
        elif validation_type == "validate full text":
            actual_text_data = visible_list_of_element_text
            CommonUtil.ExecLog(sModuleInfo, "Expected Text: " + expected_text_data, 1)
            CommonUtil.ExecLog(sModuleInfo, "Actual Text: " + str(actual_text_data), 1)
            if expected_text_data in actual_text_data:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "The text has been validated by using complete match.",
                    1,
                )
                return "passed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Unable to validate using complete match.", 3
                )
                return "zeuz_failed"

        else:
            CommonUtil.ExecLog(sModuleInfo, "Incorrect validation type. Please check step data", 3)
            return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Validate_Url(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        url = selenium_driver.current_url
        expected = ""

        for row in step_data:
            if str(row[1]).strip() == "action":
                expected = str(row[2]).strip()

        if str(expected).startswith("*"):
            expected = expected[1:]
            if expected in url:
                CommonUtil.ExecLog(sModuleInfo, "Expected URL partially matched", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(
                    sModuleInfo, "Expected URL didn't match partially", 3
                )
                return "zeuz_failed"
        else:
            if expected == url:
                CommonUtil.ExecLog(sModuleInfo, "Expected URL matched", 1)
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Expected URL didn't match", 3)
                return "zeuz_failed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to sleep for a particular duration
@logger
def Sleep(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        if 1 < len(step_data) >= 2:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Please provide single row of data for only sleep. Consider using wait instead",
                3,
            )
            return "zeuz_failed"
        else:
            tuple = step_data[0]
            seconds = int(tuple[2])
            CommonUtil.ExecLog(sModuleInfo, "Sleeping for %s seconds" % seconds, 1)
            time.sleep(seconds)
            return "passed"
        # return result
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to scroll down a page
@logger
def Scroll(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    selenium_driver.switch_to.default_content()
    try:
        scroll_inside_element = False
        scroll_window_name = "window"
        scroll_window = ""
        action_row = None

        for row in step_data:
            if str(row[1]) == "action":
                action_row = row
                break

        if not action_row:
            CommonUtil.ExecLog(sModuleInfo, "No action row defined", 3)
            return "zeuz_failed"

        if (
                len(step_data) > 1
        ):  # element given scroll inside element, not on full window
            scroll_inside_element = True
            scroll_window_name = "arguments[0]"

        if scroll_inside_element:
            scroll_window = LocateElement.Get_Element(step_data, selenium_driver)
            if scroll_window in failed_tag_list:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Element through which instructed to scroll not found",
                    3,
                )
                return "zeuz_failed"

            CommonUtil.ExecLog(
                sModuleInfo,
                "Element inside which instructed to scroll has been found. Scrolling thorugh it",
                1,
            )
        else:
            CommonUtil.ExecLog(sModuleInfo, "Scrolling through main window", 1)

        scroll_direction = str(action_row[2]).strip().lower()
        if scroll_direction == "down":
            CommonUtil.ExecLog(sModuleInfo, "Scrolling down", 1)
            result = selenium_driver.execute_script(
                "%s.scrollBy(0,750)" % scroll_window_name, scroll_window
            )
            time.sleep(2)
            return "passed"
        elif scroll_direction == "up":
            CommonUtil.ExecLog(sModuleInfo, "Scrolling up", 1)
            result = selenium_driver.execute_script(
                "%s.scrollBy(0,-750)" % scroll_window_name, scroll_window
            )
            time.sleep(2)
            return "passed"
        elif scroll_direction == "left":
            CommonUtil.ExecLog(sModuleInfo, "Scrolling left", 1)
            result = selenium_driver.execute_script(
                "%s.scrollBy(-750,0)" % scroll_window_name, scroll_window
            )
            time.sleep(2)
            return "passed"
        elif scroll_direction == "right":
            CommonUtil.ExecLog(sModuleInfo, "Scrolling right", 1)
            result = selenium_driver.execute_script(
                "%s.scrollBy(750,0)" % scroll_window_name, scroll_window
            )
            time.sleep(2)
            return "passed"
        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Value invalid. Only 'up', 'down', 'right' and 'left' allowed",
                3,
            )
            result = "zeuz_failed"
            return result

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to scroll to view an element
@logger
def scroll_to_element(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    use_js = False
    try:
        for row in step_data:

            if "use js" in row[0].lower():
                use_js = row[2].strip().lower() in ("true", "yes", "1")
        scroll_element = LocateElement.Get_Element(step_data, selenium_driver)
        if scroll_element in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Element to which instructed to scroll not found", 3
            )
            return "zeuz_failed"

        CommonUtil.ExecLog(
            sModuleInfo,
            "Element to which instructed to scroll has been found. Scrolling to view it",
            1,
        )
        if use_js:
            selenium_driver.execute_script("arguments[0].scrollIntoView(true);", scroll_element)
        else:
            actions = ActionChains(selenium_driver)
            
            actions.move_to_element(scroll_element)
            actions.perform()
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to scroll to view an element
@logger
def scroll_element_to_top(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        scroll_element = LocateElement.Get_Element(step_data, selenium_driver)
        if scroll_element in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Element to which instructed to scroll not found", 3
            )
            return "zeuz_failed"
        CommonUtil.ExecLog(
            sModuleInfo,
            "Element to which instructed to scroll to top of the page has been found. Scrolling to view it at the top",
            1,
        )
        scroll_element.location_once_scrolled_into_view
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to return pass or fail for the step outcome
@logger
def Navigate(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        if 1 < len(step_data) >= 2:
            CommonUtil.ExecLog(sModuleInfo, "Please provide only single row of data", 3)
            return "zeuz_failed"
        else:
            navigate = step_data[0][2]
            if navigate == "back":
                selenium_driver.back()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser back", 1)
            elif navigate == "forward":
                selenium_driver.forward()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser forward", 1)
            elif navigate == "refresh":
                selenium_driver.refresh()
                CommonUtil.ExecLog(sModuleInfo, "Performing browser refresh", 1)
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Value invalid. Only 'back', 'forward', 'refresh' allowed",
                    3,
                )
                return "zeuz_failed"
            return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def Select_Deselect(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        Element = LocateElement.Get_Element(step_data, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

        for each in step_data:
            if each[1] == "action":
                if each[0] == "deselect all":
                    CommonUtil.ExecLog(sModuleInfo, "Deselect all elements", 1)
                    result = Select(Element).deselect_all()
                    # result = selected_Element.deselect_all()
                    return "passed"
                elif each[0] == "deselect by visible text":
                    CommonUtil.ExecLog(sModuleInfo, "Deselect by visible text", 1)
                    visible_text = each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.deselect_by_visible_text(visible_text)
                    return "passed"
                elif each[0] == "deselect by value":
                    CommonUtil.ExecLog(sModuleInfo, "Deselect by value", 1)
                    value = each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.deselect_by_value(value)
                    return "passed"
                elif each[0] == "deselect by index":
                    CommonUtil.ExecLog(sModuleInfo, "Deselect by index", 1)
                    index = int(each[2])
                    selected_Element = Select(Element)
                    result = selected_Element.deselect_by_index(index)
                    return "passed"
                elif each[0] == "select by index":
                    CommonUtil.ExecLog(sModuleInfo, "Select by index", 1)
                    index = each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.select_by_index(index)
                    return "passed"
                elif each[0] == "select by value":
                    CommonUtil.ExecLog(sModuleInfo, "Select by value", 1)
                    value = each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.select_by_value(value)
                    return "passed"
                elif each[0] == "select by visible text":
                    CommonUtil.ExecLog(sModuleInfo, "Select by visible text", 1)
                    visible_text = each[2]
                    selected_Element = Select(Element)
                    result = selected_Element.select_by_visible_text(visible_text)
                    return "passed"
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Value invalid. Only 'deselect all', 'deselect by visible text', etc allowed",
                        3,
                    )
                    result = "zeuz_failed"

            else:
                continue

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def validate_table(data_set):
    """ Compare the table provided in step data with the one found on the web page """
    # Compare a webpage table with one specified in the step data
    # All inputs have the sub-field set as "table parameter"
    # Valid table parameters:
    # > ignore rows: Ignores the comma delimited rows specified in the Value field
    # > ignore columns: Ignores the comma delimited columns specified in the Value field
    # > case: Value=Sensitive: This is the default, and values must match exactly. Value=insensitive: Perform case insensitive matching
    # > exact: True (default) do nothing. False= Infer which cells to ignore. This is similar to ignore rows/cols, but can ignore specific cells if the user does not specify them. Mutually exclusive of ignore rows/cols
    global selenium_driver
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # Initialize variables
    have_table = False  # Tells us if we read a table from the step data
    case_sensitive = True  # Case sensitive search
    coordinates_exact = True  # Table coordinates should match by default
    ignore_rows = []  # List of rows to ignore/skip
    ignore_cols = []  # List of columns to ignore/skip
    user_table = {}  # Constructed user-defined table
    webpage_table = {}  # Constructed webpage table
    exact_table = True  # Require exact table match
    table_type = ""  # Type of table (css/html)

    # Parse data set
    try:
        for row in data_set:
            field, subfield, value = (
                row[0],
                row[1],
                row[2],
            )  # Put data row in understandable variables

            if subfield == "action":
                if value.strip().lower() in ("css", "html"):
                    table_type = value
                else:
                    CommonUtil.ExecLog(
                        sModuleInfo,
                        "Invalid table type in Value on Action line. Should be 'html' or 'css'",
                        3,
                    )
                    return "zeuz_failed"
            elif (
                    subfield == "table parameter"
            ):  # Inspect the table parameters (element parameters go to a different section)

                # Parse table instructions
                if (
                        field == "ignore row" or field == "ignore rows"
                ):  # User specified list of rows to ignore
                    ignore_rows = value.split(
                        ","
                    )  # Get rows as comma delimited string and store in list
                    ignore_rows = list(map(int, ignore_rows))  # Convert to integers
                elif (
                        field == "ignore column" or field == "ignore columns"
                ):  # User specified list of columns to ignore
                    ignore_cols = value.split(
                        ","
                    )  # Get columns as comma delimited string and store in list
                    ignore_cols = list(map(int, ignore_cols))  # Convert to integers
                elif (
                        field == "coordinates"
                ):  # Check if user specifies if table coordinates should match
                    if (
                            value.lower().strip() == "identical"
                    ):  # Table coordinates should match
                        coordinates_exact = True
                    elif (
                            value.lower().strip() == "nonidentical"
                    ):  # Table coordinates don't have to match
                        coordinates_exact = False
                elif field == "case":  # User specified case sensitivity
                    if (
                            value.lower().strip() == "exact"
                            or value.lower().strip() == "sensitive"
                    ):  # Sensitive match (default)
                        case_sensitive = True
                    elif (
                            value.lower().strip() == "insensitive"
                    ):  # Insensitive match - we'll convert everything to lower case
                        case_sensitive = False
                elif field == "exact":  # User specified type of table matching
                    if (
                            value.lower().strip() == "true"
                            or value.lower().strip() == "yes"
                    ):  # Exact table match, but user can specify rows/columns to ignore
                        exact_table = True
                    elif (
                            value.lower().strip() == "false"
                            or value.lower().strip() == "no"
                    ):  # Not an exact match for all cells, only match the ones the user specified
                        exact_table = False
                    else:
                        CommonUtil.ExecLog(
                            sModuleInfo,
                            "Unknown Value for table parameter 'exact'. Should be true or false.",
                            3,
                        )
                        return "zeuz_failed"

                # Create user-defined table
                else:
                    try:
                        table_row, table_col = ("", "")
                        table_row, table_col = field.split(
                            ","
                        )  # Field should be in the format of ROW,COL
                        if (
                                table_row != "" and table_col != ""
                        ):  # Check to ensure this was a table cell identifier - may not be
                            if (
                                    case_sensitive == False
                            ):  # User specified case insensitive serach
                                value = (
                                    value.lower()
                                )  # Prepare this table by setting all cell values to lowercase
                            user_table[
                                "%s,%s" % (table_row, table_col)
                                ] = value  # Save value using the row,col as an identifier
                            have_table = True  # Indicate we have at least one cell of a table specified
                        else:
                            CommonUtil.ExecLog(
                                sModuleInfo, "Unknown Field for table parameter", 3
                            )
                            return "zeuz_failed"
                    except:  # Row may have been blank, or some other issue
                        return CommonUtil.Exception_Handler(
                            sys.exc_info(), None, "Unknown Field for table parameter"
                        )

        # Ensure we have a table from the user
        if have_table == False:
            CommonUtil.ExecLog(
                sModuleInfo,
                "No table values found, or they were not entered in the format of row,column (Eg: 1,2). Please create a table as defined in the documentation",
                3,
            )
            return "zeuz_failed"
        CommonUtil.ExecLog(
            sModuleInfo,
            "Table parameters - Case Sensitive: %s - ignore_rows: %s - ignore_cols: %s - exact: %s"
            % (
                str(case_sensitive),
                str(ignore_rows),
                str(ignore_cols),
                str(exact_table),
            ),
            0,
        )
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error while parsing the data set"
        )

    # Get table from web page
    if table_type == "html":  # HTML type table
        webpage_table = get_webpage_table_html(
            data_set, ignore_rows, ignore_cols, case_sensitive
        )  # Produces an array that should match the user array
    elif table_type == "css":  # CSS type table
        webpage_table = get_webpage_table_css(
            data_set, ignore_rows, ignore_cols, case_sensitive
        )  # Produces an array that should match the user array
    CommonUtil.ExecLog(sModuleInfo, "Webpage table  : %s" % webpage_table, 0)
    CommonUtil.ExecLog(sModuleInfo, "Step data table: %s" % user_table, 0)
    if webpage_table in failed_tag_list:
        CommonUtil.ExecLog(
            sModuleInfo, "Unable to locate your element with given data.", 3
        )
        return "zeuz_failed"

    # If user did not specify any rows or columns to ignore, we will infer that rows and columns NOT defined are meant to be ignored
    # We do this by modifying the webpage table to remove rows and columns that don't match
    if (
            exact_table == False and ignore_rows == [] and ignore_cols == []
    ):  # If user did not specify anything to ignore
        CommonUtil.ExecLog(
            sModuleInfo, "Inferring which cells from the webpage table to ignore", 0
        )
        unmatched_cells = []
        for (
                ids
        ) in (
                webpage_table
        ):  # For each table cell on the user table - basically looking for items that are specified, but not found
            if (
                    ids not in user_table
            ):  # if cell from user table not found in webpage table
                unmatched_cells.append(
                    ids
                )  # Keep list of cell IDs we want to trim from the webpage table
        CommonUtil.ExecLog(
            sModuleInfo, "Removing inferred cells: %s" % str(unmatched_cells), 0
        )
        for ids in unmatched_cells:  # Remove these cells from the webpage table
            if (
                    ids in webpage_table
            ):  # Check if the ID exists in case the user specified something that's not actually in the webpage table
                del webpage_table[ids]

    if (
            coordinates_exact == False
    ):  # If user specifies that cells locations do not have to match
        unmatched_cells = []
        for ids in user_table:
            if user_table[ids] not in webpage_table.values():
                unmatched_cells.append(user_table[ids])

        if len(unmatched_cells) > 0:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Not all elements exist in webpage table - %s" % str(unmatched_cells),
                3,
            )
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Elements exist in webpage table", 1)
            return "passed"

    # Check if arrays match
    failed_matches = []
    for ids in webpage_table:  # For each table cell on the webpage table
        if ids in user_table:  # If that table cell is also in the user defined table
            if (
                    webpage_table[ids] != user_table[ids]
            ):  # Check if the values of these two cells match
                failed_matches.append(
                    '%s:"%s" != %s:"%s"'
                    % (ids, user_table[ids], ids, webpage_table[ids])
                )  # Record the unmatched cells
        else:  # Not in user table
            failed_matches.append("Cell %s is not defined in the step data" % ids)

    for (
            ids
    ) in (
            user_table
    ):  # For each table cell on the user table - basically looking for items that are specified, but not found
        if (
                ids not in webpage_table
        ):  # if cell from user table not found in webpage table
            failed_matches.append("Cell %s is not found in the webpage table" % ids)

    # If any failed matches, list them in the log, so the user can see and exit
    if len(failed_matches) > 0:
        CommonUtil.ExecLog(
            sModuleInfo, "Tables do not match - %s" % str(failed_matches), 3
        )
        return "zeuz_failed"

    CommonUtil.ExecLog(sModuleInfo, "Tables match", 1)
    return "passed"


@logger
def validate_table_row_size(data_set):
    """ Save row size in a share variable of the table provided in step data"""

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        # Initialize variables
        expected_row = ""  # variable where the row size will be saved
        table_type = ""  # Type of table (css/html)

        # Parse data set

        for row in data_set:
            field, subfield, value = (
                row[0],
                row[1],
                row[2],
            )  # Put data row in understandable variables

            if subfield == "action":
                table_type, expected_row = str(value).split(",")

        if table_type == "" or expected_row == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "No table type or expected row is given.. table type should be html or css, expected row is a number which is the expected row size",
                3,
            )
            return "zeuz_failed"

        # Get table from web page
        table = LocateElement.Get_Element(data_set, selenium_driver)

        if table in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your table with given data.", 3
            )
            return "zeuz_failed"

        all_rows = []
        if table_type == "html":  # HTML type table
            all_rows = table.find_elements("tag name",
                "tr"
            )  # Get element list for all rows
        elif table_type == "css":  # CSS type table
            all_rows = WebDriverWait(table, WebDriver_Wait).until(
                EC.presence_of_all_elements_located((By.XPATH, "*"))
            )

        row_size = len(all_rows)

        CommonUtil.ExecLog(sModuleInfo, "Webpage table row size: %s" % row_size, 1)
        CommonUtil.ExecLog(sModuleInfo, "Expected table row size: %s" % expected_row, 1)

        if int(row_size) != int(expected_row):
            CommonUtil.ExecLog(sModuleInfo, "Row sizes don't match", 3)
            return "zeuz_failed"

        CommonUtil.ExecLog(sModuleInfo, "Row sizes match", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None)


@logger
def validate_table_column_size(data_set):
    """ Save row size in a share variable of the table provided in step data"""
    global selenium_driver
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        # Initialize variables
        expected_col = ""  # variable where the row size will be saved
        table_type = ""  # Type of table (css/html)

        # Parse data set

        for row in data_set:
            field, subfield, value = (
                row[0],
                row[1],
                row[2],
            )  # Put data row in understandable variables

            if subfield == "action":
                table_type, expected_col = str(value).split(",")

        if table_type == "" or expected_col == "":
            CommonUtil.ExecLog(
                sModuleInfo,
                "No table type or expected column is given.. table type should be html or css, expected column is a number which is the expected row size",
                3,
            )
            return "zeuz_failed"

        # Get table from web page
        table = LocateElement.Get_Element(data_set, selenium_driver)

        if table in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your table with given data.", 3
            )
            return "zeuz_failed"

        all_rows = []
        all_cols = []
        if table_type == "html":  # HTML type table
            all_rows = table.find_elements("tag name",
                "tr"
            )  # Get element list for all rows
            if len(all_rows) > 0:
                all_cols = all_rows[0].find_elements("tag name",
                    "td"
                )  # Get element list for all columns in this row
                if (
                        len(all_cols) == 0
                ):  # No <TD> type columns, so check if there were header type columns, and use those instead
                    all_cols = all_rows[0].find_elements("tag name",
                        "th"
                    )  # Get element list for all header columns in this row
        elif table_type == "css":  # CSS type table
            all_rows = WebDriverWait(table, WebDriver_Wait).until(
                EC.presence_of_all_elements_located((By.XPATH, "*"))
            )
            for row_obj in all_rows:  # For each row
                if row_obj.is_displayed() != False:
                    # Get elements for each column
                    all_cols = WebDriverWait(row_obj, WebDriver_Wait).until(
                        EC.presence_of_all_elements_located((By.XPATH, "*"))
                    )
                    break

        col_size = len(all_cols)

        CommonUtil.ExecLog(sModuleInfo, "Webpage table column size: %s" % col_size, 1)
        CommonUtil.ExecLog(
            sModuleInfo, "Expected table column size: %s" % expected_col, 1
        )

        if int(col_size) != int(expected_col):
            CommonUtil.ExecLog(sModuleInfo, "Column sizes don't match", 3)
            return "zeuz_failed"

        CommonUtil.ExecLog(sModuleInfo, "Column sizes match", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None)


@logger
def get_webpage_table_html(data_set, ignore_rows=[], ignore_cols=[], retain_case=True):
    """ Find an HTML table given the elements, extract the text and return as a dictionary containing lists holding the data """
    # data_set: Contains user defined identifiers used to get the element of table
    # ignore_rows: List containing rows to ignore
    # ignore_cols: List containing columns to ignore
    # retain_case: Set to true to keep data exactly as is. Set to false to set it to lower case which is useful for case insensitive matching

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        # Get element representing entire table
        table = LocateElement.Get_Element(data_set, selenium_driver)
        if table in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

        master_text_table = {}
        table_row = 0
        tr_list = table.find_elements("tag name", "tr")  # Get element list for all rows
        for tr in tr_list:  # For each row element
            table_row += 1
            table_col = 0
            td_list = tr.find_elements("tag name",
                "td"
            )  # Get element list for all columns in this row
            if (
                    len(td_list) == 0
            ):  # No <TD> type columns, so check if there were header type columns, and use those instead
                td_list = tr.find_elements("tag name",
                    "th"
                )  # Get element list for all header columns in this row
            for td in td_list:  # For each column element
                table_col += 1
                value = str(
                    td.text
                ).strip()  # Save the text from this cell (also removing any HTML tags that may be in it)
                if retain_case == False:
                    value = value.lower()  # change cell text to lower case
                master_text_table[
                    "%s,%s" % (table_row, table_col)
                    ] = value  # Put value from cell in dictionary

        return master_text_table  # Return table text as dictionary
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error while parsing the table"
        )


@logger
def get_webpage_table_css(data_set, ignore_rows=[], ignore_cols=[], retain_case=True):
    """ Find a CSS table given the elements, extract the text and return as a dictionary containing lists holding the data """
    # data_set: Contains user defined identifiers used to get the element of table
    # ignore_rows: List containing rows to ignore
    # ignore_cols: List containing columns to ignore
    # retain_case: Set to true to keep data exactly as is. Set to false to set it to lower case which is useful for case insensitive matching

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        # Get element representing entire table
        table = LocateElement.Get_Element(data_set, selenium_driver)
        if table in failed_tag_list:
            CommonUtil.ExecLog(
                sModuleInfo, "Unable to locate your element with given data.", 3
            )
            return "zeuz_failed"

        # Get element for all rows
        all_rows = WebDriverWait(table, WebDriver_Wait).until(
            EC.presence_of_all_elements_located((By.XPATH, "*"))
        )

        master_text_table = {}
        table_row = 0
        for row_obj in all_rows:  # For each row
            table_row += 1
            if row_obj.is_displayed() != False:
                if table_row not in ignore_rows:  # Skip rows the user wants to ignore
                    try:
                        # Get elements for each column
                        col_element = WebDriverWait(row_obj, WebDriver_Wait).until(
                            EC.presence_of_all_elements_located((By.XPATH, "*"))
                        )

                        table_col = 0
                        for column_obj in col_element:  # For each column on the row
                            table_col += 1
                            if (
                                    table_col not in ignore_cols
                            ):  # Skip columns the user wants to ignore
                                value = str(
                                    column_obj.text
                                ).strip()  # Save the text from this cell (also removing any HTML tags that may be in it)
                                if retain_case == False:
                                    value = (
                                        value.lower()
                                    )  # change cell text to lower case
                                master_text_table[
                                    "%s,%s" % (table_row, table_col)
                                    ] = value  # Put value from cell in dictionary

                    except:  # This will crash for single column tables or lists
                        table_col = 1  # Likely only one column
                        value = str(
                            row_obj.text
                        ).strip()  # Save the text from this cell (also removing any HTML tags that may be in it)
                        if retain_case == False:
                            value = value.lower()  # change cell text to lower case
                        master_text_table[
                            "%s,%s" % (table_row, table_col)
                            ] = value  # Put value from cell in dictionary

        return master_text_table  # Return table text as dictionary
    except Exception:
        return CommonUtil.Exception_Handler(
            sys.exc_info(), None, "Error while parsing the table"
        )


@logger
def Tear_Down_Selenium(step_data=[]):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    global selenium_details
    global current_driver_id
    try:
        driver_id = ""
        for left, mid, right in step_data:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "driverid":
                driver_id = right.strip()

        if not driver_id:
            if not CommonUtil.teardown:
                CommonUtil.ExecLog(sModuleInfo, "Browser is already closed", 1)
                return "passed"
            CommonUtil.Join_Thread_and_Return_Result("screenshot")  # Let the capturing screenshot end in thread
            for driver in selenium_details:
                try:
                    perf_folder = ConfigModule.get_config_value("sectionOne", "performance_report", temp_ini_file)
                    perf_file = Path(perf_folder)/("matrices_"+driver+".json")
                    # metrics = selenium_details[driver]["driver"].execute_cdp_cmd('Performance.getMetrics', {})
                    # perf_json_data = {data["name"]:data["value"] for data in metrics["metrics"]}
                    # with open(perf_file, "w", encoding="utf-8") as f:
                    #     json.dump(perf_json_data, f, indent=2)
                    if selenium_driver.capabilities["browserName"].strip().lower() in ("chrome", "msedge"):
                        try:
                            selenium_details[driver]["driver"].execute_cdp_cmd("Performance.disable", {})
                        except:
                            CommonUtil.ExecLog(
                                sModuleInfo, "Unable to execute cdp command - Performance.enable", 3
                            )    
                except:
                    errMsg = "Unable to extract performance metrics of driver_id='%s'" % driver
                    CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
                    CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
                try:
                    selenium_details[driver]["driver"].quit()
                    CommonUtil.ExecLog(sModuleInfo, "Teared down driver_id='%s'" % driver, 1)
                except:
                    errMsg = "Unable to tear down driver_id='%s'. may already been killed" % driver
                    CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
                    CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
            Shared_Resources.Remove_From_Shared_Variables("selenium_driver")
            selenium_details = {}
            selenium_driver = None
            CommonUtil.teardown = False

        elif driver_id not in selenium_details:
            CommonUtil.ExecLog(sModuleInfo, "Driver_id='%s' not found. So could not tear down" % driver_id, 2)

        else:
            try:
                perf_folder = ConfigModule.get_config_value("sectionOne", "performance_report", temp_ini_file)
                perf_file = Path(perf_folder) / ("matrices_" + driver_id + ".json")
                # metrics = selenium_details[driver_id]["driver"].execute_cdp_cmd('Performance.getMetrics', {})
                # perf_json_data = {data["name"]: data["value"] for data in metrics["metrics"]}
                # with open(perf_file, "w", encoding="utf-8") as f:
                #     json.dump(perf_json_data, f, indent=2)
                if selenium_driver.capabilities["browserName"].strip().lower() in ("chrome", "msedge"):
                    try:
                        selenium_details[driver_id]["driver"].execute_cdp_cmd("Performance.disable", {})
                    except:
                        CommonUtil.ExecLog(
                            sModuleInfo, "Unable to execute cdp command - Performance.enable", 3
                        )
                selenium_details[driver_id]["driver"].quit()
                CommonUtil.ExecLog(sModuleInfo, "Teared down driver_id='%s'" % driver_id, 1)
            except:
                CommonUtil.ExecLog(sModuleInfo, "Unable to tear down driver_id='%s'. may already been killed" % driver_id, 2)
            del selenium_details[driver_id]
            if selenium_details:
                for driver in selenium_details:
                    selenium_driver = selenium_details[driver]["driver"]
                    Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
                    CommonUtil.ExecLog(sModuleInfo, "Current driver is set to driver_id='%s'" % driver, 1)
                    current_driver_id = driver
                    break
            else:
                Shared_Resources.Remove_From_Shared_Variables("selenium_driver")
                selenium_driver = None
                current_driver_id = driver_id

        global vdisplay
        if vdisplay:
            vdisplay.stop()
            vdisplay = None

        return "passed"
    except Exception:
        errMsg = "Unable to tear down selenium browsers. may already be killed"
        # return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
        CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
        return "passed"


@logger
def Switch_Browser(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    global selenium_details
    global current_driver_id
    try:
        driver_id = ""
        for left, mid, right in step_data:
            left = left.replace(" ", "").replace("_", "").replace("-", "").lower()
            if left == "driverid":
                driver_id = right.strip()

        if not driver_id:
            driver_id = "default"

        if driver_id not in selenium_details:
            CommonUtil.ExecLog(sModuleInfo, "Driver_id='%s' not found. So could not Switch" % driver_id, 3)
            return "zeuz_failed"
        else:
            selenium_driver = selenium_details[driver_id]["driver"]
            Shared_Resources.Set_Shared_Variables("selenium_driver", selenium_driver)
            current_driver_id = driver_id
            CommonUtil.ExecLog(sModuleInfo, "Current driver is set to driver_id='%s'" % driver_id, 1)

        return "passed"
    except Exception:
        errMsg = "Unable to tear down selenium browsers. may already be killed"
        # return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
        CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
        return "passed"


@logger
def Get_Current_URL(step_data):
    """
    This action saves the current url the browser is in by inspecting the address bar.

    get current url         selenium action     <saves the current url by inspecting the address bar of the browser>

    :param data_set: Action data set
    :return: string: "Current url saved in a variable named '%s'" or "zeuz_failed" depending on the outcome
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        var_name = ""
        for left, mid, right in step_data:
            if "action" in mid:
                var_name = right.strip()
        current_url = selenium_driver.current_url
        Shared_Resources.Set_Shared_Variables(var_name, current_url)
        CommonUtil.ExecLog(sModuleInfo, "Current url saved in a variable named '%s'" % var_name, 1)

        return "passed"
    except Exception:
        errMsg = "Unable to saved current url "
        # return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)
        CommonUtil.ExecLog(sModuleInfo, errMsg, 2)
        return "passed"


##@Riz and @Sreejoy: More work is needed here. Please investigate further.
@logger
def Get_Plain_Text_Element(element_parameter, element_value, parent=False):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        if parent == False:
            all_elements_with_text = selenium_driver.find_elements_by_xpath(".//*")
        else:
            all_elements_with_text = parent.find_elements_by_xpath(".//*")

        # Sequential logical flow
        if element_parameter == "plain_text":
            index = 0
            full_list = []
            for each in all_elements_with_text:
                text_to_print = None
                try:
                    text_to_print = each.text
                except:
                    False
                if text_to_print == element_value:
                    full_list.append(each)
                    break
                index = index + 1
            return_element = full_list[len(full_list) - 1]

        elif element_parameter == "partial_plain_text":
            index = 0
            full_list = []
            for each in all_elements_with_text:
                text_to_print = None
                try:
                    text_to_print = each.text
                except:
                    False
                if element_value in text_to_print:
                    full_list.append(each)
                    break
                index = index + 1
            return_element = full_list[len(full_list) - 1]

        else:
            CommonUtil.ExecLog(
                sModuleInfo,
                "Value invalid. Only 'plain_text', 'partial_plain_text' allowed",
                3,
            )
            return "zeuz_failed"

        return return_element

    except Exception:
        errMsg = "Could not get the element by plain text search"
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def get_driver():
    global selenium_driver
    return selenium_driver


# Method to open a new tab
@logger
def open_new_tab(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        time.sleep(2)
        CommonUtil.ExecLog(sModuleInfo, "Opening New Tab in Browser", 1)
        selenium_driver.execute_script("""window.open("");""")
        selenium_driver.switch_to.window(selenium_driver.window_handles[-1])

        CommonUtil.ExecLog(sModuleInfo, "New Tab Opened Successfully in Browser", 1)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to switch to a new tab
@deprecated
@logger
def switch_tab(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Try our new action named 'Switch window/tab'", 2)
    global selenium_driver
    try:
        tab = 1
        for each in step_data:
            if each[1] == "action":
                tab = int(str(each[2]))

        CommonUtil.ExecLog(sModuleInfo, "Switching to Tab %d in Browser" % tab, 1)
        windows = selenium_driver.window_handles
        selenium_driver.switch_to.window(windows[tab - 1])
        CommonUtil.ExecLog(
            sModuleInfo, "Switched to Tab %s Successfully in Browser" % tab, 1
        )

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to switch to a new tab
@deprecated
@logger
def switch_window(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    CommonUtil.ExecLog(sModuleInfo, "Try our new action named 'Switch Window/Tab'", 2)
    global selenium_driver
    try:
        switch_by_title_condition = False
        switch_by_index_condition = False
        for left, mid, right in step_data:
            left = left.lower().strip()
            if left == "window title":
                switch_by_title = right
                switch_by_title_condition = True
            elif left == "window index":
                switch_by_index = right.strip()
                switch_by_index_condition = True

        if switch_by_title_condition:
            all_windows = selenium_driver.window_handles
            window_handles_found = False
            for each in all_windows:
                selenium_driver.switch_to.window(each)
                if switch_by_title == (selenium_driver.title):
                    window_handles_found = True
                    CommonUtil.ExecLog(sModuleInfo, "switched your window", 1)
                    break
            if window_handles_found == False:
                CommonUtil.ExecLog(sModuleInfo, "unable to find your given title among the windows", 3)
                return False
            else:
                return True

        elif switch_by_index_condition:
            check_if_index = ["0", "1", "2", "3", "4", "5"]
            if switch_by_index in check_if_index:
                window_index = int(switch_by_index)
                window_to_switch = selenium_driver.window_handles[window_index]
                selenium_driver.switch_to.window(window_to_switch)
                return True
            else:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "Invalid index provided.  Please provide number between 0 to 5",
                    3,
                )
                return False
        else:
            CommonUtil.ExecLog(sModuleInfo, "Wrong data set provided. Choose between window title or window index", 3)
            return False

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "unable to switch your window", 3)
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def switch_window_or_tab(step_data):
    """
    This action will switch tab/window in browser. Basically window and tabs are same in selenium.

    Example 1:
    Field	                    Sub Field	        Value
    *window title               element parameter	googl
    switch window or frame      selenium action 	switch window or frame


    Example 2:
    Field	                    Sub Field	        Value
    window title                element parameter	google
    switch window or frame      selenium action 	switch window or frame

    Example 3:
    Field	                    Sub Field	        Value
    window index                element parameter	9
    switch window or frame      selenium action 	switch window or frame

    Example 4:
    Field	                    Sub Field	        Value
    frame index                 element parameter	1
    switch window or frame      selenium action 	switch window or frame

    Example 5:
    Field	                    Sub Field	        Value
    frame title                 element parameter	iFrame1
    switch window or frame      selenium action 	switch window or frame

    Example 6:
    Field	                    Sub Field	        Value
    frame index                 element parameter	default content
    switch window or frame      selenium action 	switch window or frame

    Example 7:
    Field	                    Sub Field	        Value
    frame title                 element parameter	iFrame1
    frame index                 element parameter	1
    switch window or frame      selenium action 	switch window or frame

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        window_title_condition = False
        window_index_condition = False
        frame_condition = False
        partial_match = False
        frame_title_index = []
        for left, mid, right in step_data:
            left = left.lower().strip()
            if left == "window title":
                switch_by_title = right
                window_title_condition = True
            elif left == "*window title":
                switch_by_title = right
                partial_match = True
                window_title_condition = True
            elif left == "window index":
                switch_by_index = right.strip()
                window_index_condition = True
                window_title_condition = False
                # break  # Index priority is highest so break the loop
            elif left == "frame title":
                frame_title_index += [right]
                frame_condition = True
            elif left == "frame index":
                frame_title_index += [-1000] if "default" in right.lower() else [int(right.strip())]
                # Using -1000 as a flag of default content
                frame_condition = True

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to parse data. Maintain correct format writen in document", 3)
        return "zeuz_failed"

    try:
        if window_title_condition:
            all_windows = selenium_driver.window_handles
            window_handles_found = False
            Tries = 3
            for Try in range(Tries):
                for each in all_windows:
                    selenium_driver.switch_to.window(each)
                    if (partial_match and switch_by_title in (selenium_driver.title)) or (
                            not partial_match and switch_by_title == (selenium_driver.title)):
                        window_handles_found = True
                        CommonUtil.ExecLog(sModuleInfo, "Window switched to '%s'" % selenium_driver.title, 1)
                        break
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Couldn't find the title. Trying again after 1 second delay", 2)
                    time.sleep(1)
                    continue  # only executed if the inner loop did not break
                break  # only executed if the inner loop did break

            if not window_handles_found:
                CommonUtil.ExecLog(
                    sModuleInfo,
                    "unable to find the title among the windows. If you want to match partially please use '*windows title'",
                    3)
                return "zeuz_failed"
            # else:
            #     return True

        elif window_index_condition:
            window_index = int(switch_by_index)
            window_to_switch = selenium_driver.window_handles[window_index]
            selenium_driver.switch_to.window(window_to_switch)
            CommonUtil.ExecLog(sModuleInfo, "Window switched to index %s" % switch_by_index, 1)
            # return True

        elif not frame_condition:
            CommonUtil.ExecLog(sModuleInfo, "Wrong data set provided. Choose between window title, window index, frame title or frame index", 3)
            return "zeuz_failed"

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to switch your window", 3)
        return CommonUtil.Exception_Handler(sys.exc_info())

    try:
        if frame_condition:
            selenium_driver.switch_to.default_content()
            CommonUtil.ExecLog(sModuleInfo, "Frame switched to default content", 1)
            for i in frame_title_index:
                if isinstance(i, int) and i != -1000:
                    selenium_driver.switch_to.frame(i)
                    CommonUtil.ExecLog(sModuleInfo, "Frame switched to index %s" % str(i), 1)
                elif isinstance(i, str):
                    if "default" in i:
                        try:
                            selenium_driver.switch_to.frame(i)
                            CommonUtil.ExecLog(sModuleInfo, "Frame switched to '%s'" % i, 1)
                        except NoSuchFrameException:
                            CommonUtil.ExecLog(
                                sModuleInfo,
                                "No such frame named '%s'. Switching to default content exiting from all frames." % i,
                                2)
                            selenium_driver.switch_to.default_content()
                    else:
                        selenium_driver.switch_to.frame(i)
                        CommonUtil.ExecLog(sModuleInfo, "Frame switched to '%s'" % i, 1)
        return "passed"

    except Exception:
        CommonUtil.ExecLog(sModuleInfo, "Unable to switch frame", 3)
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def switch_iframe(step_data):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        for left, mid, right in step_data:
            left = left.lower().strip()
            if "action" in mid.lower() and left == "switch iframe":
                pass
            elif left == "index" and "default" in right.lower():
                selenium_driver.switch_to.default_content()
                CommonUtil.ExecLog(sModuleInfo, "Exited all iframes and switched to default content", 1)
            elif left == "index":
                if mid == "iframe parameter":
                    for i in range(5):
                        iframes = selenium_driver.find_elements(By.TAG_NAME, "iframe")
                        idx = int(right.strip())
                        if -len(iframes) <= idx < len(iframes):
                            CommonUtil.ExecLog(sModuleInfo, "Iframe switched to index %s" % right.strip(), 1)
                            break
                        CommonUtil.ExecLog(sModuleInfo,
                                         "Iframe index = %s not found. retrying after 2 sec wait" % right.strip(), 2)
                        time.sleep(2)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Index out of range. Total %s iframes found." % len(iframes), 3)
                        return "zeuz_failed"
                    if idx < 0:
                        idx = len(iframes) + idx
                    try:
                        frame_attribute = iframes[idx].get_attribute('outerHTML')
                        i, c = 0, 0
                        for i in range(len(frame_attribute)):
                            if frame_attribute[i] == '"':
                                c += 1
                            if (frame_attribute[i] == ">" and c % 2 == 0):
                                break
                        frame_attribute = frame_attribute[:i + 1]
                        CommonUtil.ExecLog(sModuleInfo, "%s" % (frame_attribute), 5)
                    except:
                        pass
                    selenium_driver.switch_to.frame(idx)
                elif mid == "frame parameter":
                    for i in range(5):
                        frames = selenium_driver.find_elements(By.TAG_NAME, "frame")
                        idx = int(right.strip())
                        if -len(frames) <= idx < len(frames):
                            CommonUtil.ExecLog(sModuleInfo, "Frame switched to index %s" % right.strip(), 1)
                            break
                        CommonUtil.ExecLog(sModuleInfo,
                                         "Frame index = %s not found. retrying after 2 sec wait" % right.strip(), 2)
                        time.sleep(2)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "Index out of range. Total %s frames found." % len(frames), 3)
                        return "zeuz_failed"
                    if idx < 0:
                        idx = len(frames) + idx
                    try:
                        frame_attribute = frames[idx].get_attribute('outerHTML')
                        i, c = 0, 0
                        for i in range(len(frame_attribute)):
                            if frame_attribute[i] == '"':
                                c += 1
                            if (frame_attribute[i] == ">" and c % 2 == 0):
                                break
                        frame_attribute = frame_attribute[:i + 1]
                        CommonUtil.ExecLog(sModuleInfo, "%s" % (frame_attribute), 5)
                    except:
                        pass
                    selenium_driver.switch_to.frame(idx)

            elif "default" in right.lower():
                try:
                    iframe_data = [(left, "element parameter", right)]
                    if left != "xpath":
                        if mid == "iframe parameter":
                            iframe_data.append(("tag", "element parameter", "iframe"))
                        elif mid == "frame parameter":
                            iframe_data.append(("tag", "element parameter", "frame"))
                    element = LocateElement.Get_Element(iframe_data, selenium_driver)
                    selenium_driver.switch_to.frame(element)
                    CommonUtil.ExecLog(sModuleInfo, "Iframe switched using above Xpath", 1)
                except:
                    if mid == "iframe parameter":
                        CommonUtil.ExecLog(sModuleInfo,
                                           "No such iframe found. Exited all iframes and switched to default content",
                                           2)
                    elif mid == "frame parameter":
                        CommonUtil.ExecLog(sModuleInfo,
                                           "No such frame found. Exited all frames and switched to default content",
                                           2)
                    selenium_driver.switch_to.default_content()
            else:
                try:
                    iframe_data = [(left, "element parameter", right)]
                    if left != "xpath":
                        if mid == "iframe parameter":
                            iframe_data.append(("tag", "element parameter", "iframe"))
                        elif mid == "frame parameter":
                            iframe_data.append(("tag", "element parameter", "frame"))
                    element = LocateElement.Get_Element(iframe_data, selenium_driver)
                    selenium_driver.switch_to.frame(element)
                    CommonUtil.ExecLog(sModuleInfo, "Iframe switched using above Xpath", 1)
                except:
                    if mid == "iframe parameter":
                        CommonUtil.ExecLog(sModuleInfo, "No such iframe found using above Xpath", 3)
                    elif mid == "frame parameter":
                        CommonUtil.ExecLog(sModuleInfo, "No such frame found using above Xpath", 3)
                    return "zeuz_failed"
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


# Method to upload file
@logger
def upload_file(step_data):

    """
    This action will use normal element search parameters to locate the upload button
    You can upload the attachment to your test case and use the name as a variable for reference

    Example 1:
    Field                        Sub Field            Value
    id                           element parameter    fileUPload
    upload file                  selenium action      %|log.rtf|%

    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        file_name = ""
        for each in step_data:
            if each[1] == "action":
                file_name = str(each[2]).strip()

        if file_name == "":
            CommonUtil.ExecLog(sModuleInfo, "File name can't be empty!", 3)
            return "zeuz_failed"
        elif not os.path.exists(file_name):
            CommonUtil.ExecLog(
                sModuleInfo,
                "File '%s' can't be found.. please give a valid file path" % file_name,
                3,
            )
            return "zeuz_failed"

        upload_button = LocateElement.Get_Element(step_data, selenium_driver)
        if upload_button in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo, "Could not find the element with given data", 3)
            return "zeuz_failed"

        upload_button.send_keys(file_name)
        CommonUtil.ExecLog(sModuleInfo, "Uploaded the file: %s successfully."%file_name, 1)
        return "passed"

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def _gui_upload(path_name, pid=None):
    # Todo: Implement PID to activate the window and focus that at front
    import pyautogui
    time.sleep(3)
    pyautogui.hotkey("alt", "a")
    time.sleep(0.5)
    pyautogui.write(path_name)
    time.sleep(1)
    pyautogui.hotkey("enter")


@logger
def upload_file_through_window(step_data):
    """
    Purpose: Sometimes there are some upload window to upload one or more files which is out of selenium's scope.
    This action automate that upload window with microsoft System API and pyautogui GUI API

    Code detail:
    The upload API is searched by their pid
    The main problem is there are multiple process which open while when launching driver having multiple pid. but we need to find out the main browsers pid
    Firefox driver provides the pid inside capabilities
    For Chrome and Opera we added a custom args named "--zeuz_pid_finder" and searched in the psutil which process contains that arg and get the pid of that process
    For MS Edge browser We extracted selenium.title and searched in Microsoft System API with that window title and fetch all the pids with that window title.
    Also we had extracted all the pids from psutil having "--test-type=webdriver" arg and then matched the pids with previous one to find the genuin pid

    In windows, firstly we try to automate with Microsoft System API. If anything fails in between then we switch to GUI method
    In Mac and Linux, we automate only with GUI
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    all_file_path = []
    pid = ""
    send_keys_flag = False
    import pyautogui
    if "headless" in dependency:
        CommonUtil.ExecLog(sModuleInfo, "This action will not work on headless browsers", 3)
        return "zeuz_failed"
    try:
        for left, mid, right in step_data:
            left = left.strip().lower()
            l = left.replace(" ", "").replace("_", "").lower()
            if l in ("filepath", "directory"):
                path = CommonUtil.path_parser(right.strip())
                if os.path.isdir(path) or os.path.isfile(path):
                    all_file_path.append(path)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find any directory or file with the path: %s" % path, 3)
            if "keys" in l:
                send_keys_flag = True

        if len(all_file_path) == 0:
            CommonUtil.ExecLog(sModuleInfo, "Could not find any valid filepath or directory", 3)
            return "zeuz_failed"

        path_name = '"' + '" "'.join(all_file_path) + '"'
    except:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing dataset")

    try:


        if platform.system() == "Darwin":
            # Will require pid when we will atomate with atomacos module. Fetching PID is only tested on Chrome for now
            if selenium_driver.capabilities["browserName"].lower() == "chrome":
                for process in psutil.process_iter():
                    try:
                        if process.name() == 'Google Chrome' and '--test-type=webdriver' in process.cmdline() and "--zeuz_pid_finder" in process.cmdline():
                            pid = str(process.pid)
                            break
                    except Exception as e:
                        # print(e)
                        pass

            path_name = path_name[1:-1]

            import pyautogui
            time.sleep(3)
            pyautogui.hotkey("/")
            time.sleep(5)
            pyautogui.hotkey("command", "a")
            time.sleep(0.5)
            pyautogui.write(path_name)
            time.sleep(0.5)
            pyautogui.hotkey("enter")
            time.sleep(2)
            pyautogui.hotkey("enter")

        elif send_keys_flag is True:

            file_input = selenium_driver.find_element(By.XPATH, "//input[@type='file']")

            file_path = path_name[1:-1]
            file_input.send_keys(file_path)


        # window_ds = ("*window", "element parameter", selenium_driver.title)
        elif platform.system() == "Windows":
            if selenium_driver.capabilities["browserName"].lower() == "firefox":
                pid = str(selenium_driver.capabilities["moz:processID"])
            elif selenium_driver.capabilities["browserName"].lower() == "chrome":
                for process in psutil.process_iter():
                    if process.name() == 'chrome.exe' and '--test-type=webdriver' in process.cmdline() and "--zeuz_pid_finder" in process.cmdline():
                        pid = str(process.pid)
            elif selenium_driver.capabilities["browserName"].lower() == "opera":
                for process in psutil.process_iter():
                    if process.name() == 'opera.exe' and '--test-type=webdriver' in process.cmdline() and "--zeuz_pid_finder" in process.cmdline():
                        pid = str(process.pid)
            elif selenium_driver.capabilities["browserName"].lower() == "msedge":
                for process in psutil.process_iter():
                    if process.name() == 'msedge.exe' and '--test-type=webdriver' in process.cmdline() and "--zeuz_pid_finder" in process.cmdline():
                        pid = str(process.pid)
            from Framework.Built_In_Automation.Desktop.Windows.BuiltInFunctions import Click_Element, Enter_Text_In_Text_Box, Save_Attribute, get_pids_from_title

            """ We may need the following codes when deprecated msedge selenium stops working """
            # time.sleep(3)
            # if selenium_driver.capabilities["browserName"].lower() == "msedge": # Msedge browser only exists in windows
            #     win_pids = get_pids_from_title(selenium_driver.title)
            #     if len(win_pids) == 0:
            #         CommonUtil.ExecLog(sModuleInfo, "Could not find the pid for msedge. Switching to GUI method", 2)
            #         _gui_upload(path_name)
            #         CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
            #         return "passed"
            #     if len(win_pids) > 1:
            #         psutil_pids = []
            #         for process in psutil.process_iter():
            #             if process.name() == 'msedge.exe' and '--test-type=webdriver' in process.cmdline():
            #                 psutil_pids.append(process.pid)
            #         for i in win_pids:
            #             if i in psutil_pids:
            #                 pid = str(i)
            #                 break
            #         else:
            #             pid = str(win_pids[0])
            #     else:
            #         pid = str(win_pids[0])

            if selenium_driver.capabilities["browserName"].lower() not in ("firefox", "chrome", "opera", "msedge"):
                win_pids = get_pids_from_title(selenium_driver.title)
                if len(win_pids) == 0:
                    CommonUtil.ExecLog(sModuleInfo, "Could not find the pid for browser. Switching to GUI method", 2)
                    _gui_upload(path_name)
                    CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                    return "passed"
                if len(win_pids) > 1:
                    psutil_pids = []
                    for process in psutil.process_iter():
                        if '--test-type=webdriver' in process.cmdline():
                            psutil_pids.append(process.pid)
                    for i in win_pids:
                        if i in psutil_pids:
                            pid = str(i)
                            break
                    else:
                        pid = str(win_pids[0])
                else:
                    pid = str(win_pids[0])

            if not pid:
                CommonUtil.ExecLog(sModuleInfo, "Could not find the PID for browser. Switching to GUI method", 2)
                _gui_upload(path_name)
                CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                return "passed"

            window_ds = ("window pid", "element parameter", pid)
            save_attribute_ds = [
                window_ds,
                ("wait", "optional parameter", "20"),
                ("AutomationId", "element parameter", "1090"),
                ("Name", "save parameter", "ZeuZ_uPLOad_W1N_F1LE__OR_FOLdeR_87138131"),
                ("save attribute", "windows action", "save attribute"),
            ]
            if Save_Attribute(save_attribute_ds) == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find the Textbox. Switching to GUI method", 2)
                _gui_upload(path_name)
                CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                return "passed"
            file_or_folder = Shared_Resources.Get_Shared_Variables("ZeuZ_uPLOad_W1N_F1LE__OR_FOLdeR_87138131")
            if "file name" in file_or_folder.lower():
                id = "1148"
            elif "folder" in file_or_folder.lower():
                id = "1152"
            else:
                CommonUtil.ExecLog(sModuleInfo, "Invalid Upload type. file_or_folder = '%s'" % file_or_folder, 3)
                return "zeuz_failed"

            enter_text_ds = [
                window_ds,
                ("wait", "optional parameter", "20"),
                ("LocalizedControlType", "element parameter", "edit"),
                ("AutomationId", "element parameter", id),
                ("text", "windows action", path_name),
            ]
            if Enter_Text_In_Text_Box(enter_text_ds) == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find the Open button. Switching to GUI method", 2)
                _gui_upload(path_name)
                CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                return "passed"

            click_ds = [
                window_ds,
                ("wait", "optional parameter", "20"),
                ("AutomationId", "element parameter", "1"),
                ("Name", "element parameter", "Open"),
                ("LocalizedControlType", "element parameter", "button"),
                ("click", "windows action", "click"),
            ]
            if Click_Element(click_ds) == "zeuz_failed":
                CommonUtil.ExecLog(sModuleInfo, "Could not find the Open button. Switching to GUI method (pressing Enter)", 2)
                time.sleep(1)
                pyautogui.hotkey("enter")
                CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
                return "passed"

        # elif platform.system() == "Linux":
        #     _gui_upload(path_name)
        else:
            _gui_upload(path_name[0:-1])

        CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
        return "passed"

    except Exception:
        CommonUtil.Exception_Handler(sys.exc_info())
        CommonUtil.ExecLog(sModuleInfo, "Could not find the Textbox. Switching to GUI method", 2)
        _gui_upload(path_name)
        CommonUtil.ExecLog(sModuleInfo, "Entered the following path:\n%s" % path_name, 1)
        return "passed"


# Method to upload file
@logger
def drag_and_drop(dataset):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        source = []
        destination = []
        param_dict = {"elementparameter": "element parameter", "parentparameter": "parent parameter", "siblingparameter": "sibling parameter", "childparameter": "child parameter"}
        for left, mid, right in dataset:
            if mid.startswith("src") or mid.startswith("source"):
                mid = mid.replace("src", "").replace(" ", "").replace("source", "")
                for param in param_dict:
                    if param == mid:
                        source.append((left, param_dict[param], right))
            elif mid.startswith("dst") or mid.startswith("destination"):
                mid = mid.replace("dst", "").replace(" ", "").replace("destination", "")
                for param in param_dict:
                    if param == mid:
                        destination.append((left, param_dict[param], right))
            elif left.strip().lower() in ("wait", "allow disable", "allow hidden") and mid == "option":
                source.append((left, mid, right))
                destination.append((left, mid, right))

        if not source:
            CommonUtil.ExecLog(sModuleInfo, 'Please provide source element with "src element parameter", "src parent parameter" etc. Example:\n'+
               "(id, src element parameter, file)", 3)
            return "zeuz_failed"
        if not destination:
            CommonUtil.ExecLog(sModuleInfo, 'Please provide Destination element with "dst element parameter", "dst parent parameter" etc. Example:\n'+
               "(id, dst element parameter, table)", 3)
            return "zeuz_failed"

        source_element = LocateElement.Get_Element(source, selenium_driver)
        if source_element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Source Element is not found", 3)
            return "zeuz_failed"

        destination_element = LocateElement.Get_Element(destination, selenium_driver)
        if destination_element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Destination Element is not found", 3)
            return "zeuz_failed"

        ActionChains(selenium_driver).drag_and_drop(source_element, destination_element).perform()
        # ActionChains(selenium_driver).click_and_hold(source_element).move_to_element(destination_element).pause(0.5).release(destination_element).perform()
        CommonUtil.ExecLog(sModuleInfo, "Drag and drop completed from source to destination", 1)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def if_element_exists(data_set):
    """ Click on an element """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        variable_name = ""
        value = ""

        for left, mid, right in data_set:
            if "action" in mid:
                value, variable_name = right.split("=")
                value = value.strip()
                variable_name = variable_name.strip()

        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element in failed_tag_list:
            Shared_Resources.Set_Shared_Variables(variable_name, "false")
        else:
            Shared_Resources.Set_Shared_Variables(variable_name, value)
        return "passed"
    except Exception:
        errMsg = (
            "Failed to parse data/locate element. Data format: variableName = value"
        )
        return CommonUtil.Exception_Handler(sys.exc_info(), None, errMsg)


@logger
def check_uncheck_all(data_set):
    """ Check or uncheck all elements of a common attribute """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    use_js = False
    target = []
    command = "check"
    try:
        for left, mid, right in data_set:
            left = left.lower().strip()
            mid = mid.lower().strip()
            if "use js" == left:
                use_js = right.strip().lower() in ("true", "yes", "ok")
            elif "target parameter" == mid:
                target.append((left, "element parameter", right))
            elif "check uncheck all" == left:
                command = "uncheck" if "uncheck" in right.lower() else "check"
            elif "allow hidden" == left:
                target.append((left, "option", right))

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find the parent element", 3)
        return "zeuz_failed"

    all_elements = LocateElement.Get_Element(target, Element, return_all_elements=True)
    if not all_elements:
        CommonUtil.ExecLog("", "No target was found", 3)
        return "zeuz_failed"

    for i in range(len(all_elements)):
        th = "th"
        if i + 1 == 1:
            th = "st"
        elif i + 1 == 2:
            th = "nd"
        elif i + 1 == 3:
            th = "rd"
        if command == "check" and all_elements[i].is_selected():
            CommonUtil.ExecLog("", str(i + 1) + th + " target is already checked so skipped it", 1)
            continue
        if command == "uncheck" and not all_elements[i].is_selected():
            CommonUtil.ExecLog("", str(i + 1) + th + " target is already unchecked so skipped it", 1)
            continue

        try:
            if use_js:
                selenium_driver.execute_script("arguments[0].click();", all_elements[i])
                if command == "check":
                    CommonUtil.ExecLog("", str(i + 1) + th + " target is checked successfully using Java Script", 1)
                else:
                    CommonUtil.ExecLog("", str(i + 1) + th + " target is unchecked successfully using Java Script", 1)
            else:
                try:
                    all_elements[i].click()
                    if command == "check":
                        CommonUtil.ExecLog("", str(i + 1) + th + " target is checked successfully", 1)
                    else:
                        CommonUtil.ExecLog("", str(i + 1) + th + " target is unchecked successfully", 1)

                except ElementClickInterceptedException:
                    try:
                        selenium_driver.execute_script("arguments[0].click();", all_elements[i])
                        if command == "check":
                            CommonUtil.ExecLog("", str(i + 1) + th + " target is checked successfully using Java Script", 1)
                        else:
                            CommonUtil.ExecLog("", str(i + 1) + th + " target is unchecked successfully using Java Script", 1)
                    except:
                        if command == "check":
                            CommonUtil.ExecLog("", str(i + 1) + th + " target couldn't be checked so skipped it", 3)
                        else:
                            CommonUtil.ExecLog("", str(i + 1) + th + " target couldn't be unchecked so skipped it", 3)
        except:
            if command == "check":
                CommonUtil.ExecLog("", str(i + 1) + th + " target couldn't be checked so skipped it", 3)
            else:
                CommonUtil.ExecLog("", str(i + 1) + th + " target couldn't be unchecked so skipped it", 3)

    return "passed"

@logger
def check_uncheck(data_set):
    """ Check or uncheck all elements of a common attribute """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    use_js = False
    command = "check"
    try:
        for left, mid, right in data_set:
            left = left.lower().strip()
            if "use js" == left:
                use_js = right.strip().lower() in ("true", "yes", "ok")
            elif "check uncheck" == left:
                command = "uncheck" if "uncheck" in right.lower() else "check"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find the element", 3)
        return "zeuz_failed"

    if command == "check" and Element.is_selected():
        CommonUtil.ExecLog(sModuleInfo, "The element is already checked so skipped it", 1)
        return "passed"
    elif command == "uncheck" and not Element.is_selected():
        CommonUtil.ExecLog(sModuleInfo, "The element is already unchecked so skipped it", 1)
        return "passed"
    try:
        if use_js:
            selenium_driver.execute_script("arguments[0].click();", Element)
            if command == "check":
                CommonUtil.ExecLog(sModuleInfo, "The element is checked successfully using Java Script", 1)
            else:
                CommonUtil.ExecLog(sModuleInfo, "The element is unchecked successfully using Java Script", 1)
            return "passed"
        else:
            try:
                handle_clickability_and_click(data_set, Element)
                if command == "check":
                    CommonUtil.ExecLog(sModuleInfo, "The element is checked successfully", 1)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "The element is unchecked successfully", 1)
                return "passed"
            except ElementClickInterceptedException:
                try:
                    selenium_driver.execute_script("arguments[0].click();", Element)
                    if command == "check":
                        CommonUtil.ExecLog(sModuleInfo, "The element is checked successfully using Java Script", 1)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "The element is unchecked successfully using Java Script", 1)
                    return "passed"
                except:
                    if command == "check":
                        CommonUtil.ExecLog(sModuleInfo, "The element couldn't be checked", 3)
                    else:
                        CommonUtil.ExecLog(sModuleInfo, "The element couldn't be unchecked", 3)
                    return "zeuz_failed"
    except:
        if command == "check":
            CommonUtil.ExecLog(sModuleInfo, "The element couldn't be checked", 3)
        else:
            CommonUtil.ExecLog(sModuleInfo, "The element couldn't be unchecked", 3)
        return "zeuz_failed"


def insert(string, str_to_insert, index):
    return string[:index] + str_to_insert + string[index:]



@logger
def slider_bar(data_set):
    """Set certain value to a slider bar
    you must provide a number between 0 - 100
     """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        value = ""

        for left, mid, right in data_set:
            if "action" in mid:
                value = int(right.strip())
        # if value not in range(0, 100):
        #     CommonUtil.ExecLog(sModuleInfo, "Failed to parse data/locate element. You must provide a number between 0-100", 3)
        #     return "zeuz_failed"
        Element = LocateElement.Get_Element(data_set, selenium_driver)
        if Element == "zeuz_failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not find the element", 3)
            return "zeuz_failed"
        else:
            CommonUtil.ExecLog(sModuleInfo, f"Moving the slider by %{value} ", 1)
            move = ActionChains(selenium_driver)
            height_width = Element.size
            ele_width = int((height_width)["width"])
            ele_height = int((height_width)["height"])
            x_cord_to_tap = ((value/100) * ele_width)
            y_cord_to_tap = (ele_height/2)

            move.move_to_element_with_offset(Element, x_cord_to_tap, y_cord_to_tap).click().perform()
            CommonUtil.ExecLog(sModuleInfo, f"Successfully set the slider to %{value}", 1)

        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


@logger
def multiple_check_uncheck(data_set):
    """ Check or uncheck multiple web elements """

    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver

    use_js = False
    inside = False
    allow_hidden = ""
    try:
        for left, mid, right in data_set:
            left = left.lower().strip()
            mid = mid.lower().strip()
            if "use js" == left:
                use_js = right.strip().lower() in ("true", "yes", "ok")
            elif "allow hidden" == left:
                allow_hidden = right
            elif "target parameter" == mid:
                targets = []
                temp = right.strip()
                i = 0
                while True:
                    if i >= len(temp):
                        break
                    if temp[i] == "(":
                        inside = True
                        temp = insert(temp, "\"", i+1)
                    elif inside and temp[i] == ",":
                        temp = insert(temp, "\"", i+1)
                        temp = insert(temp, "\"", i)
                        i += 1
                    if temp[i] == ")":
                        inside = False
                        temp = insert(temp, "\"", i)
                        i += 1
                    i += 1
                temp = insert(temp, "[", 0)
                temp = insert(temp, "]", len(temp))
                temp = CommonUtil.parse_value_into_object(temp)
                for Left, Mid, Right in temp:
                    targets.append((Left.strip().lower(), Mid.strip(), Right.strip().lower()))
                    # Stripped Mid if any trailing spaces exists need to use asterisk

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error parsing data set")

    Element = LocateElement.Get_Element(data_set, selenium_driver)
    if Element == "zeuz_failed":
        CommonUtil.ExecLog(sModuleInfo, "Could not find the parent element", 3)
        return "zeuz_failed"

    element_params = []
    for left, mid, right in targets:
        if allow_hidden:
            element_params.append([("allow hidden", "option", allow_hidden), (left, "element parameter", mid)])
        else:
            element_params.append([(left, "element parameter", mid)])

    all_elements = []
    for i in element_params:
        all_elements.append(LocateElement.Get_Element(i, Element))

    for i in range(len(all_elements)):
        if all_elements[i] == "zeuz_failed":
            CommonUtil.ExecLog("", str(targets[i]) + " was not found so skipped it", 3)
            continue
        if targets[i][2] == "check" and all_elements[i].is_selected():
            CommonUtil.ExecLog("", str(targets[i]) + " is already checked so skipped it", 1)
            continue
        if targets[i][2] == "uncheck" and not all_elements[i].is_selected():
            CommonUtil.ExecLog("", str(targets[i]) + " is already unchecked so skipped it", 1)
            continue

        try:
            if use_js:
                selenium_driver.execute_script("arguments[0].click();", all_elements[i])
                if targets[i][2] == "check":
                    CommonUtil.ExecLog("", str(targets[i]) + " is checked successfully using Java Script", 1)
                else:
                    CommonUtil.ExecLog("", str(targets[i]) + " is unchecked successfully using Java Script", 1)
            else:
                try:
                    all_elements[i].click()
                    if targets[i][2] == "check":
                        CommonUtil.ExecLog("", str(targets[i]) + " is checked successfully", 1)
                    else:
                        CommonUtil.ExecLog("", str(targets[i]) + " is unchecked successfully", 1)
                except ElementClickInterceptedException:
                    try:
                        selenium_driver.execute_script("arguments[0].click();", all_elements[i])
                        if targets[i][2] == "check":
                            CommonUtil.ExecLog("", str(targets[i]) + " is checked successfully using Java Script", 1)
                        else:
                            CommonUtil.ExecLog("", str(targets[i]) + " is unchecked successfully using Java Script", 1)
                    except:
                        if targets[i][2] == "check":
                            CommonUtil.ExecLog("", str(targets[i]) + " couldn't be checked so skipped it", 3)
                        else:
                            CommonUtil.ExecLog("", str(targets[i]) + " couldn't be unchecked so skipped it", 3)
        except:
            if targets[i][2] == "check":
                CommonUtil.ExecLog("", str(targets[i]) + " couldn't be checked so skipped it", 3)
            else:
                CommonUtil.ExecLog("", str(targets[i]) + " couldn't be unchecked so skipped it", 3)

    return "passed"

@logger
def resize_window(step_data):
    """Action to resize window size"""
    """
    width          element parameter   50%
    height         element parameter   70%
    resize window  selenium action     resize window
    """
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    global selenium_driver
    try:
        window_size = selenium_driver.get_window_size()
        CommonUtil.ExecLog(sModuleInfo, f"Current window size is {window_size}", 1)
        for left, mid, right in step_data:
            left = left.lower().strip()
            right = right.lower().strip()
            if 'element parameter' in mid.lower():
                for dim in ['width','height']:
                    if left.lower().strip() == dim:
                        right = right.replace('%','').strip()
                        try:
                            right = float(right)
                            window_size[dim] = window_size[dim] * right/100
                        except:
                            CommonUtil.ExecLog(sModuleInfo, f"Enter valid size for {dim}", 3)
                            return CommonUtil.Exception_Handler(sys.exc_info())
        selenium_driver.set_window_size(window_size['width'],window_size['height'])
        CommonUtil.ExecLog(sModuleInfo, f"Successfully set the new window size to {window_size}", 1)
        return "passed"
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), None, "Error resizing window")

    
        




                
