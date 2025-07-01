import logging
logging.basicConfig(
        filename='app.log',
        level=logging.INFO,  # You can change to DEBUG, WARNING, etc.
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import webbrowser

from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from chats import chats as ch
from client import client
from session_database import database as sd
import threading
import time
from kivy.uix.spinner import Spinner
from router_database import database as rd 
from kivy.core.clipboard import Clipboard

# Dummy chat history data


# Separate chat requests with session ids, now using URLs as keys


# Your personal URL
my_url = ""

# Set the window background color
Window.clearcolor = (0.05, 0.05, 0.1, 1)  # Dark background for a sleek look

class RoundedButton(Button):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
        except:
            pass
        self.background_normal = ""
        self.color = (1, 1, 1, 1)
        self.font_size = 16
        self.size_hint_y = None
        self.height = 50
        with self.canvas.before:
            Color(0.3, 0.6, 0.8, 1)  # Light blue background for buttons
            self.rect = RoundedRectangle(radius=[20, 20, 20, 20])

        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
class RouterSettingsScreen(Screen):
    def __init__(self, client, **kwargs):
        super().__init__(**kwargs)
        self.client = client
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Title
        layout.add_widget(Label(text="Router Configuration", font_size=20, size_hint_y=None, height=40, color=(1, 1, 1, 1)))

        # Hop count label and spinner
        layout.add_widget(Label(
            text="Select Number of Routers (Hops):",
            size_hint_y=None,
            height=30,
            color=(1, 1, 1, 1)
        ))
        length=min(len(rd.get_database())-1,8)
        if(length<2):
            length=2
        self.router_spinner = Spinner(
            text='3',
            values=[str(i) for i in range(2, length+1)],
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.5, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        layout.add_widget(self.router_spinner)

        # Save and back buttons
        button_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        save_button = RoundedButton(text="Save", background_color=(0.2, 0.7, 0.4, 0.8))
        save_button.bind(on_press=self.save_settings)
        back_button = RoundedButton(text="Back", background_color=(0.5, 0.5, 0.5, 0.8))
        back_button.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))

        button_layout.add_widget(save_button)
        button_layout.add_widget(back_button)
        layout.add_widget(button_layout)

        self.add_widget(layout)

    def save_settings(self, instance):
        
        if 1==1:
            self.client.url_comm_id2={}
            self.client.session_id_comm_id2={}
            self.client.up_comm={}
            self.client.my_sessions=[]
            self.client.url_comm_id={}
            self.client.comm_ids=[]
            self.client.inbetween_routers={}
            self.client.session_id_comm_id={}
            self.client.up_connection={}
        selected_hops = int(self.router_spinner.text)
        self.client.amount_of_routers_inbetween = selected_hops
          # Store in client for use later
        self.manager.current = "home"

class HomeScreen(Screen):
    def __init__(self, chats, client, **kwargs):
        self.client = client
        self.chats = chats
        self.is_used_server = False
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Top buttons
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)

        # Add person button
        add_button = RoundedButton(text="+ Add Person", background_color=(0.9, 0.2, 0.2, 0.8))
        add_button.bind(on_press=self.open_add_person_popup)
        top_layout.add_widget(add_button)

        # Notifications button
        notifications_button = RoundedButton(text="View Notifications", background_color=(0.8, 0.2, 0.5, 0.8))
        notifications_button.bind(on_press=self.view_notifications)
        top_layout.add_widget(notifications_button)

        layout.add_widget(top_layout)
        self.layout = top_layout

        # Router settings button
        router_settings_button = RoundedButton(text="Router Settings", background_color=(0.4, 0.6, 0.8, 0.8))
        router_settings_button.bind(on_press=self.go_to_router_settings)
        layout.add_widget(router_settings_button)

        self.wait_for_become_server(top_layout)

        # URL display and copy button
        url_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=0,
            padding=(0, 0, 0, 0),
            size_hint=(None, None)
        )

        # Calculate or define a fixed width for centering
        url_box.size = (500, 40)  # You can adjust 500 based on your screen size
        url_box.pos_hint = {'center_x': 0.75}

        

        copy_button = Button(
            text=f"{client.my_url}",
            size_hint_x=None,
            width=100,
            background_color=(0.2, 0.6, 0.2, 0.8)
        )
        copy_button.bind(on_press=lambda instance: Clipboard.copy(client.my_url))
        url_box.add_widget(copy_button)

        layout.add_widget(url_box)

        # Scrollable list of contacts
        self.scroll_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))

        scroll_view = ScrollView()
        scroll_view.add_widget(self.scroll_layout)
        layout.add_widget(scroll_view)

        Clock.schedule_once(lambda dt: self.update_people_list())
        self.update_people_list()

        self.add_widget(layout)
    def go_to_router_settings(self, instance):
        if self.manager:
            self.manager.current = "router_settings"

    def wait_for_become_server(self,top_layout):
        try:
            if(self.client.can_be_server() ):
                become_server_button = RoundedButton(text="Become router", background_color=(0.2, 0.7, 0.4, 0.8))
                become_server_button.bind(on_press=self.become_server)
                top_layout.add_widget(become_server_button)
                self.my_button=become_server_button
        except:
            pass
    def become_server(self, instance):
        popup = Popup(title="Server Mode",
                    content=Label(text="You are now acting as a server."),
                    size_hint=(None, None), size=(300, 200))
        popup.open()
        self.is_used_server=True
        # Launch server functionality (if needed)
        # This is a placeholder for the actual server logic
        self.layout.remove_widget(self.my_button)

        self.client.become_server()
    def show_router_info(self, instance):
        person = instance.person_name
        url = self.client.url_name.get(person, person)
        comm_id = self.client.url_comm_id.get(url)

        routers = self.client.inbetween_routers.get(comm_id, [])

        # Main popup layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scroll_view = ScrollView(size_hint=(1, 1))
        inner_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        inner_layout.bind(minimum_height=inner_layout.setter('height'))

        if not routers:
            inner_layout.add_widget(Label(
                text="No routers found.",
                size_hint_y=None,
                height=30,
                color=(1, 1, 1, 1)
            ))
        else:
            for router in routers:
                try:
                    ip, port, *_ = router

                    row = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=40,
                        spacing=10,
                        padding=[5, 5]
                    )

                    # Computer icon — make sure the image exists at this path
                    icon = Image(
                        source='computer_icon.png',  # Change this if needed
                        size_hint=(None, None),
                        size=(32, 32),
                        allow_stretch=True,
                        keep_ratio=True
                    )

                    # IP and Port label
                    label = Label(
                        text=f"{ip}:{port}",
                        color=(1, 1, 1, 1),
                        halign='left',
                        valign='middle',
                        size_hint=(1, None),
                        height=32
                    )
                    label.bind(size=lambda *x: label.setter('text_size')(label, label.size))

                    row.add_widget(icon)
                    row.add_widget(label)
                    inner_layout.add_widget(row)

                except Exception as e:
                    inner_layout.add_widget(Label(
                        text=f"Error: {str(e)}",
                        size_hint_y=None,
                        height=30,
                        color=(1, 0, 0, 1)
                    ))

        scroll_view.add_widget(inner_layout)
        layout.add_widget(scroll_view)

        close_button = RoundedButton(
            text="Close",
            background_color=(0.7, 0.2, 0.2, 1),
            size_hint=(1, None),
            height=40
        )
        close_button.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_button)

        popup = Popup(
            title=f"Routers for {person}",
            content=layout,
            size_hint=(0.9, 0.9)
        )
        popup.open()
    def update_people_list(self):
        self.scroll_layout.clear_widgets()
        chat_history = self.chats.get_chats()

        for person, details in chat_history.items():
            if person != "":
                status = "Online" if details['is_online'] else "Offline"
                button_color = (0.2, 0.9, 0.2, 0.5) if details['is_online'] else (0.5, 0.5, 0.5, 1)

                # Horizontal container for chat + routers buttons
                outer_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10, padding=10)

                # Chat button
                chat_button = RoundedButton(
                    text=f"{person} - {status}",
                    background_color=button_color
                )
                chat_button.bind(on_press=self.show_chat_history)

                # View Routers button
                view_routers_button = RoundedButton(
                    text="View Routers", 
                    background_color=(0.4, 0.4, 0.8, 0.8),
                    size_hint=(None, None), 
                    size=(120, 40)
                )
                view_routers_button.person_name = person
                view_routers_button.bind(on_press=self.show_router_info)

                outer_box.add_widget(chat_button)
                outer_box.add_widget(view_routers_button)

                self.scroll_layout.add_widget(outer_box)

            

    def open_add_person_popup(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.name_input = TextInput(hint_text="Enter name", font_size=14, size_hint_y=None, height=50, background_color=(0.3, 0.3, 0.3, 1), foreground_color=(1, 1, 1, 1))
        self.url_input = TextInput(hint_text="Enter URL", font_size=14, size_hint_y=None, height=50, background_color=(0.3, 0.3, 0.3, 1), foreground_color=(1, 1, 1, 1))
        save_button = RoundedButton(text="Save", background_color=(0.9, 0.3, 0.3, 0.7))
        save_button.bind(on_press=self.save_person)
        content.add_widget(self.name_input)
        content.add_widget(self.url_input)
        content.add_widget(save_button)
        self.popup = Popup(title="Add New Person", content=content, size_hint=(None, None), size=(300, 250))
        self.popup.open()
    def get_names(self):
        names=[]
        for i in self.client.url_name:
            names.append(self.client.url_name[i])
        return names
    def save_person(self, instance):
        acceptable_input=True
        name = self.name_input.text.strip()
        url = self.url_input.text.strip()
        if(name in self.get_names() or name=="try again"):
            self.name_input.text="try again"
            acceptable_input=False
        if(url in self.client.url_name or url==self.client.my_url or url=="try again"):
            self.url_input.text="try again"
            acceptable_input=False
        if(acceptable_input==False):
            return
        self.client.url_name[url]=name
        self.client.url_name[name]=url
        if name and url:
            self.chats.add_chat(name,url)
            self.client.start_new_request(url)
            self.update_people_list()
            self.popup.dismiss()
    def show_chat_history(self, instance):
        person_name = instance.text.split(" - ")[0]  # Extract the name from the button text
        self.manager.current = "chat"
        self.manager.get_screen("chat").display_chat(person_name)
    def get_urls(self):
        urls=[]
        chats=ch.get_chats(self)
        for i in chats:
            urls.append(chats[i]["url"])
        return urls
    def view_notifications(self, instance):
        """ Display notifications for people who want to start a chat or new people """
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        

        
        # Create a scrollable container for the notifications
        scroll_view = ScrollView(size_hint=(1, None), height=300)  # Adjust height as needed
        notifications_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        notifications_layout.bind(minimum_height=notifications_layout.setter('height'))
        
        # Collect notifications from chat_requests
        notifications = []

        # Check for chat requests in chat_requests dictionary
        chat_requests=sd.get_requests(self.client.my_url)
        
        urls=self.get_urls()
        for i in chat_requests:
            if(i not in urls and i != self.client.my_url):
                notifications.append(i)
        
        print(f"notifications:{notifications}")

        # Clear previous notifications
        notifications_layout.clear_widgets()
        label = Label(text=f"", font_size=14, size_hint_y=None, height=40)
        notifications_layout.add_widget(label)
        
        # Create labels for notifications (shortened text)
        for url in notifications:
            # Shortened notification text
            accept_button = RoundedButton(text=f"Accept {url.split('//')[-1]}", background_color=(0.3, 0.8, 0.3, 0.7))
            accept_button.bind(on_press=lambda instance, url=url: self.accept_chat_request(url))
            notifications_layout.add_widget(accept_button)

        scroll_view.add_widget(notifications_layout)
        layout.add_widget(scroll_view)

        close_button = RoundedButton(text="Close", background_color=(0.8, 0.2, 0.5, 0.8))
        close_button.bind(on_press=self.close_notifications)
        layout.add_widget(close_button)

        self.popup = Popup(title="Chat Notifications", content=layout, size_hint=(None, None), size=(300, 400))  # Adjust the size
        self.popup.open()

    def accept_chat_request(self, url):
        """ Accept a chat request and prompt for a name to create the chat """
        # Open a popup to ask for the name
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        name_input = TextInput(hint_text="Enter name", font_size=14, size_hint_y=None, height=50)

        save_button = RoundedButton(text="Save", background_color=(0.9, 0.3, 0.3, 0.7))
        content.add_widget(name_input)
        content.add_widget(save_button)
        self.popup_name = Popup(title="Enter Name", content=content, size_hint=(None, None), size=(300, 250))
        save_button.bind(on_press=lambda *args: self.create_chat_from_request(url, name_input.text))
        self.client.accept_request(url)
        self.create_chat_from_request( url, name_input.text)
        self.popup_name.open()
        
    def create_chat_from_request(self, url, name):
        self.client.url_name[url]=name
        self.client.url_name[name]=url
        """ Create chat from accepted request and delete notification """
        if name.strip():
            # Remove the chat request
            self.chats.add_chat(name,url)
            # Go to the chat screen for that person
            self.manager.current = "chat"
            self.manager.get_screen("chat").display_chat(name)

            # Refresh the Home Screen to reflect the updated status
            self.manager.get_screen("home").update_people_list()

            # Close the popup
            self.popup_name.dismiss()

    def close_notifications(self, instance):
        self.popup.dismiss()

class ChatScreen(Screen):
    def __init__(self,chats,client, **kwargs):
        self.client=client
        self.chats=chats
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Back button
        back_button = RoundedButton(text="Back to Home", background_color=(0.2, 0.5, 0.3, 0.5))
        back_button.bind(on_press=self.go_back_home)
        layout.add_widget(back_button)

        # Chat display
        self.chat_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        scroll_view = ScrollView()
        scroll_view.add_widget(self.chat_layout)
        layout.add_widget(scroll_view)

        # New Input Box layout
        input_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)

        # Simplified text input
        self.new_message_input = TextInput(
    multiline=False,  # IMPORTANT
    hint_text="Type a message...",
    size_hint_x=0.8,
    size_hint_y=None,
    height=40
)

        # Send button (increased prominence)
        send_button = RoundedButton(text="Send", background_color=(0.8, 0.1, 0.2, 0.7), size_hint_x=0.2)
        send_button.bind(on_press=self.send_message)
        self.new_message_input.bind(on_text_validate=self.send_message)


        input_layout.add_widget(self.new_message_input)
        input_layout.add_widget(send_button)
        
        layout.add_widget(input_layout)
        self.add_widget(layout)
        
        Clock.schedule_interval(lambda dt: self.reload_chat(), 0.1)
    def reload_chat(self):
        try:
            if(self.manager and not self.manager.current == "home"):
                self.display_chat(self.person_name)
        except:
            pass
    def display_chat(self, person_name):
        self.person_name = person_name
        self.chat_layout.clear_widgets()
        chat_history=self.chats.get_chats()
        for message in chat_history.get(person_name, {}).get("messages", []):
            
            sender = message["sender"]
            text = message["text"]
            label=""
            if(sender=="me"):
                label = Label(text=f"{sender}: {text}", font_size=14, size_hint_y=None, height=44, color=(0.2, 0.8, 0.2, 1) if sender != "Me" else (0, 0.6, 1, 1))
            else:
                label = Label(text=f"{sender}: {text}", font_size=14, size_hint_y=None, height=44, color=(0.8, 0.8, 0.2, 1) if sender != "Me" else (0, 0.6, 1, 1))
            self.chat_layout.add_widget(label)
        self.chats.save_chats(chat_history)
    def write_in_chat(self,new_message,src_url,dst_url):
        try:
            chat_history=self.chats.get_chats()
            name=""
            if(src_url in self.client.url_name):
                name=self.client.url_name[src_url]
            else:
                name="me"
            
            
            if(name=="me"):
                
                self.client.send_message_to_other([new_message,chat_history[self.client.url_name[dst_url]]["messages"][-1]["id"]],dst_url)
            else:
                self.chats.add_message(self.person_name,name,new_message)
            self.new_message_input.text = ""
        except:
            pass
    def send_message(self, instance=None):
        new_message = self.new_message_input.text.strip()
        if not new_message:
            return

        url = self.chats.get_chats()[self.person_name]["url"]

        if url in self.client.url_comm_id and self.client.url_comm_id[url] in self.client.up_connection:
            self.write_in_chat(new_message, self.client.my_url, url)
        elif url in  self.client.url_comm_id and self.client.url_comm_id[url] in self.client.up_connection:
            self.client.up_connection[self.client.url_comm_id[url]] = False
        self.chats.add_message(self.person_name,"me",new_message)
        self.new_message_input.text = ""

            
        
    def go_back_home(self, instance):
        self.manager.current = "home"

class ChatApp(App):
    def __init__(self, **kwargs):
        self.chats=ch()
        self.client=client(self)
        t=threading.Thread(target=self.check_up,args=())
        t.start()
        super().__init__(**kwargs)
    def check_up(self):
        
        self.client.main()
        while(True):
            try:
                home_screen = self.root.get_screen("home")
            
            # Ensure UI updates happen on the main thread
                Clock.schedule_once(lambda dt: home_screen.update_people_list(), 0)
            except Exception as e:
                print(f"Error in check_up: {e}")
            time.sleep(0.1)

    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(HomeScreen(name="home",chats=self.chats,client=self.client))
        sm.add_widget(RouterSettingsScreen(name="router_settings", client=self.client))

        self.chat_screen=ChatScreen(name="chat",chats=self.chats,client=self.client)
        sm.add_widget(self.chat_screen)
        return sm

class main:
    def __init__(self):
        self.chats=ch()
        app=ChatApp()
        
        self.run(app)
    def run(self,app):
        app.run()
    

if __name__ == "__main__":
    main()
