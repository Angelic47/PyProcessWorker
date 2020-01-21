#coding: utf-8

import time
import threading
import multiprocessing

# 下面的代码用于临时编写简单的log函数, 实现调试输出信息
def log(level, msg):
	print('[%s][%s] %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), level, msg))

class BaseProcessManager():
	def __init__(self, processClass, workerNum):
		self.processClass = processClass
		self.processPool = []
		self.messageQueue = multiprocessing.Queue()
		self.replyQueue = multiprocessing.Queue()
		self.workerNum = workerNum
		self.stillRunning = False
	
	def spawn(self):
		for i in range(0, self.workerNum):
			try:
				log('INFO', 'Spawning process %d' % (i, ))
				process = self.processClass(messageQueue = self.messageQueue, replyQueue = self.replyQueue)
				process.start()
				self.processPool.append(process)
			except Exception as e:
				log('ERROR', 'Error while spawning process %d: %s' % (i, str(e)))

	def crashCheck(self):
		for i in range(0, len(self.processPool)):
			process = self.processPool[i]
			if self.stillRunning == True and process.is_alive() == False:
				log('WARNING', 'Detected process %d crash, restarting...' % (i, ))
				try:
					process = self.processClass(messageQueue = self.messageQueue, replyQueue = self.replyQueue)
					process.start()
					self.processPool[i] = process
				except Exception as e:
					log('ERROR', 'Error while restarting process %d: %s' % (i, str(e)))
	
	def end(self):
		log('INFO', 'Sending end process signal')
		self.stillRunning = False
		for i in range(0, len(self.processPool)):
			self.messageQueue.put(['end', ])
		# 防止callbackloop因为阻塞而死锁
		self.replyQueue.put(['end', ])
	
	def mainloop(self):
		# Override it by youself
		pass
	
	def mainloopTrap(self):
		try:
			self.mainloop()
		except Exception as e:
			log('ERROR', 'Error while executing main loop: %s' % (str(e), ))
		finally:
			self.end()
	
	def do_reply_end(self):
		# 这是为了防止callbackloop死锁的event, 退出时使用, 无实际功能
		pass
	
	def dispatchCallback(self, msg):
		event = msg[0]
		args = msg[1:]
		try:
			handler = getattr(self, "do_reply_%s" % (event, ), None)
			if not handler:
				raise NotImplementedError("Reply event [%s] handle not found" % event)
			handler(*args)
		except Exception as e:
			log('ERROR', 'Error while handling reply event [%s]: %s' % (event, str(e)))
		
	def callbackloop(self):
		while self.stillRunning:
			msg = self.replyQueue.get()
			self.dispatchCallback(msg)
	
	def crashChecker(self):
		while self.stillRunning:
			time.sleep(10)
			self.crashCheck()
	
	def start(self):
		self.stillRunning = True
		self.spawn()
		threading.Thread(target=self.crashChecker).start()
		threading.Thread(target=self.callbackloop).start()
		threading.Thread(target=self.mainloopTrap).start()
