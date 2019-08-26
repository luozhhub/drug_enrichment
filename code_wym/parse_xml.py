#20190505
#author: YaMing Wang
#downlad pubmed abstract from ncbi baseline
#cmd: nohup wget ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*.gz &

#!/usr/bin/python
from xml.dom.minidom import parse
import xml.dom.minidom
import os,sys


def parsePubmed(inputFile=None, outputFile=None):
    """
    parse the xml file
    :param inputFile:  xml file
    :param outputFile:
    :return:
    """
    w = open(outputFile, "w")
    # 使用minidom解析器打开 XML 文档
    DOMTree = xml.dom.minidom.parse(inputFile)
    PubmedArticleSet = DOMTree.documentElement
    # 在集合中获取所有PubmedArticles
    PubmedArticles = PubmedArticleSet.getElementsByTagName("PubmedArticle")
    for PubmedArticle in PubmedArticles:
        PMID_list = []
        Chemical_list = []
        MeshHeading_list = []
        # 获取PubmedArticle下所有MedlineCitation：
        MedlineCitations = PubmedArticle.getElementsByTagName("MedlineCitation")
        for MedlineCitation in MedlineCitations:
            pmid = MedlineCitation.getElementsByTagName('PMID')[0]
            PMID = pmid.childNodes[0].data
            PMID_list.append(PMID)
            if bool(MedlineCitation.getElementsByTagName('ChemicalList')) == True:
                Chemicals = MedlineCitation.getElementsByTagName('ChemicalList')
                MeshHeadings = MedlineCitation.getElementsByTagName('MeshHeadingList')
                for Chemical in Chemicals:
                    NameOfSubstance = Chemical.getElementsByTagName('NameOfSubstance')[0]
                    if NameOfSubstance.hasAttribute("UI"):
                        UI = NameOfSubstance.getAttribute("UI")
                        Chemical_list.append(UI)
                for MeshHeading in MeshHeadings:
                    DescriptorNames = MeshHeading.getElementsByTagName('DescriptorName')
                    QualifierNames = MeshHeading.getElementsByTagName('QualifierName')
                    for DescriptorName in DescriptorNames:
                        if DescriptorName.hasAttribute("UI"):
                            UI = DescriptorName.getAttribute("UI")
                            MeshHeading_list.append(UI)
                            if DescriptorName.hasAttribute("MajorTopicYN"):
                                MajorTopicYN = DescriptorName.getAttribute("MajorTopicYN")
                                MeshHeading_list.append(MajorTopicYN)
                    for QualifierName in QualifierNames:
                        if QualifierName.hasAttribute("UI"):
                            UI = QualifierName.getAttribute("UI")
                            MeshHeading_list.append(UI)
                            if QualifierName.hasAttribute("MajorTopicYN"):
                                MajorTopicYN = QualifierName.getAttribute("MajorTopicYN")
                                MeshHeading_list.append(MajorTopicYN)
            w.write(' '.join(PMID_list) + ';' + ' '.join(Chemical_list) + ';' + ' '.join(MeshHeading_list) + '\n')
    w.close()


if __name__ == "__main__":
    dirPath = "/home/ymwang/project/drug_enrichment/xmlParse_part1"
    xmlList = os.listdir(dirPath)#指定路径里的所有文件
    log = open("/home/ymwang/project/drug_enrichment/parse_xm_log.txt", "w")
    for xml_f in xmlList:
        sample_id = xml_f.split(".")[0]
        input_F = os.path.join(dirPath, xml_f)#合并目录
        output_F = os.path.join(dirPath + "_result", sample_id + ".result.txt")
        #parsePubmed(inputFile=input_F, outputFile=output_F)
        try:
            parsePubmed(inputFile=input_F, outputFile=output_F)
            log.write("%s successed!\n" % input_F)
        except:
            log.write("%s failed!!!\n" % input_F)
    log.close()