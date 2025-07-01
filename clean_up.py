import socket
import time
import threading
from router_database import database as rd
class clean:
    def __init__(self,router,client):
        self.client=client
        self.router=router
        t=threading.Thread(target=self.main)
        t.start()
    def main(self):
       
        while True:
            time.sleep(30)
            print("ddd\n\n\n\n\nn\n\n\\n\n\n\n\n")
            #self.clean_sockets()
            self.clean_dictionaries()
    def clean_dictionaries(self):
        if(len(self.client.up_comm)>100000):
            self.client.up_comm={}
        if(len(self.client.my_sessions)>100000):
            self.client.my_sessions=[]
        if(len(self.client.url_comm_id)>100000):
            self.client.url_comm_id={}
        if(len(self.client.comm_ids)>100000):
            self.client.comm_ids=[]
        if(len(self.client.inbetween_routers)>100000):
            self.client.inbetween_routers={}
        if(len(self.client.accepted_requests)>100000):
            self.client.accepted_requests={}    
        if(len(self.client.session_id_comm_id)>100000):
            self.client.session_id_comm_id={}    
        if(len(self.client.up_connection)>100000):
            self.client.up_connection={}    
        
        if(len(self.router.thread_src)>100000):
            self.router.thread_src={} 
        if(len(self.router.src_up)>100000):
            self.router.src_up={} 
        if(len(self.router.accepted_sessions)>100000):
            self.router.accepted_sessions=[]
        if(len(self.router.comm)>100000):
            self.router.comm={} 
        if(len(self.router.parallel_comm)>100000):
            self.router.parallel_comm={} 
        if(len(self.router.connected_ids)>100000):
            self.router.connected_ids={} 
        if(len(self.router.sockets)>100000):
            self.clean_sockets()
            self.router.sockets={}
        if(self.client.my_ip_port[1]==1111):
            self.is_router_up()
    def is_router_up(self):
        routers=rd.get_database()
        good_routers=[]
        for i in routers:
            try:
                s=socket.socket()
                
                s.connect((i[0],int(i[1])))
                s.close()
                print(f"all good:{i[1]}")
                good_routers.append(i)
            except:
                print(f"port:{i[1]}")
        print(f"good routers:{good_routers}")
        rd.save_database(good_routers)
    def is_socket_online(self,sock,src):
        if(src in self.router.src_up and self.router.src_up[src]):
            self.router.src_up[src]=False
            return True
        else:
            
            self.router.thread_src[src]=False
            return False
            
    def clean_sockets(self):
        for i in list(self.router.sockets):
            if(not "1111" in i and not self.is_socket_online(self.router.sockets[i],i)):

                self.router.sockets[i].close()
                self.router.sockets.pop(i)
                print("good by soc")
            else:
                print("nop")