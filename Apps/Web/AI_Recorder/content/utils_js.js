function classCreate() {
    return function() {
        this.initialize.apply(this, arguments);
    }
}

function objectExtend(destination, source) {
    for (var property in source) {
        destination[property] = source[property];
    }
    return destination;
}


function sel$() {
    var results = [],
        element;
    for (var i = 0; i < arguments.length; i++) {
        element = arguments[i];
        if (typeof element == 'string')
            element = document.getElementById(element);
        results[results.length] = element;
    }
    return results.length < 2 ? results[0] : results;
}

function sel$A(iterable) {
    if (!iterable) return [];
    if (iterable.toArray) {
        return iterable.toArray();
    } else {
        var results = [];
        for (var i = 0; i < iterable.length; i++)
            results.push(iterable[i]);
        return results;
    }
}


function fnBind() {
    var args = sel$A(arguments),
        __method = args.shift(),
        object = args.shift();
    var retval = function() {
        return __method.apply(object, args.concat(sel$A(arguments)));
    }
    retval.__method = __method;
    return retval;
}

function elementSetStyle(element, style) {
    for (var name in style) {
        var value = style[name];
        if (value == null) value = "";
        element.style[name] = value;
    }
}

function elementGetStyle(element, style) {
    var value = element.style[style];
    if (!value) {
        if (document.defaultView && document.defaultView.getComputedStyle) {
            var css = document.defaultView.getComputedStyle(element, null);
            value = css ? css.getPropertyValue(style) : null;
        } else if (element.currentStyle) {
            value = element.currentStyle[style];
        }
    }

    return value == 'auto' ? null : value;
}


String.prototype.trim = function() {
    var result = this.replace(/^\s+/g, "");
    return result.replace(/\s+$/g, "");
};
String.prototype.lcfirst = function() {
    return this.charAt(0).toLowerCase() + this.substr(1);
};
String.prototype.ucfirst = function() {
    return this.charAt(0).toUpperCase() + this.substr(1);
};
String.prototype.startsWith = function(str) {
    return this.indexOf(str) == 0;
};

function getText(element) {
    var text = "";

    var isRecentFirefox = (browserVersion.isFirefox && browserVersion.firefoxVersion >= "1.5");
    if (isRecentFirefox || browserVersion.isKonqueror || browserVersion.isSafari || browserVersion.isOpera) {
        text = getTextContent(element);
    } else if (element.textContent) {
        text = element.textContent;
    } else if (element.innerText) {
        text = element.innerText;
    }

    text = normalizeNewlines(text);
    text = normalizeSpaces(text);

    return text.trim();
}

function getTextContent(element, preformatted) {
    if (element.style && (element.style.visibility == 'hidden' || element.style.display == 'none')) return '';
    if (element.nodeType == 3 ) {
        var text = element.data;
        if (!preformatted) {
            text = text.replace(/\n|\r|\t/g, " ");
        }
        return text;
    }
    if (element.nodeType == 1 && element.nodeName != 'SCRIPT') {
        var childrenPreformatted = preformatted || (element.tagName == "PRE");
        var text = "";
        for (var i = 0; i < element.childNodes.length; i++) {
            var child = element.childNodes.item(i);
            text += getTextContent(child, childrenPreformatted);
        }
        if (element.tagName == "P" || element.tagName == "BR" || element.tagName == "HR" || element.tagName == "DIV") {
            text += "\n";
        }
        return text;
    }
    return '';
}


function normalizeNewlines(text) {
    return text.replace(/\r\n|\r/g, "\n");
}

function normalizeSpaces(text) {
    if (browserVersion.isIE) {
        return text;
    }

    text = text.replace(/\ +/g, " ");

    var nbspPattern = new RegExp(String.fromCharCode(160), "g");
    if (browserVersion.isSafari) {
        return replaceAll(text, String.fromCharCode(160), " ");
    } else {
        return text.replace(nbspPattern, " ");
    }
}

function replaceAll(text, oldText, newText) {
    while (text.indexOf(oldText) != -1) {
        text = text.replace(oldText, newText);
    }
    return text;
}

function setText(element, text) {
    if (element.textContent != null) {
        element.textContent = text;
    } else if (element.innerText != null) {
        element.innerText = text;
    }
}

function getInputValue(inputElement) {
    if (inputElement.type) {
        if (inputElement.type.toUpperCase() == 'CHECKBOX' ||
            inputElement.type.toUpperCase() == 'RADIO') {
            return (inputElement.checked ? 'on' : 'off');
        }
    }
    if (inputElement.value == null) {
    }
    return inputElement.value;
}

function getKeyCodeFromKeySequence(keySequence) {
    var match = /^\\(\d{1,3})$/.exec(keySequence);
    if (match != null) {
        return match[1];
    }
    match = /^.$/.exec(keySequence);
    if (match != null) {
        return match[0].charCodeAt(0);
    }

    match = /^\d{2,3}$/.exec(keySequence);
    if (match != null) {
        return match[0];
    }
    throw new SeleniumError("invalid keySequence");
}

function createEventObject(element, controlKeyDown, altKeyDown, shiftKeyDown, metaKeyDown) {
    var evt = element.ownerDocument.createEventObject();
    evt.shiftKey = shiftKeyDown;
    evt.metaKey = metaKeyDown;
    evt.altKey = altKeyDown;
    evt.ctrlKey = controlKeyDown;
    return evt;
}

function triggerKeyEvent(element, eventType, keySequence, canBubble, controlKeyDown, altKeyDown, shiftKeyDown, metaKeyDown) {
    var keycode = getKeyCodeFromKeySequence(keySequence);
    canBubble = (typeof(canBubble) == undefined) ? true : canBubble;
    if (element.fireEvent && element.ownerDocument && element.ownerDocument.createEventObject) { // IE
        var keyEvent = createEventObject(element, controlKeyDown, altKeyDown, shiftKeyDown, metaKeyDown);
        keyEvent.keyCode = keycode;
        element.fireEvent('on' + eventType, keyEvent);
    } else {
        var evt;
        if (window.KeyEvent) {
            var doc = goog.dom.getOwnerDocument(element);
            var view = goog.dom.getWindow(doc);
            evt = doc.createEvent('KeyEvents');
            evt.initKeyEvent(eventType, true, true, view, controlKeyDown, altKeyDown, shiftKeyDown, metaKeyDown, keycode, keycode);
        } else {
            evt = document.createEvent('UIEvents');

            evt.shiftKey = shiftKeyDown;
            evt.metaKey = metaKeyDown;
            evt.altKey = altKeyDown;
            evt.ctrlKey = controlKeyDown;

            evt.initUIEvent(eventType, true, true, window, 1);
            evt.keyCode = keycode;
            evt.which = keycode;
        }

        element.dispatchEvent(evt);
    }
}

function addLoadListener(element, command) {
    var augmentedCommand = function() {
        command.call(this, element);
    }
    if (window.addEventListener && !browserVersion.isOpera)
        element.addEventListener("load", augmentedCommand, true);
    else if (window.attachEvent)
        element.attachEvent("onload", augmentedCommand);
}

function getTagName(element) {
    var tagName;
    if (element && element.tagName && element.tagName.toLowerCase) {
        tagName = element.tagName.toLowerCase();
    }
    return tagName;
}

function selArrayToString(a) {
    if (isArray(a)) {
        var retval = [];
        for (var i = 0; i < a.length; i++) {
            var item = a[i];
            var replaced = new String(item).replace(/([,\\])/g, '\\$1');
            retval[i] = replaced;
        }
        return retval;
    }
    return new String(a);
}


function isArray(x) {
    return ((typeof x) == "object") && (x["length"] != null);
}

function absolutify(url, baseUrl) {
    
    if (/^\w+:/.test(url)) {
        return url;
    }

    var loc;
    try {
        loc = parseUrl(baseUrl);
    } catch (e) {
        if (/^\w:\\/.test(baseUrl)) {
            baseUrl = "file:///" + baseUrl.replace(/\\/g, "/");
            loc = parseUrl(baseUrl);
        } else {
            throw new SeleniumError("baseUrl wasn't absolute: " + baseUrl);
        }
    }
    loc.search = null;
    loc.hash = null;

    if (/^\//.test(url)) {
        loc.pathname = url;
        var result = reassembleLocation(loc);
        return result;
    }

    if (!loc.pathname) {
        loc.pathname = "/" + url;
        var result = reassembleLocation(loc);
        return result;
    }

    if (/\/$/.test(loc.pathname)) {
        loc.pathname += url;
        var result = reassembleLocation(loc);
        return result;
    }

    loc.pathname = loc.pathname.replace(/[^\/\\]+$/, url);
    var result = reassembleLocation(loc);
    return result;

}

var URL_REGEX = /^((\w+):\/\/)(([^:]+):?([^@]+)?@)?([^\/\?:]*):?(\d+)?(\/?[^\?#]+)?\??([^#]+)?#?(.+)?/;

function parseUrl(url) {
    var fields = ['url', null, 'protocol', null, 'username', 'password', 'host', 'port', 'pathname', 'search', 'hash'];
    var result = URL_REGEX.exec(url);
    if (!result) {
        throw new SeleniumError("Invalid URL: " + url);
    }
    var loc = new Object();
    for (var i = 0; i < fields.length; i++) {
        var field = fields[i];
        if (field == null) {
            continue;
        }
        loc[field] = result[i];
    }
    return loc;
}

function reassembleLocation(loc) {
    if (!loc.protocol) {
        throw new Error("Not a valid location object: " + o2s(loc));
    }
    var protocol = loc.protocol;
    protocol = protocol.replace(/:$/, "");
    var url = protocol + "://";
    if (loc.username) {
        url += loc.username;
        if (loc.password) {
            url += ":" + loc.password;
        }
        url += "@";
    }
    if (loc.host) {
        url += loc.host;
    }

    if (loc.port) {
        url += ":" + loc.port;
    }

    if (loc.pathname) {
        url += loc.pathname;
    }

    if (loc.search) {
        url += "?" + loc.search;
    }
    if (loc.hash) {
        var hash = loc.hash;
        hash = loc.hash.replace(/^#/, "");
        url += "#" + hash;
    }
    return url;
}

function canonicalize(url) {
    if (url == "about:blank") {
        return url;
    }
    var tempLink = window.document.createElement("link");
    tempLink.href = url; 
    var loc = parseUrl(tempLink.href)
    if (!/\/\.\.\//.test(loc.pathname)) {
        return tempLink.href;
    }

    var originalParts = loc.pathname.split("/");
    var newParts = [];
    newParts.push(originalParts.shift());
    for (var i = 0; i < originalParts.length; i++) {
        var part = originalParts[i];
        if (".." == part) {
            newParts.pop();
            continue;
        }
        newParts.push(part);
    }
    loc.pathname = newParts.join("/");
    return reassembleLocation(loc);
}

function extractExceptionMessage(ex) {
    if (ex == null) return "null exception";
    if (ex.message != null) return ex.message;
    if (ex.toString && ex.toString() != null) return ex.toString();
}

var PatternMatcher = function(pattern) {
    this.selectStrategy(pattern);
};
PatternMatcher.prototype = {

    selectStrategy: function(pattern) {
        this.pattern = pattern;
        var strategyName = 'glob';
        if (/^([a-z-]+):(.*)/.test(pattern)) {
            var possibleNewStrategyName = RegExp.$1;
            var possibleNewPattern = RegExp.$2;
            if (PatternMatcher.strategies[possibleNewStrategyName]) {
                strategyName = possibleNewStrategyName;
                pattern = possibleNewPattern;
            }
        }
        var matchStrategy = PatternMatcher.strategies[strategyName];
        if (!matchStrategy) {
            throw new SeleniumError("cannot find PatternMatcher.strategies." + strategyName);
        }
        this.strategy = matchStrategy;
        this.matcher = new matchStrategy(pattern);
    },

    matches: function(actual) {
        return this.matcher.matches(actual + '');
    }

};


PatternMatcher.matches = function(pattern, actual) {
    return new PatternMatcher(pattern).matches(actual);
};

PatternMatcher.strategies = {
    exact: function(expected) {
        this.expected = expected;
        this.matches = function(actual) {
            return actual == this.expected;
        };
    },

    regexp: function(regexpString) {
        this.regexp = new RegExp(regexpString);
        this.matches = function(actual) {
            return this.regexp.test(actual);
        };
    },

    regex: function(regexpString) {
        this.regexp = new RegExp(regexpString);
        this.matches = function(actual) {
            return this.regexp.test(actual);
        };
    },

    regexpi: function(regexpString) {
        this.regexp = new RegExp(regexpString, "i");
        this.matches = function(actual) {
            return this.regexp.test(actual);
        };
    },

    regexi: function(regexpString) {
        this.regexp = new RegExp(regexpString, "i");
        this.matches = function(actual) {
            return this.regexp.test(actual);
        };
    },

    globContains: function(globString) {
        this.regexp = new RegExp(PatternMatcher.regexpFromGlobContains(globString));
        this.matches = function(actual) {
            return this.regexp.test(actual);
        };
    },

    glob: function(globString) {
        this.regexp = new RegExp(PatternMatcher.regexpFromGlob(globString));
        this.matches = function(actual) {
            return this.regexp.test(actual);
        };
    }

};

PatternMatcher.convertGlobMetaCharsToRegexpMetaChars = function(glob) {
    var re = glob;
    re = re.replace(/([.^$+(){}\[\]\\|])/g, "\\$1");
    re = re.replace(/\?/g, "(.|[\r\n])");
    re = re.replace(/\*/g, "(.|[\r\n])*");
    return re;
};

PatternMatcher.regexpFromGlobContains = function(globContains) {
    return PatternMatcher.convertGlobMetaCharsToRegexpMetaChars(globContains);
};

PatternMatcher.regexpFromGlob = function(glob) {
    return "^" + PatternMatcher.convertGlobMetaCharsToRegexpMetaChars(glob) + "$";
};

if (!this["Assert"]) Assert = {};


Assert.fail = function(message) {
    throw new AssertionFailedError(message);
};

Assert.equals = function() {
    var args = new AssertionArguments(arguments);
    if (args.expected === args.actual) {
        return;
    }
    Assert.fail(args.comment +
        "Expected '" + args.expected +
        "' but was '" + args.actual + "'");
};

Assert.assertEquals = Assert.equals;

Assert.matches = function() {
    var args = new AssertionArguments(arguments);
    if (PatternMatcher.matches(args.expected, args.actual)) {
        return;
    }
    Assert.fail(args.comment +
        "Actual value '" + args.actual +
        "' did not match '" + args.expected + "'");
}

Assert.notMatches = function() {
    var args = new AssertionArguments(arguments);
    if (!PatternMatcher.matches(args.expected, args.actual)) {
        return;
    }
    Assert.fail(args.comment +
        "Actual value '" + args.actual +
        "' did match '" + args.expected + "'");
}

function AssertionArguments(args) {
    if (args.length == 2) {
        this.comment = "";
        this.expected = args[0];
        this.actual = args[1];
    } else {
        this.comment = args[0] + "; ";
        this.expected = args[1];
        this.actual = args[2];
    }
}

function AssertionFailedError(message) {
    this.isAssertionFailedError = true;
    this.isSeleniumError = true;
    this.message = message;
    this.failureMessage = message;
}

function SeleniumError(message) {
    var error = new Error(message);
    if (typeof(arguments.caller) != 'undefined') {
        var result = '';
        for (var a = arguments.caller; a != null; a = a.caller) {
            result += '> ' + a.callee.toString() + '\n';
            if (a.caller == a) {
                result += '*';
                break;
            }
        }
        error.stack = result;
    }
    error.isSeleniumError = true;
    return error;
}

function highlight(element) {
    var highLightColor = "yellow";
    var outline = "#8f8 solid 1px"

    if (element.originalColor == undefined) {
        element.originalColor = elementGetStyle(element, "background-color");
    }
    if (element.originalOutline == undefined) {
        element.originalOutline = elementGetStyle(element, "outline");
    }
    elementSetStyle(element, { "backgroundColor": highLightColor });
    elementSetStyle(element, { "outline": outline });
    window.setTimeout(function() {
        try {
            if (!element.parentNode) {
                return;
            }
            elementSetStyle(element, { "backgroundColor": element.originalColor });
            elementSetStyle(element, { "outline": element.originalOutline });
        } catch (e) {}
    }, 200);
}


function o2s(obj) {
    var s = "";
    for (key in obj) {
        var line = key + "->" + obj[key];
        line.replace("\n", " ");
        s += line + "\n";
    }
    return s;
}

var seenReadyStateWarning = false;

function openSeparateApplicationWindow(url, suppressMozillaWarning) {
    window.resizeTo(1200, 500);
    window.moveTo(window.screenX, 0);

    var appWindow = window.open(url + '?start=true', 'selenium_main_app_window');
    if (appWindow == null) {
        var errorMessage = "Couldn't open app window; is the pop-up blocker enabled?";
        throw new Error(errorMessage);
    }
    try {
        var windowHeight = 500;
        if (window.outerHeight) {
            windowHeight = window.outerHeight;
        } else if (document.documentElement && document.documentElement.offsetHeight) {
            windowHeight = document.documentElement.offsetHeight;
        }

        if (window.screenLeft && !window.screenX) window.screenX = window.screenLeft;
        if (window.screenTop && !window.screenY) window.screenY = window.screenTop;

        appWindow.resizeTo(1200, screen.availHeight - windowHeight - 60);
        appWindow.moveTo(window.screenX, window.screenY + windowHeight + 25);
    } catch (e) {
    }


    if (!suppressMozillaWarning && window.document.readyState == null && !seenReadyStateWarning) {
        alert("Beware!  Mozilla bug 300992 means that we can't always reliably detect when a new page has loaded.  Install the Selenium IDE extension or the readyState extension available from selenium.openqa.org to make page load detection more reliable.");
        seenReadyStateWarning = true;
    }

    return appWindow;
}

var URLConfiguration = classCreate();
objectExtend(URLConfiguration.prototype, {
    initialize: function() {},
    _isQueryParameterTrue: function(name) {
        var parameterValue = this._getQueryParameter(name);
        if (parameterValue == null) return false;
        if (parameterValue.toLowerCase() == "true") return true;
        if (parameterValue.toLowerCase() == "on") return true;
        return false;
    },

    _getQueryParameter: function(searchKey) {
        var str = this.queryString
        if (str == null) return null;
        var clauses = str.split('&');
        for (var i = 0; i < clauses.length; i++) {
            var keyValuePair = clauses[i].split('=', 2);
            var key = unescape(keyValuePair[0]);
            if (key == searchKey) {
                return unescape(keyValuePair[1]);
            }
        }
        return null;
    },

    _extractArgs: function() {
        var str = SeleniumHTARunner.commandLine;
        if (str == null || str == "") return new Array();
        var matches = str.match(/(?:\"([^\"]+)\"|(?!\"([^\"]+)\")(\S+))/g);
        var args = new Array;
        for (var i = 0; i < matches.length; i++) {
            args[i] = matches[i];
            args[i] = args[i].replace(/^"(.*)"$/, "$1");
        }
        return args;
    },

    isMultiWindowMode: function() {
        return this._isQueryParameterTrue('multiWindow');
    },

    getBaseUrl: function() {
        return this._getQueryParameter('baseUrl');

    }
});


function safeScrollIntoView(element) {
    if (element.scrollIntoView) {
        element.scrollIntoView(false);
        return;
    }
}

function getTimeoutTime(timeout) {
    var now = new Date().getTime();
    var timeoutLength = parseInt(timeout);

    if (isNaN(timeoutLength)) {
        throw new SeleniumError("Timeout is not a number: '" + timeout + "'");
    }

    return now + timeoutLength;
}

function is_IDE() {
    var locstr = window.location.href;

    if (locstr.indexOf('chrome://selenium-ide-testrunner') == 0) {
        return false;
    }

    return (typeof(SeleniumIDE) != 'undefined');
}

function safe_log(level, msg) {
    try {
    } catch (e) {
    }
}

function safe_alert(msg) {
    if (is_IDE()) {
        alert(msg);
    }
}

function hasJavascriptHref(element) {
    if (getTagName(element) != 'a') {
        return false;
    }
    if (element.getAttribute('onclick')) {
        return false;
    }
    if (!element.href) {
        return false;
    }
    if (!/\s*javascript:/i.test(element.href)) {
        return false;
    }
    return true;
}

function getAncestorOrSelfWithJavascriptHref(element) {
    if (hasJavascriptHref(element)) {
        return element;
    }
    if (element.parentNode == null) {
        return null;
    }
    return getAncestorOrSelfWithJavascriptHref(element.parentNode);
}

function parse_locator(locator) {
    if (locator.includes("d-XPath")) {
        return { type: 'tac', string: locator };
    } else {
        var result = locator.match(/^([A-Za-z]+)=.+/);
        if (result) {
            var type = result[1].toLowerCase();
            var actualLocator = locator.substring(type.length + 1);
            return { type: type, string: actualLocator };
        }
        return { type: 'implicit', string: locator };
    }
}

function XPathEngine() {
    this.doc = null;
    this.isAvailable = function() {
        return false;
    };

    this.setDocument = function(newDocument) {
        this.doc = newDocument;
        return this;
    };

    this.selectNodes = function(xpath, contextNode, namespaceResolver) {
        return [];
    };

    this.selectSingleNode = function(xpath, contextNode, namespaceResolver) {
        var nodes = this.selectNodes(xpath, contextNode, namespaceResolver);
        return (nodes.length > 0 ? nodes[0] : null);
    };

    this.countNodes = function(xpath, contextNode, namespaceResolver) {
        return this.selectNodes(xpath, contextNode, namespaceResolver).length;
    };

    this.setIgnoreAttributesWithoutValue = function(ignore) {
        return this;
    };
}

function NativeEngine() {
    this.isAvailable = function() {
        if (browserVersion && browserVersion.isIE) {
            return false;
        }

        return this.doc && this.doc.evaluate;
    };

    this.selectNodes = function(xpath, contextNode, namespaceResolver) {
        if (contextNode != this.doc) {
            xpath = '.' + xpath;
        }

        var nodes = [];

        try {
            var xpathResult = this.doc.evaluate(xpath, contextNode,
                namespaceResolver, 0, null);
        } catch (e) {
            var msg = extractExceptionMessage(e);
            throw new SeleniumError("Invalid xpath [1]: " + msg);
        } finally {
            if (xpathResult == null) {
                throw new SeleniumError("Invalid xpath [2]: " + xpath);
            }
        }

        var node = xpathResult.iterateNext();

        while (node) {
            nodes.push(node);
            node = xpathResult.iterateNext();
        }

        return nodes;
    };
}

NativeEngine.prototype = new XPathEngine();

function AjaxsltEngine() {
    var ignoreAttributesWithoutValue = false;

    function selectLogic(xpath, contextNode, namespaceResolver, firstMatch) {
        var context;

        if (contextNode == this.doc) {
            context = new ExprContext(this.doc);
        } else {
            context = new ExprContext(contextNode, false, false,
                contextNode.parentNode);
        }

        context.setCaseInsensitive(true);
        context.setIgnoreAttributesWithoutValue(ignoreAttributesWithoutValue);
        context.setReturnOnFirstMatch(firstMatch);

        try {
            var xpathObj = xpathParse(xpath);
        } catch (e) {
            var msg = extractExceptionMessage(e);
            throw new SeleniumError("Invalid xpath [3]: " + msg);
        }

        var nodes = []
        var xpathResult = xpathObj.evaluate(context);

        if (xpathResult && xpathResult.value) {
            for (var i = 0; i < xpathResult.value.length; ++i) {
                nodes.push(xpathResult.value[i]);
            }
        }

        return nodes;
    }

    this.isAvailable = function() {
        return true;
    };

    this.selectNodes = function(xpath, contextNode, namespaceResolver) {
        return selectLogic(xpath, contextNode, namespaceResolver, false);
    };

    this.selectSingleNode = function(xpath, contextNode, namespaceResolver) {
        var nodes = selectLogic(xpath, contextNode, namespaceResolver, true);
        return (nodes.length > 0 ? nodes[0] : null);
    };

    this.setIgnoreAttributesWithoutValue = function(ignore) {
        ignoreAttributesWithoutValue = ignore;
        return this;
    };
}

AjaxsltEngine.prototype = new XPathEngine();

function JavascriptXPathEngine() {

    var engineDoc = document;

    this.isAvailable = function() {
        return true;
    };


    this.selectNodes = function(xpath, contextNode, namespaceResolver) {
        if (contextNode != this.doc) {
            xpath = '.' + xpath;
        }

        var nodes = [];

        try {
            var xpathResult = engineDoc.evaluate(xpath, contextNode,
                namespaceResolver, 0, null);
        } catch (e) {
            var msg = extractExceptionMessage(e);
            throw new SeleniumError("Invalid xpath [1]: " + msg);
        } finally {
            if (xpathResult == null) {
                throw new SeleniumError("Invalid xpath [2]: " + xpath);
            }
        }

        var node = xpathResult.iterateNext();

        while (node) {
            nodes.push(node);
            node = xpathResult.iterateNext();
        }

        return nodes;
    };
}

JavascriptXPathEngine.prototype = new XPathEngine();

function BoundedCache(newMaxSize) {
    var maxSize = newMaxSize;
    var map = {};
    var size = 0;
    var counter = -1;

    this.put = function(key, value) {
        if (map[key]) {
            map[key] = { usage: ++counter, value: value };
        } else {
            map[key] = { usage: ++counter, value: value };
            ++size;

            if (size > maxSize) {
                var minUsage = counter;
                var keyToRemove = key;

                for (var key in map) {
                    if (map[key].usage < minUsage) {
                        minUsage = map[key].usage;
                        keyToRemove = key;
                    }
                }

                this.remove(keyToRemove);
            }
        }
    };

    this.get = function(key) {
        if (map[key]) {
            map[key].usage = ++counter;
            return map[key].value;
        }

        return null;
    };

    this.remove = function(key) {
        if (map[key]) {
            delete map[key];
            --size;

            if (size == 0) {
                counter = -1;
            }
        }
    }

    this.clear = function() {
        map = {};
        size = 0;
        counter = -1;
    };
}

function FinderBuilder(newDocument) {

    var doc = newDocument;

    function buildIdFinder(e) {
        if (e.id) {
            var id = e.id;

            return (function(targetDoc) {
                return targetDoc.getElementById(id);
            });
        }

        return null;
    }

    function buildTagNameFinder(e) {
        var elements = doc.getElementsByTagName(e.tagName);

        for (var i = 0, n = elements.length; i < n; ++i) {
            if (elements[i] === e) {
                return (function(targetDoc) {
                    return targetDoc.getElementsByTagName(e.tagName)[i];
                });
            }
        }

        return null;
    }

    this.setDocument = function(newDocument) {
        doc = newDocument;
        return this;
    };

    this.build = function(e) {
        return (
            buildIdFinder(e) ||
            buildTagNameFinder(e)
        );
    };
}


function MirroredDocument() {

    var originalDoc;
    var reflectionDoc;
    var namespaceResolver;
    var finderBuilder = new FinderBuilder();
    var pastReflections = new BoundedCache(50);
    var jQuery = new JQueryWrapper();

    function appendHTML(html, parentNode) {
        var scripts = jQuery.clean([html], null, parentNode);
    }

    function getHeadHtml(doc) {
        return doc.getElementsByTagName('head')[0].innerHTML;
    }

    function getBodyHtml(doc) {
        return doc.body.innerHTML;
    }

    function copyHead(headHtml, doc) {
        var head = doc.getElementsByTagName('head')[0];

        if (head.innerHTML == headHtml) {
            // the content is already correct
            return;
        }

        jQuery.init(head).empty();

        appendHTML(headHtml, head);
    }

    function copyBody(bodyHtml, doc) {
        if (doc.body.innerHTML == bodyHtml) {
            return;
        }

        jQuery.init(doc.body).empty();

        appendHTML(bodyHtml, doc.body);
    }

    this.setOriginal = function(newOriginalDoc) {
        originalDoc = newOriginalDoc;
        return this;
    };

    this.getOriginal = function() {
        return originalDoc;
    };

    this.setReflection = function(newReflectionDoc) {
        reflectionDoc = newReflectionDoc;
        return this;
    }

    this.getReflection = function() {
        return reflectionDoc;
    };

    this.setNamespaceResolver = function(newNamespaceResolver) {
        namespaceResolver = newNamespaceResolver;
        return this;
    };

    this.reflect = function() {
        if (reflectionDoc == originalDoc) {
            return this;
        }

        var originalHtml = originalDoc.documentElement.innerHTML;
        var pastReflectionHtml = pastReflections.get(originalHtml);

        if (pastReflectionHtml != null &&
            pastReflectionHtml == reflectionDoc.documentElement.innerHTML) {

            return this;
        }

        var headHtml = getHeadHtml(originalDoc);
        var bodyHtml = getBodyHtml(originalDoc);

        try {
            copyHead(headHtml, reflectionDoc);
            copyBody(bodyHtml, reflectionDoc);

            pastReflections.put(originalHtml,
                reflectionDoc.documentElement.innerHTML);
        } catch (e) {
            safe_log('warn', 'Document reflection failed: ' + e.message);
        }

        return this;
    };

    this.getReflectedNode = function(originalNode) {
        if (reflectionDoc == originalDoc) {
            return originalNode;
        }

        if (originalNode == originalDoc) {
            return reflectionDoc;
        }

        var finder = finderBuilder.setDocument(originalDoc).build(originalNode);

        return finder(reflectionDoc) || null;
    };
}


function XPathOptimizationCache(newMaxSize) {
    var cache = new BoundedCache(newMaxSize);
    this.get = function(html, xpath) {
        var byHtml = cache.get(html);

        return byHtml ? byHtml[xpath] : null;
    };

    this.getOrCreate = function(html, xpath) {
        var byHtml = cache.get(html);

        if (byHtml == null) {
            var result = {};
            var optimizations = {};

            optimizations[xpath] = result;
            cache.put(html, optimizations);
            return result;
        }

        var item = byHtml[xpath];

        if (item == null) {
            var result = {};

            byHtml[xpath] = result;
            return result;
        }

        return item;
    };
}

function XPathOptimizer(newEngine) {

    var engine = newEngine;
    var namespaceResolver;
    var mirror = new MirroredDocument(namespaceResolver);
    var finderBuilder = new FinderBuilder();

    var knownOptimizations = new XPathOptimizationCache(100);

    function isOptimizable(node) {
        return (node.nodeType == 1);
    }

   
    function isXPathValid(xpath, node) {
        var contextNode = mirror.getReflection();
        return (engine.setDocument(mirror.getReflection())
            .selectSingleNode(xpath, contextNode, namespaceResolver) === node);
    }


    this.setDocument = function(newDocument) {
        mirror.setOriginal(newDocument);
        return this;
    }

 
    this.setTestDocument = function(newTestDocument) {
        mirror.setReflection(newTestDocument);
        return this;
    };

    this.setNamespaceResolver = function(newNamespaceResolver) {
        namespaceResolver = newNamespaceResolver;
        mirror.setNamespaceResolver(newNamespaceResolver);
        return this;
    };


    this.getOptimizedFinder = function(xpath, contextNode) {
        var originalHtml = mirror.getOriginal().documentElement.innerHTML;
        var optimization = knownOptimizations.get(originalHtml, xpath);

        if (optimization) {
            var finder = optimization.finder;

            if (finder) {
                safe_log('info', 'Found cached optimized finder for ' + xpath);
                return finder;
            }
        }

        mirror.reflect();

        if (contextNode) {
            contextNode = mirror.getReflectedNode(contextNode);
        }

        var firstResult = engine.setDocument(mirror.getReflection())
            .selectSingleNode(xpath, contextNode, namespaceResolver);

        if (!firstResult) {
            return null;
        }

        if (isOptimizable(firstResult)) {
            var finder = finderBuilder.setDocument(mirror.getReflection())
                .build(firstResult);

            if (finder) {
                safe_log('info', 'Found optimized finder: ' + finder);

                if (!optimization) {
                    optimization = knownOptimizations
                        .getOrCreate(originalHtml, xpath);
                }

                optimization.finder = finder;

                return finder;
            }
        }

        return null;
    };

    this.countNodes = function(xpath, contextNode) {
        var originalHtml = mirror.getOriginal().documentElement.innerHTML;
        var optimization = knownOptimizations.get(originalHtml, xpath);

        if (optimization) {
            var nodeCount = optimization.nodeCount;

            if (nodeCount != null) {
                safe_log('info', 'Found cached node count for ' + xpath);
                return nodeCount;
            }
        }

        mirror.reflect();

        if (contextNode) {
            contextNode = mirror.getReflectedNode(contextNode);
        }

        var nodeCount = engine.setDocument(mirror.getReflection())
            .countNodes(xpath, contextNode, namespaceResolver);

        if (!optimization) {
            optimization = knownOptimizations.getOrCreate(originalHtml, xpath);
        }

        optimization.nodeCount = nodeCount;

        return nodeCount;
    };

    this.getKnownOptimizations = function() {
        return knownOptimizations;
    };
}

function MultiWindowRPCOptimizingEngine(newFrameName, newDelegateEngine) {

    var NO_RESULT = '__NO_NODE_RESULT';

    var frameName = newFrameName;
    var engine = newDelegateEngine || new JavascriptXPathEngine();
    var optimizer = new XPathOptimizer(engine);

    function createTestDocument() {
        if (!window.frames[frameName]) {
            var iframe = document.createElement('iframe');

            iframe.id = frameName;
            iframe.name = frameName;
            iframe.width = 0;
            iframe.height = 0;

            document.body.appendChild(iframe);
        }
    }

    function isMultiWindowMode() {
        return (typeof(runOptions) != 'undefined' &&
            runOptions &&
            runOptions.isMultiWindowMode());
    };

    function isDetached(node) {
        while (node = node.parentNode) {
            if (node.nodeType == 11) {
                return true;
            } else if (node.nodeType == 9) {
                return false;
            }
        }

        return true;
    }


    this.isAvailable = function() {
        return engine.isAvailable();
    };

    this.setDocument = function(newDocument) {
        this.doc = newDocument;
        engine.setDocument(newDocument);
        optimizer.setDocument(newDocument);
        return this;
    };


    this.selectNodes = function(xpath, contextNode, namespaceResolver) {
        return engine.selectNodes(xpath, contextNode, namespaceResolver);
    };

    this.selectSingleNode = function(xpath, contextNode, namespaceResolver) {
        var html = this.doc.documentElement.innerHTML;
        var knownOptimizations = optimizer.getKnownOptimizations();
        var optimization = knownOptimizations.get(html, xpath);

        if (optimization) {
            var node = optimization.node;
            var sourceIndex = optimization.sourceIndex;

            if (node == NO_RESULT) {
                return null;
            }

            if (!isDetached(node) && node.sourceIndex == sourceIndex) {
                safe_log('info', 'Found cached node for ' + xpath);
                return node;
            }
        }

        var node;
        var finder = optimizer.setNamespaceResolver(namespaceResolver)
            .setTestDocument(this.getTestDocument())
            .getOptimizedFinder(xpath, contextNode);

        if (finder) {
            node = finder(this.doc);
        } else {
            node = engine.selectSingleNode(xpath, contextNode,
                namespaceResolver);
        }

        if (!optimization) {
            optimization = knownOptimizations.getOrCreate(html, xpath);
        }

        if (node) {
            optimization.node = node;
            optimization.sourceIndex = node.sourceIndex;
        } else {
            optimization.node = NO_RESULT;
        }

        return node;
    };


    this.countNodes = function(xpath, contextNode, namespaceResolver) {
        return optimizer.setNamespaceResolver(namespaceResolver)
            .setTestDocument(this.getTestDocument())
            .countNodes(xpath, contextNode);
    };


    this.setIgnoreAttributesWithoutValue = function(ignore) {
        engine.setIgnoreAttributesWithoutValue(ignore);
        return this;
    };

    this.getTestDocument = function() {
        return (isMultiWindowMode() ? window.frames[frameName].document : this.doc);
    };

    if (isMultiWindowMode()) {
        createTestDocument();
    }
}

MultiWindowRPCOptimizingEngine.prototype = new XPathEngine();

function XPathEvaluator(newDefaultEngineName) {

    var nativeEngine = new NativeEngine();
    var defaultEngineName = newDefaultEngineName || 'ajaxslt';
    var engines = {
        'ajaxslt': new AjaxsltEngine(),
        'javascript-xpath': new JavascriptXPathEngine(),
        'rpc-optimizing-ajaxslt': new MultiWindowRPCOptimizingEngine('test-doc-frame', new AjaxsltEngine()),
        'rpc-optimizing-jsxpath': new MultiWindowRPCOptimizingEngine('test-doc-frame', new JavascriptXPathEngine()),
        'native': nativeEngine
    };

    var currentEngineName = defaultEngineName;
    var allowNativeXPath = true;
    var ignoreAttributesWithoutValue = true;

    function preprocess(xpath) {
        if (xpath.charAt(xpath.length - 1) == '/') {
            xpath = xpath.slice(0, -1);
        }

        if (browserVersion && browserVersion.isIE) {
            xpath = xpath.replace(/x:/g, '')
        }

        return xpath;
    }


    function getEngineFor(inDocument) {
        if (allowNativeXPath &&
            nativeEngine.setDocument(inDocument).isAvailable()) {
            return nativeEngine;
        }

        var currentEngine = engines[currentEngineName];

        if (currentEngine &&
            currentEngine.setDocument(inDocument).isAvailable()) {
            return currentEngine;
        }

        return engines[defaultEngineName].setDocument(inDocument);
    }

    function dispatch(methodName, inDocument, xpath, contextNode, namespaceResolver) {
        xpath = preprocess(xpath);

        if (!contextNode) {
            contextNode = inDocument;
        }

        var result = getEngineFor(inDocument)
            .setIgnoreAttributesWithoutValue(ignoreAttributesWithoutValue)[methodName](xpath, contextNode, namespaceResolver);

        return result;
    }

   
    this.registerEngine = function(name, engine) {

        if (name == 'ajaxslt' ||
            name == 'javascript-xpath' ||
            name == 'native' ||
            name == 'default') {
            return false;
        }

        if (!(engine instanceof XPathEngine)) {
            return false;
        }

        engines[name] = engine;
        return true;
    };

    this.getRegisteredEngine = function(name) {
        return engines[name];
    };

    this.setCurrentEngine = function(name) {
        if (name == 'default') {
            currentEngineName = defaultEngineName;
        } else if (!engines[name]) {
            return;
        } else {
            currentEngineName = name;
        }
    };

    this.getCurrentEngine = function() {
        return currentEngineName || defaultEngineName;
    };

    this.setAllowNativeXPath = function(allow) {
        allowNativeXPath = allow;
    };

    this.isAllowNativeXPath = function() {
        return allowNativeXPath;
    };

    this.setIgnoreAttributesWithoutValue = function(ignore) {
        ignoreAttributesWithoutValue = ignore;
    };

    this.isIgnoreAttributesWithoutValue = function() {
        return ignoreAttributesWithoutValue;
    };

    this.selectNodes = function(inDocument, xpath, contextNode, namespaceResolver) {
        return dispatch('selectNodes', inDocument, xpath, contextNode,
            namespaceResolver);
    };

    this.selectSingleNode = function(inDocument, xpath, contextNode, namespaceResolver) {
        return dispatch('selectSingleNode', inDocument, xpath, contextNode,
            namespaceResolver);
    };

    this.countNodes = function(inDocument, xpath, contextNode, namespaceResolver) {
        return dispatch('countNodes', inDocument, xpath, contextNode,
            namespaceResolver);
    };

    // initialization
    this.init();
};

XPathEvaluator.prototype.init = function() {};

function eval_xpath(xpath, inDocument, opts) {
    if (!opts) {
        var opts = {};
    }

    var contextNode = opts.contextNode ? opts.contextNode : inDocument;
    var namespaceResolver = opts.namespaceResolver ? opts.namespaceResolver : null;
    var xpathLibrary = opts.xpathLibrary ? opts.xpathLibrary : null;
    var allowNativeXpath = (opts.allowNativeXpath != undefined) ? opts.allowNativeXpath : true;
    var ignoreAttributesWithoutValue = (opts.ignoreAttributesWithoutValue != undefined) ? opts.ignoreAttributesWithoutValue : true;
    var returnOnFirstMatch = (opts.returnOnFirstMatch != undefined) ? opts.returnOnFirstMatch : false;

    if (!eval_xpath.xpathEvaluator) {
        eval_xpath.xpathEvaluator = new XPathEvaluator();
    }

    var xpathEvaluator = eval_xpath.xpathEvaluator;

    xpathEvaluator.setCurrentEngine(xpathLibrary);
    xpathEvaluator.setAllowNativeXPath(allowNativeXpath);
    xpathEvaluator.setIgnoreAttributesWithoutValue(ignoreAttributesWithoutValue);

    if (returnOnFirstMatch) {
        var singleNode = xpathEvaluator.selectSingleNode(inDocument, xpath,
            contextNode, namespaceResolver);

        var results = (singleNode ? [singleNode] : []);
    } else {
        var results = xpathEvaluator.selectNodes(inDocument, xpath, contextNode,
            namespaceResolver);
    }

    return results;
}


function eval_css(locator, inDocument) {
    var results = [];
    try {
        Sizzle(locator, inDocument, results);
    } catch (ignored) {
    }
    return results;
}

function eval_locator(locator, inDocument, opt_contextNode) {
    locator = parse_locator(locator);

    var pageBot;
    if (typeof(selenium) != 'undefined' && selenium != undefined) {
        if (typeof(editor) == 'undefined' || editor.state == 'playing') {
            safe_log('info', 'Trying [' + locator.type + ']: ' + locator.string);
        }
        pageBot = selenium.browserbot;
    } else {
        if (!UI_GLOBAL.mozillaBrowserBot) {
            UI_GLOBAL.mozillaBrowserBot = new MozillaBrowserBot(window)
        }
        pageBot = UI_GLOBAL.mozillaBrowserBot;
    }

    var results = [];

    if (locator.type == 'xpath' || (locator.string.charAt(0) == '/' &&
            locator.type == 'implicit')) {
        results = eval_xpath(locator.string, inDocument, { contextNode: opt_contextNode });
    } else if (locator.type == 'css') {
        results = eval_css(locator.string, inDocument);
    } else {
        var element = pageBot
            .findElementBy(locator.type, locator.string, inDocument);
        if (element != null) {
            results.push(element);
        }
    }

    for (var i = 0; i < results.length; i++) {
        results[i] = core.firefox.unwrap(results[i]);
    }
    return results;
}

RegExp.escape = (function() {
    var specials = [
        '/', '.', '*', '+', '?', '|', '^', '$',
        '(', ')', '[', ']', '{', '}', '\\'
    ];

    var sRE = new RegExp(
        '(\\' + specials.join('|\\') + ')', 'g'
    );

    return function(text) {
        return text.replace(sRE, '\\$1');
    }
})();


function are_equal(a1, a2) {
    if (typeof(a1) != typeof(a2))
        return false;

    switch (typeof(a1)) {
        case 'object':
            // arrays
            if (a1.length) {
                if (a1.length != a2.length)
                    return false;
                for (var i = 0; i < a1.length; ++i) {
                    if (!are_equal(a1[i], a2[i]))
                        return false
                }
            }
            // associative arrays
            else {
                var keys = {};
                for (var key in a1) {
                    keys[key] = true;
                }
                for (var key in a2) {
                    keys[key] = true;
                }
                for (var key in keys) {
                    if (!are_equal(a1[key], a2[key]))
                        return false;
                }
            }
            return true;

        default:
            return a1 == a2;
    }
}


function clone(orig) {
    var copy;
    switch (typeof(orig)) {
        case 'object':
            copy = (orig.length) ? [] : {};
            for (var attr in orig) {
                copy[attr] = clone(orig[attr]);
            }
            break;
        default:
            copy = orig;
            break;
    }
    return copy;
}


function print_r(object, maxDepth, indent) {
    var parentIndent, attr, str = "";
    if (arguments.length == 1) {
        var maxDepth = Number.MAX_VALUE;
    } else {
        maxDepth--;
    }
    if (arguments.length < 3) {
        parentIndent = ''
        var indent = '    ';
    } else {
        parentIndent = indent;
        indent += '    ';
    }

    switch (typeof(object)) {
        case 'object':
            if (object.length != undefined) {
                if (object.length == 0) {
                    str += "Array ()\r\n";
                } else {
                    str += "Array (\r\n";
                    for (var i = 0; i < object.length; ++i) {
                        str += indent + '[' + i + '] => ';
                        if (maxDepth == 0)
                            str += "...\r\n";
                        else
                            str += print_r(object[i], maxDepth, indent);
                    }
                    str += parentIndent + ")\r\n";
                }
            } else {
                str += "Object (\r\n";
                for (attr in object) {
                    str += indent + "[" + attr + "] => ";
                    if (maxDepth == 0)
                        str += "...\r\n";
                    else
                        str += print_r(object[attr], maxDepth, indent);
                }
                str += parentIndent + ")\r\n";
            }
            break;
        case 'boolean':
            str += (object ? 'true' : 'false') + "\r\n";
            break;
        case 'function':
            str += "Function\r\n";
            break;
        default:
            str += object + "\r\n";
            break;

    }
    return str;
}


function keys(object) {
    var keys = [];
    for (var k in object) {
        keys.push(k);
    }
    return keys;
}


function range(start, end) {
    if (arguments.length == 1) {
        var end = start;
        start = 0;
    }

    var r = [];
    if (start < end) {
        while (start != end)
            r.push(start++);
    } else {
        while (start != end)
            r.push(start--);
    }
    return r;
}


function parse_kwargs(kwargs) {
    var args = new Object();
    var pairs = kwargs.split(/,/);
    for (var i = 0; i < pairs.length;) {
        if (i > 0 && pairs[i].indexOf('=') == -1) {
            // the value string contained a comma. Glue the parts back together.
            pairs[i - 1] += ',' + pairs.splice(i, 1)[0];
        } else {
            ++i;
        }
    }
    for (var i = 0; i < pairs.length; ++i) {
        var splits = pairs[i].split(/=/);
        if (splits.length == 1) {
            continue;
        }
        var key = splits.shift();
        var value = splits.join('=');
        args[key.trim()] = value.trim();
    }
    return args;
}

function to_kwargs(args, sortedKeys) {
    var s = '';
    if (!sortedKeys) {
        var sortedKeys = keys(args).sort();
    }
    for (var i = 0; i < sortedKeys.length; ++i) {
        var k = sortedKeys[i];
        if (args[k] != undefined) {
            if (s) {
                s += ', ';
            }
            s += k + '=' + args[k];
        }
    }
    return s;
}


function is_ancestor(node, target) {
    while (target.parentNode) {
        target = target.parentNode;
        if (node == target)
            return true;
    }
    return false;
}

function parseUri(str) {
    var o = parseUri.options,
        m = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
        uri = {},
        i = 14;

    while (i--) uri[o.key[i]] = m[i] || "";

    uri[o.q.name] = {};
    uri[o.key[12]].replace(o.q.parser, function($0, $1, $2) {
        if ($1) uri[o.q.name][$1] = $2;
    });

    return uri;
};

parseUri.options = {
    strictMode: false,
    key: ["source", "protocol", "authority", "userInfo", "user", "password", "host", "port", "relative", "path", "directory", "file", "query", "anchor"],
    q: {
        name: "queryKey",
        parser: /(?:^|&)([^&=]*)=?([^&]*)/g
    },
    parser: {
        strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*):?([^:@]*))?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
        loose: /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*):?([^:@]*))?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
    }
};


(function(window, undefined) {

    var jQuery = function(selector, context) {
            return new jQuery.fn.init(selector, context);
        },

        _jQuery = window.jQuery,

        _$ = window.$,

        document = window.document,

        rootjQuery,
        quickExpr = /^[^<]*(<[\w\W]+>)[^>]*$|^#([\w-]+)$/,

        isSimple = /^.[^:#\[\.,]*$/,

        rnotwhite = /\S/,

        rtrim = /^(\s|\u00A0)+|(\s|\u00A0)+$/g,

        rsingleTag = /^<(\w+)\s*\/?>(?:<\/\1>)?$/,

        // Keep a UserAgent string for use with jQuery.browser
        userAgent = navigator.userAgent,

        // For matching the engine and version of the browser
        browserMatch,

        // Has the ready events already been bound?
        readyBound = false,

        // The functions to execute on DOM ready
        readyList = [],

        // The ready event handler
        DOMContentLoaded,

        // Save a reference to some core methods
        toString = Object.prototype.toString,
        hasOwnProperty = Object.prototype.hasOwnProperty,
        push = Array.prototype.push,
        slice = Array.prototype.slice,
        indexOf = Array.prototype.indexOf;

    jQuery.fn = jQuery.prototype = {
        init: function(selector, context) {
            var match, elem, ret, doc;

            // Handle $(""), $(null), or $(undefined)
            if (!selector) {
                return this;
            }

            // Handle $(DOMElement)
            if (selector.nodeType) {
                this.context = this[0] = selector;
                this.length = 1;
                return this;
            }

            // Handle HTML strings
            if (typeof selector === "string") {
                // Are we dealing with HTML string or an ID?
                match = quickExpr.exec(selector);

                // Verify a match, and that no context was specified for #id
                if (match && (match[1] || !context)) {

                    // HANDLE: $(html) -> $(array)
                    if (match[1]) {
                        doc = (context ? context.ownerDocument || context : document);

                        // If a single string is passed in and it's a single tag
                        // just do a createElement and skip the rest
                        ret = rsingleTag.exec(selector);

                        if (ret) {
                            if (jQuery.isPlainObject(context)) {
                                selector = [document.createElement(ret[1])];
                                jQuery.fn.attr.call(selector, context, true);

                            } else {
                                selector = [doc.createElement(ret[1])];
                            }

                        } else {
                            ret = buildFragment([match[1]], [doc]);
                            selector = (ret.cacheable ? ret.fragment.cloneNode(true) : ret.fragment).childNodes;
                        }

                        // HANDLE: $("#id")
                    } else {
                        elem = document.getElementById(match[2]);

                        if (elem) {
                            // Handle the case where IE and Opera return items
                            // by name instead of ID
                            if (elem.id !== match[2]) {
                                return rootjQuery.find(selector);
                            }

                            // Otherwise, we inject the element directly into the jQuery object
                            this.length = 1;
                            this[0] = elem;
                        }

                        this.context = document;
                        this.selector = selector;
                        return this;
                    }

                    // HANDLE: $("TAG")
                } else if (!context && /^\w+$/.test(selector)) {
                    this.selector = selector;
                    this.context = document;
                    selector = document.getElementsByTagName(selector);

                    // HANDLE: $(expr, $(...))
                } else if (!context || context.jquery) {
                    return (context || rootjQuery).find(selector);

                    // HANDLE: $(expr, context)
                    // (which is just equivalent to: $(context).find(expr)
                } else {
                    return jQuery(context).find(selector);
                }

                // HANDLE: $(function)
                // Shortcut for document ready
            } else if (jQuery.isFunction(selector)) {
                return rootjQuery.ready(selector);
            }

            if (selector.selector !== undefined) {
                this.selector = selector.selector;
                this.context = selector.context;
            }

            return jQuery.isArray(selector) ?
                this.setArray(selector) :
                jQuery.makeArray(selector, this);
        },

        // Start with an empty selector
        selector: "",

        // The current version of jQuery being used
        jquery: "1.4.1",

        // The default length of a jQuery object is 0
        length: 0,

        // The number of elements contained in the matched element set
        size: function() {
            return this.length;
        },

        toArray: function() {
            return slice.call(this, 0);
        },

        // Get the Nth element in the matched element set OR
        // Get the whole matched element set as a clean array
        get: function(num) {
            return num == null ?

                // Return a 'clean' array
                this.toArray() :

                // Return just the object
                (num < 0 ? this.slice(num)[0] : this[num]);
        },

        // Take an array of elements and push it onto the stack
        // (returning the new matched element set)
        pushStack: function(elems, name, selector) {
            // Build a new jQuery matched element set
            var ret = jQuery(elems || null);

            // Add the old object onto the stack (as a reference)
            ret.prevObject = this;

            ret.context = this.context;

            if (name === "find") {
                ret.selector = this.selector + (this.selector ? " " : "") + selector;
            } else if (name) {
                ret.selector = this.selector + "." + name + "(" + selector + ")";
            }

            // Return the newly-formed element set
            return ret;
        },

        // Force the current matched set of elements to become
        // the specified array of elements (destroying the stack in the process)
        // You should use pushStack() in order to do this, but maintain the stack
        setArray: function(elems) {
            // Resetting the length to 0, then using the native Array push
            // is a super-fast way to populate an object with array-like properties
            this.length = 0;
            push.apply(this, elems);

            return this;
        },

        // Execute a callback for every element in the matched set.
        // (You can seed the arguments with an array of args, but this is
        // only used internally.)
        each: function(callback, args) {
            return jQuery.each(this, callback, args);
        },

        ready: function(fn) {
            // Attach the listeners
            jQuery.bindReady();

            // If the DOM is already ready
            if (jQuery.isReady) {
                // Execute the function immediately
                fn.call(document, jQuery);

                // Otherwise, remember the function for later
            } else if (readyList) {
                // Add the function to the wait list
                readyList.push(fn);
            }

            return this;
        },

        eq: function(i) {
            return i === -1 ?
                this.slice(i) :
                this.slice(i, +i + 1);
        },

        first: function() {
            return this.eq(0);
        },

        last: function() {
            return this.eq(-1);
        },

        slice: function() {
            return this.pushStack(slice.apply(this, arguments),
                "slice", slice.call(arguments).join(","));
        },

        map: function(callback) {
            return this.pushStack(jQuery.map(this, function(elem, i) {
                return callback.call(elem, i, elem);
            }));
        },

        end: function() {
            return this.prevObject || jQuery(null);
        },

        // For internal use only.
        // Behaves like an Array's method, not like a jQuery method.
        push: push,
        sort: [].sort,
        splice: [].splice
    };

    // Give the init function the jQuery prototype for later instantiation
    jQuery.fn.init.prototype = jQuery.fn;

    jQuery.extend = jQuery.fn.extend = function() {
        // copy reference to target object
        var target = arguments[0] || {},
            i = 1,
            length = arguments.length,
            deep = false,
            options, name, src, copy;

        // Handle a deep copy situation
        if (typeof target === "boolean") {
            deep = target;
            target = arguments[1] || {};
            // skip the boolean and the target
            i = 2;
        }

        // Handle case when target is a string or something (possible in deep copy)
        if (typeof target !== "object" && !jQuery.isFunction(target)) {
            target = {};
        }

        // extend jQuery itself if only one argument is passed
        if (length === i) {
            target = this;
            --i;
        }

        for (; i < length; i++) {
            // Only deal with non-null/undefined values
            if ((options = arguments[i]) != null) {
                // Extend the base object
                for (name in options) {
                    src = target[name];
                    copy = options[name];

                    // Prevent never-ending loop
                    if (target === copy) {
                        continue;
                    }

                    // Recurse if we're merging object literal values or arrays
                    if (deep && copy && (jQuery.isPlainObject(copy) || jQuery.isArray(copy))) {
                        var clone = src && (jQuery.isPlainObject(src) || jQuery.isArray(src)) ? src : jQuery.isArray(copy) ? [] : {};

                        // Never move original objects, clone them
                        target[name] = jQuery.extend(deep, clone, copy);

                        // Don't bring in undefined values
                    } else if (copy !== undefined) {
                        target[name] = copy;
                    }
                }
            }
        }

        // Return the modified object
        return target;
    };

    jQuery.extend({
        noConflict: function(deep) {
            window.$ = _$;

            if (deep) {
                window.jQuery = _jQuery;
            }

            return jQuery;
        },

        // Is the DOM ready to be used? Set to true once it occurs.
        isReady: false,

        // Handle when the DOM is ready
        ready: function() {
            // Make sure that the DOM is not already loaded
            if (!jQuery.isReady) {
                // Make sure body exists, at least, in case IE gets a little overzealous (ticket #5443).
                if (!document.body) {
                    return setTimeout(jQuery.ready, 13);
                }

                // Remember that the DOM is ready
                jQuery.isReady = true;

                // If there are functions bound, to execute
                if (readyList) {
                    // Execute all of them
                    var fn, i = 0;
                    while ((fn = readyList[i++])) {
                        fn.call(document, jQuery);
                    }

                    // Reset the list of functions
                    readyList = null;
                }

                // Trigger any bound ready events
                if (jQuery.fn.triggerHandler) {
                    jQuery(document).triggerHandler("ready");
                }
            }
        },

        bindReady: function() {
            if (readyBound) {
                return;
            }

            readyBound = true;

            // Catch cases where $(document).ready() is called after the
            // browser event has already occurred.
            if (document.readyState === "complete") {
                return jQuery.ready();
            }

            // Mozilla, Opera and webkit nightlies currently support this event
            if (document.addEventListener) {
                // Use the handy event callback
                document.addEventListener("DOMContentLoaded", DOMContentLoaded, false);

                // A fallback to window.onload, that will always work
                window.addEventListener("load", jQuery.ready, false);

                // If IE event model is used
            } else if (document.attachEvent) {
                // ensure firing before onload,
                // maybe late but safe also for iframes
                document.attachEvent("onreadystatechange", DOMContentLoaded);

                // A fallback to window.onload, that will always work
                window.attachEvent("onload", jQuery.ready);

                // If IE and not a frame
                // continually check to see if the document is ready
                var toplevel = false;

                try {
                    toplevel = window.frameElement == null;
                } catch (e) {}

                if (document.documentElement.doScroll && toplevel) {
                    doScrollCheck();
                }
            }
        },


        isFunction: function(obj) {
            return toString.call(obj) === "[object Function]";
        },

        isArray: function(obj) {
            return toString.call(obj) === "[object Array]";
        },

        isPlainObject: function(obj) {

            if (!obj || toString.call(obj) !== "[object Object]" || obj.nodeType || obj.setInterval) {
                return false;
            }

            // Not own constructor property must be Object
            if (obj.constructor && !hasOwnProperty.call(obj, "constructor") && !hasOwnProperty.call(obj.constructor.prototype, "isPrototypeOf")) {
                return false;
            }

            var key;
            for (key in obj) {}

            return key === undefined || hasOwnProperty.call(obj, key);
        },

        isEmptyObject: function(obj) {
            for (var name in obj) {
                return false;
            }
            return true;
        },

        error: function(msg) {
            throw msg;
        },

        parseJSON: function(data) {
            if (typeof data !== "string" || !data) {
                return null;
            }

            if (/^[\],:{}\s]*$/.test(data.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, "@")
                    .replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, "]")
                    .replace(/(?:^|:|,)(?:\s*\[)+/g, ""))) {

                return window.JSON && window.JSON.parse ?
                    window.JSON.parse(data) :
                    (new Function("return " + data))();

            } else {
                jQuery.error("Invalid JSON: " + data);
            }
        },

        noop: function() {},


        globalEval: function(data) {
            if (data && rnotwhite.test(data)) {
                var head = document.getElementsByTagName("head")[0] || document.documentElement,
                    script = document.createElement("script");

                script.type = "text/javascript";

                if (jQuery.support.scriptEval) {
                    script.appendChild(document.createTextNode(data));
                } else {
                    script.text = data;
                }
                head.insertBefore(script, head.firstChild);
                head.removeChild(script);
            }
        },

        nodeName: function(elem, name) {
            return elem.nodeName && elem.nodeName.toUpperCase() === name.toUpperCase();
        },

        each: function(object, callback, args) {
            var name, i = 0,
                length = object.length,
                isObj = length === undefined || jQuery.isFunction(object);

            if (args) {
                if (isObj) {
                    for (name in object) {
                        if (callback.apply(object[name], args) === false) {
                            break;
                        }
                    }
                } else {
                    for (; i < length;) {
                        if (callback.apply(object[i++], args) === false) {
                            break;
                        }
                    }
                }

                // A special, fast, case for the most common use of each
            } else {
                if (isObj) {
                    for (name in object) {
                        if (callback.call(object[name], name, object[name]) === false) {
                            break;
                        }
                    }
                } else {
                    for (var value = object[0]; i < length && callback.call(value, i, value) !== false; value = object[++i]) {}
                }
            }

            return object;
        },

        trim: function(text) {
            return (text || "").replace(rtrim, "");
        },

        // results is for internal usage only
        makeArray: function(array, results) {
            var ret = results || [];

            if (array != null) {
                if (array.length == null || typeof array === "string" || jQuery.isFunction(array) || (typeof array !== "function" && array.setInterval)) {
                    push.call(ret, array);
                } else {
                    jQuery.merge(ret, array);
                }
            }

            return ret;
        },

        inArray: function(elem, array) {
            if (array.indexOf) {
                return array.indexOf(elem);
            }

            for (var i = 0, length = array.length; i < length; i++) {
                if (array[i] === elem) {
                    return i;
                }
            }

            return -1;
        },

        merge: function(first, second) {
            var i = first.length,
                j = 0;

            if (typeof second.length === "number") {
                for (var l = second.length; j < l; j++) {
                    first[i++] = second[j];
                }
            } else {
                while (second[j] !== undefined) {
                    first[i++] = second[j++];
                }
            }

            first.length = i;

            return first;
        },

        grep: function(elems, callback, inv) {
            var ret = [];

            for (var i = 0, length = elems.length; i < length; i++) {
                if (!inv !== !callback(elems[i], i)) {
                    ret.push(elems[i]);
                }
            }

            return ret;
        },

        map: function(elems, callback, arg) {
            var ret = [],
                value;

            for (var i = 0, length = elems.length; i < length; i++) {
                value = callback(elems[i], i, arg);

                if (value != null) {
                    ret[ret.length] = value;
                }
            }

            return ret.concat.apply([], ret);
        },

        // A global GUID counter for objects
        guid: 1,

        proxy: function(fn, proxy, thisObject) {
            if (arguments.length === 2) {
                if (typeof proxy === "string") {
                    thisObject = fn;
                    fn = thisObject[proxy];
                    proxy = undefined;

                } else if (proxy && !jQuery.isFunction(proxy)) {
                    thisObject = proxy;
                    proxy = undefined;
                }
            }

            if (!proxy && fn) {
                proxy = function() {
                    return fn.apply(thisObject || this, arguments);
                };
            }

            // Set the guid of unique handler to the same of original handler, so it can be removed
            if (fn) {
                proxy.guid = fn.guid = fn.guid || proxy.guid || jQuery.guid++;
            }

            // So proxy can be declared as an argument
            return proxy;
        },


        uaMatch: function(ua) {
            ua = ua.toLowerCase();

            var match = /(webkit)[ \/]([\w.]+)/.exec(ua) ||
                /(msie) ([\w.]+)/.exec(ua) ||
                !/compatible/.test(ua) && /(mozilla)(?:.*? rv:([\w.]+))?/.exec(ua) || [];

            return { browser: match[1] || "", version: match[2] || "0" };
        },

        browser: {}
    });

    browserMatch = jQuery.uaMatch(userAgent);
    if (browserMatch.browser) {
        jQuery.browser[browserMatch.browser] = true;
        jQuery.browser.version = browserMatch.version;
    }

    // Deprecated, use jQuery.browser.webkit instead
    if (jQuery.browser.webkit) {
        jQuery.browser.safari = true;
    }

    if (indexOf) {
        jQuery.inArray = function(elem, array) {
            return indexOf.call(array, elem);
        };
    }

    // All jQuery objects should point back to these
    rootjQuery = jQuery(document);

    // Cleanup functions for the document ready method
    if (document.addEventListener) {
        DOMContentLoaded = function() {
            document.removeEventListener("DOMContentLoaded", DOMContentLoaded, false);
            jQuery.ready();
        };

    } else if (document.attachEvent) {
        DOMContentLoaded = function() {
            // Make sure body exists, at least, in case IE gets a little overzealous (ticket #5443).
            if (document.readyState === "complete") {
                document.detachEvent("onreadystatechange", DOMContentLoaded);
                jQuery.ready();
            }
        };
    }

    // The DOM ready check for Internet Explorer
    function doScrollCheck() {
        if (jQuery.isReady) {
            return;
        }

        try {
            document.documentElement.doScroll("left");
        } catch (error) {
            setTimeout(doScrollCheck, 1);
            return;
        }

        // and execute any waiting functions
        jQuery.ready();
    }

    function evalScript(i, elem) {
        if (elem.src) {
            jQuery.ajax({
                url: elem.src,
                async: false,
                dataType: "script"
            });
        } else {
            jQuery.globalEval(elem.text || elem.textContent || elem.innerHTML || "");
        }

        if (elem.parentNode) {
            elem.parentNode.removeChild(elem);
        }
    }

    function access(elems, key, value, exec, fn, pass) {
        var length = elems.length;

        if (typeof key === "object") {
            for (var k in key) {
                access(elems, k, key[k], exec, fn, value);
            }
            return elems;
        }

        // Setting one attribute
        if (value !== undefined) {
            // Optionally, function values get executed if exec is true
            exec = !pass && exec && jQuery.isFunction(value);

            for (var i = 0; i < length; i++) {
                fn(elems[i], key, exec ? value.call(elems[i], i, fn(elems[i], key)) : value, pass);
            }

            return elems;
        }

        // Getting an attribute
        return length ? fn(elems[0], key) : null;
    }

    function now() {
        return (new Date).getTime();
    }
    (function() {

        jQuery.support = {};

        var root = document.documentElement,
            script = document.createElement("script"),
            div = document.createElement("div"),
            id = "script" + now();

        div.style.display = "none";
        div.innerHTML = "   <link/><table></table><a href='/a' style='color:red;float:left;opacity:.55;'>a</a><input type='checkbox'/>";

        var all = div.getElementsByTagName("*"),
            a = div.getElementsByTagName("a")[0];

        // Can't get basic test support
        if (!all || !all.length || !a) {
            return;
        }

        jQuery.support = {
            // IE strips leading whitespace when .innerHTML is used
            leadingWhitespace: div.firstChild.nodeType === 3,

            // Make sure that tbody elements aren't automatically inserted
            // IE will insert them into empty tables
            tbody: !div.getElementsByTagName("tbody").length,

            // Make sure that link elements get serialized correctly by innerHTML
            // This requires a wrapper element in IE
            htmlSerialize: !!div.getElementsByTagName("link").length,

            // Get the style information from getAttribute
            // (IE uses .cssText insted)
            style: /red/.test(a.getAttribute("style")),

            // Make sure that URLs aren't manipulated
            // (IE normalizes it by default)
            hrefNormalized: a.getAttribute("href") === "/a",

            // Make sure that element opacity exists
            // (IE uses filter instead)
            // Use a regex to work around a WebKit issue. See #5145
            opacity: /^0.55$/.test(a.style.opacity),

            // Verify style float existence
            // (IE uses styleFloat instead of cssFloat)
            cssFloat: !!a.style.cssFloat,

            // Make sure that if no value is specified for a checkbox
            // that it defaults to "on".
            // (WebKit defaults to "" instead)
            checkOn: div.getElementsByTagName("input")[0].value === "on",

            // Make sure that a selected-by-default option has a working selected property.
            // (WebKit defaults to false instead of true, IE too, if it's in an optgroup)
            optSelected: document.createElement("select").appendChild(document.createElement("option")).selected,

            // Will be defined later
            checkClone: false,
            scriptEval: false,
            noCloneEvent: true,
            boxModel: null
        };

        script.type = "text/javascript";
        try {
            script.appendChild(document.createTextNode("window." + id + "=1;"));
        } catch (e) {}

        root.insertBefore(script, root.firstChild);


        if (window[id]) {
            jQuery.support.scriptEval = true;
            delete window[id];
        }

        root.removeChild(script);

        if (div.attachEvent && div.fireEvent) {
            div.attachEvent("onclick", function click() {
                // Cloning a node shouldn't copy over any
                // bound event handlers (IE does this)
                jQuery.support.noCloneEvent = false;
                div.detachEvent("onclick", click);
            });
            div.cloneNode(true).fireEvent("onclick");
        }

        div = document.createElement("div");
        div.innerHTML = "<input type='radio' name='radiotest' checked='checked'/>";

        var fragment = document.createDocumentFragment();
        fragment.appendChild(div.firstChild);

        // WebKit doesn't clone checked state correctly in fragments
        jQuery.support.checkClone = fragment.cloneNode(true).cloneNode(true).lastChild.checked;

        // Figure out if the W3C box model works as expected
        // document.body must exist before we can do this
        jQuery(function() {
            var div = document.createElement("div");
            div.style.width = div.style.paddingLeft = "1px";

            document.body.appendChild(div);
            jQuery.boxModel = jQuery.support.boxModel = div.offsetWidth === 2;
            document.body.removeChild(div).style.display = 'none';
            div = null;
        });

        
        var eventSupported = function(eventName) {
            var el = document.createElement("div");
            eventName = "on" + eventName;

            var isSupported = (eventName in el);
            if (!isSupported) {
                el.setAttribute(eventName, "return;");
                isSupported = typeof el[eventName] === "function";
            }
            el = null;

            return isSupported;
        };

        jQuery.support.submitBubbles = eventSupported("submit");
        jQuery.support.changeBubbles = eventSupported("change");

        // release memory in IE
        root = script = div = all = a = null;
    })();

    jQuery.props = {
        "for": "htmlFor",
        "class": "className",
        readonly: "readOnly",
        maxlength: "maxLength",
        cellspacing: "cellSpacing",
        rowspan: "rowSpan",
        colspan: "colSpan",
        tabindex: "tabIndex",
        usemap: "useMap",
        frameborder: "frameBorder"
    };
    var expando = "jQuery" + now(),
        uuid = 0,
        windowData = {};
    var emptyObject = {};

    jQuery.extend({
        cache: {},

        expando: expando,

        // The following elements throw uncatchable exceptions if you
        // attempt to add expando properties to them.
        noData: {
            "embed": true,
            "object": true,
            "applet": true
        },

        data: function(elem, name, data) {
            if (elem.nodeName && jQuery.noData[elem.nodeName.toLowerCase()]) {
                return;
            }

            elem = elem == window ?
                windowData :
                elem;

            var id = elem[expando],
                cache = jQuery.cache,
                thisCache;

            // Handle the case where there's no name immediately
            if (!name && !id) {
                return null;
            }

            // Compute a unique ID for the element
            if (!id) {
                id = ++uuid;
            }

            // Avoid generating a new cache unless none exists and we
            // want to manipulate it.
            if (typeof name === "object") {
                elem[expando] = id;
                thisCache = cache[id] = jQuery.extend(true, {}, name);
            } else if (cache[id]) {
                thisCache = cache[id];
            } else if (typeof data === "undefined") {
                thisCache = emptyObject;
            } else {
                thisCache = cache[id] = {};
            }

            // Prevent overriding the named cache with undefined values
            if (data !== undefined) {
                elem[expando] = id;
                thisCache[name] = data;
            }

            return typeof name === "string" ? thisCache[name] : thisCache;
        },

        removeData: function(elem, name) {
            if (elem.nodeName && jQuery.noData[elem.nodeName.toLowerCase()]) {
                return;
            }

            elem = elem == window ?
                windowData :
                elem;

            var id = elem[expando],
                cache = jQuery.cache,
                thisCache = cache[id];

            // If we want to remove a specific section of the element's data
            if (name) {
                if (thisCache) {
                    // Remove the section of cache data
                    delete thisCache[name];

                    // If we've removed all the data, remove the element's cache
                    if (jQuery.isEmptyObject(thisCache)) {
                        jQuery.removeData(elem);
                    }
                }

                // Otherwise, we want to remove all of the element's data
            } else {
                // Clean up the element expando
                try {
                    delete elem[expando];
                } catch (e) {
                    // IE has trouble directly removing the expando
                    // but it's ok with using removeAttribute
                    if (elem.removeAttribute) {
                        elem.removeAttribute(expando);
                    }
                }

                // Completely remove the data cache
                delete cache[id];
            }
        }
    });

    jQuery.fn.extend({
        data: function(key, value) {
            if (typeof key === "undefined" && this.length) {
                return jQuery.data(this[0]);

            } else if (typeof key === "object") {
                return this.each(function() {
                    jQuery.data(this, key);
                });
            }

            var parts = key.split(".");
            parts[1] = parts[1] ? "." + parts[1] : "";

            if (value === undefined) {
                var data = this.triggerHandler("getData" + parts[1] + "!", [parts[0]]);

                if (data === undefined && this.length) {
                    data = jQuery.data(this[0], key);
                }
                return data === undefined && parts[1] ?
                    this.data(parts[0]) :
                    data;
            } else {
                return this.trigger("setData" + parts[1] + "!", [parts[0], value]).each(function() {
                    jQuery.data(this, key, value);
                });
            }
        },

        removeData: function(key) {
            return this.each(function() {
                jQuery.removeData(this, key);
            });
        }
    });
    jQuery.extend({
        queue: function(elem, type, data) {
            if (!elem) {
                return;
            }

            type = (type || "fx") + "queue";
            var q = jQuery.data(elem, type);

            // Speed up dequeue by getting out quickly if this is just a lookup
            if (!data) {
                return q || [];
            }

            if (!q || jQuery.isArray(data)) {
                q = jQuery.data(elem, type, jQuery.makeArray(data));

            } else {
                q.push(data);
            }

            return q;
        },

        dequeue: function(elem, type) {
            type = type || "fx";

            var queue = jQuery.queue(elem, type),
                fn = queue.shift();

            // If the fx queue is dequeued, always remove the progress sentinel
            if (fn === "inprogress") {
                fn = queue.shift();
            }

            if (fn) {
                // Add a progress sentinel to prevent the fx queue from being
                // automatically dequeued
                if (type === "fx") {
                    queue.unshift("inprogress");
                }

                fn.call(elem, function() {
                    jQuery.dequeue(elem, type);
                });
            }
        }
    });

    jQuery.fn.extend({
        queue: function(type, data) {
            if (typeof type !== "string") {
                data = type;
                type = "fx";
            }

            if (data === undefined) {
                return jQuery.queue(this[0], type);
            }
            return this.each(function(i, elem) {
                var queue = jQuery.queue(this, type, data);

                if (type === "fx" && queue[0] !== "inprogress") {
                    jQuery.dequeue(this, type);
                }
            });
        },
        dequeue: function(type) {
            return this.each(function() {
                jQuery.dequeue(this, type);
            });
        },

        delay: function(time, type) {
            time = jQuery.fx ? jQuery.fx.speeds[time] || time : time;
            type = type || "fx";

            return this.queue(type, function() {
                var elem = this;
                setTimeout(function() {
                    jQuery.dequeue(elem, type);
                }, time);
            });
        },

        clearQueue: function(type) {
            return this.queue(type || "fx", []);
        }
    });
    var rclass = /[\n\t]/g,
        rspace = /\s+/,
        rreturn = /\r/g,
        rspecialurl = /href|src|style/,
        rtype = /(button|input)/i,
        rfocusable = /(button|input|object|select|textarea)/i,
        rclickable = /^(a|area)$/i,
        rradiocheck = /radio|checkbox/;

    jQuery.fn.extend({
        attr: function(name, value) {
            return access(this, name, value, true, jQuery.attr);
        },

        removeAttr: function(name, fn) {
            return this.each(function() {
                jQuery.attr(this, name, "");
                if (this.nodeType === 1) {
                    this.removeAttribute(name);
                }
            });
        },

        addClass: function(value) {
            if (jQuery.isFunction(value)) {
                return this.each(function(i) {
                    var self = jQuery(this);
                    self.addClass(value.call(this, i, self.attr("class")));
                });
            }

            if (value && typeof value === "string") {
                var classNames = (value || "").split(rspace);

                for (var i = 0, l = this.length; i < l; i++) {
                    var elem = this[i];

                    if (elem.nodeType === 1) {
                        if (!elem.className) {
                            elem.className = value;

                        } else {
                            var className = " " + elem.className + " ";
                            for (var c = 0, cl = classNames.length; c < cl; c++) {
                                if (className.indexOf(" " + classNames[c] + " ") < 0) {
                                    elem.className += " " + classNames[c];
                                }
                            }
                        }
                    }
                }
            }

            return this;
        },

        removeClass: function(value) {
            if (jQuery.isFunction(value)) {
                return this.each(function(i) {
                    var self = jQuery(this);
                    self.removeClass(value.call(this, i, self.attr("class")));
                });
            }

            if ((value && typeof value === "string") || value === undefined) {
                var classNames = (value || "").split(rspace);

                for (var i = 0, l = this.length; i < l; i++) {
                    var elem = this[i];

                    if (elem.nodeType === 1 && elem.className) {
                        if (value) {
                            var className = (" " + elem.className + " ").replace(rclass, " ");
                            for (var c = 0, cl = classNames.length; c < cl; c++) {
                                className = className.replace(" " + classNames[c] + " ", " ");
                            }
                            elem.className = className.substring(1, className.length - 1);

                        } else {
                            elem.className = "";
                        }
                    }
                }
            }

            return this;
        },

        toggleClass: function(value, stateVal) {
            var type = typeof value,
                isBool = typeof stateVal === "boolean";

            if (jQuery.isFunction(value)) {
                return this.each(function(i) {
                    var self = jQuery(this);
                    self.toggleClass(value.call(this, i, self.attr("class"), stateVal), stateVal);
                });
            }

            return this.each(function() {
                if (type === "string") {
                    // toggle individual class names
                    var className, i = 0,
                        self = jQuery(this),
                        state = stateVal,
                        classNames = value.split(rspace);

                    while ((className = classNames[i++])) {
                        // check each className given, space seperated list
                        state = isBool ? state : !self.hasClass(className);
                        self[state ? "addClass" : "removeClass"](className);
                    }

                } else if (type === "undefined" || type === "boolean") {
                    if (this.className) {
                        // store className if set
                        jQuery.data(this, "__className__", this.className);
                    }

                    // toggle whole className
                    this.className = this.className || value === false ? "" : jQuery.data(this, "__className__") || "";
                }
            });
        },

        hasClass: function(selector) {
            var className = " " + selector + " ";
            for (var i = 0, l = this.length; i < l; i++) {
                if ((" " + this[i].className + " ").replace(rclass, " ").indexOf(className) > -1) {
                    return true;
                }
            }

            return false;
        },

        val: function(value) {
            if (value === undefined) {
                var elem = this[0];

                if (elem) {
                    if (jQuery.nodeName(elem, "option")) {
                        return (elem.attributes.value || {}).specified ? elem.value : elem.text;
                    }

                    // We need to handle select boxes special
                    if (jQuery.nodeName(elem, "select")) {
                        var index = elem.selectedIndex,
                            values = [],
                            options = elem.options,
                            one = elem.type === "select-one";

                        // Nothing was selected
                        if (index < 0) {
                            return null;
                        }

                        // Loop through all the selected options
                        for (var i = one ? index : 0, max = one ? index + 1 : options.length; i < max; i++) {
                            var option = options[i];

                            if (option.selected) {
                                // Get the specifc value for the option
                                value = jQuery(option).val();

                                // We don't need an array for one selects
                                if (one) {
                                    return value;
                                }

                                // Multi-Selects return an array
                                values.push(value);
                            }
                        }

                        return values;
                    }

                    // Handle the case where in Webkit "" is returned instead of "on" if a value isn't specified
                    if (rradiocheck.test(elem.type) && !jQuery.support.checkOn) {
                        return elem.getAttribute("value") === null ? "on" : elem.value;
                    }


                    // Everything else, we just grab the value
                    return (elem.value || "").replace(rreturn, "");

                }

                return undefined;
            }

            var isFunction = jQuery.isFunction(value);

            return this.each(function(i) {
                var self = jQuery(this),
                    val = value;

                if (this.nodeType !== 1) {
                    return;
                }

                if (isFunction) {
                    val = value.call(this, i, self.val());
                }

                // Typecast each time if the value is a Function and the appended
                // value is therefore different each time.
                if (typeof val === "number") {
                    val += "";
                }

                if (jQuery.isArray(val) && rradiocheck.test(this.type)) {
                    this.checked = jQuery.inArray(self.val(), val) >= 0;

                } else if (jQuery.nodeName(this, "select")) {
                    var values = jQuery.makeArray(val);

                    jQuery("option", this).each(function() {
                        this.selected = jQuery.inArray(jQuery(this).val(), values) >= 0;
                    });

                    if (!values.length) {
                        this.selectedIndex = -1;
                    }

                } else {
                    this.value = val;
                }
            });
        }
    });

    jQuery.extend({
        attrFn: {
            val: true,
            css: true,
            html: true,
            text: true,
            data: true,
            width: true,
            height: true,
            offset: true
        },

        attr: function(elem, name, value, pass) {
            // don't set attributes on text and comment nodes
            if (!elem || elem.nodeType === 3 || elem.nodeType === 8) {
                return undefined;
            }

            if (pass && name in jQuery.attrFn) {
                return jQuery(elem)[name](value);
            }

            var notxml = elem.nodeType !== 1 || !jQuery.isXMLDoc(elem),
                // Whether we are setting (or getting)
                set = value !== undefined;

            // Try to normalize/fix the name
            name = notxml && jQuery.props[name] || name;

            // Only do all the following if this is a node (faster for style)
            if (elem.nodeType === 1) {
                // These attributes require special treatment
                var special = rspecialurl.test(name);

                // Safari mis-reports the default selected property of an option
                // Accessing the parent's selectedIndex property fixes it
                if (name === "selected" && !jQuery.support.optSelected) {
                    var parent = elem.parentNode;
                    if (parent) {
                        parent.selectedIndex;

                        // Make sure that it also works with optgroups, see #5701
                        if (parent.parentNode) {
                            parent.parentNode.selectedIndex;
                        }
                    }
                }

                // If applicable, access the attribute via the DOM 0 way
                if (name in elem && notxml && !special) {
                    if (set) {
                        // We can't allow the type property to be changed (since it causes problems in IE)
                        if (name === "type" && rtype.test(elem.nodeName) && elem.parentNode) {
                            jQuery.error("type property can't be changed");
                        }

                        elem[name] = value;
                    }

                    // browsers index elements by id/name on forms, give priority to attributes.
                    if (jQuery.nodeName(elem, "form") && elem.getAttributeNode(name)) {
                        return elem.getAttributeNode(name).nodeValue;
                    }

                    
                    if (name === "tabIndex") {
                        var attributeNode = elem.getAttributeNode("tabIndex");

                        return attributeNode && attributeNode.specified ?
                            attributeNode.value :
                            rfocusable.test(elem.nodeName) || rclickable.test(elem.nodeName) && elem.href ?
                            0 :
                            undefined;
                    }

                    return elem[name];
                }

                if (!jQuery.support.style && notxml && name === "style") {
                    if (set) {
                        elem.style.cssText = "" + value;
                    }

                    return elem.style.cssText;
                }

                if (set) {
                    // convert the value to a string (all browsers do this but IE) see #1070
                    elem.setAttribute(name, "" + value);
                }

                var attr = !jQuery.support.hrefNormalized && notxml && special ?
                    // Some attributes require a special call on IE
                    elem.getAttribute(name, 2) :
                    elem.getAttribute(name);

                // Non-existent attributes return null, we normalize to undefined
                return attr === null ? undefined : attr;
            }

            // elem is actually elem.style ... set the style
            // Using attr for specific style information is now deprecated. Use style insead.
            return jQuery.style(elem, name, value);
        }
    });
    var fcleanup = function(nm) {
        return nm.replace(/[^\w\s\.\|`]/g, function(ch) {
            return "\\" + ch;
        });
    };

    jQuery.event = {

        add: function(elem, types, handler, data) {
            if (elem.nodeType === 3 || elem.nodeType === 8) {
                return;
            }

            if (elem.setInterval && (elem !== window && !elem.frameElement)) {
                elem = window;
            }

            // Make sure that the function being executed has a unique ID
            if (!handler.guid) {
                handler.guid = jQuery.guid++;
            }

            // if data is passed, bind to handler
            if (data !== undefined) {
                // Create temporary function pointer to original handler
                var fn = handler;

                // Create unique handler function, wrapped around original handler
                handler = jQuery.proxy(fn);

                // Store data in unique handler
                handler.data = data;
            }

            // Init the element's event structure
            var events = jQuery.data(elem, "events") || jQuery.data(elem, "events", {}),
                handle = jQuery.data(elem, "handle"),
                eventHandle;

            if (!handle) {
                eventHandle = function() {
                    // Handle the second event of a trigger and when
                    // an event is called after a page has unloaded
                    return typeof jQuery !== "undefined" && !jQuery.event.triggered ?
                        jQuery.event.handle.apply(eventHandle.elem, arguments) :
                        undefined;
                };

                handle = jQuery.data(elem, "handle", eventHandle);
            }

            if (!handle) {
                return;
            }


            handle.elem = elem;

            types = types.split(/\s+/);

            var type, i = 0;

            while ((type = types[i++])) {
                // Namespaced event handlers
                var namespaces = type.split(".");
                type = namespaces.shift();

                if (i > 1) {
                    handler = jQuery.proxy(handler);

                    if (data !== undefined) {
                        handler.data = data;
                    }
                }

                handler.type = namespaces.slice(0).sort().join(".");

                // Get the current list of functions bound to this event
                var handlers = events[type],
                    special = this.special[type] || {};

                // Init the event handler queue
                if (!handlers) {
                    handlers = events[type] = {};

                    if (!special.setup || special.setup.call(elem, data, namespaces, handler) === false) {
                        // Bind the global event handler to the element
                        if (elem.addEventListener) {
                            elem.addEventListener(type, handle, false);
                        } else if (elem.attachEvent) {
                            elem.attachEvent("on" + type, handle);
                        }
                    }
                }

                if (special.add) {
                    var modifiedHandler = special.add.call(elem, handler, data, namespaces, handlers);
                    if (modifiedHandler && jQuery.isFunction(modifiedHandler)) {
                        modifiedHandler.guid = modifiedHandler.guid || handler.guid;
                        modifiedHandler.data = modifiedHandler.data || handler.data;
                        modifiedHandler.type = modifiedHandler.type || handler.type;
                        handler = modifiedHandler;
                    }
                }

                // Add the function to the element's handler list
                handlers[handler.guid] = handler;

                // Keep track of which events have been used, for global triggering
                this.global[type] = true;
            }

            // Nullify elem to prevent memory leaks in IE
            elem = null;
        },

        global: {},

        // Detach an event or set of events from an element
        remove: function(elem, types, handler) {
            // don't do events on text and comment nodes
            if (elem.nodeType === 3 || elem.nodeType === 8) {
                return;
            }

            var events = jQuery.data(elem, "events"),
                ret, type, fn;

            if (events) {
                // Unbind all events for the element
                if (types === undefined || (typeof types === "string" && types.charAt(0) === ".")) {
                    for (type in events) {
                        this.remove(elem, type + (types || ""));
                    }
                } else {
                    // types is actually an event object here
                    if (types.type) {
                        handler = types.handler;
                        types = types.type;
                    }

                    // Handle multiple events separated by a space
                    // jQuery(...).unbind("mouseover mouseout", fn);
                    types = types.split(/\s+/);
                    var i = 0;
                    while ((type = types[i++])) {
                        // Namespaced event handlers
                        var namespaces = type.split(".");
                        type = namespaces.shift();
                        var all = !namespaces.length,
                            cleaned = jQuery.map(namespaces.slice(0).sort(), fcleanup),
                            namespace = new RegExp("(^|\\.)" + cleaned.join("\\.(?:.*\\.)?") + "(\\.|$)"),
                            special = this.special[type] || {};

                        if (events[type]) {
                            // remove the given handler for the given type
                            if (handler) {
                                fn = events[type][handler.guid];
                                delete events[type][handler.guid];

                                // remove all handlers for the given type
                            } else {
                                for (var handle in events[type]) {
                                    // Handle the removal of namespaced events
                                    if (all || namespace.test(events[type][handle].type)) {
                                        delete events[type][handle];
                                    }
                                }
                            }

                            if (special.remove) {
                                special.remove.call(elem, namespaces, fn);
                            }

                            // remove generic event handler if no more handlers exist
                            for (ret in events[type]) {
                                break;
                            }
                            if (!ret) {
                                if (!special.teardown || special.teardown.call(elem, namespaces) === false) {
                                    if (elem.removeEventListener) {
                                        elem.removeEventListener(type, jQuery.data(elem, "handle"), false);
                                    } else if (elem.detachEvent) {
                                        elem.detachEvent("on" + type, jQuery.data(elem, "handle"));
                                    }
                                }
                                ret = null;
                                delete events[type];
                            }
                        }
                    }
                }

                // Remove the expando if it's no longer used
                for (ret in events) {
                    break;
                }
                if (!ret) {
                    var handle = jQuery.data(elem, "handle");
                    if (handle) {
                        handle.elem = null;
                    }
                    jQuery.removeData(elem, "events");
                    jQuery.removeData(elem, "handle");
                }
            }
        },

        // bubbling is internal
        trigger: function(event, data, elem /*, bubbling */ ) {
            // Event object or event type
            var type = event.type || event,
                bubbling = arguments[3];

            if (!bubbling) {
                event = typeof event === "object" ?
                    // jQuery.Event object
                    event[expando] ? event :
                    // Object literal
                    jQuery.extend(jQuery.Event(type), event) :
                    // Just the event type (string)
                    jQuery.Event(type);

                if (type.indexOf("!") >= 0) {
                    event.type = type = type.slice(0, -1);
                    event.exclusive = true;
                }

                // Handle a global trigger
                if (!elem) {
                    // Don't bubble custom events when global (to avoid too much overhead)
                    event.stopPropagation();

                    // Only trigger if we've ever bound an event for it
                    if (this.global[type]) {
                        jQuery.each(jQuery.cache, function() {
                            if (this.events && this.events[type]) {
                                jQuery.event.trigger(event, data, this.handle.elem);
                            }
                        });
                    }
                }

                // Handle triggering a single element

                // don't do events on text and comment nodes
                if (!elem || elem.nodeType === 3 || elem.nodeType === 8) {
                    return undefined;
                }

                // Clean up in case it is reused
                event.result = undefined;
                event.target = elem;

                // Clone the incoming data, if any
                data = jQuery.makeArray(data);
                data.unshift(event);
            }

            event.currentTarget = elem;

            // Trigger the event, it is assumed that "handle" is a function
            var handle = jQuery.data(elem, "handle");
            if (handle) {
                handle.apply(elem, data);
            }

            var parent = elem.parentNode || elem.ownerDocument;

            // Trigger an inline bound script
            try {
                if (!(elem && elem.nodeName && jQuery.noData[elem.nodeName.toLowerCase()])) {
                    if (elem["on" + type] && elem["on" + type].apply(elem, data) === false) {
                        event.result = false;
                    }
                }

                // prevent IE from throwing an error for some elements with some event types, see #3533
            } catch (e) {}

            if (!event.isPropagationStopped() && parent) {
                jQuery.event.trigger(event, data, parent, true);

            } else if (!event.isDefaultPrevented()) {
                var target = event.target,
                    old,
                    isClick = jQuery.nodeName(target, "a") && type === "click";

                if (!isClick && !(target && target.nodeName && jQuery.noData[target.nodeName.toLowerCase()])) {
                    try {
                        if (target[type]) {
                            // Make sure that we don't accidentally re-trigger the onFOO events
                            old = target["on" + type];

                            if (old) {
                                target["on" + type] = null;
                            }

                            this.triggered = true;
                            target[type]();
                        }

                        // prevent IE from throwing an error for some elements with some event types, see #3533
                    } catch (e) {}

                    if (old) {
                        target["on" + type] = old;
                    }

                    this.triggered = false;
                }
            }
        },

        handle: function(event) {
            // returned undefined or false
            var all, handlers;

            event = arguments[0] = jQuery.event.fix(event || window.event);
            event.currentTarget = this;

            // Namespaced event handlers
            var namespaces = event.type.split(".");
            event.type = namespaces.shift();

            // Cache this now, all = true means, any handler
            all = !namespaces.length && !event.exclusive;

            var namespace = new RegExp("(^|\\.)" + namespaces.slice(0).sort().join("\\.(?:.*\\.)?") + "(\\.|$)");

            handlers = (jQuery.data(this, "events") || {})[event.type];

            for (var j in handlers) {
                var handler = handlers[j];

                // Filter the functions by class
                if (all || namespace.test(handler.type)) {
                    // Pass in a reference to the handler function itself
                    // So that we can later remove it
                    event.handler = handler;
                    event.data = handler.data;

                    var ret = handler.apply(this, arguments);

                    if (ret !== undefined) {
                        event.result = ret;
                        if (ret === false) {
                            event.preventDefault();
                            event.stopPropagation();
                        }
                    }

                    if (event.isImmediatePropagationStopped()) {
                        break;
                    }

                }
            }

            return event.result;
        },

        props: "altKey attrChange attrName bubbles button cancelable charCode clientX clientY ctrlKey currentTarget data detail eventPhase fromElement handler keyCode layerX layerY metaKey newValue offsetX offsetY originalTarget pageX pageY prevValue relatedNode relatedTarget screenX screenY shiftKey srcElement target toElement view wheelDelta which".split(" "),

        fix: function(event) {
            if (event[expando]) {
                return event;
            }

            // store a copy of the original event object
            // and "clone" to set read-only properties
            var originalEvent = event;
            event = jQuery.Event(originalEvent);

            for (var i = this.props.length, prop; i;) {
                prop = this.props[--i];
                event[prop] = originalEvent[prop];
            }

            // Fix target property, if necessary
            if (!event.target) {
                event.target = event.srcElement || document; // Fixes #1925 where srcElement might not be defined either
            }

            // check if target is a textnode (safari)
            if (event.target.nodeType === 3) {
                event.target = event.target.parentNode;
            }

            // Add relatedTarget, if necessary
            if (!event.relatedTarget && event.fromElement) {
                event.relatedTarget = event.fromElement === event.target ? event.toElement : event.fromElement;
            }

            // Calculate pageX/Y if missing and clientX/Y available
            if (event.pageX == null && event.clientX != null) {
                var doc = document.documentElement,
                    body = document.body;
                event.pageX = event.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc && doc.clientLeft || body && body.clientLeft || 0);
                event.pageY = event.clientY + (doc && doc.scrollTop || body && body.scrollTop || 0) - (doc && doc.clientTop || body && body.clientTop || 0);
            }

            // Add which for key events
            if (!event.which && ((event.charCode || event.charCode === 0) ? event.charCode : event.keyCode)) {
                event.which = event.charCode || event.keyCode;
            }

            // Add metaKey to non-Mac browsers (use ctrl for PC's and Meta for Macs)
            if (!event.metaKey && event.ctrlKey) {
                event.metaKey = event.ctrlKey;
            }

            // Add which for click: 1 === left; 2 === middle; 3 === right
            // Note: button is not normalized, so don't use it
            if (!event.which && event.button !== undefined) {
                event.which = (event.button & 1 ? 1 : (event.button & 2 ? 3 : (event.button & 4 ? 2 : 0)));
            }

            return event;
        },

        // Deprecated, use jQuery.guid instead
        guid: 1E8,

        // Deprecated, use jQuery.proxy instead
        proxy: jQuery.proxy,

        special: {
            ready: {
                // Make sure the ready event is setup
                setup: jQuery.bindReady,
                teardown: jQuery.noop
            },

            live: {
                add: function(proxy, data, namespaces, live) {
                    jQuery.extend(proxy, data || {});

                    proxy.guid += data.selector + data.live;
                    data.liveProxy = proxy;

                    jQuery.event.add(this, data.live, liveHandler, data);

                },

                remove: function(namespaces) {
                    if (namespaces.length) {
                        var remove = 0,
                            name = new RegExp("(^|\\.)" + namespaces[0] + "(\\.|$)");

                        jQuery.each((jQuery.data(this, "events").live || {}), function() {
                            if (name.test(this.type)) {
                                remove++;
                            }
                        });

                        if (remove < 1) {
                            jQuery.event.remove(this, namespaces[0], liveHandler);
                        }
                    }
                },
                special: {}
            },
            beforeunload: {
                setup: function(data, namespaces, fn) {
                    // We only want to do this special case on windows
                    if (this.setInterval) {
                        this.onbeforeunload = fn;
                    }

                    return false;
                },
                teardown: function(namespaces, fn) {
                    if (this.onbeforeunload === fn) {
                        this.onbeforeunload = null;
                    }
                }
            }
        }
    };

    jQuery.Event = function(src) {
        // Allow instantiation without the 'new' keyword
        if (!this.preventDefault) {
            return new jQuery.Event(src);
        }

        // Event object
        if (src && src.type) {
            this.originalEvent = src;
            this.type = src.type;
            // Event type
        } else {
            this.type = src;
        }

        // timeStamp is buggy for some events on Firefox(#3843)
        // So we won't rely on the native value
        this.timeStamp = now();

        // Mark it as fixed
        this[expando] = true;
    };

    function returnFalse() {
        return false;
    }

    function returnTrue() {
        return true;
    }

    jQuery.Event.prototype = {
        preventDefault: function() {
            this.isDefaultPrevented = returnTrue;

            var e = this.originalEvent;
            if (!e) {
                return;
            }

            if (e.preventDefault) {
                e.preventDefault();
            }
            // otherwise set the returnValue property of the original event to false (IE)
            e.returnValue = false;
        },
        stopPropagation: function() {
            this.isPropagationStopped = returnTrue;

            var e = this.originalEvent;
            if (!e) {
                return;
            }
            // if stopPropagation exists run it on the original event
            if (e.stopPropagation) {
                e.stopPropagation();
            }
            // otherwise set the cancelBubble property of the original event to true (IE)
            e.cancelBubble = true;
        },
        stopImmediatePropagation: function() {
            this.isImmediatePropagationStopped = returnTrue;
            this.stopPropagation();
        },
        isDefaultPrevented: returnFalse,
        isPropagationStopped: returnFalse,
        isImmediatePropagationStopped: returnFalse
    };

    var withinElement = function(event) {
            // Check if mouse(over|out) are still within the same parent element
            var parent = event.relatedTarget;

            // Traverse up the tree
            while (parent && parent !== this) {
                // Firefox sometimes assigns relatedTarget a XUL element
                // which we cannot access the parentNode property of
                try {
                    parent = parent.parentNode;

                    // assuming we've left the element since we most likely mousedover a xul element
                } catch (e) {
                    break;
                }
            }

            if (parent !== this) {
                // set the correct event type
                event.type = event.data;

                // handle event if we actually just moused on to a non sub-element
                jQuery.event.handle.apply(this, arguments);
            }

        },

        // In case of event delegation, we only need to rename the event.type,
        // liveHandler will take care of the rest.
        delegate = function(event) {
            event.type = event.data;
            jQuery.event.handle.apply(this, arguments);
        };

    // Create mouseenter and mouseleave events
    jQuery.each({
        mouseenter: "mouseover",
        mouseleave: "mouseout"
    }, function(orig, fix) {
        jQuery.event.special[orig] = {
            setup: function(data) {
                jQuery.event.add(this, fix, data && data.selector ? delegate : withinElement, orig);
            },
            teardown: function(data) {
                jQuery.event.remove(this, fix, data && data.selector ? delegate : withinElement);
            }
        };
    });

    // submit delegation
    if (!jQuery.support.submitBubbles) {

        jQuery.event.special.submit = {
            setup: function(data, namespaces, fn) {
                if (this.nodeName.toLowerCase() !== "form") {
                    jQuery.event.add(this, "click.specialSubmit." + fn.guid, function(e) {
                        var elem = e.target,
                            type = elem.type;

                        if ((type === "submit" || type === "image") && jQuery(elem).closest("form").length) {
                            return trigger("submit", this, arguments);
                        }
                    });

                    jQuery.event.add(this, "keypress.specialSubmit." + fn.guid, function(e) {
                        var elem = e.target,
                            type = elem.type;

                        if ((type === "text" || type === "password") && jQuery(elem).closest("form").length && e.keyCode === 13) {
                            return trigger("submit", this, arguments);
                        }
                    });

                } else {
                    return false;
                }
            },

            remove: function(namespaces, fn) {
                jQuery.event.remove(this, "click.specialSubmit" + (fn ? "." + fn.guid : ""));
                jQuery.event.remove(this, "keypress.specialSubmit" + (fn ? "." + fn.guid : ""));
            }
        };

    }

    if (!jQuery.support.changeBubbles) {

        var formElems = /textarea|input|select/i;

        function getVal(elem) {
            var type = elem.type,
                val = elem.value;

            if (type === "radio" || type === "checkbox") {
                val = elem.checked;

            } else if (type === "select-multiple") {
                val = elem.selectedIndex > -1 ?
                    jQuery.map(elem.options, function(elem) {
                        return elem.selected;
                    }).join("-") :
                    "";

            } else if (elem.nodeName.toLowerCase() === "select") {
                val = elem.selectedIndex;
            }

            return val;
        }

        function testChange(e) {
            var elem = e.target,
                data, val;

            if (!formElems.test(elem.nodeName) || elem.readOnly) {
                return;
            }

            data = jQuery.data(elem, "_change_data");
            val = getVal(elem);

            // the current data will be also retrieved by beforeactivate
            if (e.type !== "focusout" || elem.type !== "radio") {
                jQuery.data(elem, "_change_data", val);
            }

            if (data === undefined || val === data) {
                return;
            }

            if (data != null || val) {
                e.type = "change";
                return jQuery.event.trigger(e, arguments[1], elem);
            }
        }

        jQuery.event.special.change = {
            filters: {
                focusout: testChange,

                click: function(e) {
                    var elem = e.target,
                        type = elem.type;

                    if (type === "radio" || type === "checkbox" || elem.nodeName.toLowerCase() === "select") {
                        return testChange.call(this, e);
                    }
                },

                keydown: function(e) {
                    var elem = e.target,
                        type = elem.type;

                    if ((e.keyCode === 13 && elem.nodeName.toLowerCase() !== "textarea") ||
                        (e.keyCode === 32 && (type === "checkbox" || type === "radio")) ||
                        type === "select-multiple") {
                        return testChange.call(this, e);
                    }
                },


                beforeactivate: function(e) {
                    var elem = e.target;

                    if (elem.nodeName.toLowerCase() === "input" && elem.type === "radio") {
                        jQuery.data(elem, "_change_data", getVal(elem));
                    }
                }
            },
            setup: function(data, namespaces, fn) {
                for (var type in changeFilters) {
                    jQuery.event.add(this, type + ".specialChange." + fn.guid, changeFilters[type]);
                }

                return formElems.test(this.nodeName);
            },
            remove: function(namespaces, fn) {
                for (var type in changeFilters) {
                    jQuery.event.remove(this, type + ".specialChange" + (fn ? "." + fn.guid : ""), changeFilters[type]);
                }

                return formElems.test(this.nodeName);
            }
        };

        var changeFilters = jQuery.event.special.change.filters;

    }

    function trigger(type, elem, args) {
        args[0].type = type;
        return jQuery.event.handle.apply(elem, args);
    }

    // Create "bubbling" focus and blur events
    if (document.addEventListener) {
        jQuery.each({ focus: "focusin", blur: "focusout" }, function(orig, fix) {
            jQuery.event.special[fix] = {
                setup: function() {
                    this.addEventListener(orig, handler, true);
                },
                teardown: function() {
                    this.removeEventListener(orig, handler, true);
                }
            };

            function handler(e) {
                e = jQuery.event.fix(e);
                e.type = fix;
                return jQuery.event.handle.call(this, e);
            }
        });
    }

    jQuery.each(["bind", "one"], function(i, name) {
        jQuery.fn[name] = function(type, data, fn) {
            // Handle object literals
            if (typeof type === "object") {
                for (var key in type) {
                    this[name](key, data, type[key], fn);
                }
                return this;
            }

            if (jQuery.isFunction(data)) {
                fn = data;
                data = undefined;
            }

            var handler = name === "one" ? jQuery.proxy(fn, function(event) {
                jQuery(this).unbind(event, handler);
                return fn.apply(this, arguments);
            }) : fn;

            return type === "unload" && name !== "one" ?
                this.one(type, data, fn) :
                this.each(function() {
                    jQuery.event.add(this, type, handler, data);
                });
        };
    });

    jQuery.fn.extend({
        unbind: function(type, fn) {
            // Handle object literals
            if (typeof type === "object" && !type.preventDefault) {
                for (var key in type) {
                    this.unbind(key, type[key]);
                }
                return this;
            }

            return this.each(function() {
                jQuery.event.remove(this, type, fn);
            });
        },
        trigger: function(type, data) {
            return this.each(function() {
                jQuery.event.trigger(type, data, this);
            });
        },

        triggerHandler: function(type, data) {
            if (this[0]) {
                var event = jQuery.Event(type);
                event.preventDefault();
                event.stopPropagation();
                jQuery.event.trigger(event, data, this[0]);
                return event.result;
            }
        },

        toggle: function(fn) {
            // Save reference to arguments for access in closure
            var args = arguments,
                i = 1;

            // link all the functions, so any of them can unbind this click handler
            while (i < args.length) {
                jQuery.proxy(fn, args[i++]);
            }

            return this.click(jQuery.proxy(fn, function(event) {
                // Figure out which function to execute
                var lastToggle = (jQuery.data(this, "lastToggle" + fn.guid) || 0) % i;
                jQuery.data(this, "lastToggle" + fn.guid, lastToggle + 1);

                // Make sure that clicks stop
                event.preventDefault();

                // and execute the function
                return args[lastToggle].apply(this, arguments) || false;
            }));
        },

        hover: function(fnOver, fnOut) {
            return this.mouseenter(fnOver).mouseleave(fnOut || fnOver);
        }
    });

    jQuery.each(["live", "die"], function(i, name) {
        jQuery.fn[name] = function(types, data, fn) {
            var type, i = 0;

            if (jQuery.isFunction(data)) {
                fn = data;
                data = undefined;
            }

            types = (types || "").split(/\s+/);

            while ((type = types[i++]) != null) {
                type = type === "focus" ? "focusin" : // focus --> focusin
                    type === "blur" ? "focusout" : // blur --> focusout
                    type === "hover" ? types.push("mouseleave") && "mouseenter" : // hover support
                    type;

                if (name === "live") {
                    // bind live handler
                    jQuery(this.context).bind(liveConvert(type, this.selector), {
                        data: data,
                        selector: this.selector,
                        live: type
                    }, fn);

                } else {
                    // unbind live handler
                    jQuery(this.context).unbind(liveConvert(type, this.selector), fn ? { guid: fn.guid + this.selector + type } : null);
                }
            }

            return this;
        }
    });

    function liveHandler(event) {
        var stop, elems = [],
            selectors = [],
            args = arguments,
            related, match, fn, elem, j, i, l, data,
            live = jQuery.extend({}, jQuery.data(this, "events").live);

        // Make sure we avoid non-left-click bubbling in Firefox (#3861)
        if (event.button && event.type === "click") {
            return;
        }

        for (j in live) {
            fn = live[j];
            if (fn.live === event.type ||
                fn.altLive && jQuery.inArray(event.type, fn.altLive) > -1) {

                data = fn.data;
                if (!(data.beforeFilter && data.beforeFilter[event.type] &&
                        !data.beforeFilter[event.type](event))) {
                    selectors.push(fn.selector);
                }
            } else {
                delete live[j];
            }
        }

        match = jQuery(event.target).closest(selectors, event.currentTarget);

        for (i = 0, l = match.length; i < l; i++) {
            for (j in live) {
                fn = live[j];
                elem = match[i].elem;
                related = null;

                if (match[i].selector === fn.selector) {
                    // Those two events require additional checking
                    if (fn.live === "mouseenter" || fn.live === "mouseleave") {
                        related = jQuery(event.relatedTarget).closest(fn.selector)[0];
                    }

                    if (!related || related !== elem) {
                        elems.push({ elem: elem, fn: fn });
                    }
                }
            }
        }

        for (i = 0, l = elems.length; i < l; i++) {
            match = elems[i];
            event.currentTarget = match.elem;
            event.data = match.fn.data;
            if (match.fn.apply(match.elem, args) === false) {
                stop = false;
                break;
            }
        }

        return stop;
    }

    function liveConvert(type, selector) {
        return "live." + (type ? type + "." : "") + selector.replace(/\./g, "`").replace(/ /g, "&");
    }

    jQuery.each(("blur focus focusin focusout load resize scroll unload click dblclick " +
        "mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave " +
        "change select submit keydown keypress keyup error").split(" "), function(i, name) {

        // Handle event binding
        jQuery.fn[name] = function(fn) {
            return fn ? this.bind(name, fn) : this.trigger(name);
        };

        if (jQuery.attrFn) {
            jQuery.attrFn[name] = true;
        }
    });

    // Prevent memory leaks in IE
    // Window isn't included so as not to unbind existing unload events
    // More info:
    //  - http://isaacschlueter.com/2006/10/msie-memory-leaks/
    if (window.attachEvent && !window.addEventListener) {
        window.attachEvent("onunload", function() {
            for (var id in jQuery.cache) {
                if (jQuery.cache[id].handle) {
                    // Try/Catch is to handle iframes being unloaded, see #4280
                    try {
                        jQuery.event.remove(jQuery.cache[id].handle.elem);
                    } catch (e) {}
                }
            }
        });
    }
   
    (function() {

        var chunker = /((?:\((?:\([^()]+\)|[^()]+)+\)|\[(?:\[[^[\]]*\]|['"][^'"]*['"]|[^[\]'"]+)+\]|\\.|[^ >+~,(\[\\]+)+|[>+~])(\s*,\s*)?((?:.|\r|\n)*)/g,
            done = 0,
            toString = Object.prototype.toString,
            hasDuplicate = false,
            baseHasDuplicate = true;

        [0, 0].sort(function() {
            baseHasDuplicate = false;
            return 0;
        });

        var Sizzle = function(selector, context, results, seed) {
            results = results || [];
            var origContext = context = context || document;

            if (context.nodeType !== 1 && context.nodeType !== 9) {
                return [];
            }

            if (!selector || typeof selector !== "string") {
                return results;
            }

            var parts = [],
                m, set, checkSet, extra, prune = true,
                contextXML = isXML(context),
                soFar = selector;

            // Reset the position of the chunker regexp (start from head)
            while ((chunker.exec(""), m = chunker.exec(soFar)) !== null) {
                soFar = m[3];

                parts.push(m[1]);

                if (m[2]) {
                    extra = m[3];
                    break;
                }
            }

            if (parts.length > 1 && origPOS.exec(selector)) {
                if (parts.length === 2 && Expr.relative[parts[0]]) {
                    set = posProcess(parts[0] + parts[1], context);
                } else {
                    set = Expr.relative[parts[0]] ? [context] :
                        Sizzle(parts.shift(), context);

                    while (parts.length) {
                        selector = parts.shift();

                        if (Expr.relative[selector]) {
                            selector += parts.shift();
                        }

                        set = posProcess(selector, set);
                    }
                }
            } else {
                // Take a shortcut and set the context if the root selector is an ID
                // (but not if it'll be faster if the inner selector is an ID)
                if (!seed && parts.length > 1 && context.nodeType === 9 && !contextXML &&
                    Expr.match.ID.test(parts[0]) && !Expr.match.ID.test(parts[parts.length - 1])) {
                    var ret = Sizzle.find(parts.shift(), context, contextXML);
                    context = ret.expr ? Sizzle.filter(ret.expr, ret.set)[0] : ret.set[0];
                }

                if (context) {
                    var ret = seed ? { expr: parts.pop(), set: makeArray(seed) } :
                        Sizzle.find(parts.pop(), parts.length === 1 && (parts[0] === "~" || parts[0] === "+") && context.parentNode ? context.parentNode : context, contextXML);
                    set = ret.expr ? Sizzle.filter(ret.expr, ret.set) : ret.set;

                    if (parts.length > 0) {
                        checkSet = makeArray(set);
                    } else {
                        prune = false;
                    }

                    while (parts.length) {
                        var cur = parts.pop(),
                            pop = cur;

                        if (!Expr.relative[cur]) {
                            cur = "";
                        } else {
                            pop = parts.pop();
                        }

                        if (pop == null) {
                            pop = context;
                        }

                        Expr.relative[cur](checkSet, pop, contextXML);
                    }
                } else {
                    checkSet = parts = [];
                }
            }

            if (!checkSet) {
                checkSet = set;
            }

            if (!checkSet) {
                Sizzle.error(cur || selector);
            }

            if (toString.call(checkSet) === "[object Array]") {
                if (!prune) {
                    results.push.apply(results, checkSet);
                } else if (context && context.nodeType === 1) {
                    for (var i = 0; checkSet[i] != null; i++) {
                        if (checkSet[i] && (checkSet[i] === true || checkSet[i].nodeType === 1 && contains(context, checkSet[i]))) {
                            results.push(set[i]);
                        }
                    }
                } else {
                    for (var i = 0; checkSet[i] != null; i++) {
                        if (checkSet[i] && checkSet[i].nodeType === 1) {
                            results.push(set[i]);
                        }
                    }
                }
            } else {
                makeArray(checkSet, results);
            }

            if (extra) {
                Sizzle(extra, origContext, results, seed);
                Sizzle.uniqueSort(results);
            }

            return results;
        };

        Sizzle.uniqueSort = function(results) {
            if (sortOrder) {
                hasDuplicate = baseHasDuplicate;
                results.sort(sortOrder);

                if (hasDuplicate) {
                    for (var i = 1; i < results.length; i++) {
                        if (results[i] === results[i - 1]) {
                            results.splice(i--, 1);
                        }
                    }
                }
            }

            return results;
        };

        Sizzle.matches = function(expr, set) {
            return Sizzle(expr, null, null, set);
        };

        Sizzle.find = function(expr, context, isXML) {
            var set, match;

            if (!expr) {
                return [];
            }

            for (var i = 0, l = Expr.order.length; i < l; i++) {
                var type = Expr.order[i],
                    match;

                if ((match = Expr.leftMatch[type].exec(expr))) {
                    var left = match[1];
                    match.splice(1, 1);

                    if (left.substr(left.length - 1) !== "\\") {
                        match[1] = (match[1] || "").replace(/\\/g, "");
                        set = Expr.find[type](match, context, isXML);
                        if (set != null) {
                            expr = expr.replace(Expr.match[type], "");
                            break;
                        }
                    }
                }
            }

            if (!set) {
                set = context.getElementsByTagName("*");
            }

            return { set: set, expr: expr };
        };

        Sizzle.filter = function(expr, set, inplace, not) {
            var old = expr,
                result = [],
                curLoop = set,
                match, anyFound,
                isXMLFilter = set && set[0] && isXML(set[0]);

            while (expr && set.length) {
                for (var type in Expr.filter) {
                    if ((match = Expr.leftMatch[type].exec(expr)) != null && match[2]) {
                        var filter = Expr.filter[type],
                            found, item, left = match[1];
                        anyFound = false;

                        match.splice(1, 1);

                        if (left.substr(left.length - 1) === "\\") {
                            continue;
                        }

                        if (curLoop === result) {
                            result = [];
                        }

                        if (Expr.preFilter[type]) {
                            match = Expr.preFilter[type](match, curLoop, inplace, result, not, isXMLFilter);

                            if (!match) {
                                anyFound = found = true;
                            } else if (match === true) {
                                continue;
                            }
                        }

                        if (match) {
                            for (var i = 0;
                                (item = curLoop[i]) != null; i++) {
                                if (item) {
                                    found = filter(item, match, i, curLoop);
                                    var pass = not ^ !!found;

                                    if (inplace && found != null) {
                                        if (pass) {
                                            anyFound = true;
                                        } else {
                                            curLoop[i] = false;
                                        }
                                    } else if (pass) {
                                        result.push(item);
                                        anyFound = true;
                                    }
                                }
                            }
                        }

                        if (found !== undefined) {
                            if (!inplace) {
                                curLoop = result;
                            }

                            expr = expr.replace(Expr.match[type], "");

                            if (!anyFound) {
                                return [];
                            }

                            break;
                        }
                    }
                }

                // Improper expression
                if (expr === old) {
                    if (anyFound == null) {
                        Sizzle.error(expr);
                    } else {
                        break;
                    }
                }

                old = expr;
            }

            return curLoop;
        };

        Sizzle.error = function(msg) {
            throw "Syntax error, unrecognized expression: " + msg;
        };

        var Expr = Sizzle.selectors = {
            order: ["ID", "NAME", "TAG"],
            match: {
                ID: /#((?:[\w\u00c0-\uFFFF-]|\\.)+)/,
                CLASS: /\.((?:[\w\u00c0-\uFFFF-]|\\.)+)/,
                NAME: /\[name=['"]*((?:[\w\u00c0-\uFFFF-]|\\.)+)['"]*\]/,
                ATTR: /\[\s*((?:[\w\u00c0-\uFFFF-]|\\.)+)\s*(?:(\S?=)\s*(['"]*)(.*?)\3|)\s*\]/,
                TAG: /^((?:[\w\u00c0-\uFFFF\*-]|\\.)+)/,
                CHILD: /:(only|nth|last|first)-child(?:\((even|odd|[\dn+-]*)\))?/,
                POS: /:(nth|eq|gt|lt|first|last|even|odd)(?:\((\d*)\))?(?=[^-]|$)/,
                PSEUDO: /:((?:[\w\u00c0-\uFFFF-]|\\.)+)(?:\((['"]?)((?:\([^\)]+\)|[^\(\)]*)+)\2\))?/
            },
            leftMatch: {},
            attrMap: {
                "class": "className",
                "for": "htmlFor"
            },
            attrHandle: {
                href: function(elem) {
                    return elem.getAttribute("href");
                }
            },
            relative: {
                "+": function(checkSet, part) {
                    var isPartStr = typeof part === "string",
                        isTag = isPartStr && !/\W/.test(part),
                        isPartStrNotTag = isPartStr && !isTag;

                    if (isTag) {
                        part = part.toLowerCase();
                    }

                    for (var i = 0, l = checkSet.length, elem; i < l; i++) {
                        if ((elem = checkSet[i])) {
                            while ((elem = elem.previousSibling) && elem.nodeType !== 1) {}

                            checkSet[i] = isPartStrNotTag || elem && elem.nodeName.toLowerCase() === part ?
                                elem || false :
                                elem === part;
                        }
                    }

                    if (isPartStrNotTag) {
                        Sizzle.filter(part, checkSet, true);
                    }
                },
                ">": function(checkSet, part) {
                    var isPartStr = typeof part === "string";

                    if (isPartStr && !/\W/.test(part)) {
                        part = part.toLowerCase();

                        for (var i = 0, l = checkSet.length; i < l; i++) {
                            var elem = checkSet[i];
                            if (elem) {
                                var parent = elem.parentNode;
                                checkSet[i] = parent.nodeName.toLowerCase() === part ? parent : false;
                            }
                        }
                    } else {
                        for (var i = 0, l = checkSet.length; i < l; i++) {
                            var elem = checkSet[i];
                            if (elem) {
                                checkSet[i] = isPartStr ?
                                    elem.parentNode :
                                    elem.parentNode === part;
                            }
                        }

                        if (isPartStr) {
                            Sizzle.filter(part, checkSet, true);
                        }
                    }
                },
                "": function(checkSet, part, isXML) {
                    var doneName = done++,
                        checkFn = dirCheck;

                    if (typeof part === "string" && !/\W/.test(part)) {
                        var nodeCheck = part = part.toLowerCase();
                        checkFn = dirNodeCheck;
                    }

                    checkFn("parentNode", part, doneName, checkSet, nodeCheck, isXML);
                },
                "~": function(checkSet, part, isXML) {
                    var doneName = done++,
                        checkFn = dirCheck;

                    if (typeof part === "string" && !/\W/.test(part)) {
                        var nodeCheck = part = part.toLowerCase();
                        checkFn = dirNodeCheck;
                    }

                    checkFn("previousSibling", part, doneName, checkSet, nodeCheck, isXML);
                }
            },
            find: {
                ID: function(match, context, isXML) {
                    if (typeof context.getElementById !== "undefined" && !isXML) {
                        var m = context.getElementById(match[1]);
                        return m ? [m] : [];
                    }
                },
                NAME: function(match, context) {
                    if (typeof context.getElementsByName !== "undefined") {
                        var ret = [],
                            results = context.getElementsByName(match[1]);

                        for (var i = 0, l = results.length; i < l; i++) {
                            if (results[i].getAttribute("name") === match[1]) {
                                ret.push(results[i]);
                            }
                        }

                        return ret.length === 0 ? null : ret;
                    }
                },
                TAG: function(match, context) {
                    return context.getElementsByTagName(match[1]);
                }
            },
            preFilter: {
                CLASS: function(match, curLoop, inplace, result, not, isXML) {
                    match = " " + match[1].replace(/\\/g, "") + " ";

                    if (isXML) {
                        return match;
                    }

                    for (var i = 0, elem;
                        (elem = curLoop[i]) != null; i++) {
                        if (elem) {
                            if (not ^ (elem.className && (" " + elem.className + " ").replace(/[\t\n]/g, " ").indexOf(match) >= 0)) {
                                if (!inplace) {
                                    result.push(elem);
                                }
                            } else if (inplace) {
                                curLoop[i] = false;
                            }
                        }
                    }

                    return false;
                },
                ID: function(match) {
                    return match[1].replace(/\\/g, "");
                },
                TAG: function(match, curLoop) {
                    return match[1].toLowerCase();
                },
                CHILD: function(match) {
                    if (match[1] === "nth") {
                        // parse equations like 'even', 'odd', '5', '2n', '3n+2', '4n-1', '-n+6'
                        var test = /(-?)(\d*)n((?:\+|-)?\d*)/.exec(
                            match[2] === "even" && "2n" || match[2] === "odd" && "2n+1" ||
                            !/\D/.test(match[2]) && "0n+" + match[2] || match[2]);

                        // calculate the numbers (first)n+(last) including if they are negative
                        match[2] = (test[1] + (test[2] || 1)) - 0;
                        match[3] = test[3] - 0;
                    }

                    // TODO: Move to normal caching system
                    match[0] = done++;

                    return match;
                },
                ATTR: function(match, curLoop, inplace, result, not, isXML) {
                    var name = match[1].replace(/\\/g, "");

                    if (!isXML && Expr.attrMap[name]) {
                        match[1] = Expr.attrMap[name];
                    }

                    if (match[2] === "~=") {
                        match[4] = " " + match[4] + " ";
                    }

                    return match;
                },
                PSEUDO: function(match, curLoop, inplace, result, not) {
                    if (match[1] === "not") {
                        // If we're dealing with a complex expression, or a simple one
                        if ((chunker.exec(match[3]) || "").length > 1 || /^\w/.test(match[3])) {
                            match[3] = Sizzle(match[3], null, null, curLoop);
                        } else {
                            var ret = Sizzle.filter(match[3], curLoop, inplace, true ^ not);
                            if (!inplace) {
                                result.push.apply(result, ret);
                            }
                            return false;
                        }
                    } else if (Expr.match.POS.test(match[0]) || Expr.match.CHILD.test(match[0])) {
                        return true;
                    }

                    return match;
                },
                POS: function(match) {
                    match.unshift(true);
                    return match;
                }
            },
            filters: {
                enabled: function(elem) {
                    return elem.disabled === false && elem.type !== "hidden";
                },
                disabled: function(elem) {
                    return elem.disabled === true;
                },
                checked: function(elem) {
                    return elem.checked === true;
                },
                selected: function(elem) {
                    elem.parentNode.selectedIndex;
                    return elem.selected === true;
                },
                parent: function(elem) {
                    return !!elem.firstChild;
                },
                empty: function(elem) {
                    return !elem.firstChild;
                },
                has: function(elem, i, match) {
                    return !!Sizzle(match[3], elem).length;
                },
                header: function(elem) {
                    return /h\d/i.test(elem.nodeName);
                },
                text: function(elem) {
                    return "text" === elem.type;
                },
                radio: function(elem) {
                    return "radio" === elem.type;
                },
                checkbox: function(elem) {
                    return "checkbox" === elem.type;
                },
                file: function(elem) {
                    return "file" === elem.type;
                },
                password: function(elem) {
                    return "password" === elem.type;
                },
                submit: function(elem) {
                    return "submit" === elem.type;
                },
                image: function(elem) {
                    return "image" === elem.type;
                },
                reset: function(elem) {
                    return "reset" === elem.type;
                },
                button: function(elem) {
                    return "button" === elem.type || elem.nodeName.toLowerCase() === "button";
                },
                input: function(elem) {
                    return /input|select|textarea|button/i.test(elem.nodeName);
                }
            },
            setFilters: {
                first: function(elem, i) {
                    return i === 0;
                },
                last: function(elem, i, match, array) {
                    return i === array.length - 1;
                },
                even: function(elem, i) {
                    return i % 2 === 0;
                },
                odd: function(elem, i) {
                    return i % 2 === 1;
                },
                lt: function(elem, i, match) {
                    return i < match[3] - 0;
                },
                gt: function(elem, i, match) {
                    return i > match[3] - 0;
                },
                nth: function(elem, i, match) {
                    return match[3] - 0 === i;
                },
                eq: function(elem, i, match) {
                    return match[3] - 0 === i;
                }
            },
            filter: {
                PSEUDO: function(elem, match, i, array) {
                    var name = match[1],
                        filter = Expr.filters[name];

                    if (filter) {
                        return filter(elem, i, match, array);
                    } else if (name === "contains") {
                        return (elem.textContent || elem.innerText || getText([elem]) || "").indexOf(match[3]) >= 0;
                    } else if (name === "not") {
                        var not = match[3];

                        for (var i = 0, l = not.length; i < l; i++) {
                            if (not[i] === elem) {
                                return false;
                            }
                        }

                        return true;
                    } else {
                        Sizzle.error("Syntax error, unrecognized expression: " + name);
                    }
                },
                CHILD: function(elem, match) {
                    var type = match[1],
                        node = elem;
                    switch (type) {
                        case 'only':
                        case 'first':
                            while ((node = node.previousSibling)) {
                                if (node.nodeType === 1) {
                                    return false;
                                }
                            }
                            if (type === "first") {
                                return true;
                            }
                            node = elem;
                        case 'last':
                            while ((node = node.nextSibling)) {
                                if (node.nodeType === 1) {
                                    return false;
                                }
                            }
                            return true;
                        case 'nth':
                            var first = match[2],
                                last = match[3];

                            if (first === 1 && last === 0) {
                                return true;
                            }

                            var doneName = match[0],
                                parent = elem.parentNode;

                            if (parent && (parent.sizcache !== doneName || !elem.nodeIndex)) {
                                var count = 0;
                                for (node = parent.firstChild; node; node = node.nextSibling) {
                                    if (node.nodeType === 1) {
                                        node.nodeIndex = ++count;
                                    }
                                }
                                parent.sizcache = doneName;
                            }

                            var diff = elem.nodeIndex - last;
                            if (first === 0) {
                                return diff === 0;
                            } else {
                                return (diff % first === 0 && diff / first >= 0);
                            }
                    }
                },
                ID: function(elem, match) {
                    return elem.nodeType === 1 && elem.getAttribute("id") === match;
                },
                TAG: function(elem, match) {
                    return (match === "*" && elem.nodeType === 1) || elem.nodeName.toLowerCase() === match;
                },
                CLASS: function(elem, match) {
                    return (" " + (elem.className || elem.getAttribute("class")) + " ")
                        .indexOf(match) > -1;
                },
                ATTR: function(elem, match) {
                    var name = match[1],
                        result = Expr.attrHandle[name] ?
                        Expr.attrHandle[name](elem) :
                        elem[name] != null ?
                        elem[name] :
                        elem.getAttribute(name),
                        value = result + "",
                        type = match[2],
                        check = match[4];

                    return result == null ?
                        type === "!=" :
                        type === "=" ?
                        value === check :
                        type === "*=" ?
                        value.indexOf(check) >= 0 :
                        type === "~=" ?
                        (" " + value + " ").indexOf(check) >= 0 :
                        !check ?
                        value && result !== false :
                        type === "!=" ?
                        value !== check :
                        type === "^=" ?
                        value.indexOf(check) === 0 :
                        type === "$=" ?
                        value.substr(value.length - check.length) === check :
                        type === "|=" ?
                        value === check || value.substr(0, check.length + 1) === check + "-" :
                        false;
                },
                POS: function(elem, match, i, array) {
                    var name = match[2],
                        filter = Expr.setFilters[name];

                    if (filter) {
                        return filter(elem, i, match, array);
                    }
                }
            }
        };

        var origPOS = Expr.match.POS;

        for (var type in Expr.match) {
            Expr.match[type] = new RegExp(Expr.match[type].source + /(?![^\[]*\])(?![^\(]*\))/.source);
            Expr.leftMatch[type] = new RegExp(/(^(?:.|\r|\n)*?)/.source + Expr.match[type].source.replace(/\\(\d+)/g, function(all, num) {
                return "\\" + (num - 0 + 1);
            }));
        }

        var makeArray = function(array, results) {
            array = Array.prototype.slice.call(array, 0);

            if (results) {
                results.push.apply(results, array);
                return results;
            }

            return array;
        };

        try {
            Array.prototype.slice.call(document.documentElement.childNodes, 0);

            // Provide a fallback method if it does not work
        } catch (e) {
            makeArray = function(array, results) {
                var ret = results || [];

                if (toString.call(array) === "[object Array]") {
                    Array.prototype.push.apply(ret, array);
                } else {
                    if (typeof array.length === "number") {
                        for (var i = 0, l = array.length; i < l; i++) {
                            ret.push(array[i]);
                        }
                    } else {
                        for (var i = 0; array[i]; i++) {
                            ret.push(array[i]);
                        }
                    }
                }

                return ret;
            };
        }

        var sortOrder;

        if (document.documentElement.compareDocumentPosition) {
            sortOrder = function(a, b) {
                if (!a.compareDocumentPosition || !b.compareDocumentPosition) {
                    if (a == b) {
                        hasDuplicate = true;
                    }
                    return a.compareDocumentPosition ? -1 : 1;
                }

                var ret = a.compareDocumentPosition(b) & 4 ? -1 : a === b ? 0 : 1;
                if (ret === 0) {
                    hasDuplicate = true;
                }
                return ret;
            };
        } else if ("sourceIndex" in document.documentElement) {
            sortOrder = function(a, b) {
                if (!a.sourceIndex || !b.sourceIndex) {
                    if (a == b) {
                        hasDuplicate = true;
                    }
                    return a.sourceIndex ? -1 : 1;
                }

                var ret = a.sourceIndex - b.sourceIndex;
                if (ret === 0) {
                    hasDuplicate = true;
                }
                return ret;
            };
        } else if (document.createRange) {
            sortOrder = function(a, b) {
                if (!a.ownerDocument || !b.ownerDocument) {
                    if (a == b) {
                        hasDuplicate = true;
                    }
                    return a.ownerDocument ? -1 : 1;
                }

                var aRange = a.ownerDocument.createRange(),
                    bRange = b.ownerDocument.createRange();
                aRange.setStart(a, 0);
                aRange.setEnd(a, 0);
                bRange.setStart(b, 0);
                bRange.setEnd(b, 0);
                var ret = aRange.compareBoundaryPoints(Range.START_TO_END, bRange);
                if (ret === 0) {
                    hasDuplicate = true;
                }
                return ret;
            };
        }

        // Utility function for retreiving the text value of an array of DOM nodes
        function getText(elems) {
            var ret = "",
                elem;

            for (var i = 0; elems[i]; i++) {
                elem = elems[i];

                // Get the text from text nodes and CDATA nodes
                if (elem.nodeType === 3 || elem.nodeType === 4) {
                    ret += elem.nodeValue;

                    // Traverse everything else, except comment nodes
                } else if (elem.nodeType !== 8) {
                    ret += getText(elem.childNodes);
                }
            }

            return ret;
        }

        // Check to see if the browser returns elements by name when
        // querying by getElementById (and provide a workaround)
        (function() {
            // We're going to inject a fake input element with a specified name
            var form = document.createElement("div"),
                id = "script" + (new Date).getTime();
            form.innerHTML = "<a name='" + id + "'/>";

            // Inject it into the root element, check its status, and remove it quickly
            var root = document.documentElement;
            root.insertBefore(form, root.firstChild);

            if (document.getElementById(id)) {
                Expr.find.ID = function(match, context, isXML) {
                    if (typeof context.getElementById !== "undefined" && !isXML) {
                        var m = context.getElementById(match[1]);
                        return m ? m.id === match[1] || typeof m.getAttributeNode !== "undefined" && m.getAttributeNode("id").nodeValue === match[1] ? [m] : undefined : [];
                    }
                };

                Expr.filter.ID = function(elem, match) {
                    var node = typeof elem.getAttributeNode !== "undefined" && elem.getAttributeNode("id");
                    return elem.nodeType === 1 && node && node.nodeValue === match;
                };
            }

            root.removeChild(form);
            root = form = null; // release memory in IE
        })();

        (function() {
            // Check to see if the browser returns only elements
            // when doing getElementsByTagName("*")

            // Create a fake element
            var div = document.createElement("div");
            div.appendChild(document.createComment(""));

            // Make sure no comments are found
            if (div.getElementsByTagName("*").length > 0) {
                Expr.find.TAG = function(match, context) {
                    var results = context.getElementsByTagName(match[1]);

                    // Filter out possible comments
                    if (match[1] === "*") {
                        var tmp = [];

                        for (var i = 0; results[i]; i++) {
                            if (results[i].nodeType === 1) {
                                tmp.push(results[i]);
                            }
                        }

                        results = tmp;
                    }

                    return results;
                };
            }

            // Check to see if an attribute returns normalized href attributes
            div.innerHTML = "<a href='#'></a>";
            if (div.firstChild && typeof div.firstChild.getAttribute !== "undefined" &&
                div.firstChild.getAttribute("href") !== "#") {
                Expr.attrHandle.href = function(elem) {
                    return elem.getAttribute("href", 2);
                };
            }

            div = null; // release memory in IE
        })();

        if (document.querySelectorAll) {
            (function() {
                var oldSizzle = Sizzle,
                    div = document.createElement("div");
                div.innerHTML = "<p class='TEST'></p>";

                // Safari can't handle uppercase or unicode characters when
                // in quirks mode.
                if (div.querySelectorAll && div.querySelectorAll(".TEST").length === 0) {
                    return;
                }

                Sizzle = function(query, context, extra, seed) {
                    context = context || document;

                    // Only use querySelectorAll on non-XML documents
                    // (ID selectors don't work in non-HTML documents)
                    if (!seed && context.nodeType === 9 && !isXML(context)) {
                        try {
                            return makeArray(context.querySelectorAll(query), extra);
                        } catch (e) {}
                    }

                    return oldSizzle(query, context, extra, seed);
                };

                for (var prop in oldSizzle) {
                    Sizzle[prop] = oldSizzle[prop];
                }

                div = null; // release memory in IE
            })();
        }

        (function() {
            var div = document.createElement("div");

            div.innerHTML = "<div class='test e'></div><div class='test'></div>";

            if (!div.getElementsByClassName || div.getElementsByClassName("e").length === 0) {
                return;
            }

            // Safari caches class attributes, doesn't catch changes (in 3.2)
            div.lastChild.className = "e";

            if (div.getElementsByClassName("e").length === 1) {
                return;
            }

            Expr.order.splice(1, 0, "CLASS");
            Expr.find.CLASS = function(match, context, isXML) {
                if (typeof context.getElementsByClassName !== "undefined" && !isXML) {
                    return context.getElementsByClassName(match[1]);
                }
            };

            div = null; // release memory in IE
        })();

        function dirNodeCheck(dir, cur, doneName, checkSet, nodeCheck, isXML) {
            for (var i = 0, l = checkSet.length; i < l; i++) {
                var elem = checkSet[i];
                if (elem) {
                    elem = elem[dir];
                    var match = false;

                    while (elem) {
                        if (elem.sizcache === doneName) {
                            match = checkSet[elem.sizset];
                            break;
                        }

                        if (elem.nodeType === 1 && !isXML) {
                            elem.sizcache = doneName;
                            elem.sizset = i;
                        }

                        if (elem.nodeName.toLowerCase() === cur) {
                            match = elem;
                            break;
                        }

                        elem = elem[dir];
                    }

                    checkSet[i] = match;
                }
            }
        }

        function dirCheck(dir, cur, doneName, checkSet, nodeCheck, isXML) {
            for (var i = 0, l = checkSet.length; i < l; i++) {
                var elem = checkSet[i];
                if (elem) {
                    elem = elem[dir];
                    var match = false;

                    while (elem) {
                        if (elem.sizcache === doneName) {
                            match = checkSet[elem.sizset];
                            break;
                        }

                        if (elem.nodeType === 1) {
                            if (!isXML) {
                                elem.sizcache = doneName;
                                elem.sizset = i;
                            }
                            if (typeof cur !== "string") {
                                if (elem === cur) {
                                    match = true;
                                    break;
                                }

                            } else if (Sizzle.filter(cur, [elem]).length > 0) {
                                match = elem;
                                break;
                            }
                        }

                        elem = elem[dir];
                    }

                    checkSet[i] = match;
                }
            }
        }

        var contains = document.compareDocumentPosition ? function(a, b) {
            return a.compareDocumentPosition(b) & 16;
        } : function(a, b) {
            return a !== b && (a.contains ? a.contains(b) : true);
        };

        var isXML = function(elem) {
            // documentElement is verified for cases where it doesn't yet exist
            // (such as loading iframes in IE - #4833) 
            var documentElement = (elem ? elem.ownerDocument || elem : 0).documentElement;
            return documentElement ? documentElement.nodeName !== "HTML" : false;
        };

        var posProcess = function(selector, context) {
            var tmpSet = [],
                later = "",
                match,
                root = context.nodeType ? [context] : context;

            // Position selectors must be done after the filter
            // And so must :not(positional) so we move all PSEUDOs to the end
            while ((match = Expr.match.PSEUDO.exec(selector))) {
                later += match[0];
                selector = selector.replace(Expr.match.PSEUDO, "");
            }

            selector = Expr.relative[selector] ? selector + "*" : selector;

            for (var i = 0, l = root.length; i < l; i++) {
                Sizzle(selector, root[i], tmpSet);
            }

            return Sizzle.filter(later, tmpSet);
        };

        // EXPOSE
        jQuery.find = Sizzle;
        jQuery.expr = Sizzle.selectors;
        jQuery.expr[":"] = jQuery.expr.filters;
        jQuery.unique = Sizzle.uniqueSort;
        jQuery.getText = getText;
        jQuery.isXMLDoc = isXML;
        jQuery.contains = contains;

        return;

        window.Sizzle = Sizzle;

    })();
    var runtil = /Until$/,
        rparentsprev = /^(?:parents|prevUntil|prevAll)/,
        // Note: This RegExp should be improved, or likely pulled from Sizzle
        rmultiselector = /,/,
        slice = Array.prototype.slice;

    // Implement the identical functionality for filter and not
    var winnow = function(elements, qualifier, keep) {
        if (jQuery.isFunction(qualifier)) {
            return jQuery.grep(elements, function(elem, i) {
                return !!qualifier.call(elem, i, elem) === keep;
            });

        } else if (qualifier.nodeType) {
            return jQuery.grep(elements, function(elem, i) {
                return (elem === qualifier) === keep;
            });

        } else if (typeof qualifier === "string") {
            var filtered = jQuery.grep(elements, function(elem) {
                return elem.nodeType === 1;
            });

            if (isSimple.test(qualifier)) {
                return jQuery.filter(qualifier, filtered, !keep);
            } else {
                qualifier = jQuery.filter(qualifier, filtered);
            }
        }

        return jQuery.grep(elements, function(elem, i) {
            return (jQuery.inArray(elem, qualifier) >= 0) === keep;
        });
    };

    jQuery.fn.extend({
        find: function(selector) {
            var ret = this.pushStack("", "find", selector),
                length = 0;

            for (var i = 0, l = this.length; i < l; i++) {
                length = ret.length;
                jQuery.find(selector, this[i], ret);

                if (i > 0) {
                    // Make sure that the results are unique
                    for (var n = length; n < ret.length; n++) {
                        for (var r = 0; r < length; r++) {
                            if (ret[r] === ret[n]) {
                                ret.splice(n--, 1);
                                break;
                            }
                        }
                    }
                }
            }

            return ret;
        },

        has: function(target) {
            var targets = jQuery(target);
            return this.filter(function() {
                for (var i = 0, l = targets.length; i < l; i++) {
                    if (jQuery.contains(this, targets[i])) {
                        return true;
                    }
                }
            });
        },

        not: function(selector) {
            return this.pushStack(winnow(this, selector, false), "not", selector);
        },

        filter: function(selector) {
            return this.pushStack(winnow(this, selector, true), "filter", selector);
        },

        is: function(selector) {
            return !!selector && jQuery.filter(selector, this).length > 0;
        },

        closest: function(selectors, context) {
            if (jQuery.isArray(selectors)) {
                var ret = [],
                    cur = this[0],
                    match, matches = {},
                    selector;

                if (cur && selectors.length) {
                    for (var i = 0, l = selectors.length; i < l; i++) {
                        selector = selectors[i];

                        if (!matches[selector]) {
                            matches[selector] = jQuery.expr.match.POS.test(selector) ?
                                jQuery(selector, context || this.context) :
                                selector;
                        }
                    }

                    while (cur && cur.ownerDocument && cur !== context) {
                        for (selector in matches) {
                            match = matches[selector];

                            if (match.jquery ? match.index(cur) > -1 : jQuery(cur).is(match)) {
                                ret.push({ selector: selector, elem: cur });
                                delete matches[selector];
                            }
                        }
                        cur = cur.parentNode;
                    }
                }

                return ret;
            }

            var pos = jQuery.expr.match.POS.test(selectors) ?
                jQuery(selectors, context || this.context) : null;

            return this.map(function(i, cur) {
                while (cur && cur.ownerDocument && cur !== context) {
                    if (pos ? pos.index(cur) > -1 : jQuery(cur).is(selectors)) {
                        return cur;
                    }
                    cur = cur.parentNode;
                }
                return null;
            });
        },

        index: function(elem) {
            if (!elem || typeof elem === "string") {
                return jQuery.inArray(this[0],

                    elem ? jQuery(elem) : this.parent().children());
            }
            // Locate the position of the desired element
            return jQuery.inArray(
                // If it receives a jQuery object, the first element is used
                elem.jquery ? elem[0] : elem, this);
        },

        add: function(selector, context) {
            var set = typeof selector === "string" ?
                jQuery(selector, context || this.context) :
                jQuery.makeArray(selector),
                all = jQuery.merge(this.get(), set);

            return this.pushStack(isDisconnected(set[0]) || isDisconnected(all[0]) ?
                all :
                jQuery.unique(all));
        },

        andSelf: function() {
            return this.add(this.prevObject);
        }
    });

    function isDisconnected(node) {
        return !node || !node.parentNode || node.parentNode.nodeType === 11;
    }

    jQuery.each({
        parent: function(elem) {
            var parent = elem.parentNode;
            return parent && parent.nodeType !== 11 ? parent : null;
        },
        parents: function(elem) {
            return jQuery.dir(elem, "parentNode");
        },
        parentsUntil: function(elem, i, until) {
            return jQuery.dir(elem, "parentNode", until);
        },
        next: function(elem) {
            return jQuery.nth(elem, 2, "nextSibling");
        },
        prev: function(elem) {
            return jQuery.nth(elem, 2, "previousSibling");
        },
        nextAll: function(elem) {
            return jQuery.dir(elem, "nextSibling");
        },
        prevAll: function(elem) {
            return jQuery.dir(elem, "previousSibling");
        },
        nextUntil: function(elem, i, until) {
            return jQuery.dir(elem, "nextSibling", until);
        },
        prevUntil: function(elem, i, until) {
            return jQuery.dir(elem, "previousSibling", until);
        },
        siblings: function(elem) {
            return jQuery.sibling(elem.parentNode.firstChild, elem);
        },
        children: function(elem) {
            return jQuery.sibling(elem.firstChild);
        },
        contents: function(elem) {
            return jQuery.nodeName(elem, "iframe") ?
                elem.contentDocument || elem.contentWindow.document :
                jQuery.makeArray(elem.childNodes);
        }
    }, function(name, fn) {
        jQuery.fn[name] = function(until, selector) {
            var ret = jQuery.map(this, fn, until);

            if (!runtil.test(name)) {
                selector = until;
            }

            if (selector && typeof selector === "string") {
                ret = jQuery.filter(selector, ret);
            }

            ret = this.length > 1 ? jQuery.unique(ret) : ret;

            if ((this.length > 1 || rmultiselector.test(selector)) && rparentsprev.test(name)) {
                ret = ret.reverse();
            }

            return this.pushStack(ret, name, slice.call(arguments).join(","));
        };
    });

    jQuery.extend({
        filter: function(expr, elems, not) {
            if (not) {
                expr = ":not(" + expr + ")";
            }

            return jQuery.find.matches(expr, elems);
        },

        dir: function(elem, dir, until) {
            var matched = [],
                cur = elem[dir];
            while (cur && cur.nodeType !== 9 && (until === undefined || cur.nodeType !== 1 || !jQuery(cur).is(until))) {
                if (cur.nodeType === 1) {
                    matched.push(cur);
                }
                cur = cur[dir];
            }
            return matched;
        },

        nth: function(cur, result, dir, elem) {
            result = result || 1;
            var num = 0;

            for (; cur; cur = cur[dir]) {
                if (cur.nodeType === 1 && ++num === result) {
                    break;
                }
            }

            return cur;
        },

        sibling: function(n, elem) {
            var r = [];

            for (; n; n = n.nextSibling) {
                if (n.nodeType === 1 && n !== elem) {
                    r.push(n);
                }
            }

            return r;
        }
    });
    var rinlinejQuery = / jQuery\d+="(?:\d+|null)"/g,
        rleadingWhitespace = /^\s+/,
        rxhtmlTag = /(<([\w:]+)[^>]*?)\/>/g,
        rselfClosing = /^(?:area|br|col|embed|hr|img|input|link|meta|param)$/i,
        rtagName = /<([\w:]+)/,
        rtbody = /<tbody/i,
        rhtml = /<|&\w+;/,
        rchecked = /checked\s*(?:[^=]|=\s*.checked.)/i, // checked="checked" or checked (html5)
        fcloseTag = function(all, front, tag) {
            return rselfClosing.test(tag) ?
                all :
                front + "></" + tag + ">";
        },
        wrapMap = {
            option: [1, "<select multiple='multiple'>", "</select>"],
            legend: [1, "<fieldset>", "</fieldset>"],
            thead: [1, "<table>", "</table>"],
            tr: [2, "<table><tbody>", "</tbody></table>"],
            td: [3, "<table><tbody><tr>", "</tr></tbody></table>"],
            col: [2, "<table><tbody></tbody><colgroup>", "</colgroup></table>"],
            area: [1, "<map>", "</map>"],
            _default: [0, "", ""]
        };

    wrapMap.optgroup = wrapMap.option;
    wrapMap.tbody = wrapMap.tfoot = wrapMap.colgroup = wrapMap.caption = wrapMap.thead;
    wrapMap.th = wrapMap.td;

    // IE can't serialize <link> and <script> tags normally
    if (!jQuery.support.htmlSerialize) {
        wrapMap._default = [1, "div<div>", "</div>"];
    }

    jQuery.fn.extend({
        text: function(text) {
            if (jQuery.isFunction(text)) {
                return this.each(function(i) {
                    var self = jQuery(this);
                    self.text(text.call(this, i, self.text()));
                });
            }

            if (typeof text !== "object" && text !== undefined) {
                return this.empty().append((this[0] && this[0].ownerDocument || document).createTextNode(text));
            }

            return jQuery.getText(this);
        },

        wrapAll: function(html) {
            if (jQuery.isFunction(html)) {
                return this.each(function(i) {
                    jQuery(this).wrapAll(html.call(this, i));
                });
            }

            if (this[0]) {
                // The elements to wrap the target around
                var wrap = jQuery(html, this[0].ownerDocument).eq(0).clone(true);

                if (this[0].parentNode) {
                    wrap.insertBefore(this[0]);
                }

                wrap.map(function() {
                    var elem = this;

                    while (elem.firstChild && elem.firstChild.nodeType === 1) {
                        elem = elem.firstChild;
                    }

                    return elem;
                }).append(this);
            }

            return this;
        },

        wrapInner: function(html) {
            if (jQuery.isFunction(html)) {
                return this.each(function(i) {
                    jQuery(this).wrapInner(html.call(this, i));
                });
            }

            return this.each(function() {
                var self = jQuery(this),
                    contents = self.contents();

                if (contents.length) {
                    contents.wrapAll(html);

                } else {
                    self.append(html);
                }
            });
        },

        wrap: function(html) {
            return this.each(function() {
                jQuery(this).wrapAll(html);
            });
        },

        unwrap: function() {
            return this.parent().each(function() {
                if (!jQuery.nodeName(this, "body")) {
                    jQuery(this).replaceWith(this.childNodes);
                }
            }).end();
        },

        append: function() {
            return this.domManip(arguments, true, function(elem) {
                if (this.nodeType === 1) {
                    this.appendChild(elem);
                }
            });
        },

        prepend: function() {
            return this.domManip(arguments, true, function(elem) {
                if (this.nodeType === 1) {
                    this.insertBefore(elem, this.firstChild);
                }
            });
        },

        before: function() {
            if (this[0] && this[0].parentNode) {
                return this.domManip(arguments, false, function(elem) {
                    this.parentNode.insertBefore(elem, this);
                });
            } else if (arguments.length) {
                var set = jQuery(arguments[0]);
                set.push.apply(set, this.toArray());
                return this.pushStack(set, "before", arguments);
            }
        },

        after: function() {
            if (this[0] && this[0].parentNode) {
                return this.domManip(arguments, false, function(elem) {
                    this.parentNode.insertBefore(elem, this.nextSibling);
                });
            } else if (arguments.length) {
                var set = this.pushStack(this, "after", arguments);
                set.push.apply(set, jQuery(arguments[0]).toArray());
                return set;
            }
        },

        clone: function(events) {
            // Do the clone
            var ret = this.map(function() {
                if (!jQuery.support.noCloneEvent && !jQuery.isXMLDoc(this)) {
                    var html = this.outerHTML,
                        ownerDocument = this.ownerDocument;
                    if (!html) {
                        var div = ownerDocument.createElement("div");
                        div.appendChild(this.cloneNode(true));
                        html = div.innerHTML;
                    }

                    return jQuery.clean([html.replace(rinlinejQuery, "")
                        .replace(rleadingWhitespace, "")
                    ], ownerDocument)[0];
                } else {
                    return this.cloneNode(true);
                }
            });

            // Copy the events from the original to the clone
            if (events === true) {
                cloneCopyEvent(this, ret);
                cloneCopyEvent(this.find("*"), ret.find("*"));
            }

            // Return the cloned set
            return ret;
        },

        html: function(value) {
            if (value === undefined) {
                return this[0] && this[0].nodeType === 1 ?
                    this[0].innerHTML.replace(rinlinejQuery, "") :
                    null;

                // See if we can take a shortcut and just use innerHTML
            } else if (typeof value === "string" && !/<script/i.test(value) &&
                (jQuery.support.leadingWhitespace || !rleadingWhitespace.test(value)) &&
                !wrapMap[(rtagName.exec(value) || ["", ""])[1].toLowerCase()]) {

                value = value.replace(rxhtmlTag, fcloseTag);

                try {
                    for (var i = 0, l = this.length; i < l; i++) {
                        // Remove element nodes and prevent memory leaks
                        if (this[i].nodeType === 1) {
                            jQuery.cleanData(this[i].getElementsByTagName("*"));
                            this[i].innerHTML = value;
                        }
                    }

                    // If using innerHTML throws an exception, use the fallback method
                } catch (e) {
                    this.empty().append(value);
                }

            } else if (jQuery.isFunction(value)) {
                this.each(function(i) {
                    var self = jQuery(this),
                        old = self.html();
                    self.empty().append(function() {
                        return value.call(this, i, old);
                    });
                });

            } else {
                this.empty().append(value);
            }

            return this;
        },

        replaceWith: function(value) {
            if (this[0] && this[0].parentNode) {
                if (!jQuery.isFunction(value)) {
                    value = jQuery(value).detach();

                } else {
                    return this.each(function(i) {
                        var self = jQuery(this),
                            old = self.html();
                        self.replaceWith(value.call(this, i, old));
                    });
                }

                return this.each(function() {
                    var next = this.nextSibling,
                        parent = this.parentNode;

                    jQuery(this).remove();

                    if (next) {
                        jQuery(next).before(value);
                    } else {
                        jQuery(parent).append(value);
                    }
                });
            } else {
                return this.pushStack(jQuery(jQuery.isFunction(value) ? value() : value), "replaceWith", value);
            }
        },

        detach: function(selector) {
            return this.remove(selector, true);
        },

        domManip: function(args, table, callback) {
            var results, first, value = args[0],
                scripts = [];

            // We can't cloneNode fragments that contain checked, in WebKit
            if (!jQuery.support.checkClone && arguments.length === 3 && typeof value === "string" && rchecked.test(value)) {
                return this.each(function() {
                    jQuery(this).domManip(args, table, callback, true);
                });
            }

            if (jQuery.isFunction(value)) {
                return this.each(function(i) {
                    var self = jQuery(this);
                    args[0] = value.call(this, i, table ? self.html() : undefined);
                    self.domManip(args, table, callback);
                });
            }

            if (this[0]) {
                // If we're in a fragment, just use that instead of building a new one
                if (args[0] && args[0].parentNode && args[0].parentNode.nodeType === 11) {
                    results = { fragment: args[0].parentNode };
                } else {
                    results = buildFragment(args, this, scripts);
                }

                first = results.fragment.firstChild;

                if (first) {
                    table = table && jQuery.nodeName(first, "tr");

                    for (var i = 0, l = this.length; i < l; i++) {
                        callback.call(
                            table ?
                            root(this[i], first) :
                            this[i],
                            results.cacheable || this.length > 1 || i > 0 ?
                            results.fragment.cloneNode(true) :
                            results.fragment
                        );
                    }
                }

                if (scripts) {
                    jQuery.each(scripts, evalScript);
                }
            }

            return this;

            function root(elem, cur) {
                return jQuery.nodeName(elem, "table") ?
                    (elem.getElementsByTagName("tbody")[0] ||
                        elem.appendChild(elem.ownerDocument.createElement("tbody"))) :
                    elem;
            }
        }
    });

    function cloneCopyEvent(orig, ret) {
        var i = 0;

        ret.each(function() {
            if (this.nodeName !== (orig[i] && orig[i].nodeName)) {
                return;
            }

            var oldData = jQuery.data(orig[i++]),
                curData = jQuery.data(this, oldData),
                events = oldData && oldData.events;

            if (events) {
                delete curData.handle;
                curData.events = {};

                for (var type in events) {
                    for (var handler in events[type]) {
                        jQuery.event.add(this, type, events[type][handler], events[type][handler].data);
                    }
                }
            }
        });
    }

    function buildFragment(args, nodes, scripts) {
        var fragment, cacheable, cacheresults, doc;

        // webkit does not clone 'checked' attribute of radio inputs on cloneNode, so don't cache if string has a checked
        if (args.length === 1 && typeof args[0] === "string" && args[0].length < 512 && args[0].indexOf("<option") < 0 && (jQuery.support.checkClone || !rchecked.test(args[0]))) {
            cacheable = true;
            cacheresults = jQuery.fragments[args[0]];
            if (cacheresults) {
                if (cacheresults !== 1) {
                    fragment = cacheresults;
                }
            }
        }

        if (!fragment) {
            doc = (nodes && nodes[0] ? nodes[0].ownerDocument || nodes[0] : document);
            fragment = doc.createDocumentFragment();
            jQuery.clean(args, doc, fragment, scripts);
        }

        if (cacheable) {
            jQuery.fragments[args[0]] = cacheresults ? fragment : 1;
        }

        return { fragment: fragment, cacheable: cacheable };
    }

    jQuery.fragments = {};

    jQuery.each({
        appendTo: "append",
        prependTo: "prepend",
        insertBefore: "before",
        insertAfter: "after",
        replaceAll: "replaceWith"
    }, function(name, original) {
        jQuery.fn[name] = function(selector) {
            var ret = [],
                insert = jQuery(selector);

            for (var i = 0, l = insert.length; i < l; i++) {
                var elems = (i > 0 ? this.clone(true) : this).get();
                jQuery.fn[original].apply(jQuery(insert[i]), elems);
                ret = ret.concat(elems);
            }
            return this.pushStack(ret, name, insert.selector);
        };
    });

    jQuery.each({
        // keepData is for internal use only--do not document
        remove: function(selector, keepData) {
            if (!selector || jQuery.filter(selector, [this]).length) {
                if (!keepData && this.nodeType === 1) {
                    jQuery.cleanData(this.getElementsByTagName("*"));
                    jQuery.cleanData([this]);
                }

                if (this.parentNode) {
                    this.parentNode.removeChild(this);
                }
            }
        },

        empty: function() {
            // Remove element nodes and prevent memory leaks
            if (this.nodeType === 1) {
                jQuery.cleanData(this.getElementsByTagName("*"));
            }

            // Remove any remaining nodes
            while (this.firstChild) {
                this.removeChild(this.firstChild);
            }
        }
    }, function(name, fn) {
        jQuery.fn[name] = function() {
            return this.each(fn, arguments);
        };
    });

    jQuery.extend({
        clean: function(elems, context, fragment, scripts) {
            context = context || document;

            // !context.createElement fails in IE with an error but returns typeof 'object'
            if (typeof context.createElement === "undefined") {
                context = context.ownerDocument || context[0] && context[0].ownerDocument || document;
            }

            var ret = [];

            jQuery.each(elems, function(i, elem) {
                if (typeof elem === "number") {
                    elem += "";
                }

                if (!elem) {
                    return;
                }

                // Convert html string into DOM nodes
                if (typeof elem === "string" && !rhtml.test(elem)) {
                    elem = context.createTextNode(elem);

                } else if (typeof elem === "string") {
                    // Fix "XHTML"-style tags in all browsers
                    elem = elem.replace(rxhtmlTag, fcloseTag);

                    // Trim whitespace, otherwise indexOf won't work as expected
                    var tag = (rtagName.exec(elem) || ["", ""])[1].toLowerCase(),
                        wrap = wrapMap[tag] || wrapMap._default,
                        depth = wrap[0],
                        div = context.createElement("div");

                    // Go to html and back, then peel off extra wrappers
                    div.innerHTML = wrap[1] + elem + wrap[2];

                    // Move to the right depth
                    while (depth--) {
                        div = div.lastChild;
                    }

                    // Remove IE's autoinserted <tbody> from table fragments
                    if (!jQuery.support.tbody) {

                        // String was a <table>, *may* have spurious <tbody>
                        var hasBody = rtbody.test(elem),
                            tbody = tag === "table" && !hasBody ?
                            div.firstChild && div.firstChild.childNodes :

                            // String was a bare <thead> or <tfoot>
                            wrap[1] === "<table>" && !hasBody ?
                            div.childNodes : [];

                        for (var j = tbody.length - 1; j >= 0; --j) {
                            if (jQuery.nodeName(tbody[j], "tbody") && !tbody[j].childNodes.length) {
                                tbody[j].parentNode.removeChild(tbody[j]);
                            }
                        }

                    }

                    // IE completely kills leading whitespace when innerHTML is used
                    if (!jQuery.support.leadingWhitespace && rleadingWhitespace.test(elem)) {
                        div.insertBefore(context.createTextNode(rleadingWhitespace.exec(elem)[0]), div.firstChild);
                    }

                    elem = jQuery.makeArray(div.childNodes);
                }

                if (elem.nodeType) {
                    ret.push(elem);
                } else {
                    ret = jQuery.merge(ret, elem);
                }

            });

            if (fragment) {
                for (var i = 0; ret[i]; i++) {
                    if (scripts && jQuery.nodeName(ret[i], "script") && (!ret[i].type || ret[i].type.toLowerCase() === "text/javascript")) {
                        scripts.push(ret[i].parentNode ? ret[i].parentNode.removeChild(ret[i]) : ret[i]);
                    } else {
                        if (ret[i].nodeType === 1) {
                            ret.splice.apply(ret, [i + 1, 0].concat(jQuery.makeArray(ret[i].getElementsByTagName("script"))));
                        }
                        fragment.appendChild(ret[i]);
                    }
                }
            }

            return ret;
        },

        cleanData: function(elems) {
            for (var i = 0, elem, id;
                (elem = elems[i]) != null; i++) {
                jQuery.event.remove(elem);
                jQuery.removeData(elem);
            }
        }
    });
    // exclude the following css properties to add px
    var rexclude = /z-?index|font-?weight|opacity|zoom|line-?height/i,
        ralpha = /alpha\([^)]*\)/,
        ropacity = /opacity=([^)]*)/,
        rfloat = /float/i,
        rdashAlpha = /-([a-z])/ig,
        rupper = /([A-Z])/g,
        rnumpx = /^-?\d+(?:px)?$/i,
        rnum = /^-?\d/,

        cssShow = { position: "absolute", visibility: "hidden", display: "block" },
        cssWidth = ["Left", "Right"],
        cssHeight = ["Top", "Bottom"],

        // cache check for defaultView.getComputedStyle
        getComputedStyle = document.defaultView && document.defaultView.getComputedStyle,
        // normalize float css property
        styleFloat = jQuery.support.cssFloat ? "cssFloat" : "styleFloat",
        fcamelCase = function(all, letter) {
            return letter.toUpperCase();
        };

    jQuery.fn.css = function(name, value) {
        return access(this, name, value, true, function(elem, name, value) {
            if (value === undefined) {
                return jQuery.curCSS(elem, name);
            }

            if (typeof value === "number" && !rexclude.test(name)) {
                value += "px";
            }

            jQuery.style(elem, name, value);
        });
    };

    jQuery.extend({
        style: function(elem, name, value) {
            // don't set styles on text and comment nodes
            if (!elem || elem.nodeType === 3 || elem.nodeType === 8) {
                return undefined;
            }

            // ignore negative width and height values #1599
            if ((name === "width" || name === "height") && parseFloat(value) < 0) {
                value = undefined;
            }

            var style = elem.style || elem,
                set = value !== undefined;

            // IE uses filters for opacity
            if (!jQuery.support.opacity && name === "opacity") {
                if (set) {
                    // IE has trouble with opacity if it does not have layout
                    // Force it by setting the zoom level
                    style.zoom = 1;

                    // Set the alpha filter to set the opacity
                    var opacity = parseInt(value, 10) + "" === "NaN" ? "" : "alpha(opacity=" + value * 100 + ")";
                    var filter = style.filter || jQuery.curCSS(elem, "filter") || "";
                    style.filter = ralpha.test(filter) ? filter.replace(ralpha, opacity) : opacity;
                }

                return style.filter && style.filter.indexOf("opacity=") >= 0 ?
                    (parseFloat(ropacity.exec(style.filter)[1]) / 100) + "" :
                    "";
            }

            // Make sure we're using the right name for getting the float value
            if (rfloat.test(name)) {
                name = styleFloat;
            }

            name = name.replace(rdashAlpha, fcamelCase);

            if (set) {
                style[name] = value;
            }

            return style[name];
        },

        css: function(elem, name, force, extra) {
            if (name === "width" || name === "height") {
                var val, props = cssShow,
                    which = name === "width" ? cssWidth : cssHeight;

                function getWH() {
                    val = name === "width" ? elem.offsetWidth : elem.offsetHeight;

                    if (extra === "border") {
                        return;
                    }

                    jQuery.each(which, function() {
                        if (!extra) {
                            val -= parseFloat(jQuery.curCSS(elem, "padding" + this, true)) || 0;
                        }

                        if (extra === "margin") {
                            val += parseFloat(jQuery.curCSS(elem, "margin" + this, true)) || 0;
                        } else {
                            val -= parseFloat(jQuery.curCSS(elem, "border" + this + "Width", true)) || 0;
                        }
                    });
                }

                if (elem.offsetWidth !== 0) {
                    getWH();
                } else {
                    jQuery.swap(elem, props, getWH);
                }

                return Math.max(0, Math.round(val));
            }

            return jQuery.curCSS(elem, name, force);
        },

        curCSS: function(elem, name, force) {
            var ret, style = elem.style,
                filter;

            // IE uses filters for opacity
            if (!jQuery.support.opacity && name === "opacity" && elem.currentStyle) {
                ret = ropacity.test(elem.currentStyle.filter || "") ?
                    (parseFloat(RegExp.$1) / 100) + "" :
                    "";

                return ret === "" ?
                    "1" :
                    ret;
            }

            // Make sure we're using the right name for getting the float value
            if (rfloat.test(name)) {
                name = styleFloat;
            }

            if (!force && style && style[name]) {
                ret = style[name];

            } else if (getComputedStyle) {

                // Only "float" is needed here
                if (rfloat.test(name)) {
                    name = "float";
                }

                name = name.replace(rupper, "-$1").toLowerCase();

                var defaultView = elem.ownerDocument.defaultView;

                if (!defaultView) {
                    return null;
                }

                var computedStyle = defaultView.getComputedStyle(elem, null);

                if (computedStyle) {
                    ret = computedStyle.getPropertyValue(name);
                }

                // We should always get a number back from opacity
                if (name === "opacity" && ret === "") {
                    ret = "1";
                }

            } else if (elem.currentStyle) {
                var camelCase = name.replace(rdashAlpha, fcamelCase);

                ret = elem.currentStyle[name] || elem.currentStyle[camelCase];

                // From the awesome hack by Dean Edwards
                // http://erik.eae.net/archives/2007/07/27/18.54.15/#comment-102291

                // If we're not dealing with a regular pixel number
                // but a number that has a weird ending, we need to convert it to pixels
                if (!rnumpx.test(ret) && rnum.test(ret)) {
                    // Remember the original values
                    var left = style.left,
                        rsLeft = elem.runtimeStyle.left;

                    // Put in the new values to get a computed value out
                    elem.runtimeStyle.left = elem.currentStyle.left;
                    style.left = camelCase === "fontSize" ? "1em" : (ret || 0);
                    ret = style.pixelLeft + "px";

                    // Revert the changed values
                    style.left = left;
                    elem.runtimeStyle.left = rsLeft;
                }
            }

            return ret;
        },

        // A method for quickly swapping in/out CSS properties to get correct calculations
        swap: function(elem, options, callback) {
            var old = {};

            // Remember the old values, and insert the new ones
            for (var name in options) {
                old[name] = elem.style[name];
                elem.style[name] = options[name];
            }

            callback.call(elem);

            // Revert the old values
            for (var name in options) {
                elem.style[name] = old[name];
            }
        }
    });

    if (jQuery.expr && jQuery.expr.filters) {
        jQuery.expr.filters.hidden = function(elem) {
            var width = elem.offsetWidth,
                height = elem.offsetHeight,
                skip = elem.nodeName.toLowerCase() === "tr";

            return width === 0 && height === 0 && !skip ?
                true :
                width > 0 && height > 0 && !skip ?
                false :
                jQuery.curCSS(elem, "display") === "none";
        };

        jQuery.expr.filters.visible = function(elem) {
            return !jQuery.expr.filters.hidden(elem);
        };
    }
    var jsc = now(),
        rscript = /<script(.|\s)*?\/script>/gi,
        rselectTextarea = /select|textarea/i,
        rinput = /color|date|datetime|email|hidden|month|number|password|range|search|tel|text|time|url|week/i,
        jsre = /=\?(&|$)/,
        rquery = /\?/,
        rts = /(\?|&)_=.*?(&|$)/,
        rurl = /^(\w+:)?\/\/([^\/?#]+)/,
        r20 = /%20/g;

    jQuery.fn.extend({
        // Keep a copy of the old load
        _load: jQuery.fn.load,

        load: function(url, params, callback) {
            if (typeof url !== "string") {
                return this._load(url);

                // Don't do a request if no elements are being requested
            } else if (!this.length) {
                return this;
            }

            var off = url.indexOf(" ");
            if (off >= 0) {
                var selector = url.slice(off, url.length);
                url = url.slice(0, off);
            }

            // Default to a GET request
            var type = "GET";

            // If the second parameter was provided
            if (params) {
                // If it's a function
                if (jQuery.isFunction(params)) {
                    // We assume that it's the callback
                    callback = params;
                    params = null;

                    // Otherwise, build a param string
                } else if (typeof params === "object") {
                    params = jQuery.param(params, jQuery.ajaxSettings.traditional);
                    type = "POST";
                }
            }

            var self = this;

            // Request the remote document
            jQuery.ajax({
                url: url,
                type: type,
                dataType: "html",
                data: params,
                complete: function(res, status) {
                    // If successful, inject the HTML into all the matched elements
                    if (status === "success" || status === "notmodified") {
                        // See if a selector was specified
                        self.html(selector ?
                            // Create a dummy div to hold the results
                            jQuery("<div />")
                            // inject the contents of the document in, removing the scripts
                            // to avoid any 'Permission Denied' errors in IE
                            .append(res.responseText.replace(rscript, ""))

                            // Locate the specified elements
                            .find(selector) :

                            // If not, just inject the full result
                            res.responseText);
                    }

                    if (callback) {
                        self.each(callback, [res.responseText, status, res]);
                    }
                }
            });

            return this;
        },

        serialize: function() {
            return jQuery.param(this.serializeArray());
        },
        serializeArray: function() {
            return this.map(function() {
                    return this.elements ? jQuery.makeArray(this.elements) : this;
                })
                .filter(function() {
                    return this.name && !this.disabled &&
                        (this.checked || rselectTextarea.test(this.nodeName) ||
                            rinput.test(this.type));
                })
                .map(function(i, elem) {
                    var val = jQuery(this).val();

                    return val == null ?
                        null :
                        jQuery.isArray(val) ?
                        jQuery.map(val, function(val, i) {
                            return { name: elem.name, value: val };
                        }) : { name: elem.name, value: val };
                }).get();
        }
    });

    // Attach a bunch of functions for handling common AJAX events
    jQuery.each("ajaxStart ajaxStop ajaxComplete ajaxError ajaxSuccess ajaxSend".split(" "), function(i, o) {
        jQuery.fn[o] = function(f) {
            return this.bind(o, f);
        };
    });

    jQuery.extend({

        get: function(url, data, callback, type) {
            // shift arguments if data argument was omited
            if (jQuery.isFunction(data)) {
                type = type || callback;
                callback = data;
                data = null;
            }

            return jQuery.ajax({
                type: "GET",
                url: url,
                data: data,
                success: callback,
                dataType: type
            });
        },

        getScript: function(url, callback) {
            return jQuery.get(url, null, callback, "script");
        },

        getJSON: function(url, data, callback) {
            return jQuery.get(url, data, callback, "json");
        },

        post: function(url, data, callback, type) {
            // shift arguments if data argument was omited
            if (jQuery.isFunction(data)) {
                type = type || callback;
                callback = data;
                data = {};
            }

            return jQuery.ajax({
                type: "POST",
                url: url,
                data: data,
                success: callback,
                dataType: type
            });
        },

        ajaxSetup: function(settings) {
            jQuery.extend(jQuery.ajaxSettings, settings);
        },

        ajaxSettings: {
            url: location.href,
            global: true,
            type: "GET",
            contentType: "application/x-www-form-urlencoded",
            processData: true,
            async: true,
            xhr: window.XMLHttpRequest && (window.location.protocol !== "file:" || !window.ActiveXObject) ?
                function() {
                    return new window.XMLHttpRequest();
                } : function() {
                    try {
                        return new window.ActiveXObject("Microsoft.XMLHTTP");
                    } catch (e) {}
                },
            accepts: {
                xml: "application/xml, text/xml",
                html: "text/html",
                script: "text/javascript, application/javascript",
                json: "application/json, text/javascript",
                text: "text/plain",
                _default: "*/*"
            }
        },

        // Last-Modified header cache for next request
        lastModified: {},
        etag: {},

        ajax: function(origSettings) {
            var s = jQuery.extend(true, {}, jQuery.ajaxSettings, origSettings);

            var jsonp, status, data,
                callbackContext = origSettings && origSettings.context || s,
                type = s.type.toUpperCase();

            // convert data if not already a string
            if (s.data && s.processData && typeof s.data !== "string") {
                s.data = jQuery.param(s.data, s.traditional);
            }

            // Handle JSONP Parameter Callbacks
            if (s.dataType === "jsonp") {
                if (type === "GET") {
                    if (!jsre.test(s.url)) {
                        s.url += (rquery.test(s.url) ? "&" : "?") + (s.jsonp || "callback") + "=?";
                    }
                } else if (!s.data || !jsre.test(s.data)) {
                    s.data = (s.data ? s.data + "&" : "") + (s.jsonp || "callback") + "=?";
                }
                s.dataType = "json";
            }

            // Build temporary JSONP function
            if (s.dataType === "json" && (s.data && jsre.test(s.data) || jsre.test(s.url))) {
                jsonp = s.jsonpCallback || ("jsonp" + jsc++);

                // Replace the =? sequence both in the query string and the data
                if (s.data) {
                    s.data = (s.data + "").replace(jsre, "=" + jsonp + "$1");
                }

                s.url = s.url.replace(jsre, "=" + jsonp + "$1");

                // We need to make sure
                // that a JSONP style response is executed properly
                s.dataType = "script";

                // Handle JSONP-style loading
                window[jsonp] = window[jsonp] || function(tmp) {
                    data = tmp;
                    success();
                    complete();
                    // Garbage collect
                    window[jsonp] = undefined;

                    try {
                        delete window[jsonp];
                    } catch (e) {}

                    if (head) {
                        head.removeChild(script);
                    }
                };
            }

            if (s.dataType === "script" && s.cache === null) {
                s.cache = false;
            }

            if (s.cache === false && type === "GET") {
                var ts = now();

                // try replacing _= if it is there
                var ret = s.url.replace(rts, "$1_=" + ts + "$2");

                // if nothing was replaced, add timestamp to the end
                s.url = ret + ((ret === s.url) ? (rquery.test(s.url) ? "&" : "?") + "_=" + ts : "");
            }

            // If data is available, append data to url for get requests
            if (s.data && type === "GET") {
                s.url += (rquery.test(s.url) ? "&" : "?") + s.data;
            }

            // Watch for a new set of requests
            if (s.global && !jQuery.active++) {
                jQuery.event.trigger("ajaxStart");
            }

            // Matches an absolute URL, and saves the domain
            var parts = rurl.exec(s.url),
                remote = parts && (parts[1] && parts[1] !== location.protocol || parts[2] !== location.host);

            // If we're requesting a remote document
            // and trying to load JSON or Script with a GET
            if (s.dataType === "script" && type === "GET" && remote) {
                var head = document.getElementsByTagName("head")[0] || document.documentElement;
                var script = document.createElement("script");
                script.src = s.url;
                if (s.scriptCharset) {
                    script.charset = s.scriptCharset;
                }

                // Handle Script loading
                if (!jsonp) {
                    var done = false;

                    // Attach handlers for all browsers
                    script.onload = script.onreadystatechange = function() {
                        if (!done && (!this.readyState ||
                                this.readyState === "loaded" || this.readyState === "complete")) {
                            done = true;
                            success();
                            complete();

                            // Handle memory leak in IE
                            script.onload = script.onreadystatechange = null;
                            if (head && script.parentNode) {
                                head.removeChild(script);
                            }
                        }
                    };
                }


                head.insertBefore(script, head.firstChild);

                // We handle everything using the script element injection
                return undefined;
            }

            var requestDone = false;

            // Create the request object
            var xhr = s.xhr();

            if (!xhr) {
                return;
            }

            // Open the socket
            // Passing null username, generates a login popup on Opera (#2865)
            if (s.username) {
                xhr.open(type, s.url, s.async, s.username, s.password);
            } else {
                xhr.open(type, s.url, s.async);
            }

            // Need an extra try/catch for cross domain requests in Firefox 3
            try {
                // Set the correct header, if data is being sent
                if (s.data || origSettings && origSettings.contentType) {
                    xhr.setRequestHeader("Content-Type", s.contentType);
                }

                // Set the If-Modified-Since and/or If-None-Match header, if in ifModified mode.
                if (s.ifModified) {
                    if (jQuery.lastModified[s.url]) {
                        xhr.setRequestHeader("If-Modified-Since", jQuery.lastModified[s.url]);
                    }

                    if (jQuery.etag[s.url]) {
                        xhr.setRequestHeader("If-None-Match", jQuery.etag[s.url]);
                    }
                }

                // Set header so the called script knows that it's an XMLHttpRequest
                // Only send the header if it's not a remote XHR
                if (!remote) {
                    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                }

                // Set the Accepts header for the server, depending on the dataType
                xhr.setRequestHeader("Accept", s.dataType && s.accepts[s.dataType] ?
                    s.accepts[s.dataType] + ", */*" :
                    s.accepts._default);
            } catch (e) {}

            // Allow custom headers/mimetypes and early abort
            if (s.beforeSend && s.beforeSend.call(callbackContext, xhr, s) === false) {
                // Handle the global AJAX counter
                if (s.global && !--jQuery.active) {
                    jQuery.event.trigger("ajaxStop");
                }

                // close opended socket
                xhr.abort();
                return false;
            }

            if (s.global) {
                trigger("ajaxSend", [xhr, s]);
            }

            // Wait for a response to come back
            var onreadystatechange = xhr.onreadystatechange = function(isTimeout) {
                // The request was aborted
                if (!xhr || xhr.readyState === 0 || isTimeout === "abort") {
                    // Opera doesn't call onreadystatechange before this point
                    // so we simulate the call
                    if (!requestDone) {
                        complete();
                    }

                    requestDone = true;
                    if (xhr) {
                        xhr.onreadystatechange = jQuery.noop;
                    }

                    // The transfer is complete and the data is available, or the request timed out
                } else if (!requestDone && xhr && (xhr.readyState === 4 || isTimeout === "timeout")) {
                    requestDone = true;
                    xhr.onreadystatechange = jQuery.noop;

                    status = isTimeout === "timeout" ?
                        "timeout" :
                        !jQuery.httpSuccess(xhr) ?
                        "error" :
                        s.ifModified && jQuery.httpNotModified(xhr, s.url) ?
                        "notmodified" :
                        "success";

                    var errMsg;

                    if (status === "success") {
                        // Watch for, and catch, XML document parse errors
                        try {
                            // process the data (runs the xml through httpData regardless of callback)
                            data = jQuery.httpData(xhr, s.dataType, s);
                        } catch (err) {
                            status = "parsererror";
                            errMsg = err;
                        }
                    }

                    // Make sure that the request was successful or notmodified
                    if (status === "success" || status === "notmodified") {
                        // JSONP handles its own success callback
                        if (!jsonp) {
                            success();
                        }
                    } else {
                        jQuery.handleError(s, xhr, status, errMsg);
                    }

                    // Fire the complete handlers
                    complete();

                    if (isTimeout === "timeout") {
                        xhr.abort();
                    }

                    // Stop memory leaks
                    if (s.async) {
                        xhr = null;
                    }
                }
            };

            // Override the abort handler, if we can (IE doesn't allow it, but that's OK)
            // Opera doesn't fire onreadystatechange at all on abort
            try {
                var oldAbort = xhr.abort;
                xhr.abort = function() {
                    if (xhr) {
                        oldAbort.call(xhr);
                    }

                    onreadystatechange("abort");
                };
            } catch (e) {}

            // Timeout checker
            if (s.async && s.timeout > 0) {
                setTimeout(function() {
                    // Check to see if the request is still happening
                    if (xhr && !requestDone) {
                        onreadystatechange("timeout");
                    }
                }, s.timeout);
            }

            // Send the data
            try {
                xhr.send(type === "POST" || type === "PUT" || type === "DELETE" ? s.data : null);
            } catch (e) {
                jQuery.handleError(s, xhr, null, e);
                // Fire the complete handlers
                complete();
            }

            // firefox 1.5 doesn't fire statechange for sync requests
            if (!s.async) {
                onreadystatechange();
            }

            function success() {
                // If a local callback was specified, fire it and pass it the data
                if (s.success) {
                    s.success.call(callbackContext, data, status, xhr);
                }

                // Fire the global callback
                if (s.global) {
                    trigger("ajaxSuccess", [xhr, s]);
                }
            }

            function complete() {
                // Process result
                if (s.complete) {
                    s.complete.call(callbackContext, xhr, status);
                }

                // The request was completed
                if (s.global) {
                    trigger("ajaxComplete", [xhr, s]);
                }

                // Handle the global AJAX counter
                if (s.global && !--jQuery.active) {
                    jQuery.event.trigger("ajaxStop");
                }
            }

            function trigger(type, args) {
                (s.context ? jQuery(s.context) : jQuery.event).trigger(type, args);
            }

            // return XMLHttpRequest to allow aborting the request etc.
            return xhr;
        },

        handleError: function(s, xhr, status, e) {
            // If a local callback was specified, fire it
            if (s.error) {
                s.error.call(s.context || s, xhr, status, e);
            }

            // Fire the global callback
            if (s.global) {
                (s.context ? jQuery(s.context) : jQuery.event).trigger("ajaxError", [xhr, s, e]);
            }
        },

        // Counter for holding the number of active queries
        active: 0,

        // Determines if an XMLHttpRequest was successful or not
        httpSuccess: function(xhr) {
            try {
                // IE error sometimes returns 1223 when it should be 204 so treat it as success, see #1450
                return !xhr.status && location.protocol === "file:" ||
                    // Opera returns 0 when status is 304
                    (xhr.status >= 200 && xhr.status < 300) ||
                    xhr.status === 304 || xhr.status === 1223 || xhr.status === 0;
            } catch (e) {}

            return false;
        },

        // Determines if an XMLHttpRequest returns NotModified
        httpNotModified: function(xhr, url) {
            var lastModified = xhr.getResponseHeader("Last-Modified"),
                etag = xhr.getResponseHeader("Etag");

            if (lastModified) {
                jQuery.lastModified[url] = lastModified;
            }

            if (etag) {
                jQuery.etag[url] = etag;
            }

            // Opera returns 0 when status is 304
            return xhr.status === 304 || xhr.status === 0;
        },

        httpData: function(xhr, type, s) {
            var ct = xhr.getResponseHeader("content-type") || "",
                xml = type === "xml" || !type && ct.indexOf("xml") >= 0,
                data = xml ? xhr.responseXML : xhr.responseText;

            if (xml && data.documentElement.nodeName === "parsererror") {
                jQuery.error("parsererror");
            }

            // Allow a pre-filtering function to sanitize the response
            // s is checked to keep backwards compatibility
            if (s && s.dataFilter) {
                data = s.dataFilter(data, type);
            }

            // The filter can actually parse the response
            if (typeof data === "string") {
                // Get the JavaScript object, if JSON is used.
                if (type === "json" || !type && ct.indexOf("json") >= 0) {
                    data = jQuery.parseJSON(data);

                    // If the type is "script", eval it in global context
                } else if (type === "script" || !type && ct.indexOf("javascript") >= 0) {
                    jQuery.globalEval(data);
                }
            }

            return data;
        },

        param: function(a, traditional) {
            var s = [];

            // Set traditional to true for jQuery <= 1.3.2 behavior.
            if (traditional === undefined) {
                traditional = jQuery.ajaxSettings.traditional;
            }

            // If an array was passed in, assume that it is an array of form elements.
            if (jQuery.isArray(a) || a.jquery) {
                // Serialize the form elements
                jQuery.each(a, function() {
                    add(this.name, this.value);
                });

            } else {
                // If traditional, encode the "old" way (the way 1.3.2 or older
                // did it), otherwise encode params recursively.
                for (var prefix in a) {
                    buildParams(prefix, a[prefix]);
                }
            }

            // Return the resulting serialization
            return s.join("&").replace(r20, "+");

            function buildParams(prefix, obj) {
                if (jQuery.isArray(obj)) {
                    // Serialize array item.
                    jQuery.each(obj, function(i, v) {
                        if (traditional) {
                            // Treat each array item as a scalar.
                            add(prefix, v);
                        } else {
                            buildParams(prefix + "[" + (typeof v === "object" || jQuery.isArray(v) ? i : "") + "]", v);
                        }
                    });

                } else if (!traditional && obj != null && typeof obj === "object") {
                    // Serialize object item.
                    jQuery.each(obj, function(k, v) {
                        buildParams(prefix + "[" + k + "]", v);
                    });

                } else {
                    // Serialize scalar item.
                    add(prefix, obj);
                }
            }

            function add(key, value) {
                // If value is a function, invoke it and return its value
                value = jQuery.isFunction(value) ? value() : value;
                s[s.length] = encodeURIComponent(key) + "=" + encodeURIComponent(value);
            }
        }
    });
    var elemdisplay = {},
        rfxtypes = /toggle|show|hide/,
        rfxnum = /^([+-]=)?([\d+-.]+)(.*)$/,
        timerId,
        fxAttrs = [
            // height animations
            ["height", "marginTop", "marginBottom", "paddingTop", "paddingBottom"],
            // width animations
            ["width", "marginLeft", "marginRight", "paddingLeft", "paddingRight"],
            // opacity animations
            ["opacity"]
        ];

    jQuery.fn.extend({
        show: function(speed, callback) {
            if (speed || speed === 0) {
                return this.animate(genFx("show", 3), speed, callback);

            } else {
                for (var i = 0, l = this.length; i < l; i++) {
                    var old = jQuery.data(this[i], "olddisplay");

                    this[i].style.display = old || "";

                    if (jQuery.css(this[i], "display") === "none") {
                        var nodeName = this[i].nodeName,
                            display;

                        if (elemdisplay[nodeName]) {
                            display = elemdisplay[nodeName];

                        } else {
                            var elem = jQuery("<" + nodeName + " />").appendTo("body");

                            display = elem.css("display");

                            if (display === "none") {
                                display = "block";
                            }

                            elem.remove();

                            elemdisplay[nodeName] = display;
                        }

                        jQuery.data(this[i], "olddisplay", display);
                    }
                }

                // Set the display of the elements in a second loop
                // to avoid the constant reflow
                for (var j = 0, k = this.length; j < k; j++) {
                    this[j].style.display = jQuery.data(this[j], "olddisplay") || "";
                }

                return this;
            }
        },

        hide: function(speed, callback) {
            if (speed || speed === 0) {
                return this.animate(genFx("hide", 3), speed, callback);

            } else {
                for (var i = 0, l = this.length; i < l; i++) {
                    var old = jQuery.data(this[i], "olddisplay");
                    if (!old && old !== "none") {
                        jQuery.data(this[i], "olddisplay", jQuery.css(this[i], "display"));
                    }
                }

                // Set the display of the elements in a second loop
                // to avoid the constant reflow
                for (var j = 0, k = this.length; j < k; j++) {
                    this[j].style.display = "none";
                }

                return this;
            }
        },

        // Save the old toggle function
        _toggle: jQuery.fn.toggle,

        toggle: function(fn, fn2) {
            var bool = typeof fn === "boolean";

            if (jQuery.isFunction(fn) && jQuery.isFunction(fn2)) {
                this._toggle.apply(this, arguments);

            } else if (fn == null || bool) {
                this.each(function() {
                    var state = bool ? fn : jQuery(this).is(":hidden");
                    jQuery(this)[state ? "show" : "hide"]();
                });

            } else {
                this.animate(genFx("toggle", 3), fn, fn2);
            }

            return this;
        },

        fadeTo: function(speed, to, callback) {
            return this.filter(":hidden").css("opacity", 0).show().end()
                .animate({ opacity: to }, speed, callback);
        },

        animate: function(prop, speed, easing, callback) {
            var optall = jQuery.speed(speed, easing, callback);

            if (jQuery.isEmptyObject(prop)) {
                return this.each(optall.complete);
            }

            return this[optall.queue === false ? "each" : "queue"](function() {
                var opt = jQuery.extend({}, optall),
                    p,
                    hidden = this.nodeType === 1 && jQuery(this).is(":hidden"),
                    self = this;

                for (p in prop) {
                    var name = p.replace(rdashAlpha, fcamelCase);

                    if (p !== name) {
                        prop[name] = prop[p];
                        delete prop[p];
                        p = name;
                    }

                    if (prop[p] === "hide" && hidden || prop[p] === "show" && !hidden) {
                        return opt.complete.call(this);
                    }

                    if ((p === "height" || p === "width") && this.style) {
                        // Store display property
                        opt.display = jQuery.css(this, "display");

                        // Make sure that nothing sneaks out
                        opt.overflow = this.style.overflow;
                    }

                    if (jQuery.isArray(prop[p])) {
                        // Create (if needed) and add to specialEasing
                        (opt.specialEasing = opt.specialEasing || {})[p] = prop[p][1];
                        prop[p] = prop[p][0];
                    }
                }

                if (opt.overflow != null) {
                    this.style.overflow = "hidden";
                }

                opt.curAnim = jQuery.extend({}, prop);

                jQuery.each(prop, function(name, val) {
                    var e = new jQuery.fx(self, opt, name);

                    if (rfxtypes.test(val)) {
                        e[val === "toggle" ? hidden ? "show" : "hide" : val](prop);

                    } else {
                        var parts = rfxnum.exec(val),
                            start = e.cur(true) || 0;

                        if (parts) {
                            var end = parseFloat(parts[2]),
                                unit = parts[3] || "px";

                            // We need to compute starting value
                            if (unit !== "px") {
                                self.style[name] = (end || 1) + unit;
                                start = ((end || 1) / e.cur(true)) * start;
                                self.style[name] = start + unit;
                            }

                            // If a +=/-= token was provided, we're doing a relative animation
                            if (parts[1]) {
                                end = ((parts[1] === "-=" ? -1 : 1) * end) + start;
                            }

                            e.custom(start, end, unit);

                        } else {
                            e.custom(start, val, "");
                        }
                    }
                });

                // For JS strict compliance
                return true;
            });
        },

        stop: function(clearQueue, gotoEnd) {
            var timers = jQuery.timers;

            if (clearQueue) {
                this.queue([]);
            }

            this.each(function() {
                // go in reverse order so anything added to the queue during the loop is ignored
                for (var i = timers.length - 1; i >= 0; i--) {
                    if (timers[i].elem === this) {
                        if (gotoEnd) {
                            // force the next step to be the last
                            timers[i](true);
                        }

                        timers.splice(i, 1);
                    }
                }
            });

            // start the next in the queue if the last step wasn't forced
            if (!gotoEnd) {
                this.dequeue();
            }

            return this;
        }

    });

    // Generate shortcuts for custom animations
    jQuery.each({
        slideDown: genFx("show", 1),
        slideUp: genFx("hide", 1),
        slideToggle: genFx("toggle", 1),
        fadeIn: { opacity: "show" },
        fadeOut: { opacity: "hide" }
    }, function(name, props) {
        jQuery.fn[name] = function(speed, callback) {
            return this.animate(props, speed, callback);
        };
    });

    jQuery.extend({
        speed: function(speed, easing, fn) {
            var opt = speed && typeof speed === "object" ? speed : {
                complete: fn || !fn && easing ||
                    jQuery.isFunction(speed) && speed,
                duration: speed,
                easing: fn && easing || easing && !jQuery.isFunction(easing) && easing
            };

            opt.duration = jQuery.fx.off ? 0 : typeof opt.duration === "number" ? opt.duration :
                jQuery.fx.speeds[opt.duration] || jQuery.fx.speeds._default;

            // Queueing
            opt.old = opt.complete;
            opt.complete = function() {
                if (opt.queue !== false) {
                    jQuery(this).dequeue();
                }
                if (jQuery.isFunction(opt.old)) {
                    opt.old.call(this);
                }
            };

            return opt;
        },

        easing: {
            linear: function(p, n, firstNum, diff) {
                return firstNum + diff * p;
            },
            swing: function(p, n, firstNum, diff) {
                return ((-Math.cos(p * Math.PI) / 2) + 0.5) * diff + firstNum;
            }
        },

        timers: [],

        fx: function(elem, options, prop) {
            this.options = options;
            this.elem = elem;
            this.prop = prop;

            if (!options.orig) {
                options.orig = {};
            }
        }

    });

    jQuery.fx.prototype = {
        // Simple function for setting a style value
        update: function() {
            if (this.options.step) {
                this.options.step.call(this.elem, this.now, this);
            }

            (jQuery.fx.step[this.prop] || jQuery.fx.step._default)(this);

            // Set display property to block for height/width animations
            if ((this.prop === "height" || this.prop === "width") && this.elem.style) {
                this.elem.style.display = "block";
            }
        },

        // Get the current size
        cur: function(force) {
            if (this.elem[this.prop] != null && (!this.elem.style || this.elem.style[this.prop] == null)) {
                return this.elem[this.prop];
            }

            var r = parseFloat(jQuery.css(this.elem, this.prop, force));
            return r && r > -10000 ? r : parseFloat(jQuery.curCSS(this.elem, this.prop)) || 0;
        },

        // Start an animation from one number to another
        custom: function(from, to, unit) {
            this.startTime = now();
            this.start = from;
            this.end = to;
            this.unit = unit || this.unit || "px";
            this.now = this.start;
            this.pos = this.state = 0;

            var self = this;

            function t(gotoEnd) {
                return self.step(gotoEnd);
            }

            t.elem = this.elem;

            if (t() && jQuery.timers.push(t) && !timerId) {
                timerId = setInterval(jQuery.fx.tick, 13);
            }
        },

        // Simple 'show' function
        show: function() {
            // Remember where we started, so that we can go back to it later
            this.options.orig[this.prop] = jQuery.style(this.elem, this.prop);
            this.options.show = true;

            // Begin the animation
            // Make sure that we start at a small width/height to avoid any
            // flash of content
            this.custom(this.prop === "width" || this.prop === "height" ? 1 : 0, this.cur());

            // Start by showing the element
            jQuery(this.elem).show();
        },

        // Simple 'hide' function
        hide: function() {
            // Remember where we started, so that we can go back to it later
            this.options.orig[this.prop] = jQuery.style(this.elem, this.prop);
            this.options.hide = true;

            // Begin the animation
            this.custom(this.cur(), 0);
        },

        // Each step of an animation
        step: function(gotoEnd) {
            var t = now(),
                done = true;

            if (gotoEnd || t >= this.options.duration + this.startTime) {
                this.now = this.end;
                this.pos = this.state = 1;
                this.update();

                this.options.curAnim[this.prop] = true;

                for (var i in this.options.curAnim) {
                    if (this.options.curAnim[i] !== true) {
                        done = false;
                    }
                }

                if (done) {
                    if (this.options.display != null) {
                        // Reset the overflow
                        this.elem.style.overflow = this.options.overflow;

                        // Reset the display
                        var old = jQuery.data(this.elem, "olddisplay");
                        this.elem.style.display = old ? old : this.options.display;

                        if (jQuery.css(this.elem, "display") === "none") {
                            this.elem.style.display = "block";
                        }
                    }

                    // Hide the element if the "hide" operation was done
                    if (this.options.hide) {
                        jQuery(this.elem).hide();
                    }

                    // Reset the properties, if the item has been hidden or shown
                    if (this.options.hide || this.options.show) {
                        for (var p in this.options.curAnim) {
                            jQuery.style(this.elem, p, this.options.orig[p]);
                        }
                    }

                    // Execute the complete function
                    this.options.complete.call(this.elem);
                }

                return false;

            } else {
                var n = t - this.startTime;
                this.state = n / this.options.duration;

                // Perform the easing function, defaults to swing
                var specialEasing = this.options.specialEasing && this.options.specialEasing[this.prop];
                var defaultEasing = this.options.easing || (jQuery.easing.swing ? "swing" : "linear");
                this.pos = jQuery.easing[specialEasing || defaultEasing](this.state, n, 0, 1, this.options.duration);
                this.now = this.start + ((this.end - this.start) * this.pos);

                // Perform the next step of the animation
                this.update();
            }

            return true;
        }
    };

    jQuery.extend(jQuery.fx, {
        tick: function() {
            var timers = jQuery.timers;

            for (var i = 0; i < timers.length; i++) {
                if (!timers[i]()) {
                    timers.splice(i--, 1);
                }
            }

            if (!timers.length) {
                jQuery.fx.stop();
            }
        },

        stop: function() {
            clearInterval(timerId);
            timerId = null;
        },

        speeds: {
            slow: 600,
            fast: 200,
            // Default speed
            _default: 400
        },

        step: {
            opacity: function(fx) {
                jQuery.style(fx.elem, "opacity", fx.now);
            },

            _default: function(fx) {
                if (fx.elem.style && fx.elem.style[fx.prop] != null) {
                    fx.elem.style[fx.prop] = (fx.prop === "width" || fx.prop === "height" ? Math.max(0, fx.now) : fx.now) + fx.unit;
                } else {
                    fx.elem[fx.prop] = fx.now;
                }
            }
        }
    });

    if (jQuery.expr && jQuery.expr.filters) {
        jQuery.expr.filters.animated = function(elem) {
            return jQuery.grep(jQuery.timers, function(fn) {
                return elem === fn.elem;
            }).length;
        };
    }

    function genFx(type, num) {
        var obj = {};

        jQuery.each(fxAttrs.concat.apply([], fxAttrs.slice(0, num)), function() {
            obj[this] = type;
        });

        return obj;
    }
    if ("getBoundingClientRect" in document.documentElement) {
        jQuery.fn.offset = function(options) {
            var elem = this[0];

            if (options) {
                return this.each(function(i) {
                    jQuery.offset.setOffset(this, options, i);
                });
            }

            if (!elem || !elem.ownerDocument) {
                return null;
            }

            if (elem === elem.ownerDocument.body) {
                return jQuery.offset.bodyOffset(elem);
            }

            var box = elem.getBoundingClientRect(),
                doc = elem.ownerDocument,
                body = doc.body,
                docElem = doc.documentElement,
                clientTop = docElem.clientTop || body.clientTop || 0,
                clientLeft = docElem.clientLeft || body.clientLeft || 0,
                top = box.top + (self.pageYOffset || jQuery.support.boxModel && docElem.scrollTop || body.scrollTop) - clientTop,
                left = box.left + (self.pageXOffset || jQuery.support.boxModel && docElem.scrollLeft || body.scrollLeft) - clientLeft;

            return { top: top, left: left };
        };

    } else {
        jQuery.fn.offset = function(options) {
            var elem = this[0];

            if (options) {
                return this.each(function(i) {
                    jQuery.offset.setOffset(this, options, i);
                });
            }

            if (!elem || !elem.ownerDocument) {
                return null;
            }

            if (elem === elem.ownerDocument.body) {
                return jQuery.offset.bodyOffset(elem);
            }

            jQuery.offset.initialize();

            var offsetParent = elem.offsetParent,
                prevOffsetParent = elem,
                doc = elem.ownerDocument,
                computedStyle, docElem = doc.documentElement,
                body = doc.body,
                defaultView = doc.defaultView,
                prevComputedStyle = defaultView ? defaultView.getComputedStyle(elem, null) : elem.currentStyle,
                top = elem.offsetTop,
                left = elem.offsetLeft;

            while ((elem = elem.parentNode) && elem !== body && elem !== docElem) {
                if (jQuery.offset.supportsFixedPosition && prevComputedStyle.position === "fixed") {
                    break;
                }

                computedStyle = defaultView ? defaultView.getComputedStyle(elem, null) : elem.currentStyle;
                top -= elem.scrollTop;
                left -= elem.scrollLeft;

                if (elem === offsetParent) {
                    top += elem.offsetTop;
                    left += elem.offsetLeft;

                    if (jQuery.offset.doesNotAddBorder && !(jQuery.offset.doesAddBorderForTableAndCells && /^t(able|d|h)$/i.test(elem.nodeName))) {
                        top += parseFloat(computedStyle.borderTopWidth) || 0;
                        left += parseFloat(computedStyle.borderLeftWidth) || 0;
                    }

                    prevOffsetParent = offsetParent, offsetParent = elem.offsetParent;
                }

                if (jQuery.offset.subtractsBorderForOverflowNotVisible && computedStyle.overflow !== "visible") {
                    top += parseFloat(computedStyle.borderTopWidth) || 0;
                    left += parseFloat(computedStyle.borderLeftWidth) || 0;
                }

                prevComputedStyle = computedStyle;
            }

            if (prevComputedStyle.position === "relative" || prevComputedStyle.position === "static") {
                top += body.offsetTop;
                left += body.offsetLeft;
            }

            if (jQuery.offset.supportsFixedPosition && prevComputedStyle.position === "fixed") {
                top += Math.max(docElem.scrollTop, body.scrollTop);
                left += Math.max(docElem.scrollLeft, body.scrollLeft);
            }

            return { top: top, left: left };
        };
    }

    jQuery.offset = {
        initialize: function() {
            var body = document.body,
                container = document.createElement("div"),
                innerDiv, checkDiv, table, td, bodyMarginTop = parseFloat(jQuery.curCSS(body, "marginTop", true)) || 0,
                html = "<div style='position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;'><div></div></div><table style='position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;' cellpadding='0' cellspacing='0'><tr><td></td></tr></table>";

            jQuery.extend(container.style, { position: "absolute", top: 0, left: 0, margin: 0, border: 0, width: "1px", height: "1px", visibility: "hidden" });

            container.innerHTML = html;
            body.insertBefore(container, body.firstChild);
            innerDiv = container.firstChild;
            checkDiv = innerDiv.firstChild;
            td = innerDiv.nextSibling.firstChild.firstChild;

            this.doesNotAddBorder = (checkDiv.offsetTop !== 5);
            this.doesAddBorderForTableAndCells = (td.offsetTop === 5);

            checkDiv.style.position = "fixed", checkDiv.style.top = "20px";
            // safari subtracts parent border width here which is 5px
            this.supportsFixedPosition = (checkDiv.offsetTop === 20 || checkDiv.offsetTop === 15);
            checkDiv.style.position = checkDiv.style.top = "";

            innerDiv.style.overflow = "hidden", innerDiv.style.position = "relative";
            this.subtractsBorderForOverflowNotVisible = (checkDiv.offsetTop === -5);

            this.doesNotIncludeMarginInBodyOffset = (body.offsetTop !== bodyMarginTop);

            body.removeChild(container);
            body = container = innerDiv = checkDiv = table = td = null;
            jQuery.offset.initialize = jQuery.noop;
        },

        bodyOffset: function(body) {
            var top = body.offsetTop,
                left = body.offsetLeft;

            jQuery.offset.initialize();

            if (jQuery.offset.doesNotIncludeMarginInBodyOffset) {
                top += parseFloat(jQuery.curCSS(body, "marginTop", true)) || 0;
                left += parseFloat(jQuery.curCSS(body, "marginLeft", true)) || 0;
            }

            return { top: top, left: left };
        },

        setOffset: function(elem, options, i) {
            // set position first, in-case top/left are set even on static elem
            if (/static/.test(jQuery.curCSS(elem, "position"))) {
                elem.style.position = "relative";
            }
            var curElem = jQuery(elem),
                curOffset = curElem.offset(),
                curTop = parseInt(jQuery.curCSS(elem, "top", true), 10) || 0,
                curLeft = parseInt(jQuery.curCSS(elem, "left", true), 10) || 0;

            if (jQuery.isFunction(options)) {
                options = options.call(elem, i, curOffset);
            }

            var props = {
                top: (options.top - curOffset.top) + curTop,
                left: (options.left - curOffset.left) + curLeft
            };

            if ("using" in options) {
                options.using.call(elem, props);
            } else {
                curElem.css(props);
            }
        }
    };


    jQuery.fn.extend({
        position: function() {
            if (!this[0]) {
                return null;
            }

            var elem = this[0],

                // Get *real* offsetParent
                offsetParent = this.offsetParent(),

                // Get correct offsets
                offset = this.offset(),
                parentOffset = /^body|html$/i.test(offsetParent[0].nodeName) ? { top: 0, left: 0 } : offsetParent.offset();

            // Subtract element margins
            // note: when an element has margin: auto the offsetLeft and marginLeft
            // are the same in Safari causing offset.left to incorrectly be 0
            offset.top -= parseFloat(jQuery.curCSS(elem, "marginTop", true)) || 0;
            offset.left -= parseFloat(jQuery.curCSS(elem, "marginLeft", true)) || 0;

            // Add offsetParent borders
            parentOffset.top += parseFloat(jQuery.curCSS(offsetParent[0], "borderTopWidth", true)) || 0;
            parentOffset.left += parseFloat(jQuery.curCSS(offsetParent[0], "borderLeftWidth", true)) || 0;

            // Subtract the two offsets
            return {
                top: offset.top - parentOffset.top,
                left: offset.left - parentOffset.left
            };
        },

        offsetParent: function() {
            return this.map(function() {
                var offsetParent = this.offsetParent || document.body;
                while (offsetParent && (!/^body|html$/i.test(offsetParent.nodeName) && jQuery.css(offsetParent, "position") === "static")) {
                    offsetParent = offsetParent.offsetParent;
                }
                return offsetParent;
            });
        }
    });


    // Create scrollLeft and scrollTop methods
    jQuery.each(["Left", "Top"], function(i, name) {
        var method = "scroll" + name;

        jQuery.fn[method] = function(val) {
            var elem = this[0],
                win;

            if (!elem) {
                return null;
            }

            if (val !== undefined) {
                // Set the scroll offset
                return this.each(function() {
                    win = getWindow(this);

                    if (win) {
                        win.scrollTo(!i ? val : jQuery(win).scrollLeft(),
                            i ? val : jQuery(win).scrollTop()
                        );

                    } else {
                        this[method] = val;
                    }
                });
            } else {
                win = getWindow(elem);

                // Return the scroll offset
                return win ? ("pageXOffset" in win) ? win[i ? "pageYOffset" : "pageXOffset"] :
                    jQuery.support.boxModel && win.document.documentElement[method] ||
                    win.document.body[method] :
                    elem[method];
            }
        };
    });

    function getWindow(elem) {
        return ("scrollTo" in elem && elem.document) ?
            elem :
            elem.nodeType === 9 ?
            elem.defaultView || elem.parentWindow :
            false;
    }
    // Create innerHeight, innerWidth, outerHeight and outerWidth methods
    jQuery.each(["Height", "Width"], function(i, name) {

        var type = name.toLowerCase();

        // innerHeight and innerWidth
        jQuery.fn["inner" + name] = function() {
            return this[0] ?
                jQuery.css(this[0], type, false, "padding") :
                null;
        };

        // outerHeight and outerWidth
        jQuery.fn["outer" + name] = function(margin) {
            return this[0] ?
                jQuery.css(this[0], type, false, margin ? "margin" : "border") :
                null;
        };

        jQuery.fn[type] = function(size) {
            // Get window width or height
            var elem = this[0];
            if (!elem) {
                return size == null ? null : this;
            }

            if (jQuery.isFunction(size)) {
                return this.each(function(i) {
                    var self = jQuery(this);
                    self[type](size.call(this, i, self[type]()));
                });
            }

            return ("scrollTo" in elem && elem.document) ? // does it walk and quack like a window?
                // Everyone else use document.documentElement or document.body depending on Quirks vs Standards mode
                elem.document.compatMode === "CSS1Compat" && elem.document.documentElement["client" + name] ||
                elem.document.body["client" + name] :

                // Get document width or height
                (elem.nodeType === 9) ? // is it a document
                // Either scroll[Width/Height] or offset[Width/Height], whichever is greater
                Math.max(
                    elem.documentElement["client" + name],
                    elem.body["scroll" + name], elem.documentElement["scroll" + name],
                    elem.body["offset" + name], elem.documentElement["offset" + name]
                ) :

                // Get or set width or height on the element
                size === undefined ?
                // Get width or height on the element
                jQuery.css(elem, type) :

                // Set the width or height on the element (default to pixels if value is unitless)
                this.css(type, typeof size === "string" ? size : size + "px");
        };

    });
    // Expose jQuery to the global object
    window.jQuery = window.$ = jQuery;

})(window);


function JQueryWrapper() {

    this.init = function(selector, context) {
        return new this.jQuery.fn.init(selector, context);
    };

    this.clean = function(elems, context, fragment) {
        return this.jQuery.clean(elems, context, fragment);
    };
}

JQueryWrapper.prototype.jQuery = jQuery;

jQuery.noConflict(true); 


/*  find_matching_child  */

//Used by atom browserbot
ELEMENT_NODE_TYPE = 1;
elementFindFirstMatchingChild = function(element, selector) {

    var childCount = element.childNodes.length;
    for (var i = 0; i < childCount; i++) {
        var child = element.childNodes[i];
        if (child.nodeType == ELEMENT_NODE_TYPE) {
            if (selector(child)) {
                return child;
            }
            result = elementFindFirstMatchingChild(child, selector);
            if (result) {
                return result;
            }
        }
    }
    return null;
}


/*  tools  */

//Used by locatorbuilder
function exactMatchPattern(string) {
    if (string != null && (string.match(/^\w*:/) || string.indexOf('?') >= 0 || string.indexOf('*') >= 0)) {
        return "exact:" + string;
    } else {
        return string;
    }
}

//Used by locatorbuilder
function classObservable(clazz) {
    clazz.addObserver = function(observer) {
        if (!this.observers) this.observers = [];
        this.observers.push(observer);
    };

    clazz.removeObserver = function(observer) {
        if (!this.observers) return;
        this.observers["delete"](observer);
    };

    clazz.notify = function(event) {
        if (this.log) {
            this.log.debug("notify " + event);
        }
        if (!this.observers) return;
        var args = [];
        for (var i = 1; i < arguments.length; i++) {
            args.push(arguments[i]);
        }
        for (var i = 0; i < this.observers.length; i++) {
            var observer = this.observers[i];
            if (observer[event]) {
                try {
                    observer[event].apply(observer, args);
                } catch (e) {
                    //continue with the rest even if one observer fails
                }
            }
        }
    };
}


/*  selenium-browserdetect  */

//Used by htmlutil, api, browserbot
var BrowserVersion = function() {
    this.name = navigator.appName;

    if (navigator.userAgent.indexOf('Mac OS X') != -1) {
        this.isOSX = true;
    }

    if (navigator.userAgent.indexOf('Windows NT 6') != -1) {
        this.isVista = true;
    }

    var _getQueryParameter = function(searchKey) {
        var str = location.search.substr(1);
        if (str == null) return null;
        var clauses = str.split('&');
        for (var i = 0; i < clauses.length; i++) {
            var keyValuePair = clauses[i].split('=', 2);
            var key = unescape(keyValuePair[0]);
            if (key == searchKey) {
                return unescape(keyValuePair[1]);
            }
        }
        return null;
    };

    var self = this;

    var checkChrome = function() {
        var loc = window.document.location.href;
        try {
            loc = window.top.document.location.href;
            if (/^chrome:\/\//.test(loc)) {
                self.isChrome = true;
            } else {
                self.isChrome = false;
            }
        } catch (e) {
            // can't see the top (that means we might be chrome, but it's impossible to be sure)
            self.isChromeDetectable = "no, top location couldn't be read in this window";
            if (_getQueryParameter('thisIsChrome')) {
                self.isChrome = true;
            } else {
                self.isChrome = false;
            }
        }


    };



    if (this.name == "Microsoft Internet Explorer") {
        this.browser = BrowserVersion.IE;
        this.isIE = true;
        try {
            if (window.top.SeleniumHTARunner && window.top.document.location.pathname.match(/.hta$/i)) {
                this.isHTA = true;
            }
        } catch (e) {
            this.isHTADetectable = "no, top location couldn't be read in this window";
            if (_getQueryParameter('thisIsHTA')) {
                self.isHTA = true;
            } else {
                self.isHTA = false;
            }
        }
        if (navigator.appVersion.match(/MSIE 6.0/)) {
            this.isIE6 = true;
        }
        if ("0" == navigator.appMinorVersion) {
            this.preSV1 = true;
            if (this.isIE6) {
                this.appearsToBeBrokenInitialIE6 = true;
            }
        }
        return;
    }

    
    if (navigator.userAgent.indexOf('Chrome/') != -1) {
        this.browser = BrowserVersion.GOOGLECHROME;
        this.isGoogleChrome = true;
        this.isGecko = true;
        this.khtml = true;
        return;
    }

    if (navigator.userAgent.indexOf('Safari') != -1) {
        this.browser = BrowserVersion.SAFARI;
        this.isSafari = true;
        this.khtml = true;
        return;
    }

    if (navigator.userAgent.indexOf('Konqueror') != -1) {
        this.browser = BrowserVersion.KONQUEROR;
        this.isKonqueror = true;
        this.khtml = true;
        return;
    }

    if (navigator.userAgent.indexOf('Firefox') != -1 ||
        navigator.userAgent.indexOf('Namoroka') != -1 ||
        navigator.userAgent.indexOf('Shiretoko') != -1) {
        this.browser = BrowserVersion.FIREFOX;
        this.isFirefox = true;
        this.isGecko = true;
        var result = /.*[Firefox|Namoroka|Shiretoko]\/([\d\.]+).*/.exec(navigator.userAgent);
        if (result) {
            this.firefoxVersion = result[1];
        }
        checkChrome();
        return;
    }

    if (navigator.userAgent.indexOf('Gecko') != -1) {
        this.browser = BrowserVersion.MOZILLA;
        this.isMozilla = true;
        this.isGecko = true;
        checkChrome();
        return;
    }

    this.browser = BrowserVersion.UNKNOWN;
};

BrowserVersion.IE = "IE";
BrowserVersion.KONQUEROR = "Konqueror";
BrowserVersion.SAFARI = "Safari";
BrowserVersion.FIREFOX = "Firefox";
BrowserVersion.MOZILLA = "Mozilla";
BrowserVersion.GOOGLECHROME = "Google Chrome";
BrowserVersion.UNKNOWN = "Unknown";

var browserVersion = new BrowserVersion();



function Zeuz(ox, od, nd) {
    var op = new DOMParser();
    this.od = od;
    this.odre = op.parseFromString(this.od, "text/html");

    var np = new DOMParser();
    this.nd = nd;
    this.ndre = np.parseFromString(this.nd, "text/html");

    this.ox = ox;
    var r = this.odre.evaluate(this.ox, this.odre, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
    this.oe = r.singleNodeValue;

    this.tdt = null;
    this.adt = null;
}

Zeuz.prototype.l = function() {
    if (this.tdt == null) {
        this.tdt = this.gtdt();
    }
    if (this.adt == null) {
        this.adt = this.gadt();
    }
    this.umtr();

    var mse = this.gmse();
    var nx = this.gex(mse);

    return nx;
};

Zeuz.prototype.gtdt = function() {
    var otc = new Map();
    var otdt = new Map();
    var oae = this.odre.getElementsByTagName("*");

    for (var i = 0, oaes = oae.length; i < oaes; i++) {
        var tn = oae[i].tagName;
        var c = 0;

        if (otdt.has(tn)) {
            c = otdt.get(tn);
        }
        otdt.set(tn, c + 1);
    }

    for (var tn of otdt.keys()) {
        var tc = otdt.get(tn);
        var dv = 1.0 / tc;

        otc.set(tn, tc);
        otdt.set(tn, dv);
    }


    var ntc = new Map();
    var ntdt = new Map();
    var nae = this.ndre.getElementsByTagName("*");

    for (var i = 0, naes = nae.length; i < naes; i++) {
        var tn = nae[i].tagName;
        var c = 0;

        if (ntdt.has(tn)) {
            c = ntdt.get(tn);
        }
        ntdt.set(tn, c + 1);
    }

    for (var tn of ntdt.keys()) {
        var tc = ntdt.get(tn);
        var dv = 1.0 / tc;

        ntc.set(tn, tc);
        ntdt.set(tn, dv);
    }

    var atdt = new Map();

    for (var otn of otdt.keys()) {
        var tc = otdt.get(otn) / 2.0;

        atdt.set(otn, tc);
    }

    for (var ntn of ntdt.keys()) {
        if (atdt.has(ntn)) {
            var tc = atdt.get(ntn) + (ntdt.get(ntn) / 2.0);

            atdt.set(ntn, tc);
        } else {
            var tc = ntdt.get(ntn) / 2.0;

            atdt.set(ntn, tc);
        };
    }

    return atdt;
};

Zeuz.prototype.gadt = function() {
    var oac = new Map();
    var oadt = new Map();
    var oavdt = new Map();
    var oae = this.odre.getElementsByTagName("*");

    for (var i = 0, oaes = oae.length; i < oaes; i++) {
        var ano = oae[i].attributes.length;

        for (var j = 0; j < ano; j++) {
            var an = oae[i].attributes[j].name;
            var av = oae[i].attributes[j].value;
            var c = 0;

            if (oadt.has(an)) {
                c = oadt.get(an);
            }
            oadt.set(an, c + 1);


            var cvnos = new Set();

            if (oavdt.has(an)) {
                cvnos = oavdt.get(an);
            }
            cvnos.add(av);
            oavdt.set(an, cvnos);
        };
    }

    for (var an of oadt.keys()) {
        var ac = oadt.get(an);
        var avc = oavdt.get(an).size();
        var dv = avc / ac;

        oac.set(an, ac);
        oadt.set(an, dv);
    }


    var nac = new Map();
    var nadt = new Map();
    var navdt = new Map();
    var nae = this.ndre.getElementsByTagName("*");

    for (var i = 0, naes = nae.length; i < naes; i++) {
        var ano = nae[i].attributes.length;

        for (var j = 0; j < ano; j++) {
            var an = nae[i].attributes[j].name;
            var av = nae[i].attributes[j].value;
            var c = 0;

            if (nadt.has(an)) {
                c = nadt.get(an);
            }
            nadt.set(an, c + 1);


            var cvnos = new Set();
            if (navdt.has(an)) {
                cvnos = navdt.get(an);
            }
            cvnos.add(av);
            navdt.set(an, cvnos);
        };
    }

    for (var an of nadt.keys()) {
        var ac = nadt.get(an);
        var avc = navdt.get(an).size();
        var dv = avc / ac;

        nac.set(an, ac);
        nadt.set(an, dv);
    }


    var aadt = new Map();

    for (var oan of oadt.keys()) {
        var ac = oadt.get(oan) / 2.0;

        aadt.set(oan, ac);
    }

    for (var nan of nadt.keys()) {
        if (aadt.has(nan)) {
            var ac = aadt.get(nan) + (nadt.get(nan) / 2.0);

            aadt.set(nan, ac);
        } else {
            var ac = nadt.get(nan) / 2.0;

            aadt.set(nan, ac);
        };
    }

    return aadt;
};

Zeuz.prototype.gmse = function() {
    var ms = 0.0;
    var me = null;
    var ae = this.ndre.getElementsByTagName("*");

    for (var c = 0, aes = ae.length; c < aes; c++) {
        if (ae[c] == null) {
            continue;
        }

        var s = this.gtes(this.oe, ae[c]);
        if (s > ms) {
            ms = s;
            me = ae[c];
        } else if (s == ms) {
            if (this.gex(ae[c]) == this.gex(this.oe)) {
                ms = s;
                me = ae[c];
            }
        }
    }

    return me;
};

Zeuz.prototype.gtes = function(oe, ne) {
    var ts = this.gts(oe, ne);
    var as = this.gas(oe, ne);
    var cpas = this.gcpas(oe, ne);
    var cprs = this.gcprs(oe, ne);
    var cns = this.gcns(oe, ne);
    var ccs = this.gccs(oe, ne);
    var r = this.gr(oe, ne);
    var w = this.gw(r);
    var v = Array(ts, as, cpas, cprs, cns, ccs);
    var tv = this.gtv(w, v);

    return tv;
};

Zeuz.prototype.gts = function(oe, ne) {
    var ot = oe.textContent.toLowerCase();
    var nt = ne.textContent.toLowerCase();

    if (ot.length > 100) {
        ot = ot.substring(0, 100);
    }
    if (nt.length > 100) {
        nt = nt.substring(0, 100);
    }


    var ml = Math.max(ot.length, nt.length);
    var ed = this.ged(ot, nt);

    if (ml < 1) {
        ml = 1;
    }

    return (1.0 - (ed / ml));
};

Zeuz.prototype.ged = function(t1, t2) {
    if (t1.length === 0) {
        return t2.length;
    }
    if (t2.length === 0) {
        return t1.length;
    }

    var m = [];

    for (var i = 0; i <= t2.length; i++) {
        m[i] = [i];
    }

    for (var j = 0; j <= t1.length; j++) {
        m[0][j] = j;
    }

    for (var i = 1; i <= t2.length; i++) {
        for (var j = 1; j <= t1.length; j++) {
            if (t2.charAt(i - 1) == t1.charAt(j - 1)) {
                m[i][j] = m[i - 1][j - 1];
            } else {
                m[i][j] = Math.min(m[i - 1][j - 1] + 1,
                    Math.min(m[i][j - 1] + 1,
                        m[i - 1][j] + 1));
            };
        }
    }

    return m[t2.length][t1.length];
};

Zeuz.prototype.gas = function(oe, ne) {
    if (oe == null && ne == null) {
        return 1.0;
    }
    if (oe == null || ne == null) {
        return 0.0;
    }


    var oeas = oe.attributes;
    var ota = document.createAttribute("taaNaaa");
    ota.value = oe.tagName;
    oeas.setNamedItem(ota);

    var neas = ne.attributes;
    var nta = document.createAttribute("taaNaaa");
    nta.value = ne.tagName;
    neas.setNamedItem(nta);

    var asm = new Map();

    for (var i = 0; i < oeas.length; i++) {
        if (neas.getNamedItem(oeas[i].name) != null) {
            var sv = 0;

            if (oeas[i].value == neas.getNamedItem(oeas[i].name).value) {
                sv = 1;
            }

            if (oeas[i].name == "taaNaaa") {
                asm.set(oeas[i].name + oeas[i].value, sv);
            } else {
                asm.set(oeas[i].name, sv);
            }
        } else if (oeas[i].name == "taaNaaa") {
            var sv = 0;

            if (oe.tagName == ne.tagName) {
                sv = 1;
            }

            asm.set(oeas[i].name + oeas[i].value, sv);
        }
    }

    var dp = this.gdp(asm);
    var an = this.gan(oeas, neas);
    var cs = 1.0;

    if (dp / an < 1) {
        cs = dp / an;
    }

    return cs;
};

Zeuz.prototype.gdp = function(asm) {
    var s = 0.0;

    for (var an of asm.keys()) {
        var sv = asm.get(an);
        var w = 0.0;

        if (an.length > 7 && an.substring(0, 7) == "taaNaaa") {
            w = this.tdt.get(an.substring(7));
        } else {
            w = this.adt.get(an);
        }
        s += w * w * sv;
    }

    return s;
};

Zeuz.prototype.gan = function(a1, a2) {
    var s = 0.0;

    for (var i = 0; i < a1.length; i++) {
        var w = 0.0;

        if (a1[i].name == "taaNaaa") {
            w = this.tdt.get(a1[i].value);
        } else {
            w = this.adt.get(a1[i].name);
        }
        s += w * w;
    }

    for (var i = 0; i < a2.length; i++) {
        if (a2.getNamedItem(a1.name) != null) {
            var w = 0.0;

            if (a2[i].name == "taaNaaa") {
                w = this.tdt.get(a2[i].value);
            } else {
                w = this.adt.get(a2[i].name);
            }
            s += w * w;
        }
    }

    return s;
};

Zeuz.prototype.gcpas = function(oe, ne) {
    var opae = oe.parentElement;
    var npae = ne.parentElement;
    var pas = this.gas(opae, npae);

    return pas;
};

Zeuz.prototype.gcprs = function(oe, ne) {
    var opre = oe.previousElementSibling;
    var npre = ne.previousElementSibling;
    var prs = this.gas(opre, npre);

    return prs;
};

Zeuz.prototype.gcns = function(oe, ne) {
    var one = oe.nextElementSibling;
    var nne = ne.nextElementSibling;
    var ns = this.gas(one, nne);

    return ns;
};

Zeuz.prototype.gccs = function(oe, ne) {
    var oce = oe.children;
    var nce = ne.children;
    var oces = oce.length;
    var nces = nce.length;

    if (oces == 0 && nces == 0) {
        return 1.0;
    }
    if (oces == 0 || nces == 0) {
        return 0.0;
    }


    var mces = Math.min(oces, nces);
    var cs = 0.0;

    for (var i = 0; i < mces; i++) {
        cs += this.gas(oce[i], nce[i]);
    }

    cs /= (Math.sqrt(oces) * Math.sqrt(nces));
    if (cs > 1) {
        cs = 1.0;
    }

    return cs;
};

Zeuz.prototype.gr = function(oe, ne) {
    var ra = new Array(6);

    var otlr = oe.textContent.length;
    ra[0] = this.lo(otlr, 1.0 / 3.0);

    ra[1] = this.lo((oe.attributes.length + ne.attributes.length) / 2.0, 1.0);

    var opae = oe.parentElement;
    var npae = ne.parentElement;
    var opaeal = 0;
    var npaeal = 0;
    if (opae != null) {
        opaeal = opae.attributes.length;
    }
    if (npae != null) {
        npaeal = npae.attributes.length;
    }
    ra[2] = this.lo((opaeal + npaeal) / 2.0, 1.0);

    var opre = oe.previousElementSibling;
    var npre = ne.previousElementSibling;
    var opreal = 0;
    var npreal = 0;
    if (opre != null) {
        opreal = opre.attributes.length;
    }
    if (npre != null) {
        npreal = npre.attributes.length;
    }
    ra[3] = this.lo((opreal + npreal) / 2.0, 1.0);

    var one = oe.nextElementSibling;
    var nne = ne.nextElementSibling;
    var oneal = 0;
    var nneal = 0;
    if (one != null) {
        oneal = one.attributes.length;
    }
    if (nne != null) {
        nneal = nne.attributes.length;
    }
    ra[4] = this.lo((oneal + nneal) / 2.0, 1.0);

    ra[5] = this.lo((oe.children.length + ne.children.length) / 2.0, 1.0);

    return ra;
};

Zeuz.prototype.lo = function(x, k) {
    return (2.0 / (1.0 + Math.exp(-x * k))) - 1.0;
};

Zeuz.prototype.gw = function(r) {
    var wa = new Array(6);
    var s = 0.0;

    r[0] *= 0.35;
    r[1] *= 0.35;
    r[2] *= 0.05;
    r[3] *= 0.25;
    r[4] *= 0.25;
    r[5] *= 0.75;
    for (var i = 0; i < r.length; i++) {
        s += r[i];
    }

    for (var i = 0; i < r.length; i++) {
        wa[i] = r[i] / s;
    }

    return wa;
};

Zeuz.prototype.gtv = function(w, v) {
    var fv = 0.0;

    for (var i = 0; i < v.length; i++) {
        fv += v[i] * w[i];
    }

    return fv;
};

Zeuz.prototype.gex = function(e) {
    if (e == null) {
        return "null";
    }
    if (e.parentElement == null) {
        return "/" + e.tagName;
    }


    var se = e.parentElement.children;
    var tc = 0;
    var ttc = 0;
    var ifd = false;

    for (var i = 0; i < se.length; i++) {
        if (se[i].tagName == e.tagName && !ifd) {
            tc++;
            ttc++;
        } else if (se[i].tagName == e.tagName) {
            ttc++;
        }
        if (se[i] == e) {
            ifd = true;
        }
    }

    if (ttc > 1) {
        return this.gex(e.parentElement) + "/" + e.tagName + "[" + tc + "]";
    }

    return this.gex(e.parentElement) + "/" + e.tagName;
};

Zeuz.prototype.umtr = function() {
    var oae = this.odre.getElementsByTagName("*");
    var nae = this.ndre.getElementsByTagName("*");

    for (var c = 0, oaes = oae.length; c < oaes; c++) {
        if (oae[c] == null) {
            continue;
        }
        if (oae[c].childNodes.length != 0) {
            if (oae[c].firstChild.nodeType != 3) {
                continue;
            }
        }

        var ot = "";
        if (oae[c].childNodes.length == 0) {
            ot = oae[c].textContent;
        } else {
            ot = oae[c].firstChild.nodeValue.trim();
        }
        if (ot == "") {
            if (oae[c].tagName == "input" && oae[c].hasAttribute("type") && ((oae[c].getAttribute("type") == "submit") || (oae[c].getAttribute("type") == "button")) && oae[c].hasAttribute("value")) {
                if (oae[c].childNodes.length == 0) {
                    oae[c].textContent = oae[c].getAttribute("value");
                    ot = oae[c].textContent;
                } else {
                    oae[c].firstChild.nodeValue = oae[c].getAttribute("value");
                    ot = oae[c].firstChild.nodeValue;
                }
                oae[c].removeAttribute("value");
            }
            if (ot == "" && oae[c].hasAttribute("title")) {
                if (oae[c].childNodes.length == 0) {
                    oae[c].textContent = oae[c].getAttribute("title");
                    ot = oae[c].textContent;
                } else {
                    oae[c].firstChild.nodeValue = oae[c].getAttribute("title");
                    ot = oae[c].firstChild.nodeValue;
                }
                oae[c].removeAttribute("title");
            }
            if (ot == "" && oae[c].hasAttribute("alt")) {
                if (oae[c].childNodes.length == 0) {
                    oae[c].textContent = oae[c].getAttribute("alt");
                    ot = oae[c].textContent;
                } else {
                    oae[c].firstChild.nodeValue = oae[c].getAttribute("alt");
                    ot = oae[c].firstChild.nodeValue;
                }
                oae[c].removeAttribute("alt");
            }
        }
    }

    for (var c = 0, naes = nae.length; c < naes; c++) {
        if (nae[c] == null) {
            continue;
        }
        if (nae[c].childNodes.length != 0) {
            if (nae[c].firstChild.nodeType != 3) {
                continue;
            }
        }

        var nt = "";
        if (nae[c].childNodes.length == 0) {
            nt = nae[c].textContent;
        } else {
            nt = nae[c].firstChild.nodeValue.trim();
        }
        if (nt == "") {
            if (nae[c].tagName == "input" && nae[c].hasAttribute("type") && ((nae[c].getAttribute("type") == "submit") || (nae[c].getAttribute("type") == "button")) && nae[c].hasAttribute("value")) {
                if (nae[c].childNodes.length == 0) {
                    nae[c].textContent = nae[c].getAttribute("value");
                    nt = nae[c].textContent;
                } else {
                    nae[c].firstChild.nodeValue = nae[c].getAttribute("value");
                    nt = nae[c].firstChild.nodeValue;
                }
                nae[c].removeAttribute("value");
            }
            if (nt == "" && nae[c].hasAttribute("title")) {
                if (nae[c].childNodes.length == 0) {
                    nae[c].textContent = nae[c].getAttribute("title");
                    nt = nae[c].textContent;
                } else {
                    nae[c].firstChild.nodeValue = nae[c].getAttribute("title");
                    nt = nae[c].firstChild.nodeValue;
                }
                nae[c].removeAttribute("title");
            }
            if (nt == "" && nae[c].hasAttribute("alt")) {
                if (nae[c].childNodes.length == 0) {
                    nae[c].textContent = nae[c].getAttribute("alt");
                    nt = nae[c].textContent;
                } else {
                    nae[c].firstChild.nodeValue = nae[c].getAttribute("alt");
                    nt = nae[c].firstChild.nodeValue;
                }
                nae[c].removeAttribute("alt");
            }
        }
    }
};
