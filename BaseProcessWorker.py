#coding: utf-8

import time
import multiprocessing

# 下面的代码用于临时编写简单的log函数, 实现调试输出信息
def log(level, msg):
	print('[%s][%s] %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), level, msg))

class BaseProcessWorker(multiprocessing.Process):
	def __init__(self, *args, **kwargs):
		multiprocessing.Process.__init__(self)
		self.args = args
		self.kwargs = kwargs
		self.messageQueue = self.kwargs['messageQueue']
		self.replyQueue = self.kwargs['replyQueue']
		self.stillRunning = False
	
	def sendBack(self, sendBackMsg):
		self.replyQueue.put(sendBackMsg)

	def do_end(self):
		self.stillRunning = False
	
	def dispatch(self, msg):
		event = msg[0]
		args = msg[1:]
		try:
			handler = getattr(self, "do_%s" % (event, ), None)
			if not handler:
				raise NotImplementedError("Event [%s] handle not found" % event)
			handler(*args)
		except Exception as e:
			log('ERROR', 'Error while handling event [%s]: %s' % (event, str(e)))
		
	def run(self):
		self.stillRunning = True
		while self.stillRunning:
			msg = self.messageQueue.get()
			self.dispatch(msg)
