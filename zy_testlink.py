# -*- coding:utf-8 -*-
__author__ = "ZiYa Wang"

import testlink
from dbHandler import dbHandler


class zy_testlink:
    """
    这个类封装了testlink api，方便操作testlink
    """

    def __init__(self, testlinkAddr, key):
        """
        初始化类，需要传递testlink的地址，及testlink的key
        :param testlinkAddr: testlink地址，类似http://testlink.wanqian.store/lib/api/xmlrpc/v1/xmlrpc.php
        :param key:testlink的key
        """
        self.tlc = testlink.TestlinkAPIClient(testlinkAddr, key)

    def addTestCase(self, caseName, tsId, tpId, author, steps, summary="", preconditions="null", importance=2):
        """
        添加测试用例方法
        :param caseName: 用例名
        :param tsId: 用例集id
        :param tpId: 项目id
        :param author: 登陆用户账号
        :param summary:
        :param steps: 需要传入 [{"step_number": 1, "actions": "step1", "expected_results": "resultA", "execution_type": 0}]
        :param preconditions: 前置条件
        :param importance: 重要性 0:high 1:low 2:medium
        :return:
        """
        self.tlc.createTestCase(caseName, tsId, tpId, author, summary, steps=steps, preconditions=preconditions,
                                importance=importance)

    def addTestSuit(self, projectId, suiteName, describe, fatherId):
        """
        创建测试套件
        :param projectId:项目id
        :param suiteName:套件名
        :param describe:描述
        :param fatherId:上级id
        :return:
        """
        if fatherId == "":
            self.tlc.createTestSuite(projectId, suiteName, describe)
        else:
            self.tlc.createTestSuite(projectId, suiteName, describe, fatherId)

    def getSuiteId(self, suiteName, prefix="wanqian"):
        """
        获取测试套件Id，只取数组中第一个套件的id
        :param suiteName: 套件名称
        :param prefix: 前缀，默认是"wanqian"
        :return: 返回套件的id
        """
        suite = self.tlc.getTestSuite(suiteName, prefix)
        if suite:
            return suite[0]["id"]
        else:
            return False

    def getProjectId(self, projectName):
        """
        获取项目Id
        :param projectName: 项目名称
        :return:
        """
        if projectName == "":
            raise ValueError
        else:
            id = self.tlc.getProjectIDByName(projectName)
            if id == -1:
                return False
            else:
                return id

    def getAllProjects(self):
        """
        获取所有的项目
        :return: 返回项目总数和存储项目的字典
        """
        total_projects = self.tlc.countProjects()
        projects = self.tlc.getProjects()
        return total_projects, projects

    def getTestSuite(self, suiteName, prefix="wanqian"):
        suite = self.tlc.getTestSuite(suiteName, prefix)
        if suite:
            return suite
        else:
            return False

    def getTestCaseSteps(self, caseid):
        """
        获取测试用例的steps
        :param caseid: 实际是数据库中的nodes_hirearchy中的id,node_type_id=3
        :return: 如果id存在，返回steps，不存在返回False
        """
        try:
            cases = self.tlc.getTestCase(testcaseid=caseid)
            steps = []
            for index in xrange(len(cases)):
                case_detail = cases[index]
                steps = case_detail["steps"]
            return steps
        except testlink.testlinkerrors.TLResponseError:
            print "caseid 不存在"
            return False
        # step_dict = {}

    def getTestPlanId(self, name):
        """
        通过测试计划名获取测试计划id
        :param name:
        :return: tpid
        """
        db = dbHandler()
        # sql = 'select * from nodes_hierarchy WHERE name="%s"'% name
        datas = db.getTestPlanId(name)
        db.closeConnection()
        return datas[0][0]

    def getPlanTV(self, tpid):
        """
        获取testversion id
        :param tpid: 测试计划Id，可调用getTestPlanId来获取
        :return: 返回测试计划中包含的用例tvid list
        """

        db = dbHandler()
        datas = db.getTVidByTP(tpid)
        db.closeConnection()
        tcversionids = []
        for i in xrange(len(datas)):
            tcversionids.append(datas[i][2])
        return tcversionids

    def getExternalId(self, tvids):
        """
        获取测试用例的id
        :param tvids: 传入list[testversion_id, ]
        :return: 返回列表
        """
        if not tvids:
            return False
        db = dbHandler()
        externalids = []
        for i in xrange(len(tvids)):

            datas = db.getTCidByTV(tvids[i])
            for j in xrange(len(datas)):
                externalids.append(datas[j][1])

        db.closeConnection()
        return externalids

    def getCaseId(self, tvids):
        """
        获取数据库中的caseId
        :param tvid:
        :return:
        """
        if not tvids:
            return False
        db = dbHandler()
        caseids = []
        for i in xrange(len(tvids)):
            datas = db.getCaseid(tvids[i])
            for j in xrange(len(datas)):
                caseids.append(datas[j][0])

        db.closeConnection()
        return caseids


    def writeResults(self, tcid, tpid, status="f", buildid=1):
        """
        回写测试结果
        :param tcid: 用例id
        :param tpid: 测试计划id
        :param status: f or p
        :param buildid:
        :return:
        """
        self.tlc.reportTCResult(testcaseid=tcid, testplanid=tpid, status=status, buildid=buildid)

    def getSteps(self, p_name):
        """
        通过测试计划，找到其下的所有case，返回字典结构为{'testplanid':testplanid,'caseid':steps},
        steps结构为
        [{
        'step_number': '1',
        'actions': '',
        'execution_type': '1',
        'active': '1',
        'id': '42',
        'expected_results': 'resultA'
        },
         {
         'step_number': '2',
         'actions': '',
         'execution_type': '1',
         'active': '1',
         'id': '43',
         'expected_results': 'resultB'
         }]
        :param p_name: 测试计划名
        :return:
        """

        tpid = self.getTestPlanId(p_name)
        tvids = self.getPlanTV(tpid)
        cids = self.getCaseId(tvids)
        dic = {
            "testplanid": tpid,
               }
        for i in xrange(len(cids)):

            steps = tc.getTestCaseSteps(cids[i])
            caseid = cids[i]
            dic[caseid] = steps
        return dic

'''if __name__ == "__main__":

    url = "http://testlink.wanqian.store/lib/api/xmlrpc/v1/xmlrpc.php"
    key = "084aec4c7fe80e871988886aba8da28e"
    tc = zy_testlink(url, key)
    stepsdict = tc.getSteps(u"testplandemo")
    for step in stepsdict:
        if step != "testplanid":
            tc.writeResults(step, stepsdict["testplanid"], 'p')'''



