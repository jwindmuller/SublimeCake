import sublime, sublime_plugin, subprocess, os, logging, re, time, tempfile
 
class CakephpTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        logging.basicConfig(level=logging.DEBUG)
        sels = self.view.sel()
        newSelections = []
        for sel in sels:
            functionName = self.__fetchCurrentFunctionName(sel)
            if functionName:
                self.__executeTest(functionName)
    def __fetchCurrentFunctionName(self, currentSelection):
        functionName = None
        preg = re.compile('^\s+function\s+([^\(]+).*$')
        line = self.view.line(currentSelection)
        while line.a > 0:
            line = self.view.line(sublime.Region(line.a-1,line.a-1))
            lineText = self.view.substr(line)
            matches = preg.search(lineText)
            if matches:
                functionName = matches.group(1) 
                break
        return functionName
    def __executeTest(self, functionName):
        params = [os.getcwd().replace(' ', '\\ ') + os.sep + "offload.sh"
            ,self.__getCake2Console()
            ,self.__getAppPath() ,
            # self.__getCake2Console(), "-app", self.__getAppPath(),
            # "testsuite --no-colors app", 
            self.__getTestName(), 
            # ">" , self.__getAppPath() + 'random.txt'
        ]
        # params = [os.getcwd().replace(' ', '\\ ') + os.sep + "offload.sh"]
        # params = ['ls', '-la', ' > ' + self.__getAppPath() + 'random.txt']
        params = " ".join(params)
        logging.debug(params);
        # logging.debug(" ".join(params))
        logging.debug(os.getcwd())
        # subprocess.call(params, shell=True)
        # return;
        result = subprocess.call(params, shell=True)
        
        # result, e = p.communicate()
        logging.debug(result);
        # logging.debug(e)
        return
        result = params + '\n\n' + result

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
    def __getBasePath(self):
        filePath = os.path.dirname( self.view.file_name() )
        while not os.path.isdir(filePath + os.sep + 'webroot'):
            filePath = os.path.dirname( filePath )
        filePath = os.path.dirname( filePath )
        return filePath + os.sep
    def __getAppPath(self):
        return self.__getBasePath() + 'app' + os.sep
    def __getCake2Path(self):
        return self.__getBasePath() + 'lib' + os.sep + 'Cake' + os.sep
    def __getCake2Console(self):
        return '%(file_path)sConsole%(sep)scake' % \
            {"file_path": self.__getCake2Path(), "sep": os.sep}
    def __getTestName(self):
        wholeName = self.view.file_name()
        typeOfTest = os.path.basename( os.path.dirname(wholeName) )
        fileName =  os.path.basename( wholeName )
        regex = '^(.*?%s).*$' % typeOfTest
        testName = re.match(regex, fileName).group(1)
        return typeOfTest + '/' + testName
    def is_visible(self, args = None):
        sel = self.view.sel()[0]
        functionName = self.__fetchCurrentFunctionName(sel)
        return functionName != None and functionName[:4] == "test"
    def description(self, args = None):
        sel = self.view.sel()[0]
        functionName = self.__fetchCurrentFunctionName(sel)
        # # if functionName and functionName.substr(0,4)=='test':
        return 'Run test: ' + functionName

