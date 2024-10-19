WARNING: Use at your own risk. This code is not tested and is for experimental basis only

1. Setup Breeze Virtual Environment as per instructions on https://pypi.org/project/breeze-connect/ OR make setup.sh executable and execute it on a bash terminal. NOTE: The python scripts have been developed for breeze-connect v.1.0.58
2. Update the cred.py code to specify the path and name of the credentials - API, Secret Key and Session Token in .json format as shown in the sample cred.json. The application will subsequently keep updating that same file with the session token you provide via the application
3. Run the BreezeOptimizerGUI in the same virtual environment - it fetches the options offering highest premiums on the margin available and allows you to fire an order straight from the same window
4. Run the BreezeOrderGUI separately if you want to fire different orders


CHANGE BACKLOG
Important:
1. Show Bid:Ask spread when placing order so user can decide whether price likely to move up or down
2. Group positions by Expiry Date & Stock Code and calculate hedging / risk at these group levels
3. Post Breeze Session connection, use application without having to restart it
4. Catch all breeze exceptions

Nice to have:
1. Point breeze config file to local directories for securities master files as long as we don't use them
2. If ICICI Direct is down, import of Cred fails. Move the session initiation out of __init__ in cred.py
3. Parameterise Lot Sizes and Max Order Sizes via an external config file
4. Allow clickable link to Breeze API login on the screen if session connection fails due to invalid token
5. Restructure code: too much of logic sitting in GUI scripts.
