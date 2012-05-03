
from json import loads, dumps
from modulehelper import modules, modulenames, MODULES, enabled_modules, load_modules

class JSONRPCHandlerException(Exception):
    pass

class JSONRequestNotTranslatable(JSONRPCHandlerException):
    pass

class BadServiceRequest(JSONRPCHandlerException):
    pass

class MethodNotFoundException(JSONRPCHandlerException):
    def __init__(self,name):
        self.methodname = name


class JSONRPCHandler(object):

    def __init__(self,modulename):
        '''
         This should be only once called. Atleast my assumption
        '''
        self.modulename = modulename
        load_modules()

    def translate_request(self,data):
        try:
            req = loads(data)
        except:
            raise JSONRequestNotTranslatable
        return req

    def translate_result(self, result, error, id_):
        if error != None:
            error = {"name": error.__class__.__name__, "message": error}
            result = None

        try:
            data = dumps({"result": result, "id":id_, "error":error})
        except :
            error = {"name":"JSONEncodeException", "message": "Result object is not serializable"}
            data = dumps({"result":None, "id": id_, "error": error})

        return data
            
    def handle_request(self, json):
        err = None
        meth = None
        id_ = ''
        result = None
        args = None

        try:
            req = self.translate_request(json)
        except JSONRequestNotTranslatable, e:
            err = e
            req = {'id' : id_}

        if err == None:
            try:
                id_ = req['id']
                meth = req['method']
                try:
                    args = req['params']
                except:
                    pass
            except:
                err = BadServiceRequest(json)

            module_instance = None
            if err == None:
                try:
                    module_instance = MODULES.get(meth)
                except:
                    err = ServiceMethodNotFound(meth)
