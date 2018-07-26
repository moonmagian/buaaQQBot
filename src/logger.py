from logLevel import *
import os
import time


class FileWritter:
    def __init__(self, fileName: str, maxSizeM=20):
        self._fname = fileName
        self._maxSizeM = maxSizeM

    def write(self, content: str):
        with open(self._fname, 'a') as f:
            if(os.path.getsize(self._fname) / 1024 / 1024 > self._maxSizeM):
                f.truncate(0)
            f.write(content + '\n')


class StdoutWritter:
    def write(self, content: str):
        print(content)


class Logger:
    def __init__(self, level, *dest):
        self._level = level
        self._dest = dest

    def setLevel(self, level):
        self._level = level

    def getLevel(self):
        return self._level.value

    def log(self, text: str, level=LEVEL_INFORMATION):
        prefix = str(time.time())
        level = level & self._level
        if(level == LEVEL_DEBUG):
            prefix += ' [DEBUG]:'
        if(level == LEVEL_ERROR):
            prefix += ' [ERROR]:'
        if(level == LEVEL_INFORMATION):
            prefix += ' [INFO]:'
        if(level == LEVEL_WARNING):
            prefix += ' [WARNING]:'
        for writter in self._dest:
            writter.write(prefix + text)
