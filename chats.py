link="chats.json"
import json
import time
class chats:
    def __init__(self):
        self.chats=self.get_chats()
    def get_chats(self):
       
        try:
            with open(link, 'r+') as f:
                content = f.read()
                if content.endswith("}}}"):
                    content = content[:-3] + "}}"
                    f.seek(0)
                    f.write(content)
                    f.truncate()
            with open(link, "r") as file:
                loaded_data = json.load(file)
                return loaded_data
        except:
            return {}
    def save_chats(self,chats):
        if(chats=={}):
            return
        try:
            with open(link, "w") as file:
                json.dump(chats, file)
        except:
            with open(link, "w") as file:
                json.dump({}, file)
    def add_chat(self,name,url):
        chat_history=self.get_chats()
        chat_history[name] = {"messages": [], "url": url, "is_online": False}
        self.save_chats(chat_history)
    def change_online_status(self,name,status):
        try:
            chat_history=self.get_chats(self)
            chat_history[name]["is_online"] =status
            self.save_chats(self,chat_history)
        except:
            pass
    def add_message(self,name,src_name,message):
        chat_history=self.get_chats()
        seen=True if src_name!="me" else False
        id=0
        if(chat_history[name]["messages"]==[]):
            id=0
        else:
            id=chat_history[name]["messages"][-1]["id"]+1
        chat_history[name]["messages"].append({"text": message, "sender": f"{src_name}","is_seen":seen,"id":id})
        self.save_chats(chat_history)
    
    def get_unseen_chats(self,name):
        try:
            chat_history=self.get_chats(self)
            unseen=[]
            chat=chat_history[name]
            for i in chat["messages"]:
                if(i["is_seen"]==False and i["sender"]=="me"):
                    unseen.append([i["text"],i["id"]])
            return unseen
        except:
            pass
    def accept_message(self,name,id):
        for i in range(5):
            try:
                chat_history=self.get_chats(self)
                chat=chat_history[name]
                messages=chat["messages"]
                for i in range(len(messages)):
                    if(messages[i]["sender"]=="me" and messages[i]["id"]==id):
                        messages[i]["is_seen"]=True
                        chat["messages"]=messages
                        chat_history[name]=chat
                        self.save_chats(self,chat_history)
                        return
                return
            except:
                time.sleep(2)
    def is_id_accepted(self,name,id):
        chat_history=self.get_chats(self)
        chat=chat_history[name]
        messages=chat["messages"]
        for i in range(len(messages)):
            if(messages[i]["sender"]!="me" and messages[i]["id"]==id):
                return True
        return False
            
