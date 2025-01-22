# Oracle Database Scripting Tool

Scripting GUI-based tool which orchestrated the Turbonomic REST API to satisfy a customer use case regarding target configuration for Oracle targets. Some of the features of the tool are as follows:
- Add database targets en masse via a CSV file, where before this would have to be done individually
- Remove all malfunctioning targets that failed to discover or connect at once, instead of selected each in the UI and deleting manually.
- Edit database credential info en masse via input through the tool's UI. Select any subset of Oracle targets in the UI and collectively rotate their passwords, for example. Once changed, the targets will be re-discovered.

Built by Lucas Hancock (lucashancock@ibm.com)

## Frontend GUI Image

<img width="1294" alt="Screenshot 2025-01-22 at 12 47 21 PM" src="https://github.com/user-attachments/assets/143c6310-cfe8-4263-bdc8-9a661e84257c" />

## Installation & Running

1. If not done so already, get this folder on your machine. You can do this either by downloading the content which was sent to you, or by cloning the github.
2. Verify you have a recent version of python on your machine. You can do this by downloading python off the internet or by using a package manager.
3. Once installed, make sure your terminal recognizes the python keyword (you can run python scripts from the terminal). This may require adding the python binary to your PATH.

First time installation instructions:

4. Change directory to the folder.
5. Run `python3 -m venv venv`. Keep in mind you may need to use `python` instead of `python3`. This will create a virtual environment to keep everything contained in this folder and avoid installing packages elsewhere on your machine.
6. Run `source ./venv/bin/activate` to activate the virtual environment on macOS, or `.\venv\Scripts\activate` on Windows.
7. Next, run `pip install -r requirements.txt` to install the requirements for the script.
8. Finally, run `python3 gui.py` to start the tool.

After first time installation instructions:

1. Change directory to the folder.
2. Activate the virtual environment using the commands detailed above in step 6.
3. Run the tool using `python3 gui.py`

## Important Notes

- When entering the IP Address, please don't forget to include `https://` to the front of the URL.
- You can select multiple records in the table view on the tool by using selection modifier keys according to your OS. On mac, for example, I can use Shift and click two different records to select them and everything in between. I can also use Command and Click to select individual records and add them to the selection.

## Contact

Please reach out to lucashancock@ibm.com if you have any issues, improvements, or trouble installing or running the application.

Thank you!
