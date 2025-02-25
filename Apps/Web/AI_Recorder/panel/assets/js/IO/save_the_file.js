/* Start the zeuz function */
var textFile = null,
    makeTextFile = function(text) {
        var data = new Blob([text], {
            type: 'text/html'
        });
        if (textFile !== null) {
            window.URL.revokeObjectURL(textFile);
        }
        textFile = window.URL.createObjectURL(data);
        return textFile;
    };

function downloadSuite(s_suite,callback) {
    if (s_suite) {
        var cases = s_suite.getElementsByTagName("p"),
            output = "",
            old_case = getSelectedCase();
        for (var i = 0; i < cases.length; ++i) {
            setSelectedCase(cases[i].id);
            saveNewTarget();
            output = output +
                '<table cellpadding="1" cellspacing="1" border="1">\n<thead>\n<tr><td rowspan="1" colspan="3">' +
                zeuz_testCase[cases[i].id].title +
                '</td></tr>\n</thead>\n' +
                panelToFile(document.getElementById("records-grid").innerHTML) +
                '</table>\n';
        }
        output = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" ' +
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" xml:' +
            'lang="en" lang="en">\n<head>\n\t<meta content="text/html; charset=UTF-8" http-equiv="content-type" />\n\t<title>' +
            zeuz_testSuite[s_suite.id].title +
            '</title>\n</head>\n<body>\n' +
            output +
            '</body>\n</html>';

        if (old_case) {
            setSelectedCase(old_case.id);
        } else {
            setSelectedSuite(s_suite.id);
        }

        var f_name = zeuz_testSuite[s_suite.id].file_name,
            link = makeTextFile(output);
        var downloading = browser.downloads.download({
            filename: f_name,
            url: link,
            saveAs: true,
            conflictAction: 'overwrite'
        });

        var result = function(id) {
            browser.downloads.onChanged.addListener(function downloadCompleted(downloadDelta) {
                if (downloadDelta.id == id && downloadDelta.state &&
                    downloadDelta.state.current == "complete") {
                    browser.downloads.search({
                        id: downloadDelta.id
                    }).then(function(download){
                        download = download[0];
                        f_name = download.filename.split(/\\|\//).pop();
                        zeuz_testSuite[s_suite.id].file_name = f_name;
                        zeuz_testSuite[s_suite.id].title = f_name.substring(0, f_name.lastIndexOf("."));
                        $(s_suite).find(".modified").removeClass("modified");
                        closeConfirm(false);
                        s_suite.getElementsByTagName("STRONG")[0].textContent = zeuz_testSuite[s_suite.id].title;
                        if (callback) {
                            callback();
                        }
                        browser.downloads.onChanged.removeListener(downloadCompleted);
                    })
                } else if (downloadDelta.id == id && downloadDelta.error) {
                    browser.downloads.onChanged.removeListener(downloadCompleted);
                }
            })
        };

        var onError = function(error) {
            console.log(error);
        };

        downloading.then(result, onError);
    } else {
        alert("Choose a test suite to download!");
    }
}

document.getElementById('save-testSuite').addEventListener('click', function(event) {
    event.stopPropagation();
    var s_suite = getSelectedSuite();
    downloadSuite(s_suite);
}, false);

function savelog() {
    var now = new Date();
    var date = now.getDate();
    var month = now.getMonth()+1;
    var year = now.getFullYear();
    var seconds = now.getSeconds();
    var minutes = now.getMinutes();
    var hours = now.getHours();
    var f_name = year + '-' + month + '-' + date + '-' + hours + '-' + minutes + '-' + seconds + '.html';
    var logcontext = "";
    var logcontainer = document.getElementById('logcontainer');
    logcontext =
    '<!doctype html>\n' +
    '<html>\n' +
    '<head>\n' +
    '<title>' + f_name + '</title>\n' +
    '<link href="https://fonts.googleapis.com/css?family=Roboto+Mono:400,700|Roboto:400,500,700" rel="stylesheet">\n' +
    '<style>\n' +
    '.thumbnail { max-width: 320px; max-height: 200px; }\n' +
    'h4 { font-weight: normal; font-family: \'Roboto Mono\', monospace; font-size: 11px; }\n' +
    'p.log-info { color: #333333; }\n' +
    'p.log-error { color: #EA4335; }\n' +
    '</style>\n' +
    '</head>\n' +
    '<body>\n' +
    logcontainer.innerHTML
    '</body>';
    var link = makeTextFile(logcontext);

    var downloading = browser.downloads.download({
        filename: f_name,
        url: link,
        saveAs: true,
        conflictAction: 'overwrite'
    });
}

function saveNewTarget() {
    var records = getRecordsArray();
    for (var i = 0; i < records.length; ++i) {
        var datalist = records[i].getElementsByTagName("datalist")[0];
        var options = datalist.getElementsByTagName("option");
        var target = getCommandTarget(records[i]);

        if (options.length == 1 && options[0].innerHTML == "") {
            options[0].innerHTML = escapeHTML(target);
        } else {
            var new_target = 1;
            for (var j = 0; j < options.length; ++j) {
                if (unescapeHtml(options[j].innerHTML) == target) {
                    new_target = 0;
                    break;
                }
            }

            if (new_target) {
                var new_option = document.createElement("option");
                new_option.innerHTML = escapeHTML(target);
                datalist.appendChild(new_option);
                var x = document.createTextNode("\n        ");
                datalist.appendChild(x);
            }
        }
    }
}

function panelToFile(str) {
    if (!str) {
        return null;
    }
    str = str.replace(/<div style="overflow[\s\S]+?">[\s\S]*?<\/div>/gi, "")
        .replace(/<div style="display[\s\S]+?">/gi, "")
        .replace(/<\/div>/gi, "")
        .replace(/<input[\s\S]+?>/, "")
        .replace(/<tr[\s\S]+?>/gi, "<tr>");

    var tr = str.match(/<tr>[\s\S]*?<\/tr>/gi);
    temp_str = str;
    str = "\n";
    if(tr)
    for (var i = 0; i < tr.length; ++i) {
        var pattern = tr[i].match(/([\s]*?)(?:<td[\b\s\S]*>)([\s\S]*?)(?:<\/td>)([\s]*?)(?:<td>)([\s\S]*?)(?:<datalist>)([\s\S]*?)(?:<\/datalist><\/td>)([\s]*?)(?:<td>)([\s\S]*?)(?:<\/td>)/);
        if (!pattern) {
            str = temp_str;
            break;
        }

        var option = pattern[5].match(/<option>[\s\S]*?<\/option>/gi);
        
        str = str + "<tr>" + pattern[1] + "<td>" + pattern[2] + "</td>" + pattern[3] + "<td>" + pattern[4].replace(/\n\s+/g, "") + "<datalist>";
        for (var j = 0; j < option.length; ++j) {
            option[j] = option[j].replace(/<option>/, "").replace(/<\/option>/, "");
            str = str + "<option>" + option[j] + "</option>";
        }
        str = str + "</datalist></td>" + pattern[6] + "<td>" + pattern[7] + "</td>\n</tr>\n";
    }
    str = '<tbody>' + str + '</tbody>';
    return str;
}
