import json
import random
database_link="database_router.json"
from cryptography.hazmat.primitives import serialization

class database:
    def compact_to_json(self,key):
        pem_key = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
        return pem_key
    def compact_from_json(self,key):
        return serialization.load_pem_public_key(key.encode())
    def get_key(ip,port):
        databas=database.get_database()
        for i in range(len(databas)):
            if(databas[i][0]==ip and databas[i][1]==port):
                return databas[i][2] 
    def get_database():
        try:
            content=""
            file= open(database_link, "r") 
            content = file.read()
            content=json.loads(content)
            for i in range(len(content)):
                content[i][2]=database.compact_from_json("",content[i][2])    

            return content
        except:
            database.save_database([])
            return []
    def add_router(ip,port,public_key):
        databas=database.get_database()
        try:
            port=port[1]
        except:
            pass
        for i in range (len(databas)):
            try:
                if(databas[i][0]==ip and databas[i][1]==port):
                    databas.pop(i)
            except:
                pass
        databas.append([ip,port,public_key])
        for i in range(len(databas)):
            try:
                databas[i][2]=database.compact_to_json("",databas[i][2]) 
            except:
                databas[i][2]=databas[i][2]
         
          
        
        database.save_database(databas)
    def add_routers(routers):
        for i in routers:
            database.add_router(i[0],i[1],i[2])

    def save_database(db):

        try:
            with open(database_link,'w') as file:
                file.write(json.dumps(db))
        except:
            pass
    def remove_router(ip,port):
        data=database.get_database()
        for i in range(len(data)):
            if(data[i][0]==ip and data[i][1]==port):
                data.pop(i)
                database.save_database(database)
                return

    def get_router(length,my_ip_port):
        databas=database.get_database()
        for i in range(len(databas)):
            databas[i][2]=database.compact_to_json("",databas[i][2]) 
        if(length==1):
            try:
                return [databas[random.randint(0,len(databas)-1)]]
            except:
                return []
        if(length<len(databas)):
            lis=[]
            for i in range(len(databas)):
                if(databas[i][:2]==my_ip_port):
                    databas.pop(i)
                    break
            for i in range(length):
                num=random.randint(0,len(databas)-1)

                lis.append(databas[num])
                databas.pop(num)
            return lis
        else:
            return databas