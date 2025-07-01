import json
import time


database_link="database_session.json"
class database:
    
    def get_database():
        
        try:
            content=""
            with open(database_link, "r") as file:
                content = file.read()
                content=json.loads(content)
                
            return content
        except:
            
            
            return {}
    def is_session(url,session_id):
        db=database.get_database()
        if(url in db):
            for i in db[url]:
                if(session_id == db[url][i]["session_id"]):
                    return True
        return False
    def give_session_id(my_url,src_url):
        db=database.get_database()
        if(my_url in db):
            if(src_url in db[my_url]):
                return db[my_url][src_url]["session_id"]

        return ""
    def save_database(db):

        with open(database_link,'w') as file:
            file.write(json.dumps(db))
    def is_url_in_database(url,my_url):
        database_requests=database.get_database()
        if my_url in database_requests:
            if(url in database_requests[my_url]):
                return True
        return False
    def add_request(self,target_url,src_url,dst,session_id):
        database_requests=database.get_database()
        if(target_url not in database_requests):
            database_requests[target_url]={}
            database_requests[target_url][src_url]={}
            database_requests[target_url][src_url]["ip"]=dst[0]
            database_requests[target_url][src_url]["port"]=dst[1]
            database_requests[target_url][src_url]["session_id"]=session_id
            database_requests[target_url][src_url]["src_url"]=src_url
            
        else:
            
            database_requests[target_url][src_url]={}
            database_requests[target_url][src_url]["ip"]=dst[0]
            database_requests[target_url][src_url]["port"]=dst[1]
            database_requests[target_url][src_url]["session_id"]=session_id
            database_requests[target_url][src_url]["src_url"]=src_url
        database.save_database(database_requests)
    def add_requests(url,data):
        if(url not in data ):
            print("not in!!!!!!!!!\n\n")
            return
        for i in data[url]:
            database.add_request(database,url,i,[data[url][i]["ip"],data[url][i]["port"]],data[url][i]["session_id"])
    def get_requests(url):
        database_requests=database.get_database()
        if(url in database_requests):
            return database_requests[url]
        else:
            return []
    def lower_request(url,src_url):
        database_requests=database.get_database()
        if url in database_requests:
            if(src_url in database_requests[url]):
                database_requests[url].pop(src_url)
                database.save_database(database_requests)
                return
