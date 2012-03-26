import sublime, sublime_plugin, subprocess, os, re, threading

PRINT_CONTEXT = False
DEBUG_ENABLED = True
 
class CakephpTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = self.view.sel()
        threads = []
        for sel in sels:
            functionName = self.__fetchCurrentFunctionName(sel)
            if functionName:
                t = CakePHPTestProcess(self, functionName)
                threads.append( t )
                t.start()
        self.handle_threads(edit, threads)

    def handle_threads(self, edit, threads, i = 0):
        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
                continue
            if thread.result == False:
                continue
            else:
                self.__displayResult(thread)
                debug(thread.result);
        threads = next_threads
        if len(threads):
            self.view.set_status('sublime_cake', 'Testing' + ('.' * i).ljust(5) )
            sublime.set_timeout(lambda: self.handle_threads(edit, threads, (i+1) % 4), 500)
            return
        self.view.end_edit(edit)

        self.view.erase_status('sublime_cake')
        selections = len(self.view.sel())
        sublime.status_message(
            'Sublime Cake ran %s test%s' %
            (selections, '' if selections == 1 else 's')
        )

    def __displayResult(self, thread):
        result = thread.params + '\n\n' + thread.result
        result.replace("\n", "")

        if not hasattr(self, 'output_view'):
            self.output_view = self.view.window().get_output_panel("php_result")

        v = self.output_view
        v.set_scratch(True)
        v.set_read_only(False)

        edit = v.begin_edit()
        v.erase(edit, sublime.Region(0, v.size()))
        v.insert(edit, 0, result)
        v.end_edit(edit)
        v.show( v.size() )

        self.view.window().run_command("show_panel", {"panel": "output.php_result"})

    def __fetchCurrentFunctionName(self, currentSelection):
        functionName = None
        preg = re.compile('^\s+[^s]*\s*function\s+([^\(]+).*$')
        line = self.view.line(currentSelection)
        while line.a > 0:
            line = self.view.line(sublime.Region(line.a-1,line.a-1))
            lineText = self.view.substr(line)
            matches = preg.search(lineText)
            if matches:
                functionName = matches.group(1)
                break
        return functionName

    def is_visible(self, args = None):
        sel = self.view.sel()[0]
        functionName = self.__fetchCurrentFunctionName(sel)
        debug(functionName)
        return functionName != None and functionName[:4] == "test"

    def description(self, args = None):
        sel = self.view.sel()[0]
        functionName = self.__fetchCurrentFunctionName(sel)
        debug('description')
        # # if functionName and functionName.substr(0,4)=='test':
        return 'Run test: ' + functionName

class CakePHPTestProcess(threading.Thread):
    def __init__(self, command, functionName = None):

        self.result = False
        self.command = command

        params = [
            self.command.view.settings().get('php_binary_path'),
            self.__getCake2ConsolePath() + 'cake.php',
            "testsuite app",
            self.__getTestName(),
            "--debug --no-colors"
        ]

        if functionName:
            params.append("--filter")
            params.append("/^%(function_name)s$/" % {"function_name" : functionName})
        params = " ".join(params)

        self.params = params
        self.functionName = functionName
        threading.Thread.__init__(self)

    def run(self):
        self.p = subprocess.Popen(self.params, stdout=subprocess.PIPE, shell=True)
        self.result, self.error = self.p.communicate()

    def __getBasePath(self):
        filePath = os.path.dirname( self.command.view.file_name() )
        while not os.path.isdir(filePath + os.sep + 'webroot'):
            filePath = os.path.dirname( filePath )
        filePath = os.path.dirname( filePath )
        return filePath + os.sep

    def __getCake2Path(self):
        return self.__getBasePath() + 'lib' + os.sep + 'Cake' + os.sep

    def __getCake2ConsolePath(self):
        return self.__getCake2Path() + 'Console'+ os.sep

    def __getTestName(self):
        wholeName = self.command.view.file_name()
        typeOfTest = os.path.basename( os.path.dirname(wholeName) )
        fileName =  os.path.basename( wholeName )
        regex = '^(.*?%s).*$' % typeOfTest
        testName = re.match(regex, fileName).group(1)
        return typeOfTest + '/' + testName

def debug(text, context=""):
    if DEBUG_ENABLED:
        print '[toggle_single_line_css]: ' + text
    if PRINT_CONTEXT and context != "":
        print '>>> ' + context