declarations = (
    { "name": "click",                         "function": "Click_Element",                 "screenshot": "web" },
    { "name": "click and hold",                "function": "Click_and_Hold_Element",        "screenshot": "web" },
    { "name": "click and download",            "function": "Click_and_Download",            "screenshot": "web" },
    { "name": "context click",                 "function": "Context_Click_Element",         "screenshot": "web" },
    { "name": "double click",                  "function": "Double_Click_Element",          "screenshot": "web" },
    { "name": "move to element",               "function": "Move_To_Element",               "screenshot": "web" },
    { "name": "hover",                         "function": "Hover_Over_Element",            "screenshot": "web" },
    { "name": "keystroke keys",                "function": "Keystroke_For_Element",         "screenshot": "web" },
    { "name": "keystroke chars",               "function": "Keystroke_For_Element",         "screenshot": "web" },
    { "name": "text",                          "function": "Enter_Text_In_Text_Box",        "screenshot": "web" },
    { "name": "initialize list",               "function": "Initialize_List",               "screenshot": "web" },
    { "name": "validate full text",            "function": "Validate_Text",                 "screenshot": "web" },
    { "name": "validate partial text",         "function": "Validate_Text",                 "screenshot": "web" },
    { "name": "scroll",                        "function": "Scroll",                        "screenshot": "web" },
    { "name": "deselect all",                  "function": "Select_Deselect",               "screenshot": "web" },
    { "name": "select by visible text",        "function": "Select_Deselect",               "screenshot": "web" },
    { "name": "deselect by visible text",      "function": "Select_Deselect",               "screenshot": "web" },
    { "name": "select by value",               "function": "Select_Deselect",               "screenshot": "web" },
    { "name": "deselect by value",             "function": "Select_Deselect",               "screenshot": "web" },
    { "name": "select by index",               "function": "Select_Deselect",               "screenshot": "web" },
    { "name": "deselect by index",             "function": "Select_Deselect",               "screenshot": "web" },
    { "name": "open browser",                  "function": "Open_Browser_Wrapper",          "screenshot": "web" },
    { "name": "open electron app",             "function": "Open_Electron_App",             "screenshot": "web" },
    { "name": "go to link",                    "function": "Go_To_Link",                    "screenshot": "web" },
    { "name": "tear down browser",             "function": "Tear_Down_Selenium",            "screenshot": "none"},
    { "name": "switch browser",                "function": "Switch_Browser",                "screenshot": "none"},
    { "name": "get current url",               "function": "Get_Current_URL",               "screenshot": "none"},
    { "name": "navigate",                      "function": "Navigate",                      "screenshot": "web" },
    { "name": "get location",                  "function": "get_location_of_element",       "screenshot": "web" },
    { "name": "validate table",                "function": "validate_table",                "screenshot": "web" },
    { "name": "handle alert",                  "function": "Handle_Browser_Alert",          "screenshot": "desktop"},
    { "name": "browser",                       "function": "Open_Browser_Wrapper",          "screenshot": "web" },
    { "name": "teardown",                      "function": "Tear_Down_Selenium",            "screenshot": "none"},
    { "name": "open new tab",                  "function": "open_new_tab",                  "screenshot": "web" },
    { "name": "switch tab",                    "function": "switch_tab",                    "screenshot": "web" },
    { "name": "validate table row size",       "function": "validate_table_row_size",       "screenshot": "web" },
    { "name": "validate table column size",    "function": "validate_table_column_size",    "screenshot": "web" },
    { "name": "upload file",                   "function": "upload_file",                   "screenshot": "web" },
    { "name": "upload through window",         "function": "upload_file_through_window",    "screenshot": "web" },
    { "name": "drag and drop",                 "function": "drag_and_drop",                 "screenshot": "web" },
    { "name": "scroll to element",             "function": "scroll_to_element",             "screenshot": "web" },
    { "name": "if element exists",             "function": "if_element_exists",             "screenshot": "web" },
    { "name": "click and enter text",          "function": "Click_and_Text",                "screenshot": "web" },
    { "name": "validate url",                  "function": "Validate_Url",                  "screenshot": "web" },
    { "name": "scroll element to top",         "function": "scroll_element_to_top",         "screenshot": "web" },
    { "name": "switch window",                 "function": "switch_window",                 "screenshot": "web" },
    { "name": "switch window or frame",        "function": "switch_window_or_tab",          "screenshot": "web" },
    { "name": "switch window/tab",             "function": "switch_window_or_tab",          "screenshot": "web" },
    { "name": "switch iframe",                 "function": "switch_iframe",                 "screenshot": "web" },
    { "name": "save attribute",                "function": "Save_Attribute",                "screenshot": "web" },
    { "name": "save attribute values in list", "function": "save_attribute_values_in_list", "screenshot": "web" },
    { "name": "extract table data",            "function": "Extract_Table_Data",            "screenshot": "web" },
    { "name": "save web elements in list",     "function": "save_web_elements_in_list",     "screenshot": "web" },
    { "name": "take screenshot web",           "function": "take_screenshot_selenium",      "screenshot": "web" },
    { "name": "mouse click",                   "function": "Mouse_Click_Element",           "screenshot": "web" },
    { "name": "execute javascript",            "function": "execute_javascript",            "screenshot": "web" },
    { "name": "check uncheck all",             "function": "check_uncheck_all",             "screenshot": "web" },
    { "name": "check uncheck",                 "function": "check_uncheck",                 "screenshot": "web" },
    { "name": "multiple check uncheck",        "function": "multiple_check_uncheck",        "screenshot": "web" },
    { "name": "slider bar",                    "function": "slider_bar",                    "screenshot": "web" },
    { "name": "_devtools_end",                    "function": "_devtools_end",                    "screenshot": "web" },
) # yapf: disable

module_name = "selenium"

for dec in declarations:
    dec["module"] = module_name
