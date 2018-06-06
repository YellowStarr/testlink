# -*- coding:utf-8 -*-


import MySQLdb


class dbHandler:

    def __init__(self):

       self.conn = MySQLdb.connect(host="172.16.1.254",
                              port=3307,
                              user="root",
                              passwd="Zhang98722@",
                              db="testlink",
                              charset='utf8')    # 写入数据库时解决 latin-1的问题
       self.cur = self.conn.cursor()

    def getTestPlanId(self, name):

       sql = 'select * from nodes_hierarchy WHERE name="%s"' % name
       n = self.cur.execute(sql)
       datas = self.cur.fetchmany(n)
       return datas

    def getTVidByTP(self, tpid):
        sql = 'select * from testplan_tcversions WHERE testplan_id=%s' % tpid

        n = self.cur.execute(sql)
        datas = self.cur.fetchmany(n)
        return datas

    def getTCidByTV(self, tvid):
        sql = 'select * from tcversions WHERE id=%s' % tvid
        n = self.cur.execute(sql)
        datas = self.cur.fetchmany(n)
        return datas

    def getCaseid(self, tvid):
        """
        返回caseid
        :param tvid:
        :return:
        """
        sql = 'select parent_id from nodes_hierarchy WHERE id=%s' % tvid
        n = self.cur.execute(sql)
        datas = self.cur.fetchmany(n)
        return datas

    def closeConnection(self):
        self.conn.close()
