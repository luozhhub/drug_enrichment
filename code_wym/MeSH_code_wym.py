#20190505
#author: YaMing Wang
#downlad pubmed abstract from ncbi baseline
#cmd: nohup wget ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*.gz &

#!/usr/bin/python

#对baseline的meshid进行term的计算以及D,C term 以及人类相关的pubmed的筛选

import pandas as pd
import json
from pyMeSHSim.Sim.similarity import termComp
import os,sys
def get_term(inputFile=None, outputFile=None):
    x = open(inputFile,"r")
    w = open(outputFile,"w")
    simCom = termComp()
    for line in x:
        list = []
        dict = {}
        errorline = 0
        linest = line.strip().split(";")
        try:
            ty = simCom.getCategory(dui=linest[1])
            if bool(ty) == True:
                ty_che = ','.join(ty)
        except:
            pass
        meshidline = linest[2].strip().split(" ")
        if 'ty_che' in vars().keys():#（对第一行进行了判断：如果变量不存在）
            if 'D' in ty_che and 'D006801' in meshidline :
                for meshid in meshidline:
                    dict = {}
                    if meshid != "N" and meshid != "Y" :
                        try:
                            ty = simCom.getCategory(dui=meshid)#（罗师兄的python包内函数）
                            if bool(ty) == True:
                                ty_mesh = ','.join(ty)
                                if 'C' in ty_mesh:
                                    dict[meshid] = ty_mesh
                                    w.write(linest[0] + ' ' + linest[1] + " " + ty_che + " "  + json.dumps(dict) + '\n')
                        except:
                            pass
    w.close()
if __name__ == "__main__":
    dirPathin = "/home/ymwang/project/drug_enrichment/xmlParse_result"
    dirPathout = "/home/ymwang/project/drug_enrichment/xmlParse_result_term"
    resultList = os.listdir(dirPathin)#指定路径里的所有文件
    log = open("/home/ymwang/project/drug_enrichment/xmlParse_result_term/parse_result_term_log.txt", "w")
    for result in resultList:
        sample_id = result.split(".")[0]
        input_F = os.path.join(dirPathin, result)#合并目录
        output_F = dirPathout +"/"+ sample_id + ".term.txt"
        if os.path.getsize(output_F)==0:#（只对输出文件不为0的输入文件重新计算）            
#parsePubmed(inputFile=input_F, outputFile=output_F)
            get_term(inputFile=input_F, outputFile=output_F)
            log.write("%s successed!\n" % input_F)
    log.close()

#统计drug—disease pairs co-occurrence 情况

import pandas as pd
import json
from pyMeSHSim.Sim.similarity import termComp
import os,sys
log = open("/home/ymwang/project/drug_enrichment/result_term/term.log","w")
inputFile = open(sys.argv[1],"r")
outputFile = open(sys.argv[2],"w")
simCom = termComp()
for line in inputFile:
    list = []
    dict = {}
    errorline = 0
    linest = line.strip().split(";")
    try:
        ty = simCom.getCategory(dui=linest[1])
        if bool(ty) == True:
            ty_che = ','.join(ty)
    except:
        pass
    meshidline = linest[2].strip().split(" ")
    if 'ty_che' in vars().keys():
        if 'D' in ty_che and 'D006801' in meshidline :
            for meshid in meshidline:
                dict = {}
                if meshid != "N" and meshid != "Y" :
                    try:
                        ty = simCom.getCategory(dui=meshid)#（罗师兄的python包内函数）
                        if bool(ty) == True:
                            ty_mesh = ','.join(ty)
                            if 'C' in ty_mesh:
                                dict[meshid] = ty_mesh
                                outputFile.write(linest[0] + ';' + linest[1] + ";" + ty_che + ";" + json.dumps(dict) + '\n')
                                log.write("%s successed!\n" % inputFile)
                    except:
                        log.write("%s failed!!!\n" % inputFile)
inputFile.close()
outputFile.close()
log.close()
#pbs脚本
for dir in `ls /home/ymwang/project/drug_enrichment/xmlParse_result`; do echo -e python /home/ymwang/project/drug_enrichment/new_term.py /home/ymwang/project/drug_enrichment/xmlParse_result/$dir /home/ymwang/project/drug_enrichment/result_term/$(echo $dir|sed 's/result/term/g') >/home/ymwang/project/drug_enrichment/pbs/$(echo $dir|sed 's/result.txt/term.pbs/g'); done
for i in `ls /home/ymwang/project/drug_enrichment/pbs/*`; do qsub -q batch -l nodes=1:ppn=1 $i;done #提交命令

#计算pairs co-occurrence frequency（900多个文件分别生成一个大字典）

import json
import os,sys
import json
keys = []
dic = {}
pub = []
inputFile = open(sys.argv[1],"r")
outputFile = open(sys.argv[2],"w")
log = open("/home/ymwang/project/drug_enrichment/dru_dis_piars/dru_dis_piars.log.txt", "w")
try:
    for line in inputFile:
        linest = line.strip().split(';')
        di =[]
        for i in eval(linest[3]).keys():
            di.append(i)
        key = linest[1] + '_'+ ' '.join(di)
        if key not in keys:
            keys.append(key)
            dic[key] = 1
        else:
            dic[key] += 1
        if linest[0] not in pub:
            pub.append(linest[0])
    a = str(len(set(pub)))
    outputFile.write(a + ‘；’+ json.dumps(dic))
    log.write("%s successed!\n" % inputFile)
    inputFile.close()
    outputFile.close()
except:
    log.write("%s failed!\n" % inputFile)
log.close()
#pbs脚本
for dir in `ls /home/ymwang/project/drug_enrichment/result_term`; do echo -e python /home/ymwang/project/drug_enrichment/pairs_fre.py /home/ymwang/project/drug_enrichment/result_term/$dir /home/ymwang/project/drug_enrichment/dru_dis_piars/$(echo $dir|sed 's/term.txt/pair_fre.pbs/g') >/home/ymwang/project/drug_enrichment/pbs/$(echo $dir|sed 's/term.txt/pairs.pbs/g'); done
for i in `ls /home/ymwang/project/drug_enrichment/pbs/*pairs.pbs`; do qsub -q batch -l nodes=1:ppn=1 $i;done

#计算all pairs co-occurrence frequency（把所有文件的大字典相加）

import os
import json
from collections import Counter
path = "/home/ymwang/project/drug_enrichment/dru_dis_piars" #文件夹目录
files= os.listdir(path) #得到文件夹下的所有文件名称
dict = {}
w = open("/home/ymwang/project/drug_enrichment/fre_sum.txt",'w')
log = open("/home/ymwang/project/drug_enrichment/fre_sum.log",'w')
for file in files: #遍历文件夹
     f = open(path+"/"+file)
     try:
         for line in f:
            linest = line.strip().split(";")
            dic = eval(linest[1])
            dict = Counter(dic)+Counter(dict)
            log.write("%s successed!!!\n" % file)
     except:
         log.write("%s failed!!!\n" % file)
w.write(json.dumps(dict))

#计算筛选后的PubMed数量（pubmed：5537638）

import os
import json
from collections import Counter
path = "/home/ymwang/project/drug_enrichment/dru_dis_piars" #文件夹目录
files= os.listdir(path) #得到文件夹下的所有文件名称
dict = {}
w = open("/home/ymwang/project/drug_enrichment/pub_sum.txt",'w')
log = open("/home/ymwang/project/drug_enrichment/pub_sum.log",'w')
for file in files: #遍历文件夹
     f = open(path+"/"+file)
     try:
         for line in f:
            dic = {}
            linest = line.strip().split(";")
            dic['pub'] = int(linest[0])
            dict = Counter(dic)+Counter(dict)
            log.write("%s successed!!!\n" % file)
     except:
         log.write("%s failed!!!\n" % file)
w.write(json.dumps(dict))

#进行fisher test
#pair_num = pairs 
#drug_num = Di - CiDi 
#disease_num = Ci - CiDi 
#all_num = all_pub - Di - Ci + CiDi

import numpy as np
import scipy.stats as stats
x = open("/home/ymwang/project/drug_enrichment/C_fre.txt",'r')
y = open("/home/ymwang/project/drug_enrichment/D_fre.txt",'r')
z = open("/home/ymwang/project/drug_enrichment/fre_sum.txt",'r')
w = open("/home/ymwang/project/drug_enrichment/fisher.txt",'w')
cdic =eval(x.readline());ddic =eval(y.readline());ocdic =eval(z.readline())
oclist = ocdic.keys()
clist = cdic.keys()
dlist = ddic.keys()
for i in oclist:
    oc = str(i).split('_')
    cidi = ocdic[i];ci = cdic[oc[1]];di = ddic[oc[0]];all = 5537638
    obs = np.array([[cidi, di - cidi], [ci - cidi, 5537638]])
    f = stats.fisher_exact(obs)
    if f[0] > 1 and f[1] < 0.05:
        w.write(oc[0] + ' ' + oc[1] + ' ' + str(ocdic[i]) + ' ' +' '.join(str(i) for i in f) + "\n")
w.close()
x.close()
y.close()
z.close()
#计算pubchem对应的mesh term：
#ftp://ftp.ncbi.nih.gov/pubchem/Compound/Extras/CID-MeSH

from pyMeSHSim.metamapWrap.MetamapInterface import MetaMap
metamap = MetaMap(path="/home/shimw/software/public_mm/bin/metamap16")

w = open("/home/ymwang/mesh_pubc","w")



with open('/home/ymwang/drugenrichment/CID-MeSH', 'r') as x:
    for linex in x:
        linexst = linex.strip().split("\t")

        meshst = str(linexst[1])
        word = meshst
        concept = metamap.runMetaMap(text=word)
        if bool(concept) == True:
            c = concept[0]['MeSHID']
            if bool(c) == True:
                w.write(linexst[0] + "\t" + c + "\n")

w.close()
