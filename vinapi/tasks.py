from threading import Thread


def background(function):
    """
    Decorator function that handles functions in threads
    :param function: function to run in the separate thread
    :return: decorator function
    """
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator
