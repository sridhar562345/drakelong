__version__ = '2.2.7'


class Singleton:
    __storage = None

    @classmethod
    def get_instance(cls):
        if cls.__storage == None:
            from threading import local
            cls.__storage = local()
            return cls.__storage
        else:
            return cls.__storage

    def __init__(self):
        print('init storage', self.__storage)
        if self.__storage != None:
            raise Exception('Single cannot be initiated more than once')
        else:
            from threading import local
            self.__storage = local()


local = Singleton.get_instance()
