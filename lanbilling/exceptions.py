class LBAPIError(Exception):
    def __init__(self, error):
        super(LBAPIError, self).__init__()
        self.error = error

    def __str__(self):
        error_message = '{self.error}'.format(self=self)
        return error_message
