# bwfixhttp
## Python Script to fix http:// entries in bitwarden, bitwarden self-hosted, and vaultwarden

> [!CAUTION]
> Make sure you have a backup.
> 
> Don't trust this script. It is open source, as are all of the tools it uses, but that doesn't mean you should trust it.
>
> It could destroy your vault. I destroyed my vault while testing it.
>
> It could send each of your passwords to me (it doesn't, but it could; they are all unencrypted at the point that the script is operating on each login).
>
> It relies on a tool that is not actively being maintained.  But it seems to work.
>
> Use  at your own risk. Read the source code before using it.  If you're not confident, don't run this.
>
> You have been warned.
>
> Have a nice day. 🤣

### bwfixhttp.py Usage

This python script is designed to work with bitwarden, bitwarden self hosted, and vaultwarden.

It updates uris that start with http:// to start with https://

It requires python, [bitwardentools](https://github.com/corpusops/bitwardentools) (i.e. `pip install bitwardentools` followed by `pip install packaging` to install a missing dependency).

bitwardentools requires the [bitwarden CLI](https://github.com/bitwarden/cli) installed by `sudo snap install bw`, although this project doesn't use it.

This script will not fix items without FQDNs (i.e. single word hosts) as these are typically home network devices.
Similarly, it will not fix all numeric hosts that are valid IP addresses for the same reason.
Finally, it delete a uri that is entirely http:// which sometimes happens when you set up a login without a host (i.e. for a database).

This should make your Unsecure websites report a lot shorter.

This script will not fix items with Passkeys or Password History by default.

If you want to fix these items, you **must** set environment variables BWFIX_FIXPASSKEYS and/or BWFIX_FIXHISTORY to True.

The script does not report when it skips an item with a Passkey or with Password History: this is because these items will remain (along with other skipped items such as IP address hosts) in the Unsecure websites list, and thus available for review and manual remediation.

> [!WARNING]
> Testing has found that fixing these logins with Passkeys or Password History results in invalid dates being stored (somewhere, debugging hasn't revealed where) in the item which results in these items
> a) not being editable and
> b) may result in mobile clients not being able to to sync.
> You might be able to recover by saving a new Passkey over the top, or saving a new password and updating the password history.
> In the **worst** case you may need to delete and re-create these items to recover from this situation.
> In the **_very worst_** case you may need to **delete and re-create** all items in your vault to recover from this situation.

Set environment variables for BWFIX_VAULT (address of your bitwarden or vaultwarden server), BWFIX_USER and optionally BWFIX_PASSWORD.

If you have 2FA set up, you must set up an API Key for your account, and provide the Client ID and Secret as BWFIX_CLIENTID and BWFIX_CLIENTSECRET.

If you do not have 2FA set up, you can skip these items.
If you do not set any environment variables, the script will prompt for input.

Vault will be one of
https://bitwarden.com, 
https://bitwarden.eu, 
or your self hosted URL
https://bitwarden.myselfhosted.com

## Example Usage

Obviously you'll want to replace the CLIENTID and CLIENTSECRET with your own API details, and set up the vault with your vault address and your login.  You can either enter your password when prompted, or set up a BWFIX_PASSWORD environment variable if you'd like.

You could run this on windows, linux or mac, I guess, or anywhere where bitwarden cli and python run.  I ran it on linux (Ubuntu) running as WLS2 under Windows 11, but it's all much of a muchness.

```bash
sudo snap install bw
pip install bitwardentools
pip install packaging

BWFIX_CLIENTID="user.e6181bdf-f471-410e-9b60-b9ad1283481e"
BWFIX_CLIENTSECRET="alongstringofrandomcharacters"
BWFIX_VAULT="https://bitwarden.eu"
BWFIX_USER="joe.random@gmail.com"
git clone https://github.com/BJReplay/bwfixhttp.git
python3 bwfixhttp/bwfixhttp.py
```
