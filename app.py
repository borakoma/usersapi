from flask import Flask, jsonify, request, url_for, redirect
from flask_restful import reqparse
from flask_api import status

from pymongo import MongoClient
from bson.objectid import ObjectId
import hashlib
import json

app = Flask(__name__)
mongosvr = 'localhost'
mongoport = 27017
putkeys = ("uid", "name", "date", "md5checksum")
getkeys = ("uid", "date")

cl = MongoClient(mongosvr, mongoport)

def checkMD5(jd):
    """ Small function to calculate MD5 checksum and compare to the stored value
        MD5 checksum string should be in this exact order (including spaces):
            {"date": "xxxx-xx-xx...", "uid": "xx", "name": "xxxxx"}
    """
    md5data = '{"date": "' + jd['date'] + '", "uid": "' + jd['uid'] + '", "name": "' + jd['name'] + '"}'
    if hashlib.md5(md5data).hexdigest() != jd['md5checksum']:
        return False
    else:
        return True

@app.route("/adduser/", methods=['POST'])
def adduser():
    print (request)
    print (request.get_json())
    json_data = request.get_json()
    for  jd in json_data:
        # Check if all the keys are in input
        if all (k in jd for k in putkeys):
            if checkMD5(jd):
                cl.drdb.drcol.insert_one(jd)
            else:
                return ("Invalid MD5 checksum: {}".format(jd)), 400
        else:
            return ("Invalid input format: {}".format(jd)), 400
    return ("success"), 200

@app.route("/checkuser", methods=['GET'])
def checkuser():
    print ("Request: " + str(request.args))
    if all (k in request.args for k in getkeys):
        res = cl.drdb.drcol.find({"uid": request.args['uid'], "date": {'$regex': request.args['date'][:10]}})
        return (str(res.count())), 200
    else:
        return ("Invalid parameters"), 400

if __name__ == "__main__":
    app.debug=True
    app.run(host='0.0.0.0')
