## Function to check validity of CMOR Tables


import httplib

class TableBadName(Exception):
    pass
class TableBadDate(Exception):
    pass
class TableBadMD5(Exception):
    pass

class CMORTables:
    def __init__(self,url,name):
        self.repo_url=url
        self.repo_name=name
        self.H=httplib.HTTPConnection(self.repo_url)

    def splitTableString(self,str):
        sp=str.split()
        table = sp[1]
        date=" ".join(sp[2:5])[1:-1].strip()
        md5 = sp[-1]
        if len(md5)!=32:
            md5=None
        return table,date,md5

    def preprocess(self,table,date=None,md5=None):
        if date is None and md5 is None:
            table,date,md5 = splitTableString(table)
        return table,date,md5

    def fetchLatestTable(self,table):
        table,data,md5 = self.preprocess(table)
        self.H.request("GET","/gitweb/?p=%s.git;a=blob_plain;f=Tables/CMIP5_%s;hb=HEAD" % (self.repo_name,table))
        r = self.H.getresponse()
        return r.read()


    def fetchATable(self,table,commit):
        self.H.request("GET","/gitweb/?p=%s.git;a=blob_plain;f=Tables/CMIP5_%s;h=%s" % (self.repo_name,table,commit))
        r=self.H.getresponse()
        return r.read()

    def fetchTable(self,table,date=None):
        table,date,md5 = self.preprocess(table,date)
        self.checkTable(table,date)
        # Ok now fetch the history
        self.H.request("GET","/gitweb/?p=%s.git;a=history;f=Tables/CMIP5_%s;hb=HEAD" % (self.repo_name,table))
        r = self.H.getresponse().read()
        for l in r.split("\n"):
            i= l.find(";hp=")
            if i>-1:
                commit=l[i+4:i+44]
                t = self.fetchATable(table,commit)
                j=t.find("\ntable_date:")
                tdate = t[j+12:j+100]
                tdate = tdate.split("\n")[0].split("!")[0].strip()
                if tdate == date:
                    break
        return t

    def checkTable(self,table,date=None,md5=None):
        table,date,md5 = self.preprocess(table,date,md5)
        self.H.request("GET","/gitweb/?p=%s.git;a=blob_plain;f=Tables/md5s;hb=HEAD" % self.repo_name)
        r = self.H.getresponse()
        md5Table = eval( r.read())["CMIP5"]
        table = md5Table.get(table,None)
        if table is None:
            raise TableBadName("Invalid Table name: %s" % table)
        dateMd5 = table.get(date,None)
        if dateMd5 is None:
            raise TableBadDate("Invalid Table date: %s" % date)
        if md5 is not None and md5!=dateMd5:
            raise TableBadMD5("Invalid Table md5: %s" % md5)
        return

if __name__=="__main__":
    repo_name = "cmip5-cmor-tables"
    repo_url = "uv-cdat.llnl.gov"
    Tables = CMORTables(repo_url,repo_name)
    t = Tables.fetchTable("Oclim","12 May 2010")
    print t

