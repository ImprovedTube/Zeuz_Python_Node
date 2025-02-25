# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-

import selenium
import sys
import inspect
import os, os.path, threading
import ast
import json, time
import logging
from Framework.Utilities import ConfigModule
import datetime
from Framework.Utilities import FileUtilities as FL
import uuid
from pathlib import Path
import io
from rich.console import Console
# from rich import print
from rich import print_json
from collections import namedtuple, Counter

ai_module_update_flag = None
ai_module_update_time_difference = None

ws_ss_log = True    # todo: Always keep it True
from Framework.Utilities import live_log_service
import concurrent.futures
from typing import Dict, List

# For TakeScreenShot()
from concurrent.futures import ThreadPoolExecutor
from PIL import Image  # Picture quality

try:
    from PIL import ImageGrab as ImageGrab_Mac_Win  # Screen capture for Mac and Windows
except:
    pass
try:
    import pyscreenshot as ImageGrab_Linux  # Screen capture for Linux/Unix
except:
    pass

# Import colorama for console color support
from colorama import init as colorama_init
from colorama import Fore, Back

# Initialize colorama for the current platform
colorama_init(autoreset=True)

# Initialize Rich console
console = Console()

MODULE_NAME = inspect.getmodulename(__file__)

# Get file path for temporary config file
temp_config = Path(
    os.path.join(os.path.abspath(__file__).split("Framework")[0])
    / Path("AutomationLog")
    / Path(
        ConfigModule.get_config_value(
            "Advanced Options",
            "_file",
        )
    )
)

common_modules = ["os", "sys", "platform", "time", "datetime", "random", "re", "uuid", "pathlib", "json", "ast", "yaml", "csv", "xml", "xlwings", "requests", "sr"]

passed_tag_list = [
    "Pass",
    "pass",
    "PASS",
    "PASSED",
    "Passed",
    "passed",
    "true",
    "TRUE",
    "True",
    "1",
    "Success",
    "success",
    "SUCCESS",
    True,
]
failed_tag_list = [
    "Fail",
    "fail",
    "FAIL",
    "zeuz_failed",
    "false",
    "False",
    "FALSE",
    "0",
    False,
]
skipped_tag_list = ["skip", "SKIP", "Skip", "skipped", "SKIPPED", "Skipped"]

all_logs = {}
all_logs_json, json_log_cond = [], False
tc_error_logs = []
all_logs_count = 0
all_logs_list = []
skip_list = ["step_data"]
to_dlt_from_fail_reason = " : Test Step Failed"

error_log_info = ""

load_testing = False
performance_report = {"data": [], "individual_stats": {"slowest": 0, "fastest": float("inf")}, "status_counts": {}}
performance_testing = False

# Holds the previously logged message (used for prevention of duplicate logs simultaneously)
previous_log_line = None
teardown = True
print_execlog = True
prettify_limit = None
show_browser_log = False
step_module_name = None

debug_status = False
rerunning_on_fail = False
upload_on_fail = True
rerun_on_fail = True
passed_after_rerun = False
Affirmative_words = ("yes", "true", "ok", "enable")

runid_index = 0
tc_index = 0
step_index = 0
current_action_no = ""
current_action_name = ""
previous_action_name = ""   # It requires for labelling get_performance_metrics. because performance_metrics is called on next action
current_step_no = ""    # 1 based index... Caution: this variable is dynamically changed in step loop action
current_step_name = ""
current_step_id = None
current_step_sequence = None
current_tc_no = ""
current_tc_name = ""
current_session_name = ""
custom_step_duration = ""
jwt_token = ""
run_cancel = ""
run_cancelled = False
disabled_step = []  # 1 based indexing
max_char = 0
compare_action_varnames = {"left":"Left", "right":"Right"}    # for labelling left and right variable names of compare action

# For step looping purpose
all_step_dataset = []
all_action_info = []

executor = concurrent.futures.ThreadPoolExecutor()
all_threads = {}

# Metrics variables
browser_perf = {}
action_perf = []
step_perf = []
test_case_perf = []
perf_test_perf = []

PerformanceDataPoint = namedtuple("PerformanceDataPoint", [
    "url",
    "http_verb",
    "status_code",
    "elapsed_time",
    "response_body_size",
    "time_stamp",
    "response_body",
    "upload_total",
    "download_total",
    "upload_speed",
    "download_speed",
    "namelookup_time",
    "connect_time",
    "tls_handshake_time",
    "starttransfer_time",
    "redirect_time",
])
api_performance_data: List[PerformanceDataPoint] = []

processed_performance_data = {}

skip_testcases = {}
skip_testcases_list = []
global_var = {}
global_sleep = {"selenium":{}, "appium":{}, "windows":{}, "desktop":{}}
zeuz_disable_var_print = {}

def clear_performance_metrics():
    """reset everything to initial value"""
    global browser_perf, action_perf, step_perf, test_case_perf, perf_test_perf, api_performance_data, load_testing, processed_performance_data
    action_perf = []
    step_perf = []
    test_case_perf = []
    perf_test_perf = []
    api_performance_data = []
    load_testing = False
    processed_performance_data = {}


def GetExecutor():
    return executor


def ShutdownExecutor():
    executor.shutdown()


def SaveThread(key, thread):
    if key in all_threads:
        all_threads[key].append(thread)
    else:
        all_threads[key] = [thread]


def Join_Thread_and_Return_Result(key):
    result = []
    if key in all_threads:
        for t in all_threads[key]:
            result.append(t.result())
        del all_threads[key]
    return result


def to_unicode(obj, encoding="utf-8"):
    if isinstance(obj, str):
        if not isinstance(obj, str):
            obj = str(obj, encoding)
        return obj


ZeuZ_map_code = {}


def ZeuZ_map_code_decoder(val):
    if type(val) == str and val.startswith("#ZeuZ_map_code#") and val in ZeuZ_map_code:
        return ZeuZ_map_code[val]
    return val


def parse_value_into_object(val):
    """Parses the given value into a Python object: int, str, list, dict."""
    if not isinstance(val, str):
        return val

    try:
        # val2 = ast.literal_eval(val)  # previous method
        # encoding and decoding is for handling escape characters such as \a \1 \2
        val2 = ast.literal_eval(val.encode('unicode_escape').decode())
        if not (val.startswith("(") and val.endswith(")")) and isinstance(val2, tuple):
            # We are preventing "1,2" >> (1,2) (str to tuple conversion without first brackets)
            pass
        else:
            val = val2
    except:
        try:
            val = ast.literal_eval(val)
        except:
            try:
                val = json.loads(val)
            except:
                try:
                    if val.startswith("#ZeuZ_map_code#") and val in ZeuZ_map_code:
                        #ToDo: find a way to convert the datatype to str or list
                        val = ZeuZ_map_code[val]
                except:
                    pass
    return val


dont_prettify_on_server = ["step_data"]


def prettify(key, val):
    """Tries to pretty print the given value."""
    for each_var in zeuz_disable_var_print.keys():
        if each_var != None:
            if each_var in key:
                return
    if performance_testing:
        return
    color = Fore.MAGENTA
    try:
        if prettify_limit is None:
            if type(val) == str:
                val = parse_value_into_object(val)
            print(color + "%s = " % (key), end="")
            print_json(data=val)
        else:
            print(color + "%s = " % (key), end="")
            print(json.dumps(val,indent=2)[:prettify_limit])

        expression = "%s = %s" % (key, json.dumps(val, indent=2, sort_keys=True)[:prettify_limit])
        stop_live_log = ConfigModule.get_config_value("Advanced Options", "stop_live_log")

        if debug_status and key not in dont_prettify_on_server and ws_ss_log and stop_live_log == 'False':
            live_log_service.log("VARIABLE", 4, expression.replace("\n", "<br>").replace(" ", "&nbsp;"))
            # 4 means console log which is Magenta color in server console
    except:
        # expression = "%s" % (key, val)
        print(color + str(val)[:prettify_limit])
        if debug_status and key not in dont_prettify_on_server and ws_ss_log:
            live_log_service.log("VARIABLE", 4, str(val).replace("\n", "<br>").replace(" ", "&nbsp;"))


def Add_Folder_To_Current_Test_Case_Log(src):
    try:
        # get the current test case locations
        dest_folder = ConfigModule.get_config_value(
            "sectionOne", "test_case_folder", temp_config
        )
        folder_name = [x for x in src.split("/") if x != ""][-1]
        if folder_name:
            des_path = os.path.join(dest_folder, folder_name)
            FL.copy_folder(src, des_path)
            return True
        else:
            return False

    except Exception as e:
        return Exception_Handler(sys.exc_info())


def Add_File_To_Current_Test_Case_Log(src):
    try:
        # get the current test case locations
        dest_folder = ConfigModule.get_config_value(
            "sectionOne", "test_case_folder", temp_config
        )
        file_name = [x for x in src.split("/") if x != ""][-1]
        if file_name:
            des_path = os.path.join(dest_folder, file_name)
            FL.copy_file(src, des_path)
            return True
        else:
            return False

    except Exception as e:
        return Exception_Handler(sys.exc_info())


def Exception_Handler(exec_info, temp_q=None, UserMessage=None):
    try:
        # console.print_exception(show_locals=True, max_frames=1)
        if performance_testing:
            return
        sModuleInfo_Local = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        exc_type, exc_obj, exc_tb = exec_info
        Error_Type = (
            (str(exc_type).replace("type ", ""))
            .replace("<", "")
            .replace(">", "")
            .replace(";", ":")
        )
        Error_Message = str(exc_obj)
        File_Name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Function_Name = os.path.split(exc_tb.tb_frame.f_code.co_name)[1]
        Line_Number = str(exc_tb.tb_lineno)
        Error_Detail = (
            "Error Type ~ %s: Error Message ~ %s: File Name ~ %s: Function Name ~ %s: Line ~ %s"
            % (Error_Type, Error_Message, File_Name, Function_Name, Line_Number)
        )
        sModuleInfo = Function_Name + ":" + File_Name
        ExecLog(sModuleInfo, "Following exception occurred: %s" % (Error_Detail), 3)
        # TakeScreenShot(Function_Name + "~" + File_Name)
        if UserMessage != None:
            ExecLog(
                sModuleInfo, "Following error message is custom: %s" % (UserMessage), 3
            )
        # if temp_q != None:
        #     temp_q.put("zeuz_failed")

        return "zeuz_failed"

    except Exception:
        exc_type_local, exc_obj_local, exc_tb_local = sys.exc_info()
        fname_local = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail_Local = (
            (str(exc_type_local).replace("type ", "Error Type: "))
            + ";"
            + "Error Message: "
            + str(exc_obj_local)
            + ";"
            + "File Name: "
            + fname_local
            + ";"
            + "Line: "
            + str(exc_tb_local.tb_lineno)
        )
        ExecLog(
            sModuleInfo_Local,
            "Following exception occurred: %s" % (Error_Detail_Local),
            3,
        )
        return "zeuz_failed"


def Result_Analyzer(sTestStepReturnStatus, temp_q):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    # if performance_testing:
    #     return
    try:
        if sTestStepReturnStatus in passed_tag_list:
            temp_q.put("passed")
            return "passed"
        elif sTestStepReturnStatus in failed_tag_list:
            temp_q.put("zeuz_failed")
            return "zeuz_failed"
        elif sTestStepReturnStatus in skipped_tag_list:
            temp_q.put("skipped")
            return "skipped"
        elif sTestStepReturnStatus.lower() == "cancelled":
            temp_q.put("cancelled")
            return "cancelled"
        else:
            ExecLog(
                sModuleInfo,
                "Step return type unknown: %s. The last function did not return a valid type (passed/failed/etc)"
                % (sTestStepReturnStatus),
                3,
            )
            temp_q.put("zeuz_failed")
            return "zeuz_failed"

    except Exception as e:
        return Exception_Handler(sys.exc_info())


def node_manager_json(data):
    """ Generates a json file to communicate with node_manager"""
    json_path = Path(os.path.abspath(__file__)).parent.parent.parent / "node_state.json"
    with open(json_path, "w") as f:
        json.dump(data, f)

node_manager_json(
    {
        "state": "starting",
        "report": {
            "zip": None,
            "directory": None,
        }
    }
)
report_json_time = 0.0


def CreateJsonReport(logs=None, stepInfo=None, TCInfo=None, setInfo=None):
    try:
        # if performance_testing:
        #     return
        if debug_status:
            return
        elif upload_on_fail and rerun_on_fail and not rerunning_on_fail and logs:
            return
        global all_logs_json, report_json_time, tc_error_logs, passed_after_rerun
        start = time.perf_counter()
        if logs or stepInfo or TCInfo or setInfo:
            log_id = ConfigModule.get_config_value("sectionOne", "sTestStepExecLogId", temp_config)
            if not log_id:
                return
            log_id_vals = log_id.split("|")
            if logs:
                log_id, now, iLogLevel, status, sModuleInfo, sDetails = logs
            if len(log_id_vals) == 4:
                # these loops can be optimized by saving the previous log_id_vals and comparing it with current one
                runID, testcase_no, step_id, step_no = log_id_vals
                run_id_info = all_logs_json[runid_index]
                if setInfo:
                    run_id_info["execution_detail"] = setInfo
                    return
                all_testcases_info = run_id_info["test_cases"]
                testcase_info = all_testcases_info[tc_index]
                if TCInfo:
                    testcase_info["execution_detail"] = TCInfo
                    fail_reason_str = ""
                    if TCInfo["status"] in ("Failed", "Blocked"):
                        count = -min(len(tc_error_logs), 3)
                        while count <= -1:
                            fail_reason_str += tc_error_logs[count]
                            if count != -1:
                                fail_reason_str += "\n---------------------------------------------\n"
                            count += 1
                    elif passed_after_rerun:
                        fail_reason_str = "** Test case Failed on first run but Passed when Rerun **"
                        passed_after_rerun = False
                    testcase_info["execution_detail"]["failreason"] = fail_reason_str
                    return
                if step_id == "none":
                    return
                all_step_info = testcase_info["steps"]
                step_info = all_step_info[step_index]
                if stepInfo:
                    step_info["execution_detail"] = stepInfo
                    step_error_logs = []
                    if stepInfo["status"].lower() == "failed" and "log" in step_info:
                        count, err_count, max_count = -1, 0, -len(step_info["log"])
                        # Can be optimized by taking error when occurs and append it if the step fails only
                        while count >= max_count and err_count < 3:
                            each_log = step_info["log"][count]
                            if each_log["status"].lower() == "error":
                                step_error_logs.append(each_log["details"])
                                err_count += 1
                            count -= 1
                        step_error_logs.reverse()
                        tc_error_logs += step_error_logs
                    return
                log_info = {
                    "status": status,
                    "modulename": sModuleInfo,
                    "details": sDetails,
                    "tstamp": now,
                    "loglevel": iLogLevel,
                    "logid": log_id
                }
                if "log" in step_info:
                    step_info["log"].append(log_info)
                else:
                    step_info["log"] = [log_info]
        elif stepInfo:
            pass
        report_json_time += (time.perf_counter() - start)
    except:
        debug_code_error(sys.exc_info())


def clear_logs_from_report(send_log_file_only_for_fail, rerun_on_fail, sTestCaseStatus):
    global all_logs_json
    for step in all_logs_json[runid_index]["test_cases"][tc_index]["steps"]:
        # del step["actions"]
        if send_log_file_only_for_fail and not rerun_on_fail and sTestCaseStatus == "Passed" and "log" in step:
            del step["log"]


def ExecLog(
    sModuleInfo, sDetails, iLogLevel=1, _local_run="", sStatus="", force_write=False, variable=None, print_Execlog=True
):
    # Do not log anything if load testing is going on and we're not forced to write logs
    if performance_testing:
        return
    if load_testing and not force_write:
        return

    for val in zeuz_disable_var_print.values():
        if val != None:
            if str(val).lower() in sDetails.lower():
                return

    if not print_execlog: return    # For bypass_bug() function dont print logs

    global max_char, error_log_info
    # Read from settings file
    debug_mode = ConfigModule.get_config_value("RunDefinition", "debug_mode")

    # ";" is not supported for logging.  So replacing them
    # sDetails = sDetails.replace(";", ":").replace("%22", "'")

    # Terminal output color
    line_color = ""

    # Convert logLevel from int to string for clarity
    if iLogLevel == 0:
        if debug_mode.lower() == "true":
            status = (
                "Debug"  # This is not displayed on the server log, just in the console
            )
        else:  # Do not display this log line anywhere
            return
    elif iLogLevel == 1:
        status = "Passed"
        line_color = Fore.GREEN
    elif iLogLevel == 2:
        status = "Warning"
        line_color = Fore.YELLOW
    elif iLogLevel == 3:
        status = "Error"
        line_color = Fore.RED
    elif iLogLevel == 4:
        status = "Console"
    elif iLogLevel == 5:
        status = "Info"
        iLogLevel = 1
        line_color = Fore.CYAN
    elif iLogLevel == 6:
        status = "BrowserConsole"
    else:
        print("*** Unknown log level - Set to Info ***")
        status = "Info"
        iLogLevel = 5
        line_color = Fore.CYAN

    if not sModuleInfo:
        sModuleInfo = ""
        info = ""
    else:
        info = f"{sModuleInfo}\t\n"

    # Display on console
    # Change the format for console, mainly leave out the status level
    if "saved variable" not in sDetails.lower() and print_Execlog:
        if status == "Console":
            msg = f"{info}{sDetails}" if sModuleInfo else sDetails
            print(line_color + msg)
        else:
            msg = f"{status.upper()} - {info}{sDetails}"
            print(line_color + msg)
        max_char = max(max_char, len(msg))

    current_log_line = f"{status.upper()} - {sModuleInfo} - {sDetails}"

    global previous_log_line
    # Skip duplicate logs
    if previous_log_line and previous_log_line.strip() == current_log_line.strip():
        return

    # Set current log as the next previous log
    previous_log_line = current_log_line

    stop_live_log = ConfigModule.get_config_value("Advanced Options", "stop_live_log")

    if debug_status and ws_ss_log and stop_live_log.strip().lower() in ('false', 'no', 'disable'):
        live_log_service.log(sModuleInfo, iLogLevel, sDetails)

    if iLogLevel > 0:
        if iLogLevel == 6:
            FWLogFolder = ConfigModule.get_config_value(
                "sectionOne", "log_folder", temp_config
            )
            if os.path.exists(FWLogFolder) == False:
                FL.CreateFolder(FWLogFolder)  # Create log directory if missing

            if FWLogFolder == "":
                BrowserConsoleLogFile = (
                    ConfigModule.get_config_value(
                        "sectionOne", "temp_run_file_path", temp_config
                    )
                    + os.sep
                    + "BrowserLog.log"
                )
            else:
                BrowserConsoleLogFile = FWLogFolder + os.sep + "BrowserLog.log"

            logger = logging.getLogger(__name__)

            browser_log_handler = None
            if os.name == "posix":
                try:
                    browser_log_handler = logging.FileHandler(BrowserConsoleLogFile, encoding="utf-8")
                except:
                    pass
            elif os.name == "nt":
                browser_log_handler = logging.FileHandler(BrowserConsoleLogFile, encoding="utf-8")

            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

            if browser_log_handler:
                browser_log_handler.setFormatter(formatter)
                logger.addHandler(browser_log_handler)
                logger.setLevel(logging.DEBUG)
                logger.info(sModuleInfo + " - " + sDetails + "" + sStatus)
                logger.removeHandler(browser_log_handler)
        else:
            # Except the browser logs
            global all_logs, all_logs_count, all_logs_list

            log_id = ConfigModule.get_config_value(
                "sectionOne", "sTestStepExecLogId", temp_config
            )
            if not log_id:
                return

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if variable and variable["key"] not in skip_list:
                sDetails = "%s\nVariable value: %s" % (sDetails, variable["val"])
            if upload_on_fail and rerun_on_fail and not rerunning_on_fail:
                pass
            else:
                CreateJsonReport(logs=(log_id, now, iLogLevel, status, sModuleInfo, sDetails))

            all_logs[all_logs_count] = {
                "logid": log_id,
                "modulename": sModuleInfo,
                "details": sDetails,
                "status": status,
                "loglevel": iLogLevel,
                "tstamp": str(now),
            }
            if len(all_logs_list) >= 1:
                # start logging to the log file instead of logging to the server
                try:
                    # filepath = Path(ConfigModule.get_config_value('sectionOne', 'log_folder', temp_config)) / 'execution.log'
                    filepath = (
                        Path(
                            ConfigModule.get_config_value(
                                "sectionOne", "temp_run_file_path", temp_config
                            )
                        )
                        / "execution.log"
                    )
                    with open(filepath, "a+") as f:
                        print("[%s] %s" % (now, current_log_line), file=f)
                except FileNotFoundError:
                    pass

            # log warnings and errors
            if iLogLevel in (2, 3) or len(all_logs_list) < 1:
                # log to server in case of logs less than 2k
                all_logs_count += 1
                if all_logs_count > 2000:
                    all_logs_list.append(all_logs)
                    all_logs_count = 0
                    all_logs = {}

            #saving error information of a log in a global string variable
            if iLogLevel == 3:
                error_log_info += f"[STEP-{str(current_step_no)} ACTION-{str(current_action_no)}][{sModuleInfo}] {sDetails}\n"




def FormatSeconds(sec):
    hours, remainder = divmod(sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_formatted = "%d:%02d:%02d" % (hours, minutes, seconds)
    return duration_formatted


def get_all_logs(json=False):
    if json:
        return all_logs_json
    global all_logs_list, all_logs, all_logs_count

    if all_logs_count > 0:
        all_logs_list.append(all_logs)

    return all_logs_list


def clear_all_logs():
    global all_logs, all_logs_count, all_logs_list, all_logs_json
    all_logs = {}
    all_logs_count = 0
    all_logs_list = []
    return True


def PhysicalAvailableMemory():
    try:
        import psutil
        return (int(str(psutil.virtual_memory().available))) / (1024 * 1024)

    except Exception as e:
        return 1


screen_capture_driver, screen_capture_type = (
    None,
    "none",
)  # Initialize global variables for TakeScreenShot()


def set_screenshot_vars(shared_variables):
    """ Save screen capture type and selenium/appium driver objects as global variables, so TakeScreenShot() can access them """
    # We can't import Shared Variables due to cyclic imports causing local runs to break, so this is the work around
    # Known issue: This function is called by Sequential_Actions(). Thus, Maindriver can't take screenshots until this is set
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    global screen_capture_driver, screen_capture_type

    try:
        if "screen_capture" in shared_variables:  # Type of screenshot (desktop/mobile)
            screen_capture_type = shared_variables["screen_capture"]
        if screen_capture_type == "mobile":  # Appium driver object
            if "device_id" in shared_variables:
                device_id = shared_variables[
                    "device_id"
                ]  # Name of currently selected mobile device
                appium_details = shared_variables[
                    "appium_details"
                ]  # All device details
                screen_capture_driver = appium_details[device_id][
                    "driver"
                ]  # Driver for selected device
        if screen_capture_type == "web":  # Selenium driver object
            if "selenium_driver" in shared_variables:
                screen_capture_driver = shared_variables["selenium_driver"]
    except:
        ExecLog(sModuleInfo, "Error setting screenshot variables", 3)


def TakeScreenShot(function_name, local_run=False):
    """ Puts TakeScreenShot into a thread, so it doesn't block test case execution """
    if not ws_ss_log or performance_testing: return
    try:
        if upload_on_fail and rerun_on_fail and not rerunning_on_fail and not debug_status:
            return
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        # Read values from config file
        take_screenshot_settings = ConfigModule.get_config_value("RunDefinition", "take_screenshot")
        image_folder = ConfigModule.get_config_value("sectionOne", "screen_capture_folder", temp_config)

        try:
            if not os.path.exists(image_folder):
                os.mkdir(image_folder)
        except:
            pass

        Method = screen_capture_type
        Driver = screen_capture_driver

        # Decide if screenshot should be captured
        if (
            take_screenshot_settings.lower() == "false"
            or Method == "none"
            or Method is None
        ):
            ExecLog(
                sModuleInfo, "Skipping screenshot due to screenshot or local_run setting", 0
            )
            return
        ExecLog(
            "",
            "********** Capturing Screenshot for Action: %s Method: %s **********" % (function_name, Method),
            4,
        )
        if current_action_name.strip().lower() in ("none", "undefined"):
            image_name = "Step#" + current_step_no + "_Action#" + current_action_no + "_" + str(function_name)
        else:
            filename = ""; c = 0
            for i in current_action_name.strip():
                if i in ("<", ">", ":", '"', "/", "\\", "|", "?", "*", ".", " "):
                    filename += "_"
                else:
                    filename += i
                c += 1
                if c >= 100:
                    break
            image_name = "Step#" + current_step_no + "_Action#" + current_action_no + "_" + filename

        thread = executor.submit(Thread_ScreenShot, function_name, image_folder, Method, Driver, image_name)
        SaveThread("screenshot", thread)

    except:
        return Exception_Handler(sys.exc_info())


def pil_image_to_bytearray(img):
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format="PNG")
    img_byte_array = img_byte_array.getvalue()
    return img_byte_array


def Thread_ScreenShot(function_name, image_folder, Method, Driver, image_name):
    """ Capture screen of mobile or desktop """
    if performance_testing: return
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    chars_to_remove = [
        r"?",
        r"*",
        r'"',
        r"<",
        r">",
        r"|",
        r"\\",
        r"\/",
        r":",
    ]  # Symbols that can't be used in filename
    picture_quality = 100  # Quality of picture
    picture_size = 1920, 1080  # Size of image (for reduction in file size)

    # Adjust filename and create full path (remove invalid characters, convert spaces to underscore, remove leading and trailing spaces)
    trans_table = str.maketrans(
        dict.fromkeys("".join(chars_to_remove))
    )  # python3 version of translate
    ImageName = os.path.join(image_folder, (image_name.translate(trans_table)).strip().replace(" ", "_") + ".png")
    ExecLog(sModuleInfo, "Capturing screen on %s, with driver: %s, and saving to %s" % (str(Method), str(Driver), ImageName), 0)
    try:
        # Capture screenshot of desktop
        if Method == "desktop":
            if sys.platform == "linux2":
                image = ImageGrab_Linux.grab()
                image.save(ImageName, format="PNG")  # Save to disk
            elif sys.platform == "win32" or sys.platform == "darwin":
                image = ImageGrab_Mac_Win.grab()
                image.save(ImageName, format="PNG")  # Save to disk

        # Exit if we don't have a driver yet (happens when Test Step is set to mobile/web, but we haven't setup the driver)
        elif Driver is None and Method in ("mobile", "web"):
            ExecLog(
                sModuleInfo,
                "Can't capture screen, driver not available for type: %s, or invalid driver: %s"
                % (str(Method), str(Driver)),
                3,
            )
            return

        # Capture screenshot of web browser
        elif Method == "web":
            Driver.get_screenshot_as_file(ImageName)  # Must be .png, otherwise an exception occurs

        # Capture screenshot of mobile
        elif Method == "mobile":
            Driver.save_screenshot(ImageName)  # Must be .png, otherwise an exception occurs
        else:
            ExecLog(
                sModuleInfo,
                "Unknown capture type: %s, or invalid driver: %s"
                % (str(Method), str(Driver)),
                3,
            )
        # Lower the picture quality
        if os.path.exists(ImageName):  # Make sure image was saved
            image = Image.open(ImageName)  # Re-open in standard format
            image.thumbnail(picture_size, Image.LANCZOS)  # Resize picture to lower file size
            image.save(ImageName, format="PNG", quality=picture_quality)  # Change quality to reduce file size

            if debug_status:
                # Convert image to bytearray and send it to live_log_service for streaming.
                image_byte_array = pil_image_to_bytearray(image)

                live_log_service.binary(image_byte_array)
        else:
            ExecLog(
                "",
                "********** Screen couldn't be captured for Action: %s Method: %s **********" % (function_name, Method),
                4,
            )
    except selenium.common.exceptions.WebDriverException:
        ExecLog(
            "",
            "********** Screen couldn't be captured for Action: %s Method: %s because webdriver not found or started **********" % (function_name, Method),
            4,
        )
    except Exception:
        # traceback.print_exc()
        ExecLog(
            "",
            "********** Screen couldn't be captured for Action: %s Method: %s **********" % (function_name, Method),
            4,
        )

d_day = 0
d_hours = 0
d_minutes = 0
d_seconds = 0

def get_timestamp() -> datetime:
    """Get UTC-0 times tamps for metrics and other purposes."""
    d = datetime.datetime.utcnow()
    d += datetime.timedelta(days=d_day, hours=d_hours, minutes=d_minutes, seconds=d_seconds)
    return d.strftime("%Y-%m-%d %H:%M:%S.%f")


def TimeStamp(format):
    """
    :param format: name of format ex: string , integer
    :return:
    ========= Instruction: ============
    Function Description:
    This function is used to create a Time Stamp.
    It will return current Day-Month-Date-Hour:Minute:Second-Year all in one string
    OR
    It will return current YearMonthDayHourMinuteSecond all in a integer.
    Parameter Description:
    - string: this returns a readable string for the current date and time format
        Example:
        TimeStamp = TimeStamp("string") = Fri-Jan-20-10:20:31-2012
    - integer: this returns a readable string for the current date and time format
        Example:
        TimeStamp = TimeStamp("integer") = 2012120102051
    ======= End of Instruction: =========
    """
    if format == "string":
        TimeStamp = datetime.datetime.now().ctime().replace(" ", "-").replace("--", "-")
    elif format == "integer":
        TimeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    elif format == "utc":
        TimeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
    elif format == "utcstring":
        TimeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    else:
        TimeStamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

    return TimeStamp


def set_exit_mode(emode):
    """ Sets a value in the temp config file to tell sequential actions to exit, if set to true """
    # Set by the user via the GUI
    ConfigModule.add_config_value("sectionOne", "exit_script", str(emode), temp_config)


def check_offline():
    """ Checks the value set in the temp config file to tell sequential actions to exit, if set to true """
    # Set by the user via the GUI
    value = ConfigModule.get_config_value("sectionOne", "exit_script", temp_config)
    if value == "True":
        return True
    else:
        return False


def Delete_from_list(List, to_del):
    """ This function can delete multiple elements from list with O(N) complexity """
    if not to_del:
        return List
    to_del.sort()
    cnt, del_cnt, new_list, check = 0, 0, [], True
    for i in List:
        if check and cnt == to_del[del_cnt]:
            del_cnt += 1
            if del_cnt == len(to_del):
                check = False
        else:
            new_list.append(i)
        cnt += 1
    return new_list


class MachineInfo:
    def getLocalIP(self):
        """
        :return: get local address of machine
        """
        try:
            import socket

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("gmail.com", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip

        except Exception as e:
            return Exception_Handler(sys.exc_info())

    def setLocalUser(self, custom_id):
        """
        Set node_id from node_cli Command Line Interface and returns local userid
        """
        try:
            node_id_file_path = Path(os.path.abspath(__file__).split("Framework")[0]) / "node_id.conf"
            if os.path.isfile(node_id_file_path):
                ConfigModule.clean_config_file(node_id_file_path)
                ConfigModule.add_section("UniqueID", node_id_file_path)
                custom_id = custom_id.lower()[:10]
                ConfigModule.add_config_value("UniqueID", "id", custom_id, node_id_file_path)
            else:
                f = open(node_id_file_path, "w")
                f.close()
                ConfigModule.add_section("UniqueID", node_id_file_path)
                custom_id = custom_id.lower()[:10]
                ConfigModule.add_config_value("UniqueID", "id", custom_id, node_id_file_path)
        except Exception:
            ErrorMessage = "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return Exception_Handler(sys.exc_info(), None, ErrorMessage)

    def getLocalUser(self):
        """
        :return: returns the local pc name
        """
        try:
            # node_id_file_path = os.path.join(FL.get_home_folder(), os.path.join('Desktop', 'node_id.conf'))
            # node_id_file_path = os.path.join (os.path.realpath(__file__).split("Framework")[0] , os.path.join ('node_id.conf'))

            node_id_file_path = Path(
                os.path.abspath(__file__).split("Framework")[0]
            ) / Path("node_id.conf")

            if os.path.isfile(node_id_file_path):
                unique_id = ConfigModule.get_config_value(
                    "UniqueID", "id", node_id_file_path
                )
                if unique_id == "":
                    ConfigModule.clean_config_file(node_id_file_path)
                    ConfigModule.add_section("UniqueID", node_id_file_path)
                    unique_id = uuid.uuid4()
                    unique_id = str(unique_id)[:10]
                    ConfigModule.add_config_value(
                        "UniqueID", "id", unique_id, node_id_file_path
                    )
                    machine_name = (
                        ConfigModule.get_config_value("Authentication", "username")
                        + "_"
                        + str(unique_id)
                    )
                    return machine_name[:100]
                machine_name = (
                    ConfigModule.get_config_value("Authentication", "username")
                    + "_"
                    + str(unique_id)
                )
            else:
                # create the file name
                f = open(node_id_file_path, "w")
                f.close()
                unique_id = uuid.uuid4()
                unique_id = str(unique_id).lower()[:10]
                ConfigModule.add_section("UniqueID", node_id_file_path)
                ConfigModule.add_config_value(
                    "UniqueID", "id", unique_id, node_id_file_path
                )
                machine_name = (
                    ConfigModule.get_config_value("Authentication", "username")
                    + "_"
                    + str(unique_id)
                )
            return machine_name[:100]

        except Exception:
            ErrorMessage = "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return Exception_Handler(sys.exc_info(), None, ErrorMessage)

    def getUniqueId(self):
        """
        This function is not used any more
        :return: returns the local pc unique ID
        """
        try:
            node_id_file_path = Path(
                os.path.abspath(__file__).split("Framework")[0]
            ) / Path("node_id.conf")

            if os.path.isfile(node_id_file_path):
                unique_id = ConfigModule.get_config_value(
                    "UniqueID", "id", node_id_file_path
                )
                if unique_id == "":
                    ConfigModule.clean_config_file(node_id_file_path)
                    ConfigModule.add_section("UniqueID", node_id_file_path)
                    unique_id = uuid.uuid4()
                    unique_id = str(unique_id)[:10]
                    ConfigModule.add_config_value(
                        "UniqueID", "id", unique_id, node_id_file_path
                    )
                    machine_name = str(unique_id)
                    return machine_name[:100]
                machine_name = str(unique_id)
            else:
                # create the file name
                f = open(node_id_file_path, "w")
                f.close()
                unique_id = uuid.uuid4()
                unique_id = str(unique_id)[:10]
                ConfigModule.add_section("UniqueID", node_id_file_path)
                ConfigModule.add_config_value(
                    "UniqueID", "id", unique_id, node_id_file_path
                )
                machine_name = str(unique_id)
            return machine_name[:100]

        except Exception:
            ErrorMessage = "Unable to set create a Node key.  Please check class MachineInfo() in commonutil"
            return Exception_Handler(sys.exc_info(), None, ErrorMessage)


def debug_code_error(exc_info):
    exc_type, exc_obj, exc_tb = exc_info
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Error_Detail = (
            (str(exc_type).replace("type ", "Error Type: "))
            + ";"
            + "Error Message: "
            + str(exc_obj)
            + ";"
            + "File Name: "
            + fname
            + ";"
            + "Line: "
            + str(exc_tb.tb_lineno)
    )
    print(Error_Detail)


def path_parser(path: str) -> str:
    r"""
    Case-1: (Full_path)
    C:\Users\ASUS\entreprize_5689.csv
    Case-2: (Home_dir)
    ~\Downloads\entreprize_5689.csv
    Case-3: (Partial_search)
    ~\Downloads\*entreprize_.csv
    ~\Downloads\*entreprize_
    Case-4: (Multiple_Partial_Search)
    ~\Downloads\*server\*entreprize_.csv
    Case-5: (Partial_Case-insensitive_Search)
    ~\Downloads\**server\**entreprize_.csv
    Case-6: (Partial search with Index) [It's not done yet. will be done if necessary]
    ~\Downloads\**server\[idx]*entreprize_.csv

    tested against:
    print(path_parser(r"~\Downloads"))                          C:\Users\ASUS\Downloads
    print(path_parser(r"~\**download"))                         C:\Users\ASUS\Downloads
    print(path_parser(r"C:\Users\ASUS\Downloads"))              C:\Users\ASUS\Downloads
    print(path_parser(r"C:\Users\ASUS\**download"))             C:\Users\ASUS\Downloads
    print(path_parser(r"~"))                                    C:\Users\ASUS
    print(path_parser(r"C:"))                                   C:
    print(path_parser(r"~\Downloads\*.pdf"))                    C:\Users\ASUS\Downloads\FF.pdf

    """
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        if not path.startswith("~") and "*" not in path:
            return path  # dont print execlog
        inp_path = path
        if path.startswith("~"):
            path = path.replace("~", os.path.expanduser("~"), 1)

        path = str(Path(path))
        path = path.split(os.sep)
        new_path = ''
        for a in path:
            final = a
            if "*" in a:
                extension = a.split(".")[1] if "." in a else ""
                name = a.split(".")[0].replace("*", "")
                w = list(os.walk(new_path))[0]
                w = w[1] + w[2]
                for j in w:
                    if "**" in a and name.lower() in j.lower() and j.endswith(extension):
                        final = j
                        break
                    elif "*" in a and name in j and j.endswith(extension):
                        final = j
                        break
                else:
                    ExecLog(sModuleInfo, "No file_path or directory was found with: %s" % inp_path, 3)
                    raise Exception

            new_path = new_path + final + os.sep

        new_path = new_path[:-1]
        ExecLog(sModuleInfo, new_path, 1)
        return new_path
    except:
        Exception_Handler(sys.exc_info())
        raise Exception


def calculated_percentile(elapsed_times: Dict[int, int], total_requests: int, percent: float) -> int:
    """
    Calculate the percentile of the given data
    :param elapsed_times:
    :param total_requests:
    :param percent:
    :return:
    """
    if percent == 0:
        return 0
    elif percent == 100:
        return max(elapsed_times.keys())
    else:
        rank = int(total_requests * percent / 100)
        count = 0
        for key in sorted(elapsed_times.keys()):
            count += elapsed_times[key]
            if count >= rank:
                return key


def generate_time_based_performance_report(session) -> None:
    """
    Generate the time based performance report
    :param session:
    """
    print("Generating Performance Report")

    if "execution_detail" not in session["test_cases"][0]:
        return
    elif "metrics" not in session['test_cases'][0]['execution_detail']:
        return

    perf_data = session['test_cases'][0]['execution_detail']['metrics']['node']['api_performance_data']
    run_id = session['run_id']
    teststarttime = session['test_cases'][0]['execution_detail']['teststarttime']
    testendtime = session['test_cases'][0]['execution_detail']['testendtime']
    duration = session['test_cases'][0]['execution_detail']['duration']
    tc_id = session['test_cases'][0]['testcase_no']

    endpoint_wise = {}

    for data in perf_data:
        data: PerformanceDataPoint = data
        key = data.url + '|' + data.http_verb

        input_datetime = datetime.datetime.strptime(data.time_stamp[:-3], "%Y-%m-%d %H:%M:%S.%f")
        formatted_datetime_str = input_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

        if endpoint_wise.get(key) is None:
            endpoint_wise[key] = {
                'endpoint': data.url,
                'method': data.http_verb,
                'total_request': 1,
                'total_failed_request': 0 if data.response_body == "" else 1,
                'total_elapsed_time': data.elapsed_time,
                'elapsed_time_dict': {data.elapsed_time: 1},
                'total_content_length': data.response_body_size,
                'error': {} if data.response_body == "" else {data.response_body: 1},
                'dict_response_time_per_time': {formatted_datetime_str: [data.elapsed_time]},
                'dict_byte_throughput_per_time': {formatted_datetime_str: [data.response_body_size]}
            }
        else:
            endpoint_wise[key]['total_request'] += 1
            endpoint_wise[key]['total_failed_request'] += 0 if data.response_body == "" else 1
            endpoint_wise[key]['total_elapsed_time'] += data.elapsed_time
            endpoint_wise[key]['elapsed_time_dict'][data.elapsed_time] = endpoint_wise[key]['elapsed_time_dict'].get(
                data.elapsed_time, 0) + 1
            endpoint_wise[key]['total_content_length'] += data.response_body_size
            if data.response_body != "":
                endpoint_wise[key]['error'][data.response_body] = endpoint_wise[key]['error'].get(data.response_body, 0) + 1

            if endpoint_wise[key]['dict_response_time_per_time'].get(formatted_datetime_str) is None:
                endpoint_wise[key]['dict_response_time_per_time'][formatted_datetime_str] = [data.elapsed_time]
            else:
                endpoint_wise[key]['dict_response_time_per_time'][formatted_datetime_str].append(data.elapsed_time)

            if endpoint_wise[key]['dict_byte_throughput_per_time'].get(formatted_datetime_str) is None:
                endpoint_wise[key]['dict_byte_throughput_per_time'][formatted_datetime_str] = [data.response_body_size]
            else:
                endpoint_wise[key]['dict_byte_throughput_per_time'][formatted_datetime_str].append(data.response_body_size)

    for endpoint in endpoint_wise:
        endpoint_wise[endpoint]['avg_elapsed_time'] = int(
            endpoint_wise[endpoint]['total_elapsed_time'] / endpoint_wise[endpoint]['total_request'])
        endpoint_wise[endpoint]['avg_content_length'] = int(
            endpoint_wise[endpoint]['total_content_length'] / endpoint_wise[endpoint]['total_request'])
        endpoint_wise[endpoint]['min_time'] = min(endpoint_wise[endpoint]['elapsed_time_dict'].keys())
        endpoint_wise[endpoint]['max_time'] = max(endpoint_wise[endpoint]['elapsed_time_dict'].keys())

        endpoint_wise[endpoint]['fifty'] = calculated_percentile(endpoint_wise[endpoint]['elapsed_time_dict'],
                                                                 endpoint_wise[endpoint]['total_request'], 50)
        endpoint_wise[endpoint]['sixty'] = calculated_percentile(endpoint_wise[endpoint]['elapsed_time_dict'],
                                                                 endpoint_wise[endpoint]['total_request'], 60)
        endpoint_wise[endpoint]['seventy'] = calculated_percentile(endpoint_wise[endpoint]['elapsed_time_dict'],
                                                                   endpoint_wise[endpoint]['total_request'], 70)
        endpoint_wise[endpoint]['eighty'] = calculated_percentile(endpoint_wise[endpoint]['elapsed_time_dict'],
                                                                  endpoint_wise[endpoint]['total_request'], 80)
        endpoint_wise[endpoint]['ninety'] = calculated_percentile(endpoint_wise[endpoint]['elapsed_time_dict'],
                                                                  endpoint_wise[endpoint]['total_request'], 90)
        endpoint_wise[endpoint]['ninety_nine'] = calculated_percentile(endpoint_wise[endpoint]['elapsed_time_dict'],
                                                                       endpoint_wise[endpoint]['total_request'], 99)
        endpoint_wise[endpoint]['ninety_five'] = calculated_percentile(endpoint_wise[endpoint]['elapsed_time_dict'],
                                                                       endpoint_wise[endpoint]['total_request'], 95)
        endpoint_wise[endpoint]['hundred'] = calculated_percentile(endpoint_wise[endpoint]['elapsed_time_dict'],
                                                                   endpoint_wise[endpoint]['total_request'], 100)
        endpoint_wise[endpoint]['response_time_vs_time'] = []
        endpoint_wise[endpoint]['user_count_per_second'] = []
        endpoint_wise[endpoint]['percentile_vs_time'] = []
        endpoint_wise[endpoint]['fiftypercentile_per_second'] = []
        endpoint_wise[endpoint]['ninetypercentile_per_second'] = []
        
        endpoint_wise[endpoint]['dict_response_time_per_time'] = dict(
            sorted(endpoint_wise[endpoint]['dict_response_time_per_time'].items(),
                   key=lambda x: datetime.datetime.strptime(x[0], "%Y-%m-%dT%H:%M:%SZ").timestamp()))
        endpoint_wise[endpoint]['dict_byte_throughput_per_time'] = dict(
            sorted(endpoint_wise[endpoint]['dict_byte_throughput_per_time'].items(),
                   key=lambda x: datetime.datetime.strptime(x[0], "%Y-%m-%dT%H:%M:%SZ").timestamp()))
        
        for key, value_list in endpoint_wise[endpoint]['dict_response_time_per_time'].items():
            endpoint_wise[endpoint]['response_time_vs_time'].append([key, int(sum(value_list) / len(value_list))])
            endpoint_wise[endpoint]['user_count_per_second'].append([key, len(value_list) + endpoint_wise[endpoint]['user_count_per_second'][-1][1] if len(endpoint_wise[endpoint]['user_count_per_second']) > 0 else 0])

            items_count = dict(Counter(value_list))
            endpoint_wise[endpoint]['fiftypercentile_per_second'].append(
                [key, calculated_percentile(items_count, len(value_list), 50)])
            endpoint_wise[endpoint]['ninetypercentile_per_second'].append(
                [key, calculated_percentile(items_count, len(value_list), 90)])

        endpoint_wise[endpoint]['byte_throughput_vs_time'] = []
        for key, value_list in endpoint_wise[endpoint]['dict_byte_throughput_per_time'].items():
            endpoint_wise[endpoint]['byte_throughput_vs_time'].append([key, int(sum(value_list) / len(value_list))])


    data = {
        'run_id': run_id,
        'teststarttime': teststarttime,
        'testendtime': testendtime,
        'duration': duration,
        'tc_id': tc_id,
        'endpoint_wise': endpoint_wise
    }

    global processed_performance_data
    processed_performance_data = data
    return


if __name__ == "__main__":
    pass
    # path_parser('~\Downloads\*S.exe')
