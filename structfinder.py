import sys, os, re

def meepers(struct, sourcecode, headerfolder):
    sourcecode = open(sourcecode, "r+")
    newfile = open("cache/structure_info.txt", "w")
    found = False

    parser(sourcecode)

    for filename in os.listdir(headerfolder):
        while(found == False):
            headerfile = open(filename, "r+")
            parser(headerfile)
        
def parser(file):
    target = "struct " + struct
    line = file.readline()
    while target not in line:
        line = file.readline()

    if target in line:
        #case of struct x {
        if '{' in line:
            structinfo = line
            structinfo = file.readline()
            while '}' not in structinfo:
                list = structinfo.split()
                text = list[0] + ": " + ''.join(list[1:]) + '\n';
                newfile.write(text)

                structinfo = file.readline()
        #case of struct x
        #{
        else:
            structinfo = file.readline()
            structinfo = file.readline()
            while '}' not in structinfo:
                list = structinfo.split()
                text = list[0] + ": " + ''.join(list[1:]) + '\n';
                newfile.write(text)

                structinfo = file.readline()

    found = True
    file.close()
    newfile.close()


meepers('apev2_hdr_ftr', 'test/structtest.c', 'a')
