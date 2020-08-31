from gsheets import Sheets
from oauth2client.service_account import ServiceAccountCredentials
import csv
from Venmo.venmo import Venmo

class Poker:
    
    def __init__(self):

        self.gameHistory = "Game_History.csv"
        self.playerStats = "Player_Stats.csv"
        self.playerInfo = "Player_Info.csv"
        self.games = []
        self.rank = []
        self.info = []
        self.outstanding = []
        self.totaloutstanding = []
        self.numGames = -1
        self.switch_map = {
            "1" : 'showLastGame',
            "2" : 'showPlayerStats',
            "3" : 'showOutstanding',
            "4" : 'showTotalOutstanding',
            "5" : 'requestOutstanding',
            "6" : 'payOutstanding',
            "7" : 'showRaw',
            "8" : 'updateData',
            "9" : 'updateIDs'
        }
        self.venmo = Venmo()

    def showRaw(self):
        with open('Game_History.csv', newline='') as File:
            csv_reader = csv.reader(File)
            for row in csv_reader:
                print(row)
            print("\n")

    def showLastGame(self):
        self.printGame(len(self.games))
        #print("Last Game: ", getLastGame())

    def showTotalOutstanding(self):
        print("Outstanding Payments")
        for player in self.totaloutstanding:
            if (player[1] == 0):
                continue
            print("{:<10}${:<10.2f}".format(player[0],player[1]))

    def showOutstanding(self):
        print("Outstanding Payments")
        for player in self.outstanding:
            if (player[1] == 0):
                continue
            print("{:<10}{:<10}{:<10.2f}".format(player[0],player[1],player[2]))
            
    def showPlayerStats(self):
        print("Player Ranking")
        for player in self.rank:
            print("{:<5}{:<10}${:<10.2f}".format(player[0],player[1],player[4]))

    def requestOutstanding(self):
        if(self.confirmOutstanding()):
            self.confirmRequests()

    def payOutstanding(self):
        # Before Payments go out the usernames and values must be confirmed
        if(self.confirmOutstanding()):
            self.confirmPayments()

    def confirmOutstanding(self):
        self.showOutstanding()
        response = input("Are the Following Outstanding Payments Up to Data(y/n): ")
        if (response == "y"):
            return True
        return False

    def confirmRequests(self):
        response = input("Are you sure you want to make these requests(y/n): ")
        if(response == "y"):
            print("\n\n")
            self.venmo.payPlayers(self.outstanding)

    def confirmPayments(self):
        response = input("Are you sure you want to make these requests")
        if(response == "y"):
            print("\n\n")
            self.venmo.requestPlayers(self.outstanding)

    def printGame(self,gameNum):
        print("Game: ", gameNum)
        game = self.games[gameNum - 1]
        print("Name      Hands Won      In        Out       Gain/Loss      Paid")
        for row in game:
            if(len(row) == 3):
                print("{:<10s}{:<15.2f}{:<10.2f}".format(row[0],row[1],row[2]))
            else:
                print("{:<10s}{:<15}{:<10.2f}{:<10.2f}{:<15.2f}{:<10s}".format(row[0],row[1],row[2],row[3],row[4],row[5]))

    def badInput(self):
        print("Bad Input")
    
    def updateData(self):
        print("Updating Data\n")
        self.rank = []
        self.games = []
        self.outstanding = []
        self.totaloutstanding = []
        self.info = []
        self.updateCSV()
        print("Update Complete\n")

    def updateIDs(self):
        for player in self.info:
            self.info


    # Update CSV and load Data
    def updateCSV(self):
        # Sheets object
        self.sheets = Sheets.from_files('client_secrets.json', 'storage.json')
        # GoogleSheets URL
        self.url = 'https://docs.google.com/spreadsheets/d/1qz_1Fy-2Sda76fe8bIsD4Ci0aO25cmUTMJVCHAqO7NI/edit#gid=1542267929'
        # Get Poker History Sheets
        s = self.sheets.get(self.url)
        # Update CSV files
        s.sheets[0].to_csv('Game_History.csv',encoding='utf-8',dialect='excel')
        s.sheets[1].to_csv('Player_Stats.csv',encoding='utf-8',dialect='excel')
        s.sheets[2].to_csv('Player_Info.csv',encoding='utf-8',dialect='excel')

        # Load Game History
        with open(self.gameHistory,encoding='utf-8') as sheet:
            reader = csv.reader(sheet, delimiter=',')
            # Parse Games into games structure
            row_index = 0
            gameNum = 0
            date = 'date'
            game = []
            for row in reader:
                if row_index == 0:
                    row_index += 1
                    continue
                if row:
                    if(row[0]):
                        date = row[0]
                    if (row[2] == 'Total'):
                        columns = [row[2]] + [round(float(num), 2) for num in row[4:6]]
                    else:
                        if(row[7] == 'n'):
                            self.outstanding.append([date, row[2], round(float(row[6]),2)])
                        columns = [row[2]] + [row[3]] + [round(float(num), 2) for num in row[4:7]] + [row[7]]
                    game.append(columns)
                else:
                    self.games.append(game)
                    game = []
                    gameNum += 1
                row_index += 1
            # Last Game needs to be added
            self.games.append(game)
            self.numGames = gameNum
            print(self.outstanding)

        # Load Player Stats
        with open(self.playerStats,encoding='utf-8') as sheet:
            reader = csv.reader(sheet, delimiter=',')
            row_index = 0
            for row in reader:
                if row_index == 0:
                    row_index += 1
                    continue
                columns = [row[0], row[1]] + [round(float(num), 2) for num in row[2:7]]
                self.rank.append(columns)
                self.totaloutstanding.append([row[1], round(float(row[5]),2)])

        # Only if a new player with venmo joins
        # # Load Player Venmo
        # with open(self.playerInfo,encoding='utf-8') as sheet:
        #     reader = csv.reader(sheet, delimiter=',')
        #     row_index = 0
        #     for row in reader:
        #         if row_index > 2:
        #             row_index += 1
        #             continue
        #         if (len(row) < 2):
        #             row_index += 1
        #             continue
        #         userid = self.venmo.getUserID(row[1])
        #         columns = row[0:2] + [userid]
        #         self.info.append(columns)

        # for player in self.info:
        #     print(player[0], ":   ", player[2])
            
    # Switch Function
    def switch(self, task):
        default = "badInput"
        #print(self.switch_map[task])
        return getattr(self, self.switch_map.get(str(task),default),lambda: default)()

def main():
    print("Poker History\n\n")
    print("Updating Poker History and Player Stats\n")
    P = Poker()
    P.updateCSV()
    print("Data Updated\n")
    try:
        while (1):
            print("1) View Last Game")
            print("2) View Player Stats")
            print("3) Check OutStanding Payouts")
            print("4) Check Total Outstanding Values")
            print("5) Request Losses")
            print("6) Send Winnings")
            print("7) Show Raw Data")
            print("8) Update Data")

            task = input("What would you like to do: ")

            # Run Switch Statement on user input
            print("\n\n")
            P.switch(task)
            print("\n")

    except KeyboardInterrupt:
        print("\n\nPeace Dog...Until Next Time")

if __name__ == "__main__":
    main()
