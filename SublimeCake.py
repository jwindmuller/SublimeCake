import sublime, sublime_plugin, subprocess, os, re, threading

class SublimeCakeBaseCommand:
    threads = []

    def handle_threads(self, edit, i = 0):
        next_threads = []
        for thread in self.threads:
            if thread.is_alive():
                next_threads.append(thread)
                continue
            if thread.result == False:
                continue
            else:
                self.__displayResult(thread)
        self.threads = next_threads
        if len(self.threads):
            animation = (' ' * i) + '=' + (' ' * (3-i))
            if i>3:
                animation = animation[::-1]
            self.view.set_status(
                'sublime_cake',
                'Testing [%s]' % animation
            )
            sublime.set_timeout(lambda: self.handle_threads(edit, (i+1) % 6), 500)
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

class CakephpTestCommand(SublimeCakeBaseCommand, sublime_plugin.TextCommand):
    def run(self, edit):
        sels = self.view.sel()
        for sel in sels:
            functionName = self.__fetchCurrentFunctionName(sel)
            if functionName:
                t = CakePHPTestProcess(self, functionName)
                self.threads.append( t )
                t.start()
        self.handle_threads(edit)

    def is_visible(self, args = None):
        sel = self.view.sel()[0]
        functionName = self.__fetchCurrentFunctionName(sel)
        return functionName != None and functionName[:4] == "test"

    def description(self, args = None):
        sel = self.view.sel()[0]
        functionName = self.__fetchCurrentFunctionName(sel)
        # # if functionName and functionName.substr(0,4)=='test':
        return 'Run test: ' + functionName

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

class SublimeCakeTestAll(SublimeCakeBaseCommand, sublime_plugin.TextCommand):
    def run(self, edit):
        t = CakePHPTestProcess(self)
        self.threads.append( t )
        t.start()
        self.handle_threads(edit)

class CakePHPTestProcess(threading.Thread):
    def __init__(self, command, functionName = None):

        self.result = False
        self.command = command

        params = [
            self.command.view.settings().get('php_binary_path'),
            self.__getCake2ConsolePath() + 'cake.php',
            "testsuite app",
            self.__getTestName(),
            "--debug --no-colors --stderr"
        ]

        if functionName:
            params.append("--filter")
            params.append("/%(function_name)s$/" % {"function_name" : functionName})

        params = " ".join(params)

        self.params = params
        self.functionName = functionName
        threading.Thread.__init__(self)

    def run(self):
        self.p = subprocess.Popen(self.params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.error, self.result = self.p.communicate()

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

PRINT_CONTEXT = False
DEBUG_ENABLED = True

def debug(text, context=""):
    if DEBUG_ENABLED:
        print '[toggle_single_line_css]: ' + text
    if PRINT_CONTEXT and context != "":
        print '>>> ' + context
