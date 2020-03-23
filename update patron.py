# Jeremy Goldstein
# Minuteman Library Network

# Runs SQL query to find online patron registrations with the online patron ptype
# and then uses the patron API to update their ptypes to that of each patron's associated library
# assuming the patron entered a valid address into the registration form

import requests
import json
import configparser
from base64 import b64encode
import psycopg2

#authenticates to Sierra_API and retains generates access token
def get_token():
    # config api    
    config = configparser.ConfigParser()
    # api_info.ini contains login credentials needed for both the API calls and SQL access
    # file should contain the following, just enter your values after each = 
        #[api]
        #base_url = 
        #client_key = 
        #client_secret = 
        #sql_host = 
        #sql_user = 
        #sql_pass = 
    config.read('api_info.ini')
    base_url = config['api']['base_url']
    client_key = config['api']['client_key']
    client_secret = config['api']['client_secret']
    auth_string = b64encode((client_key + ':' + client_secret).encode('ascii')).decode('utf-8')
    header = {}
    header["authorization"] = 'Basic ' + auth_string
    header["Content-Type"] = 'application/x-www-form-urlencoded'
    body = {"grant_type": "client_credentials"}
    url = base_url + '/token'
    response = requests.post(url, data=json.dumps(body), headers=header)
    json_response = json.loads(response.text)
    token = json_response["access_token"]
    return token

#function makes a single API call to update the ptype of a specified record
def mod_patron(patron_id,patron_type):
    config = configparser.ConfigParser()
    config.read('api_info.ini')
    token = get_token()
    url = config['api']['base_url'] + "/patrons/" + patron_id
    header = {"Authorization": "Bearer " + token, "Content-Type": "application/json;charset=UTF-8"}
    payload = {"patronType": patron_type}
    request = requests.put(url, data=json.dumps(payload), headers = header)
    
def main():
    config = configparser.ConfigParser()
    config.read('api_info.ini')
        #Connecting to Sierra PostgreSQL database
    conn = psycopg2.connect("dbname='iii' user='" + config['api']['sql_user'] + "' host='" + config['api']['sql_host'] + "' port='1032' password='" + config['api']['sql_pass'] + "' sslmode='require'")

    #Opening a session and querying the database for weekly new items
    cursor = conn.cursor()
    #sql query will return the patron number and it needs to be updated to for each in network online registration
    cursor.execute(open("online patron registration update.sql","r").read())
    #For now, just storing the data in a variable. We'll use it later.
    rows = cursor.fetchall()
    conn.close()
    #Calls mod_patron function with the patron number and desired ptype for each row in the SQL query's output
    for rownum, row in enumerate(rows):
        mod_patron(str(row[0]),row[1])
        #printing rows to provide a script progress marker
        print(row[0])
        print(row[1]) 
    
   
                    
main()

