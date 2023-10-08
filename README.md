# MasterTicket
a qrocde ticket system with web gui

![Screenshot](/READMEFILE/header_image.png)

## How to use
1. create a firebase project
2. get service account key `serviceAccountKey.json`

   > To generate a private key file for your service account:
   > 
   > 1. In the Firebase console, open Settings > Service Accounts.
   > 2. Click Generate New Private Key, then confirm by clicking Generate Key.
   > 3. Securely store the JSON file containing the key.
   > 
   > src: https://firebase.google.com/docs/admin/setup

3. put serive account key (rename it as `serviceAccountKey.json`) in the same directory of `app.py`
4. enable firebase update
   - go to realtime database > rule
   - set the rule as following
    ```json
    {
      "rules": {
        ".read": true,
        ".write": true
      }
    }
    ```
5. run app.py
