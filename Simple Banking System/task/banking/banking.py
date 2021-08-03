# Write your code here
import random
import sqlite3

# customer_data replaced with DB
# customer_data = dict()

# create DB, name card
conn = sqlite3.connect('card.s3db')

# start the cursor
cur = conn.cursor()

# create table, only if it doesn't exist
# id is generated automatically
# https://database.guide/set-a-default-value-for-a-column-in-sqlite-default-constraint/
cur.execute('''CREATE TABLE IF NOT EXISTS card(
id INTEGER PRIMARY KEY,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT 0);
''')

conn.commit()

def menu_prompt():
    menu = ("1. Create an account\n"
            "2. Log into account\n"
            "0. Exit\n")
    print(menu)
    return int(input())

def logged_in_menu():
    menu = ("1. Balance\n"
            "2. Add income\n"
            "3. Do transfer\n"
            "4. Close account\n"
            "5. Log out\n"
            "0. Exit\n")
    print(menu)
    return int(input())

def luhn_check(target_card):
    num_list = list(str(target_card))
    num_list = [int(num) for num in num_list]
    i = 0
    number_sum = 0
    while i <= 14:
        if i % 2 == 0:
            num_list[i] = num_list[i] *2
        if num_list[i] > 9:
            num_list[i] = num_list[i] - 9
        number_sum += num_list[i]
        i += 1
    if (number_sum + num_list[-1]) % 10 != 0:
        return True

def unknown_card_check(target_card):
    cur.execute("SELECT number FROM card;")
    numbers = cur.fetchall()
    numbers = [tuple[0] for tuple in numbers]
    if target_card not in numbers:
        return True
    else:
        return False

def logged_in(acc_num):
    while True:
        nxt_step = logged_in_menu()
        if nxt_step == 1:
            # retrieve balance
            balance = cur.execute(f"SELECT balance FROM card WHERE number = {acc_num}")
            print(f"Balance: {str(balance)}")
        elif nxt_step == 2:
            inc = int(input("Enter income: \n"))
            cur.execute(f"SELECT balance FROM card WHERE number = {acc_num}")
            current_balance = cur.fetchall()[0][0]
            #print(current_balance)
            new_balance = inc + int(current_balance)
            #print(new_balance)
            cur.execute(f"UPDATE card SET balance = {new_balance} WHERE number = {acc_num}")
            conn.commit()

        elif nxt_step == 3:
            fail = 0
            target_card = input("Transfer\nEnter card number:\n")
            if luhn_check(target_card):
                fail = 1
                print("Probably you made a mistake in the card number. Please try again!\n")
            # check they're not transferring to the same account
            elif target_card == acc_num:
                fail = 1
                print("You can't transfer money to the same account!\n")
            elif unknown_card_check(target_card):
                fail = 1
                print("Such a card does not exist.\n")
            elif fail == 0:
                transfer_amount = int(input("Enter how much money you want to transfer:\n"))
                cur.execute(f"SELECT balance FROM card WHERE number = {acc_num}")
                current_balance = cur.fetchall()[0][0]
                print(f"current balance: {current_balance}")
                if current_balance < transfer_amount:
                    fail = 1
                    print("Not enough money!\n")
            # amount in account



            if fail == 0:
                #print(f"transfer amound: {transfer_amount}")
                cur.execute(f"SELECT balance FROM card WHERE number = {target_card}")
                target_balance = cur.fetchall()[0][0]
                new_target_balance = target_balance + transfer_amount
                cur.execute(f"UPDATE card SET balance = {new_target_balance} WHERE number = {target_card}")
                # debit from debit acount
                conn.commit()
                new_balance = current_balance - transfer_amount
                cur.execute(f"UPDATE card SET balance = {new_balance} WHERE number = {acc_num}")
                conn.commit()
                print("Success!\n")


        elif nxt_step == 4:
            # close account
            # drop entry
            cur.execute(f"DELETE FROM card WHERE number={acc_num}")
            conn.commit()

            pass
        elif nxt_step == 5:
            # log out
            pass
        else:
            # exit
            return 0


def luhn_algorithm(input_num):
    account_num_list = list(input_num)
    account_num_list = [int(item) for item in account_num_list]
    i = 0
    while i < len(account_num_list):
    # double every number in odd position
        if i % 2 == 0:
            account_num_list[i] = account_num_list[i] * 2
    # subtract 9 from numbers greater than 9
        if account_num_list[i] > 9:
            account_num_list[i] = account_num_list[i] - 9
        i += 1
    # sum all numbers
    sum_of_digits = sum(account_num_list)
    # find number that makes a total divisible by 10
    if sum_of_digits % 10 == 0:
        return 0
    else:
        return_num = 1
        while True:
            if (sum_of_digits + return_num ) % 10 == 0:
                return return_num
            else:
                return_num += 1


def generate_customer_entry():
    account_num = "400000"
    while len(account_num) <= 14:
        account_num += str(random.randint(0,9))
    end_num = luhn_algorithm(account_num)
    account_num += str(end_num)

    pin = ""
    for i in range(4):
        pin += str(random.randint(1,9))
    return [account_num, pin]

def log_into_acc():
    acc_num = input("Enter your card number:\n")
    cur.execute("SELECT number FROM card;")
    numbers = cur.fetchall()
    numbers = [tuple[0] for tuple in numbers]
    if acc_num not in numbers:
        print("Wrong card number or PIN!\n")
        return
    cur.execute(f"SELECT pin FROM card WHERE number = {acc_num};")
    expected_pin = cur.fetchall()[0][0]
    #print(f"expected pin: {expected_pin}")
    pin_num = input("Enter your PIN:\n")
    print(f"expected pin: {expected_pin}")

    if pin_num == expected_pin:
        print("You have successfully logged in!\n")
        log_result = logged_in(acc_num)
        return log_result
    else:
        print("Wrong card number or PIN!\n")
        return


def banking():
    selection = None
    while True:

        if selection == 0:
            print("Bye!")
            break
        selection = menu_prompt()
        if selection == 1:
            new_customer = generate_customer_entry()
            #print(new_customer)
            cur.execute(f"INSERT INTO card (number, pin, balance) VALUES ({new_customer[0]}, {new_customer[1]}, 0)")
            #cur.execute('SELECT * FROM card')
            #print(cur.fetchall())
            conn.commit()
            print("Your card has been created")
            print("Your card number:")
            print(new_customer[0])
            print("Your card PIN:")
            print(new_customer[1])
        elif selection ==2:
            next_step = log_into_acc()
            if next_step == 0:
                selection = 0



banking()
