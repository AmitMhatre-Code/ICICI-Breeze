Setup Breeze Virtual Environment as per instructions on https://pypi.org/project/breeze-connect/
Update the cred.py code to specify the path and name of the credentials - API, Secret Key and Session Token in .json format as shown in the sample cred.json. The application will subsequently keep updating that same file with the session token you provide via the application
Run the BreezeOptimizerGUI in the same virtual environment - it fetches the options offering highest premiums on the margin available and allows you to fire an order straight from the same window
Run the BreezeOrderGUI separately if you want to fire different orders


Important:
Show Bid:Ask spread when placing order so user can decide whether price likely to move up or down
Group positions by Expiry Date & Stock Code and calculate hedging / risk at these group levels
Post Breeze Session connection, use application without having to restart it
Catch all breeze exceptions

Nice to have:
Point breeze config file to local directories for securities master files as long as we don't use them
If ICICI Direct is down, import of Cred fails. Move the session initiation out of __init__ in cred.py
Parameterise Lot Sizes and Max Order Sizes via an external config file
Allow clickable link to Breeze API login on the screen if session connection fails due to invalid token
Restructure code: too much of logic sitting in GUI scripts.
