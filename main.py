import tkinter
import os


index_to_month = {
        1: "Janvier",
        2: "Février",
        3: "Mars",
        4: "Avril",
        5: "Mai",
        6: "Juin",
        7: "Juillet",
        8: "Août",
        9: "Septembre",
        10: "Octobre",
        11: "Novembre",
        12: "Décembre"
    }
month_to_index = {
        "Janvier": 1,
        "Février": 2,
        "Mars": 3,
        "Avril": 4,
        "Mai": 5,
        "Juin": 6,
        "Juillet": 7,
        "Août": 8,
        "Septembre": 9,
        "Octobre": 10,
        "Novembre": 11,
        "Décembre": 12
    }


class ThisFileIsNotAnArchive(Exception):
    def __init__(self):
        super().__init__("This file is not a WhatsApp archive, if there is one but our program does not detect it, "
                         "check that the first lines of the archive are conversations and not simple text. Please "
                         "forgive us if our program is wrong.")
    

def cut_entire_file_to_message_list(entire_data):
    messages = []
    messages_dict = []
    message = ''

    if entire_data[11] == 'à' and entire_data[19] == '-':
        for character_index, character in enumerate(entire_data):
            try:
                int(character)
            except ValueError:
                pass
            else:
                if (entire_data[character_index+2] == '/' and entire_data[character_index+5] == '/' and
                        entire_data[character_index+11] == 'à' and entire_data[character_index+19] == '-'
                        and message != ''):
                    if message.split(' ')[4][-1] == ':':

                        messages_dict.append({'date': message[:10],
                                              'time': message[13:18],
                                              'sender': message.split(' ')[4][:-1],
                                              'content': ' '.join(message.split(' ')[5:])
                                              })
                    elif message.split(' ')[5][-1] == ':':
                        messages_dict.append({'date': message[:10],
                                              'time': message[13:18],
                                              'sender': ' '.join(message.split(' ')[4:6])[:-1],
                                              'content': ' '.join(message.split(' ')[6:])
                                              })
                    else:
                        pass

                    messages.append(message)
                    message = ''
            message += character

    elif entire_data[0] == '[' and entire_data[20] == ']':
        for character_index, character in enumerate(entire_data):
            if character == '[' and entire_data[character_index + 20] == ']' and message != '':
                if message.split(' ')[2][-1] == ':':

                    messages_dict.append({'date': message[1:11],
                                          'time': message[12:20],
                                          'sender': message.split(' ')[2][:-1],
                                          'content': " ".join(message.split(' ')[3:])
                                          })
                elif message.split(' ')[3][-1] == ':':

                    messages_dict.append({'date': message[1:11],
                                          'time': message[12:20],
                                          'sender': ' '.join(message.split(' ')[2:4])[:-1],
                                          'content': " ".join(message.split(' ')[4:])
                                          })

                messages.append(message)
                message = ''
            message += character
    else:
        raise ThisFileIsNotAnArchive
    return messages_dict


class DataTools:
    def __init__(self, root=r'./data'):
        self.data_path = root
        self.datas = {}
        self.users = []
        self.load_data()

    def load_data(self):
        for file_name in os.listdir(self.data_path):
            if file_name[-4:] == '.txt':
                with (open(f'{self.data_path}/{file_name}') as file):
                    file_content = file.read()
                    try:
                        conv = cut_entire_file_to_message_list(file_content)
                    except ThisFileIsNotAnArchive:
                        pass
                    else:
                        self.datas[' - '.join(self.get_users(conv))] = conv

                    file.close()

    def get_users(self, data_dict):
        users = []
        for obj in data_dict:
            try:
                if not obj['sender'] in users:
                    users.append(obj['sender'])
            except KeyError:
                pass
        self.users.append(' - '.join(users))

        return users


class WhatsAppConv(tkinter.Tk):
    max_length_character = 63
    text_size = 10
    font = 'Comics Sans MS'

    width = 440
    height = 800

    user_names = ['Nikitas', 'Nikitas Giakkoupis']

    def __init__(self):
        super().__init__()
        self.current_index_conv = 0
        self.current_month = 10
        self.current_year = 2021
        self.current_user_index = 0
        self.current_mode = 'datetime'

        self.tools = DataTools()

        self.geometry(f'{self.height}x{self.height}')
        self.maxsize(self.width, self.height)
        self.minsize(self.width, self.height)

        self.tools_bar = ToolsBar(self)
        self.tools_bar.pack(side=tkinter.TOP, pady=0, padx=0)
        self.chat = ChatScreen(self)
        self.load_message()
        self.chat.pack(fill=tkinter.BOTH)
        self.bind('<Control-r>', self.goes_to_the_top_of_the_conv)

        #  self.tools_bar = ToolsBar(self)
        #  self.tools_bar.pack()
        #  self.chat_view = ChatScreen(self)
        #  self.chat_view.pack()

    def goes_to_the_top_of_the_conv(self, event):
        self.current_month = int((self.tools.datas[self.tools.users[self.current_user_index]][0]['date'].split('/'))[1])
        self.current_year = int((self.tools.datas[self.tools.users[self.current_user_index]][0]['date'].split('/'))[2])
        self.tools_bar.update_button_text()
        self.load_message()

    def load_message(self):

        self.chat.interior.destroy()
        self.chat.interior = tkinter.Frame(self, width=500)
        self.chat.interior_id = self.chat.create_window(0, 0, window=self.chat.interior, anchor=tkinter.NW)

        for item in self.tools.datas[self.tools.users[self.current_user_index]]:

            if self.current_month < 10:
                temporary_month_variable = f'0{self.current_month}'
            else:
                temporary_month_variable = self.current_month

            if item['date'][3:] == f'{temporary_month_variable}/{self.current_year}':
                message = Message(self, self.chat.interior, item)
                if message.sender in self.user_names:
                    message.pack(anchor='ne')
                else:
                    message.pack(anchor='nw')

    def run(self):
        self.mainloop()


class Message(tkinter.LabelFrame):
    def __init__(self, parent: WhatsAppConv, frame, message_information):
        self.parent = parent
        self.sender = message_information['sender']
        self.color = 'green' if self.sender in self.parent.user_names else 'blue'
        justify = 'right' if self.sender in self.parent.user_names else 'left'

        super().__init__(frame, text=f'{self.sender}', fg=self.color, font=(self.parent.font, self.parent.text_size - 3))

        self.content = message_information['content']
        self.content = self.content
        new_message = ''
        if len(self.content) > self.parent.max_length_character:
            new_message = ''
            index = 0
            for character in self.content:
                new_message += character
                index += 1
                if index == self.parent.max_length_character:
                    new_message += '\n'
                    index = 0
        self.label = tkinter.Label(self, text=new_message if new_message != '' else self.content[:-1],
                                   font=(self.parent.font, self.parent.text_size), justify=justify)
        self.label.pack()


"""class Message(tkinter.LabelFrame):
    def __init__(self, parent: tkinter.Frame, message_information_dict):
        self.parent = parent

        self.sender = message_information_dict['sender']
        self.date = self.sender = message_information_dict['date']
        self.time = self.sender = message_information_dict['time']
        self.content = message_information_dict['content']

        self.color = 'green'
        
        super().__init__(parent, text=self.sender, bg=self.color)"""


class ToolsBar(tkinter.Frame):
    height = 30

    def __init__(self, parent: WhatsAppConv):
        self.parent = parent
        super().__init__(self.parent, borderwidth=2, bg='blue', relief=tkinter.GROOVE)

        self.text_variable = tkinter.StringVar()

        self.button1 = tkinter.Button(self, bg='yellow', text='<', padx=10, pady=0,
                                      command=lambda: self.change_value(-1))
        self.button1.pack(side=tkinter.LEFT)

        self.button2 = tkinter.Button(self, bg='yellow', text='>', padx=10, pady=0,
                                      command=lambda: self.change_value(1))
        self.button2.pack(side=tkinter.RIGHT)

        self.label = tkinter.Button(self, textvariable=self.text_variable, command=self.switch_mode, padx=10, pady=0)
        self.label.pack(padx=50, expand=tkinter.YES)

        self.update_button_text()

    def update_button_text(self):
        if self.parent.current_mode == 'users':
            self.text_variable.set(self.parent.tools.users[self.parent.current_user_index])
            self.parent.title(f'{index_to_month[self.parent.current_month]} '
                              f'{self.parent.current_year}')
        elif self.parent.current_mode == 'datetime':
            self.text_variable.set(f'{index_to_month[self.parent.current_month]} '
                                   f'{self.parent.current_year}')
            self.parent.title(self.parent.tools.users[self.parent.current_user_index])

    def switch_mode(self):
        if self.parent.current_mode == 'datetime':
            self.parent.current_mode = 'users'
        else:
            self.parent.current_mode = 'datetime'
        self.update_button_text()

    def change_value(self, direction: int):
        if self.parent.current_mode == 'datetime':
            if direction >= 1:
                if self.parent.current_month + direction >= 13:
                    self.parent.current_month = (self.parent.current_month + direction) % 12
                    self.parent.current_year += 1
                else:
                    self.parent.current_month += direction
            elif direction <= -1:
                if self.parent.current_month + direction <= 0:
                    self.parent.current_month = 12 - (self.parent.current_month + direction)
                    self.parent.current_year -= 1
                else:
                    self.parent.current_month += direction

        elif self.parent.current_mode == 'users':
            if direction >= 1:
                self.parent.current_user_index = (self.parent.current_user_index + 1) % (len(self.parent.tools.users))
            elif direction <= -1:

                self.parent.current_user_index -= 1
                self.parent.current_user_index = (len(self.parent.tools.users)-1) \
                    if self.parent.current_user_index < 0 else self.parent.current_user_index

        self.update_button_text()
        self.parent.load_message()


class ChatScreen(tkinter.Canvas):
    def __init__(self, parent: WhatsAppConv):
        super().__init__(parent, bg='red', height=800)
        self.parent = parent

        self.interior = tkinter.Frame(self)
        self.interior_id = self.create_window(0, 0, window=self.interior, anchor=tkinter.NW)
        self.scrollbar = tkinter.Scrollbar(self.parent, orient=tkinter.VERTICAL, command=self.yview)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.configure(yscrollcommand=self.scrollbar.set)
        self.bind("<Configure>", self.resize_canvas)
        self.interior.pack(fill=tkinter.BOTH)

    def configure_interior(self, event):
        self.configure(scrollregion=self.bbox("all"))

    def resize_canvas(self, event):
        self.config(scrollregion=self.bbox("all"), width=450, height=800)




if __name__ == '__main__':
    WhatsAppConv().run()
