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

def read_api_key_from_file():
    try:
        with open('api_key.txt', 'r') as f:
            api_key = f.read().strip()
            return api_key
    except FileNotFoundError:
        print("API key file not found. Please create a file named 'api_key.txt' and paste your SteamGridDB API key into it.")
        return None

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
    # Create a shortcut for each game in the specified directories
    for games_directory in games_directories:
        for game_file in os.listdir(games_directory):
            game_path = os.path.join(games_directory, game_file)

            # Skip files that are not NSP or XCI
            if not game_file.lower().endswith(('.nsp', '.xci')):
                continue

            game_name = os.path.splitext(game_file)[0]
            create_shortcut(emulator_path, game_path, game_name, shortcuts_directory)


def select_emulator_path():
    # Automatically set the emulator directory to the default location
    default_emulator_dir = os.path.expanduser("~\\AppData\\Local\\yuzu")
    emulator_path = filedialog.askopenfilename(initialdir=default_emulator_dir, filetypes=[("Executable Files", "*.exe")])
    
    # Validate that the selected file is a valid yuzu emulator executable
    if "yuzu.exe" not in emulator_path:
        print("Invalid yuzu emulator executable.")
        logging.error("Invalid yuzu emulator executable.")
        return
    
    emulator_entry.delete(0, tk.END)
    emulator_entry.insert(tk.END, emulator_path)


def select_games_directory():
    # Use askdirectory to allow the user to select a single directory
    games_directory = filedialog.askdirectory(title="Select Games Directory")
    
    # Clear the entry and insert the selected directory
    games_directory_entry.delete(0, tk.END)
    games_directory_entry.insert(tk.END, games_directory)


def select_secondary_games_directory():
    # Use askdirectory to allow the user to select a single directory
    secondary_games_directory = filedialog.askdirectory(title="Select Secondary Games Directory (Optional)")
    
    # Clear the entry and insert the selected directory
    secondary_games_directory_entry.delete(0, tk.END)
    secondary_games_directory_entry.insert(tk.END, secondary_games_directory)


def select_shortcuts_directory():
    shortcuts_directory = filedialog.askdirectory()
    
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
window.title("Yuzu Shortcuts")
window.geometry("400x700")

style = ttk.Style()
sv_ttk.set_theme("dark")

emulator_label = tk.Label(window, text="Emulator Path:")
emulator_label.pack(pady=10)

emulator_entry = tk.Entry(window, width=40)
emulator_entry.pack(pady=10)

emulator_button = ttk.Button(window, text="Select yuzu.exe", command=select_emulator_path)
emulator_button.pack(pady=10)

games_directory_label = tk.Label(window, text="Primary Games Directory:")
games_directory_label.pack(pady=10)

games_directory_entry = tk.Entry(window, width=40)
games_directory_entry.pack(pady=10)

games_directory_button = ttk.Button(window, text="Select Primary Games Directory", command=select_games_directory)
games_directory_button.pack(pady=10)

secondary_games_directory_label = tk.Label(window, text="Secondary Games Directory (Optional):")
secondary_games_directory_label.pack(pady=10)

secondary_games_directory_entry = tk.Entry(window, width=40)
secondary_games_directory_entry.pack(pady=10)

secondary_games_directory_button = ttk.Button(window, text="Select Secondary Games Directory (Optional)", command=select_secondary_games_directory)
secondary_games_directory_button.pack(pady=10)

shortcuts_directory_label = tk.Label(window, text="Shortcuts Directory:")
shortcuts_directory_label.pack(pady=10)

shortcuts_directory_entry = tk.Entry(window, width=40)
shortcuts_directory_entry.pack(pady=10)

shortcuts_directory_button = ttk.Button(window, text="Select Shortcuts Directory", command=select_shortcuts_directory)
shortcuts_directory_button.pack(pady=10)

# Add a label and dropdown menu for selecting the icon size
icon_size_label = tk.Label(window, text="Icon Size:")
icon_size_label.pack(pady=10)

icon_size_var = tk.StringVar(window)
icon_size_var.set("64x64")

icon_size_dropdown = ttk.OptionMenu(window, icon_size_var, "64x64", "32x32", "64x64", "128x128", "256x256")
icon_size_dropdown.pack(pady=10)

create_button = ttk.Button(window, text="Create Shortcuts", command=create_shortcuts)
create_button.pack(pady=10)

window.mainloop()
