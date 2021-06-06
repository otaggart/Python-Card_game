from random import randint
# import time
import sqlite3
cards = 'black 1,black 2,black 3,black 4,black 5,black 6,black 7,black 8,black 9,black 10, ' \
        'red 1,red 2,red 3,red 4,red 5,red 6,red 7,red 8,red 9,red 10,yellow 1,' \
        'yellow 2,yellow 3,yellow 4,yellow 5,yellow 6,yellow 7,yellow 8,yellow 9,yellow 10'.split(',')

colours = {('black', 'red'): 'Player 2 wins', ('red', 'black'): 'Player 1 wins', ('red', 'yellow'):
           'Player 2 wins', ('yellow', 'red'): 'Player 1 wins', ('black', 'yellow'): 'Player 1 wins',
           ('yellow', 'black'): 'Player 2 wins'}

player_1_cards = []
player_2_cards = []


def pick_card(pack):
    n = len(pack) - 1
    x = randint(0, n)
    y = randint(0, n - 1)
    player_1_card = pack[x]
    cards.remove(player_1_card)
    player_2_card = pack[y]
    cards.remove(player_2_card)
    return player_1_card, player_2_card


def play_round():
    card_1, card_2 = pick_card(cards)
    card_1, card_2 = card_1.split(), card_2.split()
    card_1_colour, card_2_colour = card_1[0], card_2[0]
    card_1_number, card_2_number = card_1[1], card_2[1]
    if card_1_colour != card_2_colour:
        winner = colours[(card_1_colour, card_2_colour)]
    elif card_1_number > card_2_number:
        winner = 'Player 1 wins'
    else:
        winner = 'Player 2 wins'
    card_1, card_2 = ' '.join(card_1), ' '.join(card_2)
    print(card_1, card_2)
    print(winner)
    if winner == 'Player 1 wins':
        player_1_cards.append(card_1)
        player_1_cards.append(card_2)
    elif winner == 'Player 2 wins':
        player_2_cards.append(card_1)
        player_2_cards.append(card_2)
    return winner


def authenticate():
    with sqlite3.connect("Login.db") as db:
        cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user(
    userID INTEGER PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL);
    ''')
    db.commit()

    def login():
        while True:
            login_username = input("Please enter your username:\t")
            password = input("Please enter your password:\t")
            find_user = "SELECT * FROM user WHERE username = ? AND password = ?"
            cursor.execute(find_user, [login_username, password])
            results = cursor.fetchall()

            if results:
                for i in results:
                    print("Welcome " + i[2])
                break

            else:
                print("Username and password not recognised")
                again = input("Do you want to try again?(y/n)")
                if again.lower() == "n":
                    print("Goodbye")
                    break
        return login_username

    def new_user():
        found = 0
        while found == 0:
            new_username = input('Please enter a username:\t')
            find_user = "SELECT * FROM user WHERE username = ?"
            cursor.execute(find_user, [new_username])

            if cursor.fetchall():
                print('Username taken, please try again')

            else:
                found = 1

        password = input('Please enter your password:\t')
        password2 = input('Please reenter your password:\t')
        while password != password2:
            print('Your passwords don\'t match, please try again')
            password = input('Please enter your password:\t')
            password2 = input('Please reenter your password:\t')

        insert_data = '''INSERT INTO user (username,password)
        VALUES(?,?)'''
        cursor.execute(insert_data, [new_username, password])
        db.commit()
        return new_username

    def menu():
        while True:
            print('Welcome to my card game')
            login_screen = ('''
            1 - Create new user
            2 - Login to system
            ''')

            user_choice = input(login_screen)
            if user_choice == '1':
                old_player_name = new_user()
                return old_player_name
            elif user_choice == '2':
                new_player_name = login()
                return new_player_name
            else:
                print('Input not valid')

    player_name = menu()
    return player_name


def play_game():
    p_1_won = True
    player_1_account = authenticate()
    print('Player 1 successfully logged in')
    player_2_account = authenticate()
    print('Player 2 successfully logged in')
    while True:
        play_round()
        # time.sleep(3)
        if len(cards) < 2:
            if len(player_1_cards) > len(player_2_cards):
                print('Player 1 won the game! Congratulations!')
                break
            else:
                print('Player 2 won the game! Congratulations!')
                p_1_won = False
                break
    return p_1_won, player_1_account, player_2_account


def leaderboard():
    with sqlite3.connect("Leaderboard.db") as db:
        cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leaderboard(
    userID INTEGER PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    score VARCHAR(20) NOT NULL);
    ''')
    db.commit()

    game_winner, player_1_name, player_2_name = play_game()
    if game_winner:
        insert_data = '''INSERT INTO Leaderboard (username,score)
                VALUES(?,?)'''
        cursor.execute(insert_data, [player_1_name, (len(player_1_cards))])
        db.commit()
    elif not game_winner:
        insert_data = '''INSERT INTO Leaderboard (username,score)
                VALUES(?,?)'''
        cursor.execute(insert_data, [player_2_name, (len(player_2_cards))])
        db.commit()

    if input('Thank you for playing! Would you like to see the Leaderboard?(y/n)\t') == 'y':
        cursor.execute('''SELECT * FROM Leaderboard ORDER BY score DESC;''')
        rows = cursor.fetchall()
        for row in rows:
            print(str(row))

    else:
        print('Ok!')

    if input('Would you like to play again?(y/n)\t') == 'y':
        leaderboard()
    else:
        print('Goodbye!')


leaderboard()
