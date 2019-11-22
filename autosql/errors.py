class Error(Exception):
    def __init__(self, error, param):
        self.error = error
        self.param = param

    def __str__(self):
        pass


class DBError(Error):

    def __init__(self, param):
        super(DBError, self).__init__("不支持的数据库类型", param)

    def __str__(self):
        return "{}: {}".format(self.error, self.param)