import string
import random
import subprocess
import os
from getpass import getpass
from cryptography.fernet import Fernet

# Add a Gui - Eventually

# Check if running as root
def root_check():
    uid = os.getuid()
    if uid == 0:
        return True
    else:
        print("Please run this script with Sudo priviledges.")
        exit()

#Generate a random Password
def pass_gen(l):
    chars = string.printable
    password = ""
    for i in range(l):
        password += fr"{random.choice(chars)}"
    return password

#generate encryption key
def generate_key_and_cipher(loc):
    key_file_path = os.path.join(loc, ".encryption_key.key")

    if not os.path.exists(key_file_path):
        key = Fernet.generate_key()
        with open(key_file_path, "wb") as key_file:
            key_file.write(key)
            subprocess.run(["chmod", "600", key_file_path])

    with open(key_file_path, "rb") as key_file:
        key = key_file.read()

    cipher = Fernet(key)
    return cipher

#Save passwords
def save_pass(u, p, w, loc, cipher):
    loc = os.path.join(loc, ".Passwords.txt")
    if not os.path.exists(loc):
        subprocess.run(["touch", loc])
        subprocess.run(["chmod", "600", loc])
    encrypted_password = cipher.encrypt(p.encode()).decode()
    with open(f"{loc}", "a") as file:
        file.write(f"{u} : {encrypted_password} : {w}\n")

#Check if Master Password set and if correct
def check_master_password(mp, loc, cipher):
    loc = os.path.join(loc, ".MasterPass.txt")
    if not os.path.exists(loc):
        with open(loc, "w") as file:
            master_password = getpass("Please Create a Master Password: ")
            encrypted_password = cipher.encrypt(master_password.encode()).decode()
            file.write(encrypted_password)
            print("Master Password set")
            subprocess.run(["chmod", "600", loc])
            return True
    else:
        with open(loc, "r") as master_file:
            stored_encrypted_password = master_file.read().strip()
            decrypted_password = cipher.decrypt(stored_encrypted_password.encode()).decode()
            if mp == decrypted_password:
                return True
            else: 
                return False

# Retrieve password and decrypt it
def retrieve_password(data, loc, cipher):
    with open(os.path.join(loc, ".Passwords.txt"), "r") as file:
        for line in file:
            parts = line.strip().split(" : ")
            username, encrypted_password, website = parts[0], parts[1], parts[2]
            decrypted_password = cipher.decrypt(encrypted_password.encode()).decode()
            if data in [username, website]:
                print(f"Username: {username}, Password: {decrypted_password}, Website: {website}")

# Add a password without generating
def add_password(u, p, w, loc, cipher):
    loc = os.path.join(loc, ".Passwords.txt")
    encrypted_password = cipher.encrypt(p.encode()).decode()
    if not os.path.exists(loc):
        subprocess.run(["touch", loc])
        subprocess.run(["chmod", "600", loc])
    with open(f"{loc}", "a") as file:
        file.write(f"{u} : {encrypted_password} : {w}\n")

# Script starts here
root_check()
password = getpass("Please Enter your Master Password, If this is your first time running, leave blank: ")
file_location = "/root/.VaultCLI/"
if not os.path.exists(file_location):
    subprocess.run(["mkdir", file_location])
    subprocess.run(["chmod", "600", file_location])
cipher = generate_key_and_cipher(file_location)
if check_master_password(password, file_location, cipher):
    print("Password Correct")
    try:
        choice = ""
        while True:
            choice = input("Do you want to Generate, add a password or Retrieve? (Use G, A or R) ").lower()
            if choice == "g":
                pass_length = int(input("What length of password do you need? "))
                website = input("What website or App is this for? ")
                username = input("What is the username for this website? ")
                password = pass_gen(pass_length)
                save_pass(username, password, website, file_location, cipher)
                print(f"Your password has been saved to {file_location}/Passwords.txt")
            elif choice == "r":
                d = input("Type a username or app/website you want to find the password for: ")
                retrieve_password(d, file_location, cipher)
            elif choice == "a":
                username = input("What is the username for the app/website? ")
                password = getpass("What is the Password for this app/website? ")
                website = input("What website or App is this for? ")
                add_password(username, password, website, file_location, cipher)
            else:
                pass

    except KeyboardInterrupt:
        print ("\nClosing")
        exit()
