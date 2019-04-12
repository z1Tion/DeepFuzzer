import sys
import os
import re
import utilites


class LibraryInfo:
    def __init__(self, source_dir, binary_dir, header_dir):
        self.function_list = []
        self.functions = []
        self.passed_functions = dict()
        self.source_dir = source_dir
        self.binary_dir = binary_dir
        self.header_dir = header_dir
        self.includes = []
        self.name = source_dir[source_dir.rfind("/")+1:source_dir.find(".c")]

    def function_list_gen(self):
        # gets a list of all functions using ctags
        printout = os.popen(
            "find " + self.source_dir + " -type f -name '*.[ch]' -exec ctags -x --c-kinds=f {} ';'").read()
        printout = printout.splitlines()
        print("Found " + str(len(printout)) + " functions")
        self.function_list = []

        # parses ctags output for last piece of each line
        for line in printout:
            function = line.split("           ")
            function = function[-1]
            self.function_list.append(function)

    def parse_function(self):
        for function in self.function_list:
            final = []
            split = re.split("[,()]+", function)
            for part in split:
                if re.match(r'\s', part):
                    part = part[1:]
                final.append(part)
            name = final[0].split()
            if len(name) == 2:
                fn = FnInfo(name[1])
            else:
                fn = FnInfo(name[0])

            line2 = ""
            flag = False
            final2 = final[:-1]
            for part in final2:
                if flag:
                    line2 = line2 + part + ","
                flag = True
            line2 = line2[:-1]
            fn.prototype = fn.fn_name + "(" + line2 + ")"
            fn.parse_prototype()
            fn.check_build()
            self.append_function(fn)

    def includes_gen(self):
        file = open(self.source_dir, 'r')
        line4 = ""
        for line in file:
            if "#include" in line:
                line = line.replace("\n", "").replace('\r', "")
                line4 = line4 + line + ","
        file.close()
        line4 = line4[:-1]
        line4 = line4.rstrip('\r\n')
        for include in (line4.split('\n')[0]).split(','):
            self.includes.append(include)

    def sum_passed(self):
        for function in self.functions:
            if function.build:
                self.passed_functions[function.fn_name]=function

    def build_stat(self):
        for function in self.functions:
            if function.build:
                flag = "passed"
            else:
                flag = "failed"
            print("Checking " + function.prototype + " " + flag)
        print(str(len(self.passed_functions)) + " out of " + str(
            len(self.functions)) + " functions are fuzzable by DeepFuzzer")

    def set_name(self, name):
        self.name = name

    def set_binary(self, binary_dir):
        self.binary_dir = binary_dir

    def set_source(self, source_dir):
        self.source_dir = source_dir

    def set_header(self, header_dir):
        self.header_dir = header_dir

    def append_function(self, function):
        self.functions.append(function)

    def dump_info(self):
        print(self.name)
        try:
            for fn in self.functions:
                fn.info_dump()
                print()
        except AttributeError:
            pass
        print(self.source_dir)
        print(self.binary_dir)
        print(self.header_dir)
        print(self.includes)


class FnInput:
    def __init__(self, string):
        try:
            self.var_name = re.findall(r'[\w]+$', string)[0]
            var_type = string[:string.rfind(self.var_name)]
            # var_type = re.findall(r'^[\w?\s]+', string)[0]
            var_pointer = re.findall(r'\*', var_type)
            self.pointer_num = len(var_pointer)
            if self.pointer_num != 0:
                var_type = var_type[:var_type.find("*")]
            if var_type[-1] == ' ':
                var_type = var_type[:-1]
            self.var_type = var_type
            self.build = True
        except IndexError:
            # print("Not Support Yet")
            self.build = False
            pass

    def input_dump(self):
        print('    Type: ' + self.var_type)
        print('    Pointer: ' + str(self.pointer_num))
        print('    Name: ' + self.var_name)
        print('')


class FnInfo:
    def __init__(self, name):
        self.fn_name = name
        self.prototype = ""
        self.inputs = []
        self.includes = []
        self.return_type = ""
        self.build = True

    def info_dump(self):
        print(self.prototype)
        print('Function name: '+self.fn_name)
        print('Function parameters: ')
        for input_info in self.inputs:
            input_info.input_dump()
        # print('Return type: '+self.return_type)
        # print('Include: ')
        # for include in self.includes:
        #     print('    '+include)

    def parse_prototype(self):
        for para in (self.prototype.split('(')[1]).split(')')[0].split(','):
            self.inputs.append(FnInput(para))

    def check_build(self):
        for fn_input in self.inputs:
            if fn_input.build is False:
                self.build = False
                break
        if self.build is True:
            if utilites.function_checker(self) == "Error":
                self.build = False

    def write_includes(self, includes):
        self.includes = includes


def main(filename, compiledlib, includefold):
    lib_info = LibraryInfo(filename, compiledlib, includefold)
    file = open(filename, "r")
    lib_info.function_list_gen()
    lib_info.parse_function()
    lib_info.includes_gen()
    lib_info.dump_info()


if __name__ == "__main__":
    # filename = sys.argv[1]
    main(sys.argv[1],sys.argv[2],sys.argv[3])
