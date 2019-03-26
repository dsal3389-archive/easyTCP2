import logging


class Logger:

    format = "[%(asctime)s] %(levelname)s easyTCP | %(name)s -> %(message)s "
    
    @staticmethod
    def getLogger(name):
        return logging.getLogger("easyTCP | " +name)
    
    #@staticmethod
   # def raise_and_log(self, message, error):
        


