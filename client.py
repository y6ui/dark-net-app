import logging

import threading
from comm_utills import router 
from session_database import database as sd
from router_database import database as rd
from handle_message import handle_message as hm
from chats import chats as ch
import socket
import os
import time
import json
from clean_up import clean
import random
my_url="my_url.txt"
port_file="my_port.txt"
class client:
    def __init__(self,gui):
        
        self.clean=None
        self.listening_comm_id2=""
        self.url_comm_id2={}
        self.session_id_comm_id2={}
        self.up_comm={}
        self.my_sessions=[]
        self.url_comm_id={}
        self.url_name={}
        self.gui=gui
        self.url=""
        self.comm_ids=[]
        self.inbetween_routers={}#{comm_id:[[ip,port,public_key,symetric_key],[ip,port,public_key,symetric_key],...]}
        self.my_ip_port=self.get_src()
        self.accepted_requests={}
        self.session_id_comm_id={}
        self.up_connection={}
        self.my_url=self.get_url()
    def print(self,msg,level):
        
        if(level==1):
            logging.info(msg)
        elif(level==2):
            logging.warning(msg)    
        elif(level==3):
            logging.error(msg)
    def generate_url(self):
        return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=4)) 
    def get_url(self):
        if os.path.exists(my_url):
            with open(my_url, "r") as file:
                content = file.read()
                return content
        else:
            with open(my_url, "w") as file:
                url=self.generate_url()
                file.write(url)
                print(f"new url: {url}")
                return url
    def get_src(self):
        if (os.path.exists(port_file)):
            with open(port_file, "r") as f:
                port = int(f.read())
        else:

            port= random.randint(1112,9999)
            with open(port_file, "w") as f:
                f.write(f"{port}")
        
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        return [router.get_public_ip(router),port]
    def decrypt_from_routers(self,msg,id):
        routers=self.inbetween_routers[id]
        for i in routers:
            try:
                msg=self.my_router.decrypt_with_key(i[3],msg)
            except:
                return msg
        return msg
    def recived_new_message(self,msg):
        
        id=msg["comm_id"]
        url=""
        for i in self.url_comm_id.keys():
            if(self.url_comm_id[i]==id):
                url=i

        if("comm_id" in msg):
            comm_id=msg["comm_id"]
        msgg=msg
        msg=msg["msg"]
        msg=self.decrypt_from_routers(msg,id)
        url_src=url
        try:
            if(len(msg)==2):
                url_src=msg[1]
                msg=msg[0]
        except:
            pass
        if 1==1:
            #self.one_2(id,url_src)
            if(url_src in self.url_comm_id and self.url_comm_id[url_src]!=id):

                if(url_src !="" and id in self.url_comm_id2[url_src]):
                    if("op" in msg and msg["op"]!="requests" ):
                        self.move_to_2(id,url_src)
                        
                        self.send_message_to_other(hm.ping(),url_src)
                else:
                    pass
            else:
                if(url_src in self.url_comm_id2 and  id in self.url_comm_id2[url_src]):
                    pass
                    #self.move_to_2(id,url_src)
                else:
                    pass
        else:
            pass
        try:
            if("op" in msg ):
                if 1==1:
                    op=msg["op"]
                    data=msg["data"]
                    if(op=="requests"):
                        url=self.my_url
                        self.up_comm[id]=True
                        sd.add_requests(self.my_url,{self.my_url:data})
                        
                    elif(op=="ping"):
                        self.url_comm_id[url_src]=id
                        if(url_src!=self.my_url):
                            self.url_comm_id[id]=url_src
                            self.url_comm_id[url_src]=id
                            self.return_ping(id)
                            self.up_connection[id]=True
                            self.up_connections(id, True)
                    elif(op=="return_ping"):
                        self.url_comm_id[url_src]=id
                        self.url_comm_id[id]=url_src
                        if(url_src!=self.my_url):
                            self.up_connection[id]=True
                            self.up_connections(id,True)
                    elif(op=="accept_message"):
                        ch.accept_message(ch,self.url_name[self.url_comm_id[id]],data)
                    elif(op=="ping_comm"):
                        self.up_comm[id]=True
                    
                else:
                    if(url==self.my_url):
                        return
                    self.up_connections(id,True)
                    self.up_connection[id]=True                    
                    url=url_src
                    accept_message=hm.accept_message(msg[1])
                    
                    self.send_message_to_other(accept_message,url)
                    if(ch.is_id_accepted(ch,self.url_name[url],msg[1])):
                        
                        return
                    
                    msg=msg[0]
                    self.gui.chat_screen.write_in_chat(msg,url,self.my_url)  
                    id_=ch.get_chats(ch)[self.url_name[url]]["messages"][-1]["id"]
                    ch.accept_message(ch,self.url_name[self.url_comm_id[id]],id_)
            else:
                try:
                    if(url==self.my_url):
                        return
                    self.up_connections(id,True)
                    self.up_connection[id]=True                    
                    url=url_src
                    accept_message=hm.accept_message(msg[1])
                    
                    self.send_message_to_other(accept_message,url)
                    if(ch.is_id_accepted(ch,self.url_name[url],msg[1])):
                        
                        return
                    
                    msg=msg[0]
                    self.gui.chat_screen.write_in_chat(msg,url,self.my_url)  
                    id_=ch.get_chats(ch)[self.url_name[url]]["messages"][-1]["id"]
                    ch.accept_message(ch,self.url_name[self.url_comm_id[id]],id_)
                except:
                    pass
        except:
            pass
    def move_to_2(self,comm_id,url):
        self.listening_comm_id=comm_id
        self.url_comm_id[url]=comm_id
        self.url_comm_id[comm_id]=url
        for i in range (len(self.url_comm_id2[url])):
            if(comm_id in self.session_id_comm_id2 and  self.url_comm_id2[url][i]==comm_id):
                #self.session_id_comm_id[comm_id]=self.session_id_comm_id2[comm_id][i]
                pass
        self.up_comm[comm_id]=True

    def up_connections(self,comm_id,t_f):
        self.up_connection[comm_id]=t_f
        chat_history=ch.get_chats(ch)

        for chat in chat_history:
            if(comm_id in self.url_comm_id and chat_history[chat]["url"]==self.url_comm_id[comm_id]):
                ch.change_online_status(ch,chat,t_f)
                
    def return_ping(self,comm_id):
        msg=hm.return_ping()
        url=""
        for i in self.url_comm_id:
            if(self.url_comm_id[i]==comm_id):
                url=i
        self.send_message_to_other(msg,url)
    def move_through_roters(self,id,msg):
        length=len(self.inbetween_routers[id])
        print(f"sending to {length} routers")
        key=self.inbetween_routers[id][length-1][3]
        if("msg" in msg["msg"]):
           msg["msg"]["msg"]=self.my_router.encrypt_with_key(key,msg["msg"]["msg"])
        
        if(length>1):
            for i in range(length-1):
                key=self.inbetween_routers[id][length-2-i][3]
                encrypted_msg=self.my_router.encrypt_with_key(key,msg)
                dst=self.inbetween_routers[id][length-i-1][:2]
                msg={"op":"transfer_msg_to_router","dest":dst,"msg":{"comm_id":id,"msg":encrypted_msg}}


        
        return msg
    def start_connection(self,router,index,id,msg):
        dst_of_previous=[]
        

        if(index==0):
            dst_of_previous=self.my_ip_port
            msg={"op":"create comm","dest":"","msg":{"comm_id":id,"router_dest":dst_of_previous,"key":str(router[3]),"msg":msg}}
            msg["msg"]=(self.my_router.encrypt_rsa(msg["msg"],router[2]))
        else:
            
            dst_of_previous=self.inbetween_routers[id][index-1][:2]
            msg={"op":"create comm","dest":"","msg":{"comm_id":id,"router_dest":dst_of_previous,"key":str(router[3]),"msg":msg}}
            msg["msg"]=(self.my_router.encrypt_rsa(msg["msg"],router[2]))
            msg=self.move_through_roters(id,msg)
            
            

           
        if(index!=0):
            self.my_router.send(self.inbetween_routers[id][0][0],self.inbetween_routers[id][0][1],msg)

            
        else:
            self.my_router.send(router[0],router[1],msg)

            
        print("sent")
    def create_new_outside_connection(self,amount_of_routers_inbetween,url):
        #if(url in self.url_comm_id and self.url_comm_id[url] in self.up_comm and self.up_comm[self.url_comm_id[url]]):
        #    return self.url_comm_id[url]
        
        while True:
            try:
                id=self.my_router.create_comm_id()
                routers=[]
                while routers==[]:
                    try:routers=rd.get_router(amount_of_routers_inbetween,self.my_ip_port)
                    except:pass
                    time.sleep(0.1)
               
                key=self.my_router.create_key()
                router=routers[0]
                router.append(key)
                if( id in self.inbetween_routers):
                    self.inbetween_routers[id].append(router)
                else:
                    self.inbetween_routers[id]=[router]
                for i in range(amount_of_routers_inbetween):
                    if(i!=0):
                        routerr=routers[i]
                        key=self.my_router.create_key()
                        routerr.append(key)
                        self.inbetween_routers[id].append(routerr)
                    self.start_connection(self.inbetween_routers[id][i],i,id,"")
                    time.sleep(0.3)
                self.url_comm_id[url]=id
                self.up_comm[id]=True
                self.one_2(id,url)
                self.comm_ids.append(id)
                return id
            except:
                print("failed")
            time.sleep(5)

    def accept_request(self,url):
        request=sd.get_requests(self.my_url)
        sd.lower_request(self.my_url,url)
        request=request[url]
        comm_id=0
        while True:

            try:
                comm_id=self.create_new_outside_connection(self.amount_of_routers_inbetween,url)
                break
                if(not (self.inbetween_routers[comm_id][-1][0]==request["ip"] and self.inbetween_routers[comm_id][-1][1]==request["port"])):
                    break
                else:
                    print("oops")
                    time.sleep(5)
            except:
                pass

        
        self.listening_comm_id=comm_id
        self.comm_ids.append(comm_id)
        self.url_comm_id[url]=comm_id
        self.url_comm_id[comm_id]=url
        self.up_comm[comm_id]=True
        self.session_id_comm_id[comm_id]=request["session_id"]
        try:
            self.accepted_requests[request["session_id"]]=[request["ip"],request["port"]]

            session_id=request["session_id"]
            key=self.my_router.create_key()
            request=[request["ip"],request["port"]]
            request.append(rd.get_key(request[0],request[1]))
            request.append(key)
            self.inbetween_routers[comm_id].append(request)
            msg=""
            self.start_connection(request,self.amount_of_routers_inbetween,comm_id,msg)
            msg={"op":"accept connection","dest":"","msg":{"comm_id":comm_id,"session_id":session_id,"url":url}}

            msg=self.move_through_roters(comm_id,msg)
            self.my_router.send(self.inbetween_routers[comm_id][0][0],self.inbetween_routers[comm_id][0][1],msg)
            self.send_message_to_other(hm.ping(),url)
            self.print("accept conn",1)

        except  :
            pass
    def add_request(self,comm_id,url):
        try:
            self.url_comm_id[url]=comm_id
            self.url_comm_id[comm_id]=url
            session_id=self.my_router.create_session_id()
            self.my_sessions.append(session_id)
            self.session_id_comm_id[session_id]=comm_id
            self.session_id_comm_id[comm_id]=session_id
            msg={"op":"create_conn_to_dest","dest":"","msg":{"src":self.inbetween_routers[comm_id][-1][:2],"src_url":self.my_url,"comm_id":comm_id,"url_of_dest":url,"session_id":session_id}}
            msg=self.move_through_roters(comm_id,msg)
            self.my_router.send(self.inbetween_routers[comm_id][0][0],self.inbetween_routers[comm_id][0][1],msg)
        except:
            pass
    def send_message_to_other(self,msg,url):
        try:
            comm_id=self.url_comm_id[url]
            session_id=self.session_id_comm_id[comm_id]
            msg={"op":"send_msg_to_other","dest":"","msg":{"msg":[msg,self.my_url],"comm_id":comm_id,"session_id":session_id}}
            msg=self.move_through_roters(comm_id,msg)
            self.my_router.send(self.inbetween_routers[comm_id][0][0],self.inbetween_routers[comm_id][0][1],msg)
        except:
            if(url not in self.url_comm_id):
                self.start_new_request(url)
    def get_best_comm_id(self):
        return list(self.up_comm.keys())[-1]

        for i in range (len(self.comm_ids)):
            if( self.up_comm[self.comm_ids[-i-1]]):
                return self.comm_ids[-1-i]
        return self.comm_ids[-1]
    def get_open_requests(self,url):
        time.sleep(3)
        while True:
            try:
                comm_id= self.get_best_comm_id()
                self.comm_ids.append(comm_id)
                msg={"op":"give_open_requests","dest":"","msg":{"comm_id":comm_id,"url":self.my_url}}
                msg=self.move_through_roters(comm_id,msg)
                self.my_router.send(self.inbetween_routers[comm_id][0][0],self.inbetween_routers[comm_id][0][1],msg)
                print("give_open_requests")
            except:
                self.create_new_outside_connection(self.amount_of_routers_inbetween,None)

            time.sleep(2)
    def get_open_requests_t(self,url):
        t=threading.Thread(target=self.get_open_requests,args=(url,))
        t.start()
    def get_routers_t(self):
        while(True):
            time.sleep(30)
            self.get_routers()
    def get_routers(self):

        try:
            dest=self.my_router.get_super_server()
            soc=socket.socket()
            soc.connect((dest[0],dest[1]))
            code=(dest[0]+'-'+str(dest[1]))
            self.my_router.sockets[code]=soc
            t=threading.Thread(target=self.my_router.keep_connection,args=(soc,code,))
            self.my_router.thread_src[code]=True
            t.start()
            src_ip, src_port = soc.getsockname()
            src_ip=self.my_ip_port[0]
            self.my_router.send_msg({"op":"give routers","dest":[src_ip,src_port],"msg":[]},dest)
            return
        except:
            pass
    def one_2(self,comm_id,url):
        try:
            self.listening_comm_id2=comm_id
            self.comm_ids.append(comm_id)
            if (url not in self.url_comm_id2):
                self.url_comm_id2[url]=[]
            if(len(self.url_comm_id2[url])==0):
                self.url_comm_id2[url]=[]
                self.url_comm_id2[comm_id]=[]
                self.session_id_comm_id2[comm_id]=[]

            self.url_comm_id2[url].append(comm_id)
            if(comm_id in self.url_comm_id2):
                self.url_comm_id2[comm_id].append(url)
            else:
                self.url_comm_id2[comm_id]=[url]
            
            try:
                if (comm_id in self.session_id_comm_id):
                    self.session_id_comm_id2[comm_id].append(self.session_id_comm_id[comm_id])
            except:
                pass
        except  Exception as e:
            print(e)
    def keep_add_me_router(self,public_key,dest):
        while(True):
            self.my_router.send_msg({"op":"add_router","dest":self.my_router.get_my_ip_port(),"msg":{"public_key":self.my_router.compact_to_json(public_key)}},dest)
            time.sleep(30)
    def add_me_router(self,public_key):
        dest=self.my_router.get_super_server()
        soc=socket.socket()
        soc.connect((dest[0],dest[1]))
        code=(dest[0]+'-'+str(dest[1]))
        self.my_router.sockets[code]=soc
        self.my_router.send_msg({"op":"add_router","dest":self.my_router.get_my_ip_port(),"msg":{"public_key":self.my_router.compact_to_json(public_key)}},dest)
        t=threading.Thread(target=self.keep_add_me_router,args=(public_key,dest,))
        t.start()
    def replace_connection(self,comm_id,url,is_end):
        request=sd.get_requests(self.my_url)
        if url in request :
            self.one_2(comm_id,url)
            
            request=request[url]
            if((request!={} and not is_end) or (comm_id not in  self.session_id_comm_id )or (request!={}  and request["session_id"]!=self.session_id_comm_id[comm_id] and request["src_url"]==url and request["session_id"] not in self.my_sessions)):
                self.accept_request(url)
                return True
        else :#Exception as e:
            pass
        if(is_end or ( comm_id in self.up_comm and self.up_comm[comm_id]==False)):
            self.start_new_request(url)
            return True
        return False
    def casual_ping(self,chats):
        
        for i in (chats):
            try:
                comm_id=self.url_comm_id[self.url_name[i]]
                self.up_comm[comm_id]=False
                url=""
                
                for j in (self.url_comm_id):
                    if(self.url_comm_id[j]==comm_id):
                        url=j
                msg={"op":"comm_ping","dest":"","msg":{"comm_id":comm_id}}
                

                msg=self.move_through_roters(comm_id,msg)
                if 1==1:
                    if(url!=""):
                        self.my_router.send_msg(msg,self.inbetween_routers[comm_id][0][:2])
                        
                    else:
                        print("no url")
                else:
                    print("wtf\n\n")
            except:
                pass
    def ping(self,chats):
        for i in (chats):
            try:
                comm_id=self.url_comm_id[self.url_name[i]]
                url=""
                self.up_connection[comm_id]=False
                for j in (self.url_comm_id):
                    if(self.url_comm_id[j]==comm_id):
                        url=j
                msg=hm.ping()

                if 1==1:
                    if(url!=""):
                        self.send_message_to_other(msg,url)
                        
            except:
                pass
    def handle_down_router(self):
        while(True):
            try:
                chats=ch.get_chats(ch)
                
                
                self.casual_ping(chats) 
                self.ping(chats)  
                time.sleep(random.randint(10,15))
                self.replace_conn(True)
                
                
                self.casual_ping(chats)  
                self.ping(chats)  
                time.sleep(random.randint(10,15))
                self.replace_conn(True)
                self.casual_ping(chats)  
                self.ping(chats)  
                time.sleep(random.randint(10,15))
                self.replace_conn(True)
                self.casual_ping(chats)  
                self.ping(chats)  
                time.sleep(random.randint(10,15))
                self.replace_conn(True)
                self.casual_ping(chats) 
                self.ping(chats)  
                time.sleep(random.randint(10,15))
                self.replace_conn(True)
            except:
                pass
    def replace_comm(self):
        chats=ch.get_chats(ch)
        for i in (chats):
            if(chats[i]["url"] in self.url_comm_id):
                comm_id=self.url_comm_id[chats[i]["url"]]
            else:
                comm_id=self.create_new_outside_connection(self.amount_of_routers_inbetween,chats[i]["url"] )
                self.url_comm_id[chats[i]["url"]]=comm_id
                self.url_comm_id[comm_id]=chats[i]["url"]
                self.up_comm[comm_id]=False
            if(not (comm_id in self.up_comm and self.up_comm[comm_id]==True)):
                
                if(comm_id not in self.up_connection):
                    self.up_connection[comm_id]=False
                up=self.up_connection[comm_id]
                if(comm_id not in self.url_comm_id):
                    self.url_comm_id[comm_id]=chats[i]["url"]
                    self.url_comm_id[chats[i]["url"]]=comm_id
                if(comm_id in self.up_connection and self.up_connection[comm_id]==False):
                    if(self.replace_connection(comm_id,self.url_comm_id[comm_id],False) ):
                        self.up_connection[self.url_comm_id[chats[i]["url"]]]=False
                        self.up_comm[comm_id]=False
                        self.up_connection[comm_id]=False
                        self.up_connections(comm_id,False)
                    else:
                        self.up_connection[comm_id]=up
                        self.up_connections(comm_id,True)
                        self.send_unseen_messages(comm_id,i,chats[i]["url"])
            else:
                pass
    def replace_conn(self,is_end):
        chats=ch.get_chats(ch)
        for i in (chats):
            if(chats[i]["url"] in self.url_comm_id):
                comm_id=self.url_comm_id[chats[i]["url"]]
            else:
                comm_id=self.create_new_outside_connection(self.amount_of_routers_inbetween,chats[i]["url"] )
                self.url_comm_id[chats[i]["url"]]=comm_id
                self.url_comm_id[comm_id]=chats[i]["url"]
            if((comm_id in self.up_connection and self.up_connection[comm_id]==False)):
                self.up_connections(comm_id,False)
                self.up_connection[comm_id]=False
                self.replace_connection(comm_id,self.url_comm_id[comm_id],is_end)

            else:
                self.up_connections(comm_id,True)
                self.up_connection[comm_id]=True
                self.send_unseen_messages(comm_id,i,chats[i]["url"])
    def send_unseen_messages(self,comm_id,name,url):
        messages=ch.get_unseen_chats(ch,name)
        for i in messages:
            self.send_message_to_other(i,url)
    def handle_down_router_t(self):
        t=threading.Thread(target=self.handle_down_router,args=())
        t.start()
    def start_new_request(self,url):
        target_url=url
        comm_id=self.create_new_outside_connection(self.amount_of_routers_inbetween,url)
        self.up_comm[comm_id]=True
        self.listening_comm_id=comm_id
        self.url_comm_id[url]=comm_id
        self.url_comm_id[comm_id]=url
        self.add_request(comm_id,target_url)
        self.comm_ids.append(comm_id)
    def set_request_all(self):
        chats=ch.get_chats(ch)
        for i in chats:
            
            ch.change_online_status(ch,i,False) 
    def set_url_name(self):
        chats=ch.get_chats(ch)
        for i in chats:
            self.url_name[i]=chats[i]["url"]
            self.url_name[chats[i]["url"]]=i
    def accept_all(self):
        chats=ch.get_chats(ch)
        for i in chats:
            if(sd.is_url_in_database(chats[i]["url"],self.my_url)):
                self.start_new_request(chats[i]["url"])  
            else:
                self.start_new_request(chats[i]["url"])  
            comm_id=self.url_comm_id[chats[i]["url"]]
            self.up_connection[comm_id]=False
    def can_bind_to_port(self ):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", self.my_ip_port[1]))
            return True
        except OSError as e:
            print(f"Cannot bind to port {self.my_ip_port[1]}: {e}")
            return False
    def become_server(self):
        self.my_router=router(self,self.my_ip_port[1],True)
        private_key,public_key=self.my_router.generate_rsa()
        self.my_router.private_key=private_key
        if(not self.my_ip_port[1]==1111):
            self.my_router.is_inbetween_router = True
            t=threading.Thread(target=self.my_router.listen_to_traffic,args=())
            t.start()
            self.add_me_router(public_key)
        else:
            self.my_router.is_inbetween_router = True
            t=threading.Thread(target=self.my_router.listen_to_traffic,args=())
            t.start()
            self.clean=clean(self.my_router,self)
    def can_be_server(self):
        s = socket.socket()
        if(self.my_ip_port[1]==1111):
            return True
        self.my_router.send_msg({"op":"can_be_server","dest":"","msg":self.my_ip_port},self.my_router.get_super_server())
        with s:
            try:
                s.bind(("0.0.0.0", self.my_ip_port[1]))
                s.listen()
                s.settimeout(2)

                conn, addr = s.accept()
                print("you can be server")
                return True
            except:
                return False
        return False
    def main(self):
        self.my_url=self.get_url()
        print(f"my url: {self.my_url},ip-port:{self.my_ip_port}")
        if(self.my_ip_port[1]!=1111):
            self.my_router=router(self,self.my_ip_port[1],False)
            t=threading.Thread(target=self.my_router.listen_to_traffic,args=())
            t.start()
            amount_of_routers_inbetween=3#int(input("give amount of routers "))
            self.amount_of_routers_inbetween=amount_of_routers_inbetween
            self.set_url_name()
            self.get_routers()
            while(len(rd.get_router(amount_of_routers_inbetween,self.my_ip_port))<amount_of_routers_inbetween):
                print(f"len{len(rd.get_router(amount_of_routers_inbetween,self.my_ip_port))}")
                time.sleep(10)
                self.get_routers()
            t=threading.Thread(target=self.get_routers_t,args=())
            t.start()
            self.get_open_requests_t(self.my_url)
            self.set_request_all()
            self.accept_all()
            self.handle_down_router_t()
            self.clean=clean(self.my_router,self)