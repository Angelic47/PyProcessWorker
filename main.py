#coding: utf-8

import multiprocessing
from BaseProcessManager import BaseProcessManager
from BaseProcessWorker import BaseProcessWorker

# 下面的代码用于临时编写简单的log函数, 实现调试输出信息
import time
def log(level, msg):
	print('[%s][%s] %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), level, msg))

class ProcessManager(BaseProcessManager):
	def mainloop(self):
		self.number = 0
		log('INFO', 'Start 50000 event')
		for i in range(0, 50000):
			self.messageQueue.put(('test', i))
		log('INFO', 'Event sent')
		log('INFO', 'Got number: %d' % (self.number, ))
	
	def do_reply_test(self, i):
		self.number += i

class ProcessWorker(BaseProcessWorker):
	def do_test(self, i):
		self.replyQueue.put(('test', 1))

if __name__ == '__main__':
	multiprocessing.freeze_support()
	# 上面两行在windows上必须要有, 原因是windows平台不支持fork, 在py的bootstrap阶段无法创建新进程, 具体细节不多说
	pm = ProcessManager(ProcessWorker, 12)
	pm.start()
