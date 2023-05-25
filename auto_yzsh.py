import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import win32com.client
import logging
from steamgrid import SteamGridDB
from PIL import Image
import requests
from io import BytesIO

import sv_ttk

# Read values from config file

import configparser

config_file_path = 'config_yzsh.ini'
def open_config_file():
    os.startfile(config_file_path)

# Check if the config file exists
if not os.path.exists(config_file_path):
    # If the config file doesn't exist, create it with default values
    with open(config_file_path, 'w') as configfile:
        configfile.write('[DEFAULT]\n')
        configfile.write('YuzuDirectory=\n')
        configfile.write('SteamGridDBAPIKey=\n')
        configfile.write('GamesDirectory=\n')
        configfile.write('SecondaryGamesDirectory=\n')
        configfile.write('ShortcutsDirectory=\n')

config = configparser.ConfigParser()
config.read(config_file_path)

yuzu_directory = config.get('DEFAULT', 'YuzuDirectory', fallback=None)
steamgriddb_api_key = config.get('DEFAULT', 'steamgriddbapikey', fallback=None)

def read_api_key_from_file():
    api_key = steamgriddb_api_key
    if not api_key:
        print("SteamGridDB API key not found. Please add your SteamGridDB API key to the 'config_yzsh.ini' file.")
        logging.error("SteamGridDB API key not found in config file.")
    return api_key

logging.basicConfig(filename='yuzu_shortcuts.log', level=logging.INFO)

def create_shortcut(emulator_path, game_path, game_name, shortcuts_directory):
    print("Creating shortcut...")
    
    # Create a shortcut for the emulator .exe
    shortcut_name = game_name.split("[")[0].strip() + ".lnk"
    shortcut_path = os.path.join(shortcuts_directory, shortcut_name)

        # Create the shortcut with the required arguments
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = emulator_path
    shortcut.Arguments = f'-u 1 -f -g "{game_path}"'
    
    # Use the SteamGridDB API to get an icon for the game
    api_key = read_api_key_from_file()
    if api_key:
        sgdb = SteamGridDB(api_key)
    else:
        return
    
    try:
        # Search for the game on SteamGridDB
        results = sgdb.search_game(game_name)
        
        if results:
            # Get the first result
            game = results[0]
            
            # Get the icon for the game
            icons = sgdb.get_icons_by_gameid([game.id])
            
            if icons:
                # Get the first icon
                icon = icons[0]
                
                # Get the URL of the icon image
                icon_image_url = icon.url
                
                if icon_image_url:
                    # Download the icon image
                    response = requests.get(icon_image_url)
                    image_data = response.content
                    
                    # Convert the image data to a PIL Image object
                    image = Image.open(BytesIO(image_data))
                    
                    # Get the selected icon size from the dropdown menu
                    icon_size_str = icon_size_var.get()
                    icon_size = int(icon_size_str.split("x")[0])
                    
                    # Resize the image to the selected size
                    image = image.resize((icon_size, icon_size))
                    
                    # Save the image as an ICO file in the games directory
                    games_directory = os.path.dirname(game_path)
                    icon_path = os.path.join(games_directory, game_name + ".ico")
                    image.save(icon_path)
                    
                    print(f"Icon saved: {icon_path}")
                    
                    # Set the icon for the shortcut
                    shortcut.IconLocation = icon_path
                    
                    print(f"Icon location: {shortcut.IconLocation}")
    
    except Exception as e:
        print(f"Error getting icon from SteamGridDB: {e}")
        logging.error(f"Error getting icon from SteamGridDB: {e}")
    
    if not shortcut.IconLocation:
        # If no icon was found on SteamGridDB, use the default yuzu icon
        shortcut.IconLocation = emulator_path
    
    shortcut.WorkingDirectory = os.path.dirname(game_path)
    shortcut.Save()
    print(f"Shortcut created: {shortcut_path}")
    logging.info(f"Shortcut created: {shortcut_path}")

def create_shortcuts_for_directory(emulator_path, games_directories, shortcuts_directory):
    # Create a set to keep track of existing shortcuts in the specified directory
    existing_shortcuts = set(os.path.splitext(shortcut)[0] for shortcut in os.listdir(shortcuts_directory))
    
    # Create a shortcut for each game in the specified directories
    for games_directory in games_directories:
        for game_file in os.listdir(games_directory):
            game_path = os.path.join(games_directory, game_file)

            # Skip files that are not NSP or XCI
            if not game_file.lower().endswith(('.nsp', '.xci')):
                continue

            game_name = os.path.splitext(game_file)[0]
            
            # Check if a shortcut already exists for this game
            if game_name in existing_shortcuts:
                continue
            
            create_shortcut(emulator_path, game_path, game_name, shortcuts_directory)
            
            # Add the game name to the set of existing shortcuts
            existing_shortcuts.add(game_name)

def select_emulator_path():
    # Automatically set the emulator directory to the default location
    default_emulator_dir = os.path.expanduser("~\\AppData\\Local\\yuzu")
    emulator_path = filedialog.askopenfilename(initialdir=default_emulator_dir, filetypes=[("Executable Files", "*.exe")])
    
    # Validate that the selected file is a valid yuzu emulator executable
    if "yuzu.exe" not in emulator_path:
        print("Invalid yuzu emulator executable.")
        logging.error("Invalid yuzu emulator executable.")
        return
    
    # Save the selected Yuzu directory to the config file
    config.set('DEFAULT', 'YuzuDirectory', emulator_path)
    with open('config_yzsh.ini', 'w') as configfile:
        config.write(configfile)
    
    emulator_entry.delete(0, tk.END)
    emulator_entry.insert(tk.END, emulator_path)

def select_games_directory():
    # Use askdirectory to allow the user to select a single directory
    games_directory = filedialog.askdirectory(title="Select Games Directory")
    
    # Save the selected games directory to the config file
    config.set('DEFAULT', 'GamesDirectory', games_directory)
    with open('config_yzsh.ini', 'w') as configfile:
        config.write(configfile)
    
    # Clear the entry and insert the selected directory
    games_directory_entry.delete(0, tk.END)
    games_directory_entry.insert(tk.END, games_directory)

def select_secondary_games_directory():
    # Use askdirectory to allow the user to select a single directory
    secondary_games_directory = filedialog.askdirectory(title="Select Secondary Games Directory (Optional)")
    
    # Save the selected secondary games directory to the config file
    config.set('DEFAULT', 'SecondaryGamesDirectory', secondary_games_directory)
    with open('config_yzsh.ini', 'w') as configfile:
        config.write(configfile)
    
    # Clear the entry and insert the selected directory
    secondary_games_directory_entry.delete(0, tk.END)
    secondary_games_directory_entry.insert(tk.END, secondary_games_directory)

def select_shortcuts_directory():
    default_shortcuts_dir = os.path.expanduser("~/Desktop")
    shortcuts_directory = filedialog.askdirectory(initialdir=default_shortcuts_dir)
    
    # Save the selected shortcuts directory to the config file
    config.set('DEFAULT', 'ShortcutsDirectory', shortcuts_directory)
    with open('config_yzsh.ini', 'w') as configfile:
        config.write(configfile)
    
    shortcuts_directory_entry.delete(0, tk.END)
    shortcuts_directory_entry.insert(tk.END, shortcuts_directory)

def create_shortcuts():
    emulator_path = emulator_entry.get()
    
    # Get the primary and secondary games directories from their respective entries
    primary_games_directory = games_directory_entry.get()
    
    secondary_games_directory = secondary_games_directory_entry.get()
    
    # Combine the primary and secondary directories into a list of directories
    games_directories = [primary_games_directory]
    
    if secondary_games_directory:
        games_directories.append(secondary_games_directory)
    
    shortcuts_directory = shortcuts_directory_entry.get()

    if not os.path.isfile(emulator_path) or not all(os.path.exists(games_directory) for games_directory in games_directories) or not os.path.exists(shortcuts_directory):
        print("Invalid paths.")
        logging.error("Invalid paths.")
        return

    create_shortcuts_for_directory(emulator_path, games_directories, shortcuts_directory)

window = tk.Tk()
window.title("Auto Yuzu Shortcuts")
window.geometry("424x454")
window.resizable(False, False)

style = ttk.Style()
sv_ttk.set_theme("dark")

emulator_entry = tk.Entry(window,width=70)
if yuzu_directory:
    emulator_entry.insert(tk.END, yuzu_directory)
emulator_entry.grid(row=2, column=0, columnspan=4, pady=10)

emulator_button = ttk.Button(window,text="Select yuzu.exe",command = select_emulator_path,width=40)
emulator_button.grid(row=1, column=0, columnspan=4,pady=10)

games_directory_entry=tk.Entry(window,width=50)
games_directory=config.get('DEFAULT','GamesDirectory',fallback=None)
if games_directory:
        games_directory_entry.insert(tk.END,games_directory)
games_directory_entry.grid(row=4,column=0,columnspan=4,pady=10)

games_directory_button=ttk.Button(window,text="Select Primary Games Directory",command=select_games_directory,width=40)
games_directory_button.grid(row=3,column=0,columnspan=4,pady=10)

secondary_games_directory_entry=tk.Entry(window,width=50)
secondary_games_directory=config.get('DEFAULT','SecondaryGamesDirectory',fallback=None)
if secondary_games_directory:
    secondary_games_directory_entry.insert(tk.END,secondary_games_directory)
secondary_games_directory_entry.grid(row=6,column=0,columnspan=4,pady=10)

secondary_games_directory_button=ttk.Button(window,text="Select Secondary Games Directory (Optional)",command=select_secondary_games_directory,width=40)
secondary_games_directory_button.grid(row=5,column=0,columnspan=4,pady=10)

shortcuts_directory_entry=tk.Entry(window,width=50)
shortcuts_directory=config.get('DEFAULT','ShortcutsDirectory',fallback=None)
if shortcuts_directory:
    shortcuts_directory_entry.insert(tk.END,shortcuts_directory)
shortcuts_directory_entry.grid(row=8,column=0,columnspan=4,pady=10)

shortcuts_directory_button=ttk.Button(window,text="Select Shortcuts Directory",command = select_shortcuts_directory,width=40)
shortcuts_directory_button.grid(row=7,column=0,columnspan=4,pady=10)

icon_size_label=ttk.Label(window,text="Icon Size:")
icon_size_label.grid(row=10,column=1,columnspan=3,pady=10)

icon_size_var=tk.StringVar(window)
icon_size_var.set("64x64")

icon_size_dropdown=tk.OptionMenu(window,icon_size_var,"64x64","32x32","64x64","128x128","256x256")
icon_size_dropdown.grid(row=10,column=3,columnspan=1,pady=10)

open_config_button=tk.Button(window,text="Open Config File",command=open_config_file,width=20)
open_config_button.grid(row=10,column=0,columnspan=3,pady=10)

create_button=ttk.Button(window,text="Create Shortcuts",command=create_shortcuts,width=40)
create_button.grid(row=11,columnspan=4,pady=10)

window.mainloop()
