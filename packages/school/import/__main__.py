from database import PyMongo
import json
from passlib.hash import bcrypt
import base64
import os
import pathlib
import pandas as pd


import secrets
import string

def main(request_data):
    file_content = request_data['file']

    email=request_data['email']
    org_id=None

    try:
        org_id = PyMongo.getData('school', 'email', email)[0]['school_id']
        file_path=saveFile(file_content,request_data['file_name'],request_data['file_type'])
        excelData=readExcel(file_path)
        for data in excelData:
            ##Insert studetn/teacher to user table
            if (len(PyMongo.getData('user', 'email', data['email'])) == 0):
                if(data['user_type']=='student'):
                    insertionResp = insertToUserTable(data['email'], org_id,1)
                    user_seq = insertionResp['user_seq']
                    pwd = insertionResp['password']

                    class_id=getClassId(data['class'],user_seq)
                    print("class ID After STUDENT:"+str(class_id))
                    student_seq = PyMongo.getData('counter', 'table', 'student')[0]['counter']
                    parent_seq = PyMongo.getData('counter', 'table', 'parent')[0]['counter']

                    ##Student table insertion
                    student = {"user_id": user_seq, "student_id": student_seq, "name": data['name'], "age": data['age'],
                               "gender": data['gender'], 'address': data['address'], "class": class_id}
                    PyMongo.insertData('student', student)


                    ##Insert parent to userTable
                    insertionResp = insertToUserTable(data['parent_email'], org_id,3)
                    user_seq = insertionResp['user_seq']
                    pwd = insertionResp['password']




                    ##Parent table insertion
                    parent = {"user_id":user_seq,"parent_id": parent_seq, "name": data['parent_name'], "parent_of": student_seq,
                               "phone": data['parent_phone'], 'address': data['address']}
                    PyMongo.insertData('parent', parent)

                    PyMongo.updateData("counter", "counter", student_seq + 1, "table", "student")
                    PyMongo.updateData("counter", "counter", parent_seq + 1, "table", "parent")

                if(data['user_type']=='teacher'):
                    insertionResp = insertToUserTable(data['email'], org_id, 2)
                    user_seq = insertionResp['user_seq']
                    pwd = insertionResp['password']

                    print("before teacher ID :" )
                    class_id = getClassId(data['class_incharge_of'],user_seq)
                    print("Afer class ID :"+str(class_id))
                    teacher_seq = PyMongo.getData('counter', 'table', 'teacher')[0]['counter']
                    classes_involved=data['classes_involved'].split(",")
                    list_of_classes=[]
                    for cls in classes_involved:
                        list_of_classes.append(getClassId(cls,user_seq))

                    teacher = {"user_id":user_seq,"teacher_id": teacher_seq, "name": data['name'], "age": data['age'],
                               "gender": data['gender'], 'address': data['address'], "class_incharge_of": class_id,"class_involved":list_of_classes}
                    PyMongo.insertData('teacher', teacher)
                    PyMongo.updateData("counter", "counter", teacher_seq + 1, "table", "teacher")


        deleteFile(file_path)
        return {"body":{"message":"Record Added Successfully","success":(True),"statusCode":200}}
    except Exception as e:
        return {"body":{"message":str(e),"success":(False),"statusCode":400}}

def getRandomPwd():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(20))

def insertToUserTable(email,org_id,user_type):
    user_seq = PyMongo.getData('counter', 'table', 'user')[0]['counter']
    raw_random_pwd = getRandomPwd()
    hashed_pwd = bcrypt.hash(raw_random_pwd)
    user = {"user_id": user_seq, "password": hashed_pwd, "email": email,
            "refresh_token": '', "user_type": user_type, "firebase_token": ""}
    PyMongo.insertData('user', user)
    PyMongo.updateData("counter", "counter", user_seq + 1, "table", "user")
    resp={"user_seq":user_seq,"password":raw_random_pwd}
    PyMongo.insertData("user_org", {"user_id": user_seq, "org_id": org_id})
    return resp

def getClassId(class_name,user_seq):
    class_exist = PyMongo.getData('class', 'class_name', class_name)
    if (len(class_exist) == 0):
        class_seq = PyMongo.getData('counter', 'table', 'class')[0]['counter']

        class_detail = {"class_id": class_seq, "class_name": class_name, "members": [user_seq]}
        PyMongo.insertData("class", class_detail)

        PyMongo.updateData("counter", "counter", class_seq + 1, "table", "class")
        return class_seq

    else:
        import json
        jsarr=json.loads(str(class_exist[0]['members']))
        print(jsarr)
        if not user_seq in jsarr:
            jsarr.append(user_seq)
        PyMongo.updateData("class", "members", jsarr , "class_id", class_exist[0]['class_id'])
        return class_exist[0]['class_id']


def readExcel(file_path):
    df = pd.read_excel(file_path)
    return df.to_dict(orient='records')

def saveFile(file_content,file_name,file_type):
    try:
        encoded = file_content  # retrieving the contents of xls in base64 form
        decoded = base64.b64decode(encoded)
        type(decoded)  # => <class 'bytes'>
        xlsfile = open(file_name+ "." + file_type, 'wb')
        xlsfile.write(decoded)
        xlsfile.close()
        print(xlsfile.name)
        return os.path.abspath(xlsfile.name)
    except Exception as e:
        return "Exception"+str(e)

def deleteFile(file_path):
    try:
        path = pathlib.Path(file_path)
        path.unlink()
    except Exception as e:
        print(e)

