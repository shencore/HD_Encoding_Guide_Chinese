# -*- coding: utf-8 -*-
#-----------------------------------------
# Original Script by jamesthebard http://www.jamesthebard.net/blog/?p=125
# MOD based on BD_Chapters_0.3.py by cunhan(cunhan.cyx#gmail.com)
# 
# Environment: Python2 and Python3 are both OK.
# 运行环境：Python2/3均可
#
# changlog:
# 2012-07-21:
#       * bug fix: delete "link point"
#                  删除"link point"类型的Playlist Mark entry
# 2012-02-05:
#       * bug fix: exception occured when extract a empty playlist of some m2ts
#       *          当mpls里的m2ts的playlist为空时，处理不当而抛异常。
# 2011-12-29:
#       * add: --scene-cut, give a file contains scene cut frame number, to help script ajust qpfile/chapter output.
#                           指定一个内容为scene cut帧号的文件，辅助本脚本修正qpfile/chapter的输出。
#                           至于scene cut文件如何来，就请八仙过海吧。例如可以用taro新发布的SCDetect脚本。
#       * add: add a comment line to the end of splited qpfile, to give a hint where to trim m2ts file
#              在分割的qpfile文件某位写入一行注释，记录分割项的第一项在源m2ts的位置，以便trim。
# 2011-12-26:
#       * bug fix: error output of splited chapter/qpfile.
#                  修正分割时的输出错误
#       * bug fix: some mpls fill 00 at the end can't extract.
#                  不能抽取那些在文件尾填充00的mpls（例如白兔糖的BD）
# 2011-12-21:
#       * bug fix: fix inaccurate algo. of getting framenum.
#       * add --force-fps xxxxx/xxxx. Some source need to IVTC, then fps would change. At this time, you need to force a fps.
#       * add --time-code, it requires a v2 format timecode file. 
#         Maybe it's useful if your m2ts source have to output as VFR. Hope your good luck.
#       * add --include <5 digit number like 00001>
#         a mpls may contain serval m2ts info, but timecode of every m2ts is different in many case. 
#         so you can use this param to limit output.
#       * 修正帧号计算算法：计算出来的float帧号应该四舍五入round后再转成int，而不应该直接砍小数。
#       * 增加指定fps的参数--force-fps，格式为xxxxx/xxxx。适用于需要IVTC的30i源。
#       * 增加指定timecode的参数--time-code，要求输入为v2格式的tc。适用于需要处理成VFR的片源。
#         经过多个VFR片源测试，帧数变化后，错位的几率不小，于是此功能就权当参考吧。
#         要得到VFR后的准确qpfile，还需要使用其他方法细调。
#       * 配合--time-code增加参数--include，给定一个5位的数字，只输出该m2ts的信息。
#         mpls中一般包含多个m2ts的信息，如果片源处理成vfr的话，各个tc一般都不一样
#         因此可通过此参数限定只输出tc对应的片源的qpfile/chapterfile.
# 2011-12-20:
#       * support qpfile output, use -q/--qpfile.
#       * qpfile输出追加，参数-q/--qpfile。
# 2011-12-19: 
#       * some change of cmdline, see --help.
#       * output param -o/--output is options. if you don't set it, the script will name and save automatically to the path of *.mpls
#         if you set output, this param will be use as prefix of output file, 
#         and postfix of output file will generate by rules of script.
#       * Do not output chapter info that contains only one entry.
#       * use -n/--chapter-name to set a txt file, which content is chaptername per line. then the script will fill them to output chapter file in order.
#       * use -l/--max-length to set a max length of a chap time. Script would spilt a chapter file according to this value.
#       * support multi inputfile.
#       * 命令行参数有所变化，详见--help。
#       * 输出参数-o/--output非必需。
#         若不指定，脚本会按内置命名规则命名并保存至mpls文件同目录；
#         若指定该参数，参数值会作为输出路径的前缀，输出路径的后缀会由脚本按内置命名规则生成。
#       * 只有1个章节项的playlist不输出。
#       * -n/--chapter-name，指定一个包含章节标题的txt文件（每行一个标题，ansi/utf8均可），则脚本会按顺序填入输出文件中
#       * -l/--max-length，指定章节项的最大长度，格式hh:mm:ss。 
#         当脚本遇到时间戳大于此值的章节项时，即进行分割。分割前后的chapter均会输出。
#         此参数一般用于对付一个m2ts内含多个episode的情况
#       * 支持多个mpls输入，也就是说您可以拖放一堆mpls喂给这个脚本。
# 2011-12-16: 
#       * output one file per m2ts file(need for more test); force to output utf8(with BOM).
#       * 按m2ts输出章节文件；强制输出utf8（with BOM）。
# long long ago: 
#       * First MOD Ver., add OGM format output.
#       * OGM格式输出追加。
#-----------------------------------------

#!/usr/bin/env python
#
# HH:MM:SS.SSS - starts with 00:00:00.000

import os
import sys
import types
import traceback
import optparse
import string
import math
import codecs
import time

FrameRate = {}
FrameRate[0] = (0,0)
FrameRate[1] = (24000,1001)
FrameRate[2] = (24000,1000)
FrameRate[3] = (25000,1000)
FrameRate[4] = (30000,1001)
FrameRate[6] = (50000,1000)
FrameRate[7] = (60000,1001)

if sys.version[0:1] == '2':
    #python2
    CHAPTER_MARK = '\xff\xff\x00\x00\x00\x00'
    SEARCH_M2TS = 'M2TS'
    VIDEO_ATT_MARK = '\x05\x1b'
    PALY_MARK_TYPE = '\x01'
else:
    #python3
    CHAPTER_MARK = b'\xff\xff\x00\x00\x00\x00'
    SEARCH_M2TS = b'M2TS' 
    VIDEO_ATT_MARK = b'\x05\x1b'   
    PALY_MARK_TYPE = b'\x01'
    raw_input = input        

class ChapInfo():
    def __init__(self, pts, m2ts_index):
        self.pts = pts
        self.m2ts_index = m2ts_index
        self.splited = []
        self.splited_count = 0
        self.requirments = {}
        
    def shift_pts(self):
        if not self.pts:
            return
        offset = self.pts[0]
        self.pts = [(p-offset) for p in self.pts]
   
    def spilt(self, max_lenght):
        self.splited = []
        self.splited_count = 0
        max_length = returnTicket(options.maxlength, 0)
        max_ptsmark = 0
        self.splited_count = 0
        offset = self.pts[0]
        for x in self.pts:         
            if x >= max_ptsmark:                  
                new_pi = []
                self.splited_count += 1    
                self.splited.append(new_pi)
                max_ptsmark = x + max_length
            new_pi.append(x - offset)
        if self.splited_count == 1:
            #have no split
            self.splited.remove(new_pi)  
            self.splited_count = 0  
    
    def pts2time(self, pts):
        strtime = []
        offset = pts[0]
        for p in pts:
            strtime.append(returnTime(p, offset))
        return strtime
    
    def pts2frame(self, pts):
        frames = []
        offset = pts[0]
        for p in pts:
            frames.append(returnFrame(p, offset, self.requirments['custom_fps']))
        cut_point = returnFrame(offset, 0, self.requirments['ori_fps'])
        if cut_point:
            frames.append('#Cut Point in Original m2ts is: %d' % cut_point)
        return frames 
    
    def write_chap(self, name, strtime):
        outputfile = self.requirments['outputfile'] \
                    + '_%s_chapter' % name\
                    + self.requirments['chap_ext'] 
        output_chapter(outputfile,\
                       strtime,\
                       self.requirments['chap_type'],\
                       self.requirments['chap_name'])
        
    def write_qpfile(self, name, frames):
        outputfile = self.requirments['outputfile'] \
                    + '_%s.qpfile' % name
        output_qpfile(outputfile, frames)
            
    def get_all_pts(self):
        all_pts = []
        all_pts.append((self.requirments['m2ts_name'], self.pts))
        for count in range(self.splited_count):
            pts = self.splited[count]
            all_pts.append(('%s_%d' % (self.requirments['m2ts_name'], count+1), pts))
        return all_pts
    
    def output(self, outputqp=False):
        for p in self.get_all_pts():            
            self.write_chap(p[0], self.pts2time(p[1]))
            if outputqp:
                self.write_qpfile(p[0], self.pts2frame(p[1]))
            if self.requirments['scenecut']:
                ajusted_frames = [ajustFrame(x, self.requirments['scenecut']) \
                                  for x in self.pts2frame(p[1])]
                
                ajusted_chap_time = [time_format(frame2time(f, self.requirments['custom_fps'])) \
                                     for f in ajusted_frames \
                                     if type(f) == type(1)] 
                self.write_chap(p[0] +'_fix', ajusted_chap_time)
                self.write_qpfile(p[0]+'_fix', ajusted_frames)
                

def generateMkvXml(strtime, chapterNum, chapterName=''):
    matroskaXml = "\t\t<ChapterAtom>\n"
    matroskaXml += "\t\t\t<ChapterTimeStart>" + strtime + "</ChapterTimeStart>\n"
    matroskaXml += "\t\t\t<ChapterDisplay>\n"
    matroskaXml += "\t\t\t\t<ChapterString>" + chapterName + "</ChapterString>\n"
    matroskaXml += "\t\t\t\t<ChapterLanguage>eng</ChapterLanguage>\n"
    matroskaXml += "\t\t\t</ChapterDisplay>\n"
    matroskaXml += "\t\t</ChapterAtom>\n"
    return matroskaXml

def generateOGG(strtime, chapterNum, chapterName=''):
    formattedCN = "%02d" % chapterNum
    OGGLine = "CHAPTER%s=%s\nCHAPTER%sNAME=%s\n" %(formattedCN, strtime, formattedCN, chapterName)
    return OGGLine

def returnFrame(ptsMark, offset, fps):
    '''
    convert a ptsMark to frame number.
    '''
    ptsFreq = 45000
    ptsMark -= offset    
    if type(fps) != type((0,)):
        ptsTime = 1000 * float(ptsMark) / float(ptsFreq)
        #fps is not a tuple, it's a list of v2 timecode.
        framecount = 0
        pre_timestamp = 0.0
        for timestamp in fps:
            if ptsTime <= timestamp:
                #print framecount, pre_timestamp, timestamp, ptsTime
                #print (timestamp - ptsTime), (ptsTime - pre_timestamp)
                if (timestamp - ptsTime) <= (ptsTime - pre_timestamp):
                    return framecount
                else:
                    return framecount - 1
            framecount += 1
            pre_timestamp = timestamp
    return int(round(float(ptsMark * fps[0]) / float(ptsFreq * fps[1])) )

def ajustFrame(frame, scenecut):
    '''
    according to the given scene cut infos, ajust qpfile output.
    '''
    if type(frame) != type(1):
        return frame
    newframe = frame
    min = 50
    for sc in scenecut:
        diff = abs(sc - frame)
        if diff < min:
            min = diff
            newframe = sc
    if newframe != frame:
        print("Ajust qpfile frame: %s -> %s" % (frame, newframe))
    return newframe

def frame2time(frame, fps):
    '''
    convert a frame number to seconds.
    '''
    if type(frame) != type(1):
        return frame
    if type(fps) == type(FrameRate[0]):
        return float(frame) * fps[1] / fps[0]
    else:
        #timecode v2
        return fps[frame]/1000.0
    
def time_format(sec):
    '''
    format a seconds as hh:mm:ss.sss
    '''
    hour = math.modf(sec / 3600)
    minute = math.modf(float(hour[0]) * 60)
    sec = minute[0] * 60    
    if sec >= 10:
        return '%(hour)02d:%(minute)02d:%(second)02.3F' % {'hour': hour[1], 'minute': minute[1], 'second': sec}
    else:
        return '%(hour)02d:%(minute)02d:0%(second)02.3F' % {'hour': hour[1], 'minute': minute[1], 'second': sec}

def returnTime( ptsMark, offset ):
    ptsFreq = 45000
    ptsMark -= offset
    ptsTime = float(ptsMark) / float(ptsFreq)
    return time_format(ptsTime)

def returnTicket(str_time, offset):
    ptsFreq = 45000
    time_s = time.strptime(str_time, '%H:%M:%S')
    seconds = time_s.tm_hour * 3600 + time_s.tm_min * 60 + time_s.tm_sec
    ptsMask = seconds * ptsFreq
    return ptsMask

def str2int(str):
    res = 0
    for i in range(len(str)):
        res += ord(str[i])*256**(len(str)-i-1)
    return res
    
def get_m2ts_list(mpls):
    m2ts_list = []
    input = open(mpls, 'rb')    
    content = input.read()
    input.close()
    
    #get m2ts file list    
    pos_from = 0

    while True:            
        pos = content.find(SEARCH_M2TS, pos_from)
        if pos == -1:
            break
        m2ts_name = content[pos-5:pos+4]
        videoatt_pos = content.find(VIDEO_ATT_MARK, pos) 
        if videoatt_pos != -1:
            attr = content[videoatt_pos+2:videoatt_pos+3]
            fpstype = ord(attr) & 15
            format = ord(attr) >> 4
            fps = FrameRate.get(fpstype, 0)
        #python3
        if not type(content) == type(''):
            m2ts_name = str(m2ts_name, encoding='ascii')
        m2ts_list.append((m2ts_name, fps))
        pos_from = pos+4  
    return m2ts_list

def get_playlist(mpls):
    '''
    get playlist info
    '''
    input = open(mpls, 'rb')       
    content = input.read()
    bytelist = []
    ptsinfo = []
    multi_ptsinfo = []
    #read the 14 bytes from buttom eachtime
    #eg. 0001 yyyy xxxxxxxx FFFF 000000
    offset=0
    offset = content.rfind(CHAPTER_MARK)
    offset = len(content) - offset - 6
    
    pl_index=0
    pre_m2ts_index = -1
    
    while True:
        pl_index += 1
        input.seek(-14*pl_index-offset, 2)
        
        bytelist = []
        for x in range(14):
            bytelist.append(input.read(1))
        
        m2ts_index = str2int(bytelist[2:4])
        if m2ts_index != pre_m2ts_index:
            ptsinfo = []
            cinfo = ChapInfo(ptsinfo, m2ts_index)            
            multi_ptsinfo.append(cinfo)
            pre_m2ts_index = m2ts_index
        
        #last 6 bits: ff ff 00 00 00 00 per section
        if ord(bytelist[13]) != 0:
            break 
        if bytelist[1] == PALY_MARK_TYPE:
            ptsinfo.insert(0, str2int(bytelist[4:8]))
        
        if len(ptsinfo)>1 and ptsinfo[-1] == ptsinfo[-2]:
            ptsinfo.pop(-1)
            break
        
    for info in multi_ptsinfo:
        info.shift_pts()
            
    input.close()
    temp = []
    temp.extend(multi_ptsinfo)
    for ci in temp:
            pi = ci.pts 
            #remove playlist that contains only one entry.
            if len(pi) < 2:
                multi_ptsinfo.remove(ci)
    return multi_ptsinfo

def output_qpfile(outputfile, frames):
    print('Write: %s' % outputfile)
    output = codecs.open(outputfile, 'w')
    for x in frames:
        if type(x) == type(1):
            output.write('%d I -1\n' % x)
        else:
            output.write('9999999 I -1\n%s' % x)
    output.close()
    
def output_chapter(outputfile, strtime, chapterType, chapternames):    
    print('Write: %s' % outputfile)
    output = codecs.open(outputfile, 'w', encoding='utf-8-sig')
    
    matroskaXmlHeader = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n<Chapters>\n\t<EditionEntry>\n"
    matroskaXmlFooter = "\t</EditionEntry>\n</Chapters>"
    if chapterType == "ogm":
        matroskaXmlHeader = matroskaXmlFooter = ""
        generateLine = generateOGG
    else:
        generateLine = generateMkvXml
    output.write(matroskaXmlHeader)
    
    chap_count = 0
    for x in strtime:
        chap_count += 1
        chaptername = ''
        if chap_count <= len(chapternames):
            chaptername = chapternames[chap_count-1]
        output.write(generateLine(x, chap_count, chaptername))
    output.write(matroskaXmlFooter)
    output.close()

def get_custom_fps(options, m2ts_fps):  
    '''
    read timecode file, otherwise return default fps
    ''' 
    new_fps = m2ts_fps
    if options.force_fps is not None:
        new_fps = [int(x) for x in options.force_fps.split('/')]
        new_fps = tuple(new_fps)
    if options.timecode is not None:
        new_fps = [ float(x) \
                   for x in open(options.timecode, 'r').readlines() \
                   if x.strip() and not x.startswith('#') ]
    return new_fps
    
def get_scene_cut(options):
    '''
    read scene cut file.
    '''
    if options.scenecut is not None:
        scenecut = [ int(x) \
                    for x in open(options.scenecut, 'r').readlines() \
                    if x.strip() and not x.startswith('#') ]
        return scenecut
    return []
    
def main(mpls, options, p):    
    if mpls is None:
        p.error("no inputfile specified.")   
    
    #setting output format
    chapterType = 'ogm'
    ext = '.txt'
    if options.format is not None:
        chapterType = options.format.lower()
        if chapterType == 'xml':
            ext = '.xml'
    
    #setting output file name.
    mpls_path, mpls_name= os.path.split(os.path.splitext(mpls)[0])
    outputfile = os.path.splitext(mpls)[0]
    if options.output is not None:
        o_parta, o_ext = os.path.splitext(options.output)
        if o_ext == '.xml': 
            chapterType = 'xml'
            ext = '.xml'
        if o_ext == '.txt': 
            chapterType = 'ogm'
            ext = '.txt'
        o_path, o_name = os.path.split(o_parta)
        o_name = os.path.splitext(o_name)[0]
        if os.path.isdir(options.output):
            outputfile = os.path.join(options.output, mpls_name)
        else:           
            outputfile = os.path.join(o_path, o_name + "_%s" % mpls_name)
    
    #get chapter names provide by user.
    chapternames = []
    if options.chaptername is not None:
        set_encoding = 'utf-8-sig'
        try:
            #open with utf-8 by default
            chapternames = [c.strip() for c in codecs.open(options.chaptername, 'r', encoding=set_encoding).readlines()]
        except:
            #try to use asni, if utf-8 does not work.
            chapternames = [c.strip() for c in codecs.open(options.chaptername, 'r', encoding=sys.getfilesystemencoding()).readlines()]
        
    print('Input file: %s' % mpls)
    print('Output file: %s' % outputfile)
    print('Output format: %s' % chapterType)
    
    #get m2ts list
    m2ts_list = get_m2ts_list(mpls)
    
    #get chapter info
    multi_ptsinfo = get_playlist(mpls)
    
    if options.include is not None:
        keys = []
        keys.extend(multi_ptsinfo)
        for k in keys:
            if m2ts_list[k.m2ts_index][0] != options.include + 'M2TS':
                multi_ptsinfo.remove(k)
    
    if not len(multi_ptsinfo):
        print("No Chapter file is generated.")
        
    scenecut = get_scene_cut(options)
    
    #split
    if options.maxlength is not None:
        split_multi_ptsinfo = {}
        max_length = returnTicket(options.maxlength, 0)
        for item in multi_ptsinfo:
            item.spilt(max_length)
    
    #output chapter/qpfile info
    for cinfo in multi_ptsinfo:               
        cinfo.requirments = {}
        m2ts_name, m2ts_fps = m2ts_list[cinfo.m2ts_index] 
        cinfo.requirments['m2ts_name'] = m2ts_name
        cinfo.requirments['ori_fps'] = m2ts_fps
        
        m2ts_fps = get_custom_fps(options, m2ts_fps)
        cinfo.requirments['custom_fps'] = m2ts_fps
        
        cinfo.requirments['scenecut'] = scenecut
        cinfo.requirments['chap_type'] = chapterType
        cinfo.requirments['chap_ext'] = ext
        cinfo.requirments['chap_name'] = chapternames
        cinfo.requirments['outputfile'] = outputfile
                
        cinfo.output(outputqp=options.qpfile)


if __name__ == '__main__':
    filename = os.path.split(__file__)[1]
    p = optparse.OptionParser(description=' Deconstructs the MPLS file and converts the PTS information to create properly formatted OGM chapter file for Muxer.  This program needs the MPLS file from the BluRay disc associated with the M2TS file(s) that you are processing.',
                              prog=filename,
                              version='BluRay Chapter Converter 0.3 MOD r20111220',
                              usage='%prog [options] [input mplsfile...]')
    p.add_option('--chapter-name', '-n', action="store", help='give a template of chapter name, and script will fill them to chapter file.', dest="chaptername")
    p.add_option('--format', '-f', action="store", help='xml or ogm, default is ogm', dest="format")
    p.add_option('--output', '-o', action="store", help='set path to output chapter files.', dest="output")
    p.add_option('--qpfile', '-q', action="store_true", help='output qpfile', dest="qpfile")
    p.add_option('--force-fps', action="store", help='give a fps to override original m2ts', dest="force_fps")
    p.add_option('--time-code', action="store", help='give a v2 format timecode file', dest="timecode")
    p.add_option('--scene-cut', action="store", help='give a scene cut log file to help this script ajust qpfile', dest="scenecut")
    p.add_option('--include', action="store", help='give a five digit number of a m2ts, script will only output info files of this m2ts', dest="include")
    # p.add_option('--whole', action="store", help='output a whole chapter for mpls', dest="whole")
    p.add_option('--max-length', '-l', action="store", help='hh:mm:ss, set the max length of a chapter file, it\'s use for split a m2ts with 2 or more episode', dest="maxlength")
    (options, arguments) = p.parse_args()
    
    for arg in arguments:
        try:
            main(arg, options, p)
        except:
            traceback.print_exc()            
            print("An exception occured.")
            print("Maybe you can send the info above to the author for debug.")
            raw_input("Press Enter to continue")
        print('')
