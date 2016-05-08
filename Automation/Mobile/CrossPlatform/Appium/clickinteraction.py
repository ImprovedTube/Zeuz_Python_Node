
import os , sys, inspect
from Utilities import CommonUtil
from Automation.Mobile.CrossPlatform.Appium import locateinteraction as li

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def click_element_by_id(driver, _id, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by id: %s"%_id,1,local_run)
        elem = li.locate_element_by_id(driver, _id, parent)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
    
def click_element_by_name(driver, _name, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by name: %s"%_name,1,local_run)
        elem = li.locate_element_by_name(driver, _name, parent)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
    
def click_element_by_class_name(driver, _class, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by class: %s"%_class,1,local_run)
        elem = li.locate_element_by_class_name(driver, _class, parent)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
    
def click_element_by_xpath(driver, _classpath, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by xpath: %s"%_classpath,1,local_run)
        elem = li.locate_element_by_xpath(driver, _classpath, parent)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
    
def click_element_by_accessibility_id(driver, _id, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by accessibility id: %s"%_id,1,local_run)
        elem = li.locate_element_by_accessibility_id(driver, _id, parent)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
    
def click_element_by_android_uiautomator_text(driver, _text, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by android uiautomator text: %s"%_text,1,local_run)
        elem = li.locate_element_by_android_uiautomator_text(driver, _text, parent)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
    
def click_element_by_android_uiautomator_description(driver, _description, parent=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by android uiautomator description: %s"%_description,1,local_run)
        elem = li.locate_element_by_android_uiautomator_description(driver, _description, parent)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"
