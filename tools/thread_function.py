from threading import Thread


def thread_function(target, *args, **kwargs):
	Thread(target=target, args=args, kwargs=kwargs).start()