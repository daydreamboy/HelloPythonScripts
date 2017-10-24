import argparse
import re


class OCProjectParser(object):
    def parseLinkMapFile(self, path):
        arch = ''
        projectname = ''
        packageDic = {}
        objectSizeDic = {}
        skipline = 0
        symbolPartStarted = False
        sectionPartStarted = False
        lineNumber = -1
        # this part should not be calculated
        startPosDataBss = ''
        for line in open(path):
            if skipline > 0:
                skipline -= 1
                continue
            # get project name
            lineNumber += 1
            if line.startswith("# Path:"):
                searchObj = re.search(ur'.*/(.*)$', line)
                if searchObj:
                    projectname = searchObj.group(1)
                else:
                    projectname = 'undefined'
                continue
            # get architecture
            if line.startswith("# Arch:"):
                arch = line.lower().replace('# arch:', '').strip('\n').strip()
                continue
            # parse object files from current project, lib, dylib and framework
            if line.startswith('['):
                matchObj = re.match(ur'(\[.*\]).*/(.*)', line)
                if matchObj:
                    oid = matchObj.group(1)
                    packageName = matchObj.group(2)
                    objectName = ''
                    subMatchObj = re.match(ur'(.*)\((.*)\)', packageName)
                    if subMatchObj:
                        packageName = subMatchObj.group(1)
                        objectName = subMatchObj.group(2)
                    if objectName:
                        if packageName in packageDic:
                            objlist = packageDic[packageName]
                            objlist.append((objectName, oid))
                        else:
                            packageDic[packageName] = [(objectName, oid)]
                continue
            # flag control
            # section part
            if line.startswith('# Sections'):
                skipline = 1
                sectionPartStarted = True
                continue
            # symbol part
            if line.startswith('# Symbols'):
                skipline = 1
                sectionPartStarted = False
                symbolPartStarted = True
                continue
            if startPosDataBss and line.startswith(startPosDataBss):
                symbolPartStarted = False
                break
            if sectionPartStarted:
                sectionInfos = line.strip('\n').split('\t')
                if sectionInfos[3] == '__bss':
                    startPosDataBss = sectionInfos[0]
                    sectionPartStarted = False
                continue
            # symbol parse
            if symbolPartStarted:
                symbolInfos = line.split('\t')
                if len(symbolInfos) < 3:
                    continue
                match = re.match(ur'(\[.*?\]).*', symbolInfos[2])
                if match:
                    key = match.group(1)
                    if key in objectSizeDic:
                        objectSizeDic[key] += int(symbolInfos[1], 16)
                    else:
                        objectSizeDic[key] = int(symbolInfos[1], 16)
        # output app size
        packageSizeDic = {}
        totalSize = 0
        for k in packageDic:
            objlist = packageDic[k]
            curPackageSize = 0
            for objInfo in objlist:
                objectName = objInfo[0]
                oid = objInfo[1]
                if oid in objectSizeDic:
                    size = objectSizeDic[oid] or 0
                else:
                    size = 0
                curPackageSize += size
            totalSize += curPackageSize
            packageSizeDic[k] = curPackageSize
        sortedDic = sorted(packageSizeDic.iteritems(), key=lambda d: d[1], reverse=True)
        return (projectname, arch, totalSize, sortedDic)


def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("filepath")
    args = argParser.parse_args()
    parser = OCProjectParser()
    result = parser.parseLinkMapFile(args.filepath)
    print 'name:\t', result[0], '\n', 'arch:\t', result[1]
    print 'totalSize:\t', result[2]
    print '#libName\tsize(Byte):'
    for k, v in result[3]:
        print k, '\t', v

if __name__ == '__main__':
    main()
