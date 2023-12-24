from bitwardentools import Client
from bitwardentools import CipherType
from urllib.parse import urlparse
from urllib.parse import urlunparse
import socket
import getpass
import os

def valid_ip(address):
    try: 
        socket.inet_aton(address)
        return True
    except:
        return False
def api_key(loginpayload):
    loginpayload.update(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "api",
            "grant_type": "client_credentials"
        }
    )
    return loginpayload

vault = os.getenv('BWFIX_VAULT')
user = os.getenv('BWFIX_USER')
client_id = os.getenv('BWFIX_CLIENTID')
client_secret = os.getenv('BWFIX_CLIENTSECRET')
password = os.getenv('BWFIX_PASSWORD')
fix_passkeys = os.getenv('BWFIX_FIXPASSKEYS', 'False').lower() in ('true', '1', 't')
fix_history = os.getenv('BWFIX_FIXHISTORY', 'False').lower() in ('true', '1', 't')

print("\nbwfixhttp.py Usage\n")
print("This python script is designed to work with bitwarden, bitwarden self hosted, and vaultwarden.\n")
print("It updates uris that start with http:// to start with https://\n")
print("It requires python, bitwardentools (e.g. 'pip install bitwardentools' followed by 'pip install packaging' to install a missing dependency).\n")
print("bitwardentools requires the bitwarden CLI, although this project doesn't use it.\n")
print("This script will not fix items without FQDNs (i.e. single word hosts) as these are typically home network devices.")
print("Similarly, it will not fix all numeric hosts that are valid IP addresses for the same reason.")
print("Finally, it delete a uri that is entirely http:// which sometimes happens when you set up a login without a host (i.e. for a database).\n")
print("This should make your Unsecure websites report a lot shorter.\n")
print("This script will not fix items with Passkeys or Password History by default.\n")
print("If you want to fix these items, you must set environment variables BWFIX_FIXPASSKEYS and/or BWFIX_FIXHISTORY to True.\n")
print("Note: Testing has found that fixing these logins with Passkeys or Password History results in invalid dates being stored in the item")
print("      which results in these items a) not being editable and b) may result in mobile clients not being able to to sync.\n")
print("      You might be able to recover by saving a new Passkey over the top, or saving a new password and updating the password history.\n")
print("      In the worst case you may need to delete and re-create these items to recover from this situation.\n")
print("      In the very worst case you may need to delete and re-create all items in your vault to recover from this situation.\n")
print("Set environment variables for BWFIX_VAULT (address of your bitwarden or vaultwarden server), BWFIX_USER and optionally BWFIX_PASSWORD.\n")
print("If you have 2FA set up, you must set up an API Key for your account, and provide the Client ID and Secret as BWFIX_CLIENTID and BWFIX_CLIENTSECRET.\n")
print("If you do not have 2FA set up, you can skip these items.\nIf you do not set any environment variables, the script will prompt for input.\n")
print("If you do not have 2FA set up, you can skip these items.\nIf you do not set any environment variables, the script will prompt for input.\n")

usercont = input("Do you want to continue? Y/n... ").lower() in ('yes', 'y', '')
if not usercont:
    quit()

if vault is None:
    vault = input("Enter the vault to connect to including https://\n For example:\nhttps://bitwarden.com\nhttps://bitwarden.eu\nhttps://bitwarden.myselfhosted.com\n")

if user is None:
    user = input("Enter userid (email) of account: ")

if client_id is None: 
    client_id = input("Enter API client_id for account (optional, Required for 2FA protected accounts): ")

if client_secret is None: 
    client_secret = input("Enter API client_secret for account (optional, Required for 2FA protected accounts): ")

if password is None:
    password = getpass.getpass("Enter password of account: ")
 
myclient = Client(vault,user,password,authentication_cb=api_key)

fixcypher = None #initialise nothing to do

all_ciphers_ids = myclient.get_ciphers()['id'] # get a list of cipher IDs.
for id, login in all_ciphers_ids.items():
    if login.type == CipherType.Login: # Only process logins (skip secure notes, cards, identities)
        if "uris" in login.login: # With URIs (some don't have any)
            if login.login['uris'] is not None:  # And some have a None type
                # Check no Passkey or OK to fix / #Check Password History or OK to fix
                if (fix_passkeys or not ("fido2Credentials" in login.data and login.login['fido2Credentials'] is not None and len(login.login['fido2Credentials']) > 0)) and (fix_history or login.passwordHistory is None): 
                    for i, uri in enumerate(login.login['uris']): # Process each URI
                        myuri = uri['uri']
                        url = urlparse(myuri)
                        if not myuri == "http://" and url.scheme == "http" and "." in url.hostname and not valid_ip(url.hostname): # only do http, skip non FQDNs (e.g. home devices) and numeric hosts
                            if fixcypher is None: #if we haven't got a reference to the login yet (important if we're enumerating multiple URIs)
                                fixcypher = myclient.get_cipher(id,None,None,None,False,None) #get it
                            newuri = urlunparse(tuple(["https", url.netloc, url.path, url.params, url.query, url.fragment])) #re create the URL with https
                            fixcypher.login['uris'][i]['uri'] = newuri # and update the login
                        if myuri == "http://": # empty placeholder; let's delete
                            newuri = ""
                            if fixcypher is None: #if we haven't got a reference to the login yet (important if we're enumerating multiple URIs)
                                fixcypher = myclient.get_cipher(id,None,None,None,False,None) #get it
                            del fixcypher.login['uris'][i]
        if  fixcypher is not None: # if we did anything
            myclient.edit_login(fixcypher, id=login.id) #update.  The id=login.id doesn't *seem* to do anything, but is required for the update to work.  Normally you'd update a field, but we're passing in the entire object.
            print(f"fixed login '{login.name}' with URI '{newuri}'") #log output
            myclient.sync #tell other clients
            fixcypher = None #let the loop know that it can skip updates on next item, if no http sites are found.
myclient.bust_cache
