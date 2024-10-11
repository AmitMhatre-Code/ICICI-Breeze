Setup Breeze Virtual Environment as per instructions on https://pypi.org/project/breeze-connect/
Update the cred.py code to specify the path and name of the credentials - API, Secret Key and Session Token in .json format as shown in the sample cred.json. The application will subsequently keep updating that same file with the session token you provide via the application
Run the BreezeOptimizerGUI in the same virtual environment - it fetches the options offering highest premiums on the margin available and allows you to fire an order straight from the same window
Run the BreezeOrderGUI separately if you want to fire different orders
