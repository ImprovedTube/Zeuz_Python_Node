'''
Created on May 15, 2016

@author: AutomationSolutionz Inc.
'''

import os,sys,time
import inspect
from Utilities import CommonUtil
from Projects.ITSolutionsInc import ITSolutionsInc as ITS

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def Select_Gear_Menu(dependency,run_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        item_text = step_data[0][1]
        sTestStepReturnStatus=ITS.Select_Gear_Menu_Item(item_text)
        
        temp_q.put(sTestStepReturnStatus)
        return sTestStepReturnStatus
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go to webpage: Error:%s" %( Error_Detail), 3,local_run)
        temp_q.put("Failed")
        return "failed"

