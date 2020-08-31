from venmo_api import Client
import csv
import json

class Venmo:

    def __init__(self):
        json_file = open("venmo_secrets.json")
        variables = json.load(json_file)
        json_file.close()
        print(variables)
        access_token = variables["access_token"]
        self.venmo = Client(access_token=access_token)
        self.friendsList = "friendsList.csv"

        self.user_ids = {
            "Anton" : '2031501856210944616',
            "Barry" : '1815582936662016024',
            "Kole" : '1911944990687232235',
            "Baz" : '1812002871705600540',
            "Jub" : '1791601047240704241',
            "Goose" : '1797187583344640739',
            "Flynn" : '1739210281189376997',
            "Wukie" : '1524990465802240001'
        }
        self.switch_map = {
            "1" : 'makePayment',
            "2" : 'makeRequest',
            "3" : 'checkFriendsList'
        }
    # Find New Players
    def getUserID(self,username):
        users = self.venmo.user.search_for_users(username)
        # Unable to search yourself on Venmo
        if(username == "Owen-Beringer"):
            return -1
        user_id = users[0].id
        print("Username: ", username, "  User ID: ", user_id)
        correctUser = input("Is this the correct User?(y/n): ")
        if (correctUser == 'y'):
            friend = input("Would you like to add this user to your friends list?(y/n): ")
            if (friend == 'y'):
                nickName = input("Nickname: ")
                self.addFriend(nickName,user_id)
            return user_id
        else:
            return False

    def addFriend(self,nickName,id):
        with open(self.friendsList, mode='w') as friends:
            writer = csv.writer(friends,delimiter=',')
            writer.writerow([nickName, user_id])
            print("Added ",Nickname," to Friends List\n")

    def loadFriends(self):
        with open(self.friendsList,encoding='utf-8') as sheet:
            reader = csv.reader(sheet, delimiter=',')
            row_index = 0
            for row in reader:
                if(row):
                    self.user_ids.update({row[0] : row[1]})

    def checkFriendsList(self):
        for friend in self.user_ids:
            print(friend, ": ", self.user_ids[friend])

    def makePayment(self,userid,amount,description):
        print("Payed: " + userid + " " + str(amount) + " with description: " + description)
        #self.venmo.payment.send_money(amount,description,userid)

    def makeRequest(self,userid,amount,description):
        print("Requested: " + userid + " " + str(-1 * amount) + " with description: " + description)
        #self.venmo.payment.request_money(amount,description,userid)

    def payPlayers(self, payments):
        #self.venmo.payment.send_money(amount,description,username)
        for payment in payments:
            if(payment[1] not in self.user_ids):
                print("\nPayment Error: ", payment[1], " has no venmo id\n")
                continue
            if(payment[2] < 0):
                continue
            self.makePayment(self.user_ids[payment[1]],payment[2],payment[0])

    def requestPlayers(self, payments):
        for payment in payments:
            if(payment[1] not in self.user_ids):
                print("\nPayment Error: ", payment[1], " has no venmo id\n")
                continue
            if(payment[2] > 0):
                continue
            self.makeRequest(self.user_ids[payment[1]],payment[2],payment[0])

    # Deconstructor revokes Token
    def __del__(self):
        pass
        #self.venmo.log_out("Owen-Beringer")

    # Switch Function
    def switch(self, task, userid, quantity, description):
        default = "badInput"
        #print(self.switch_map[task])
        return getattr(self, self.switch_map.get(str(task),default),lambda: default)(userid, quantity, description)

def main():
    print("Venmo\n\n")

    V = Venmo()
    
    print("Data Updated\n")
    try:
        print("Loading Frinds List...")
        V.loadFriends()
        while (1):
            print("\n\n1) Make Payment")
            print("2) Make Request")
            print("3) Check Friends List")
            task = input("What would you like to do: ")
            print("\n")
            if(task == '3'):
                V.checkFriendsList()
            else:
                username = input("Name or Username: ")

                if (username in V.user_ids):
                    print("Found ", username, " in friends list.")
                    userid = V.user_ids[username]
                else:
                    print("Searching for Username")
                    userid = V.getUserID(username)
                    if(userid == False):
                        continue
                    
                quantity = input("How much?: ")
                description = input("Description: ")

                # Run Switch Statement on user input
                print("\n\n")
                V.switch(task,userid, quantity, description)
                print("\n")

    except KeyboardInterrupt:
        print("\n\nPeace Dog...Until Next Time")

if __name__ == "__main__":
    main()
