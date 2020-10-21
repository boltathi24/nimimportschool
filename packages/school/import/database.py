from pymongo import MongoClient
from bson.json_util import dumps
from bson.json_util import loads
import urllib

class PyMongo:
    __conn = None

    @staticmethod
    def getConn():
        if PyMongo.__conn is None:  # Read only once, lazy.

            username = urllib.parse.quote_plus('bolt24')
            password = urllib.parse.quote_plus('ZohoTest@24')
            PyMongo.__conn = MongoClient('mongodb+srv://%s:%s@cluster0.dyo3i.mongodb.net/NewDB?retryWrites=true&w=majority' % (username,password))
        return PyMongo.__conn

    @staticmethod
    def getData(table, key, value):
        cursor = PyMongo.getConn()["school_DB"][table].find({key: value}, {'_id': False})
        return loads(dumps(cursor))

    @staticmethod
    def getAllData( table):
        cursor = PyMongo.getConn()["school_DB"][table].find({}, {'_id': False})
        return loads(dumps(cursor))

    @staticmethod
    def insertData( table, data):
        PyMongo.getConn()["school_DB"][table].insert(data)

    # @staticmethod
    # def updateData( table, keyToUpdate, valueToUpdate, searchKey, searchValue, key2, value2):
    #     PyMongo.getConn()["school_DB"][table].update({searchKey:searchValue},{"$set":{keyToUpdate:valueToUpdate,key2:value2}},upsert = True)

    @staticmethod
    def updateData(table, keyToUpdate, valueToUpdate, searchKey, searchValue):
        PyMongo.getConn()["school_DB"][table].update({searchKey: searchValue},
                                                     {"$set": {keyToUpdate: valueToUpdate}}, upsert=True)


if __name__ == '__main__':
    print(PyMongo.getAllData("User"))
