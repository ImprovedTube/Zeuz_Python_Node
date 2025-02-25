declarations = (
    { "name": "save response",                 "function": "Get_Response_Wrapper",             "screenshot": "none" },
    { "name": "search response",               "function": "Search_Response",                  "screenshot": "none" },
    { "name": "save response into list",       "function": "Insert_Into_List",                 "screenshot": "none" },
    { "name": "save response and cookie",      "function": "Get_Response_Wrapper_With_Cookie", "screenshot": "none" },
    { "name": "save response tuple into list", "function": "Insert_Tuple_Into_List",           "screenshot": "none" },

# Oauth2.0 actions made for taxcalc
    {"name": "get oauth2 access token url",    "function": "Get_Oauth2_Access_Token_URl",       "screenshot": "none"},

) # yapf: disable

module_name = "rest"

for dec in declarations:
    dec["module"] = module_name
