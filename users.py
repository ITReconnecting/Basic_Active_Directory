import ast
import os
from numpy import mod
import configparser
from functools import lru_cache
import csv
from dataclasses import dataclass, field

@dataclass
class User:
    username: str
    password: str
    groups: list[str] = field(default_factory=list)
    enabled: bool = True

BLANK = object()
DELETED = object()

class Users():

    __slots__ = "length", "values", "delete_counter"

    def __init__(self):
        
        config = configparser.ConfigParser()
        config.read("./Config/users.ini")

        capacity = int(config.get("General", "capacity"))
        
        self.length = capacity
        self.values = capacity * [BLANK]
        self.delete_counter = 0

        self.load_file()

    def load_file(self):
        previous = ""
        with open("accounts.csv", mode="r") as file:
            csv_reader = csv.reader(file, delimiter=",")
            for row in csv_reader:
                if previous == row[0]:
                    pass
                else:
                    previous = row[0]
                    user = User(row[0], row[1], row[2], row[3])
                    hash = self.get_hash_values(row[0])
                    self.values[hash] = [row[0], user]

    def __len__(self):
        return self.length

    @lru_cache(maxsize=25)
    def get_hash_values(self, data):
        
        if data == "":
            return "Cannot insert nothing!"
    
        elif type(data) == str:
            index = 0
            hash_value = 0
            letters = [x for x in data]
            
            while index != len(letters):
                value = ord(letters[index])
                hash_value = hash_value + value
                index = index + 1
                    
            index = mod(hash_value, (self.length))
                
        elif type(data) == int:
            index = mod(data, (self.len()))
    
        elif type(data) == float:
            index = mod(round(data), (self.len()))
    
        else:
            index = 0
            hash_value = 0
            valuetoHash = data['Value to Hash']        
            letters = [x for x in valuetoHash]
                
            while index != len(letters):
                value = ord(letters[index])
                hash_value = hash_value + value
                index = index + 1
    
            index = mod(hash_value, (self.len()))
    
        return index

    def data_verification(self, data):

        if data == "":
            return False

        if type(data) == dict:
            if data['Value to Hash'] == "":
                return False

        return True

    def insert(self, data):

        to_hash_data = data[0]

        verify = self.data_verification(to_hash_data)
        dictionary = {
            "Test": "Test"
        }

        if verify == True:
            index = 0
            
            index = self.get_hash_values(to_hash_data)
    
            self.values[index] = data
            self.backup(data)
            return 200
        else:
            return 101
        
    def search(self, data):

        self.delete_counter = 0
        index = 0
        dictionary = {
            "Test": "Test"
        }

        verify = self.data_verification(data)

        if verify == True:
            
            index = self.get_hash_values(data)
                
            while self.values[index] != BLANK:
                temp = self.values[index]
    
                if isinstance(temp, type(dictionary)) == True:
                    temp_dict = temp
                    if temp_dict['Value to Hash'] == data:
                        return temp
                        
                elif isinstance(temp, type(dictionary)) == False:
                    pass
    
                if temp[0] == data:
                    return temp
    
                elif temp == DELETED:
                    index += 1
                    self.delete_counter = self.delete_counter + 1
    
                elif temp == dict:
                    index += 1

                else:
                    index += 1
    
            return 102

        else:
            return 101

    def delete(self, data):

        verify = self.data_verification(data)

        if verify == True:
            
            index = self.get_hash_values(data)
    
            while self.values[index] != BLANK:

                temp = self.values[index]
                
                if temp[0] == data:
                    csv_remove = temp[1]
                    self.values[index] = DELETED
                    self.remove_backup(csv_remove)
                    return 200
                
                else:
                    index = index + 1
    
            return 102

        else:
            return 101

    def update(self, username, data):
        index = 0

        verify = self.data_verification(data)

        if verify == True:
            
            index = self.get_hash_values(username)
                
            while self.values[index] != BLANK:
                temp = self.values[index]
    
                if temp == data:
                    position = index
    
                elif temp == DELETED:
                    index += 1
                    self.delete_counter = self.delete_counter + 1
    
                elif temp == dict:
                    index += 1

                else:
                    index += 1
            
            self.values[position] = data
            return 200
        
        return 101

    def backup(self, data):
        field_names = ["Username", "Password", "Groups", "Enabled"]
        with open("accounts.csv", mode="a", newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=field_names)
            username = data[1].username
            password = data[1].password
            groups = data[1].groups
            enabled = data[1].enabled
            data_to_insert = {
                "Username": username,
                "Password": password,
                "Groups": groups,
                "Enabled": enabled
            }
            csv_writer.writerow(data_to_insert)

    def remove_backup(self, name):
        field_names = ["Username", "Password", "Groups", "Enabled"]
        previous = ""
        save_fields = []
        with open("accounts.csv", mode="r") as file:
            csv_reader = csv.reader(file, delimiter=",")
            for row in csv_reader:
                if previous == row[0]:
                    pass
                else:
                    previous = row[0]
                    if row[0] == name.username:
                        print(row[0])
                    elif row[0] != name.username:
                        save_fields.append(row)

        with open("accounts.csv", mode="w") as file:
            file.write("")
            for data in save_fields:
                username = data[0]
                password = data[1]
                groups = data[2]
                enabled = data[3]
                backup = [BLANK, User(username, password, groups, enabled)]
                self.backup(backup)