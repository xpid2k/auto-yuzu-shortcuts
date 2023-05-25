# auto-yuzu-shortcuts

## Downloading a Prebuilt Executable

If you don't want to install Python and the dependencies required to run this script, you can download a prebuilt executable from the [releases page](https://github.com/xpid2k/auto-yuzu-shortcuts/releases) of this repository.

Simply download the latest release and run the `yuzu_shortcuts.exe` file.

## Getting Started

1. Download the `yuzu_shortcuts.py` script and `requirements.txt` file from this repository.
2. Install the dependencies by running the command `pip install -r requirements.txt`.

## Using the Script

1. Run the `yuzu_shortcuts.py` script to open the GUI.
2. In the GUI, enter the path to your Yuzu emulator in the `Emulator` field.
3. Select your primary games directory by clicking the `Select Games Directory` button. (Optionally, you can select a secondary games directory.)
4. Select the directory where you want to save your shortcuts by clicking the `Select Shortcuts Directory` button.
5. Select the size of the icons from the `Icon Size` dropdown menu.
6. Click the `Create Shortcuts` button and voila! You now have shortcuts for your Yuzu games.

## Obtaining a SteamGridDB API Key

This script uses the SteamGridDB API to automatically assign icons to your Yuzu game shortcuts. To use this feature, you will need to obtain a SteamGridDB API key.

Here's how you can obtain a SteamGridDB API key:

1. Log in with your Steam account at [SteamGridDB](https://www.steamgriddb.com/).
2. Go to your [API settings page](https://www.steamgriddb.com/profile/preferences/api) to generate a new API key.

Once you have obtained your API key, open the file named `api_key.txt` in the same directory as the `yuzu_shortcuts.py` script and paste your API key into it.

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
