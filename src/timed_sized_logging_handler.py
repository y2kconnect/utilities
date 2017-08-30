# -*- encoding: utf-8 -*-
''' 定时定长翻转，进程安全
参考：
    https://github.com/Acrisel/acris/tree/master/acris
'''

# python apps
import logging.config
import multiprocessing as mp
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


def rename_dfn(baseFilename):
    ''' rename
        baseFilename --> baseFilename.<max_number+1>
    '''
    plen = len(baseFilename) + 1
    s = '{}.*'.format(baseFilename)
    arr = glob.glob(s)
    arr_i = [int(s[plen:]) for s in arr if s[plen:].isdigit()]
    if arr_i and max(arr_i):
        i = max(arr_i) + 1
    else:
        i = 1
    f_name = '{}.{}'.format(baseFilename, i)
    return f_name


class TimedSizedRotatingHandler(TimedRotatingFileHandler, RotatingFileHandler):
    ''' log文件：定时定长翻转，进程安全
    By default, the file grows indefinitely. 
    Handler for logging to a file, rotating the log file at certain timed
    intervals.
    You can specify particular values of when (and maxBytes) to allow the file
    to rollover at certain timed intervals (and at a predetermined size).

    backupCount=0: 定时定长翻转
    '''
 
    def __init__(
            self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None,
            delay=False, when='h', interval=1, utc=False, atTime=None,
            ):
        'Combines RotatingFileHandler TimedRotatingFileHandler'
        f_name = filename.format(pid=mp.current_process().name)
        RotatingFileHandler.__init__(
                self, filename=f_name, mode=mode, maxBytes=maxBytes,
                backupCount=backupCount, encoding=encoding, delay=delay,
                )
        TimedRotatingFileHandler.__init__(
                self, filename=f_name, when=when, interval=interval,
                backupCount=backupCount, encoding=encoding, delay=delay,
                utc=utc, atTime=atTime,
                )

    def shouldRollover(self, record):
        'Check the need to rotate.'
        timed_rollover = TimedRotatingFileHandler.shouldRollover(self, record) 
        sized_rollover = RotatingFileHandler.shouldRollover(self, record)
        return timed_rollover or sized_rollover

    def getFilesToDelete(self):
        'It is enough to use timed base rollover.'
        return super(TimedRotatingFileHandler, self).getFilesToDelete()        
 
    def doRollover(self):
        ''' do a rollover; in this case, a date/time stamp is appended to the
        filename when the rollover happens.  However, you want the file to be
        named for the start of the interval, not the current time.  If there
        is a backup count, then we have to get a list of matching filenames,
        sort them and remove the one with the oldest suffix.
        '''
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename('{}.{}'.format(self.baseFilename,
                time.strftime(self.suffix, timeTuple)))
        if os.path.exists(dfn):
            dfn = rename_dfn(dfn)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and \
                not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:
                    # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:
                    # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


