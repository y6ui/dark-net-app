import ipaddress
import pickle
from cryptography.fernet import Fernet
import time
import os
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import socket
import base64
from handle_message import handle_message as hm
import json
import ast
import requests
from router_database import database as rd
from session_database import database as db_session
import random
import threading
import pickle
from cryptography.fernet import Fernet
import time
import os

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import socket
import base64
from handle_message import handle_message as hm
import json
import ast
import requests
from router_database import database as rd
from session_database import database as db_session
import random
import threading
len_of_op=2
len_of_lenn=8
class router:
    ip_port=[]
    def __init__(self,client,port,is_inbetween_router):
        self.thread_src={}
        self.src_up={}
        self.accepted_sessions=[]
        self.sockets={}#{dest:socket}
        self.is_inbetween_router=is_inbetween_router
        self.comm={}
        self.parallel_comm={}
        self.port=port
        self.connected_ids={}
        self.my_client=client
        self.private_key=""
    def generate_rsa(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        return private_key,public_key
    def encrypt_rsa(self,message,public_key):
        #return message
        reg=message
        message=message["key"]
        
        message=pickle.dumps(message)
        try:
            public_key = load_pem_public_key(public_key.encode(), backend=default_backend())
        except:
            pass
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        #print("Encrypted:", ciphertext)
        ciphertext= base64.b64encode(ciphertext).decode()
        #print(f"ciphertext:{ciphertext}")
        while("b'" in ciphertext):
            ciphertext=ciphertext[2:len(ciphertext)-1]
        reg["key"]=ciphertext
        return reg
    def decrypt_rsa(self,encrypted_msg,private_key):
        encrypted_msg=encrypted_msg
        reg=encrypted_msg
        encrypted_msg=encrypted_msg["key"]
        while("b'" in encrypted_msg):
            encrypted_msg=encrypted_msg[2:len(encrypted_msg)-1]
        encrypted_msg= base64.b64decode(encrypted_msg)
        #print(f"encrypted_msg:{encrypted_msg}")
        plaintext = private_key.decrypt(
            encrypted_msg,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        plaintext=pickle.loads(plaintext)
        #print(plaintext)
        reg["key"]=plaintext
        return reg


    def char_to_numbers(self,chars)->str:
        string=""
        for i in chars:
            string+=str(ord(i))
        return string
    def get_destination(self,des):
        return self.char_to_numbers(des[0:3])+'.'+self.char_to_numbers(des[3:6])+'.'+self.char_to_numbers(des[6:9])+'.'+self.char_to_numbers(des[9:12])
    def open_my_msg(self,msg):
        op=msg["op"]
        dest=msg["dest"]
        msg=msg["msg"]
        return op,dest,msg
    def to_byte(self,msg):
        json_msg=json.dumps(msg)  
        length=str(len(json_msg))
        length_in_len_of_lenn=""
        for i in range(8-len(length)):
            length_in_len_of_lenn+='0'
        length_in_len_of_lenn+=length
        
        return length_in_len_of_lenn.encode()+json_msg.encode()
    def send(self,ip,port,msg):
        if([ip,port]==self.get_my_ip_port()):
            msg=self.to_byte(msg)
            self.decrypt_incoming_message("",msg)
        code=(ip+'-'+str(port))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if(code in self.sockets):
                try:
                    client_socket=self.sockets[code]
                    msg1=self.to_byte(msg)
                    client_socket.sendall(msg1)  # Send bytes
                    
                except:
                    self.sockets.pop(code)
                    for i in self.sockets:
                        if (not isinstance(i, str)):
                            host, portt = i.getsockname()
                            if(host==ip and port==portt):
                                self.sockets[code]=self.sockets[i]
                                msg1=self.to_byte(msg)
                                i.sendall(msg1)
                                return
                    client_socket.connect((ip,port))
                    src_ip, src_port = client_socket.getsockname()
                    
                    if("router_dest" in msg["msg"]):
                        msg["msg"]["router_dest"]=[src_ip,src_port]
                    self.sockets[code]=client_socket
                    t=threading.Thread(target=self.keep_connection,args=(client_socket,code,))
                    t.start()
                    msg=self.to_byte(msg)
                    client_socket.sendall(msg)
            else:
                for i in self.sockets:
                    if (not isinstance(i, str)):
                        host, portt = i.getsockname()
                        if(host==ip and port==portt):
                            self.sockets[code]=self.sockets[i]
                            msg1=self.to_byte(msg)
                            i.sendall(msg1)
                            return
                client_socket.connect((ip,port))
                src_ip, src_port = client_socket.getsockname()
                
                if("msg" in msg and "router_dest" in msg["msg"]):
                    msg["msg"]["router_dest"]=[src_ip,src_port]
                else:
                    pass
                self.sockets[code]=client_socket
                t=threading.Thread(target=self.keep_connection,args=(client_socket,code,))
                t.start()
                msg=self.to_byte(msg)
                client_socket.sendall(msg)  # Send bytes
        except:
            rd.remove_router(ip,port)
            pass 
    def recive(self,conn):
        length_of_msg = conn.recv(len_of_lenn).decode() 
        data= conn.recv(int(length_of_msg))
        msg = json.loads(data)

        return msg
    def send_msg(self,msg,dest):
        
        ip,port=dest[0],int(dest[1])
        self.send(ip,port,msg)
    def encrypt_with_key(self,key,decrypted_msg):
        try:
            key=key.decode()
        except:
            pass
        while("b'" in key):
            key=key[2:len(key)-1]
        key=key.encode()    
        cipher = Fernet( (key))
        return str( cipher.encrypt((json.dumps(decrypted_msg )).encode('utf-8')))
    def decrypt_with_key(self,key,encrypted_msg):
        while("b'" in encrypted_msg):
            encrypted_msg=encrypted_msg[2:len(encrypted_msg)-1]
        encrypted_msg=encrypted_msg.encode("utf-8")    
        key=key.decode()
        while("b'" in key):
            key=key[2:len(key)-1]
        key=key.encode()   
        cipher = Fernet((key))
        try: return json.loads( cipher.decrypt(encrypted_msg))
        except:
            return encrypted_msg.decode()
    def put_in_struct(self,op,dest,msg):
        return {"op":op,"dest":dest,"msg":msg}
    def return_back(self,comm_id,msg,op):
        dest,key=self.parallel_comm[comm_id]["dest"],self.parallel_comm[comm_id]["key"]
        msg=self.encrypt_with_key(key,msg)
        msg=self.put_in_struct(op,None,{"msg":msg})
        msg["msg"]["comm_id"]=self.parallel_comm[comm_id]["comm_id"]
        self.send_msg(msg,dest)
    def get_super_server(self):
        with open("settings.json") as file:
            file=json.loads(file.read())
            routers=file["ip_port_of_routers_server"]
            return routers[random.randint(0,len(routers)-1)]
    def send_request_to_all(self,url,session_id,intended_dst,src_url):
        if(not 1111==self.port):
            req={url:{src_url:{"session_id":session_id,"ip":intended_dst[0],"port":intended_dst[1],"src_url":src_url}}}
            msg={"op":"add request","dest":intended_dst,"msg":{"data":req,"dst_url":url}}
            self.send_msg(msg,self.get_super_server())
        db_session.add_request(self,url,src_url,intended_dst,session_id)
    def get_public_ip(self):
        try:
            return self.get_my_ip(self)
        except:
            return self.get_my_ip()
        try:
            if(router.ip_port!=[]):
                return router.ip_port

            response = requests.get('https://api.ipify.org', timeout=5)
            router.ip_port= response.text
            return router.ip_port
        except requests.RequestException as e:
            return None
    def get_my_ip(self):
        s=socket.socket()
        s.connect(('8.8.8.8',53))
        ip_address = s.getsockname()[0]
        return ip_address
        
    def get_my_ip_port(self):
        
        try:
            if(self==router):
                response = self.get_public_ip(router)
                return [response,self.port]
            else:
                response = self.get_public_ip()
                return [response,self.port]
        except requests.RequestException as e:
            return f"Error: {e}"
    def find_dst(self,url,session_id,src_url):
        dst=self.get_my_ip_port()
        self.send_request_to_all(url,session_id,dst,src_url)
    def create_session_id(self):
        return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=12))   
    def create_comm_id(self):
        return ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=12))  
    def create_key(self):
        return Fernet.generate_key()
    def compact_to_json(self,key):
        pem_key = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
        return pem_key
    def compact_from_json(self,key):
        return serialization.load_pem_public_key(key.encode())
    def send_msg_to_other(self,comm_id,session_id,dst,msg,key):
        msg=self.encrypt_with_key(key,msg)
        url=""
        for i in self.my_client.url_comm_id.keys():
            if(self.my_client.url_comm_id[i]==comm_id):
                url=i

        msg={"msg":msg,"comm_id":comm_id,"session_id":session_id,"url_of_dest":url}
        msg=self.put_in_struct("return_back",None,msg)
        self.send_msg(msg,dst)

    def handle_msg(self,op,dest,msg,src_ip_port):
        match (op):
            case "create comm":
                msg=self.decrypt_rsa(msg,self.private_key)
                key,comm_id=msg["key"],msg["comm_id"]
                self.comm[comm_id]={}
                self.comm[comm_id]["key"]=bytes(key, 'utf-8')
                self.comm[comm_id]["router_dest"]=[src_ip_port[0],src_ip_port[1]]
            case "can_be_server":
                s=socket.socket()
                with s:
                    try:
                        s.connect((msg[0],msg[1]))
                        s.close()
                    except:
                        pass
            case "transfer_msg_to_router":
                comm_id,encrypted_msg=msg["comm_id"],msg["msg"]
                if(comm_id in self.comm):
                    if(comm_id in self.parallel_comm):
                        key=self.comm[comm_id]["key"]
                        msg=self.decrypt_with_key(key,encrypted_msg)
                        other_comm_id=self.parallel_comm[comm_id]["comm_id"]

                        msg["msg"]["comm_id"]=other_comm_id
                        self.parallel_comm[other_comm_id]={"key":self.comm[comm_id]["key"],"comm_id":comm_id,"dest":self.comm[comm_id]["router_dest"]}
                        self.parallel_comm[comm_id]={"key":self.comm[comm_id]["key"],"comm_id":other_comm_id,"dest":dest}
                        
                        self.send_msg(msg,dest) 
                    else:
                        key=self.comm[comm_id]["key"]
                        msg=self.decrypt_with_key(key,encrypted_msg)
                        other_comm_id=self.create_comm_id()
                        msg["msg"]["comm_id"]=other_comm_id
                        self.parallel_comm[other_comm_id]={"key":self.comm[comm_id]["key"],"comm_id":comm_id,"dest":self.comm[comm_id]["router_dest"]}
                        self.parallel_comm[comm_id]={"key":self.comm[comm_id]["key"],"comm_id":other_comm_id,"dest":dest}
                        
                        self.send_msg(msg,dest) 
                else:
                    pass
                
            case "give_open_requests":
                if(self.port==1111):
                    src_url=msg["src_url"]
                    req=db_session.get_requests(src_url)
                    try:
                        msg={"op":"add request","dest":[req["ip"],req["port"]],"msg":{"data":req,"dst_url":src_url}}
                        self.send_msg(msg,dest)
                    except:
                        
                        pass
                    return
                op="return_back"
                url=msg["url"]
                comm_id=msg["comm_id"]
                times=0
                while(db_session.get_requests(url)=={} or not db_session.get_requests(url) or times<4):
                    msg={"op":"give_open_requests","dest":self.get_my_ip_port(),"msg":{"src_url":url}}
                    self.send_msg(msg,self.get_super_server())
                    time.sleep(1)
                    times+=1
                    if(times==6):
                        return
                requestss=db_session.get_requests(url)
                msg={"op":"requests","url":url,"data":requestss}
                msg={"op":op,"dest":"","msg":{"msg":msg,"comm_id":comm_id}}
                self.send_msg(msg,self.comm[comm_id]["router_dest"])
            case "return_back":
                if(msg["comm_id"] in self.my_client.comm_ids):
                    self.my_client.recived_new_message(msg)
                    return
                else:
                    pass
                if(self.is_inbetween_router):
                    self.return_back(msg["comm_id"],msg["msg"],"return_back")
            case "add request":
                data=msg["data"]
                dst_url=msg["dst_url"]
                db_session.add_requests(dst_url,data)
            case "create_conn_to_dest":
                
                comm_id=msg["comm_id"]
                key=self.comm[comm_id]["key"]
                session_id=msg["session_id"]    
                src_url=msg["src_url"]            
                self.find_dst(msg["url_of_dest"],session_id,src_url)
                self.connected_ids[session_id]=[msg["comm_id"]]
                #self.parallel_comm[self.connected_ids[session_id][0]]={"comm_id":comm_id,"key":key,"dest":msg["src"]}
                #msg=self.decrypt_with_key(key,encrypted_msg)
            case "accept connection":#accept request conection from the other party
                
                session_id=msg["session_id"]
                comm_id=msg["comm_id"]
                url=msg["url"]
                if(session_id in self.accepted_sessions):
                    return
                self.accepted_sessions.append(session_id)
                other_comm_id=self.connected_ids[session_id][0]
                #msg["comm_id"]=other_comm_id
                self.parallel_comm[other_comm_id]={"key":self.comm[comm_id]["key"],"comm_id":comm_id,"dest":self.comm[comm_id]["router_dest"]}
                self.parallel_comm[comm_id]={"key":self.comm[other_comm_id]["key"],"comm_id":other_comm_id,"dest":self.comm[other_comm_id]["router_dest"]}
                if(session_id in self.connected_ids):
                    self.connected_ids[session_id].append(msg["comm_id"])

                    #db_session.lower_request(url)
                msg=hm.ping()
                self.send_msg_to_other(comm_id,session_id,self.comm[comm_id]["router_dest"],msg,self.comm[comm_id]["key"])
                self.send_msg_to_other(self.parallel_comm[comm_id]["comm_id"],session_id,self.parallel_comm[comm_id]["dest"],msg,self.comm[self.parallel_comm[comm_id]["comm_id"]]["key"])
            case "send_msg_to_other":
                session_id=msg["session_id"]
                comm_id=msg["comm_id"]
                key=self.comm[msg["comm_id"]]["key"]
                try:
                    msg["msg"]=self.decrypt_with_key(key,msg["msg"])
                except:
                    pass
                #if(self.connected_ids[session_id][0]==msg["comm_id"]):
                #    comm_id=self.connected_ids[session_id][1]
                #else:
                #    comm_id=self.connected_ids[session_id][0]
                self.send_msg_to_other(self.parallel_comm[comm_id]["comm_id"],session_id,self.parallel_comm[comm_id]["dest"],msg["msg"],self.parallel_comm[comm_id]["key"])
            case "add_router":
                if(self.port==1111 or src_ip_port in self.get_super_server()):
                    rd.add_router(src_ip_port[0],dest[1],self.compact_from_json(msg["public_key"]))
                else:
                    pass
            case "give routers":
                msg=rd.get_router(500,self.get_my_ip_port())
                msg={"op":"recived routers","dest":'',"msg":msg}
                self.send(src_ip_port[0],src_ip_port[1],msg)
            case "recived routers":                

                rd.add_routers(msg)
            case "comm_ping":
                comm_id=msg["comm_id"]
                msg=hm.ping_comm()
                self.send_msg_to_other(comm_id,"",self.comm[comm_id]["router_dest"],msg,self.comm[comm_id]["key"])

    def keep_connection(self,socket,code):
        self.thread_src[code]=True
        counter=0
        while(self.thread_src[code]):
            try: 
                socket.settimeout(1) 
                msg=self.recive(socket)
                t=threading.Thread(target=self.decrypt_incoming_message,args=(socket,msg,))
                t.start()
                counter=0

            except:
                pass
            counter+=1
            if(counter==61):
                self.thread_src[code]=False
                try:
                    self.sockets.pop(code)
                except:
                    pass
                return
    def listen_to_traffic(self):
        if(self.is_inbetween_router):
            s=socket.socket()
            src=self.get_my_ip_port()
            s.bind(("0.0.0.0",src[1]))
            s.listen() 
            while(True):
                c, addr = s.accept() 
                add=[addr[0],addr[1]]
                #if( self.is_private_ip(add[0])):
                #    add[0]=self.get_my_ip_port()[0]
                self.sockets[add[0]+'-'+str(add[1])]=c

                t=threading.Thread(target=self.keep_connection,args=(c,add[0]+'-'+str(add[1]),))
                self.thread_src[add[0]+"-"+str(add[1])]=True
                t.start()
    def is_private_ip(self,ip):
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private            
    def decrypt_incoming_message(self,s,msg):
        ip=""
        port=1
        
        if(not s== ""):
            ip ,port= s.getpeername()
            print(f"ip:{ip}")
            #if( self.is_private_ip(ip)):
            #    ip=self.get_my_ip_port()[0]
        else:
            return
            ip_p=self.get_my_ip_port()
            ip=ip_p[0]
            port=ip_p[1]
            if( self.is_private_ip(ip)):
                ip=self.get_my_ip_port()[0]
        op,dest,msg=self.open_my_msg(msg)
        print(f"op:{op}")
        src_ip_port=[ip,port]
        code=f"{ip}-{port}"
        self.src_up[code]=True
        self.handle_msg(op,dest,msg,src_ip_port)