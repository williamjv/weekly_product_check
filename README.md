# Weekly Product Check

This script is run weekly to check on products that Networking supports.  Here is a list of the products.

* DDoS - Premium DDoS Protection
* CDN - Akamai only
* Load Balancer - Licensing only


Script will by default check the last 7 days for product additions and terminations. It can be run with option `-d $NUM` to search the logs for more or less days than the default.  Once completed it will run 

---
### Python 3

This script was designed for Python 3.x.  I recommend running it from a Python Environment.  With below example commands on your workstation.


```
cd ~/location of audit script/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---
### Options

`-d $NUMBER` - By default the script will check the last 7 days.  Using this optino you can increase or decrease the number of days searched

`-p` - By default the script will generate a Jira card if any information is found.  Using this option will ensure the information is only displayed on screen.

`--help` - Display the options listed above.

---
### Example of use

Here is an example of running the script and output.  For the time being the output is primarily in JSON format.

```
cd ~/location of script/
source venv/bin/activate
python subAudit.py

Username: (Your Username)
Password: (Your Password)

One moment as we gather data.
CDN

	 Additions:
{
    "accnt": 123456,
    "date": "0000-01-01 00:00:00",
    "id": 100000000,
    "message": "Added domain [example.com] to sub accounts. Sub accnt type [Akamai], uniq_id [FFFHHH].",
    "remote_addr": "10.0.0.0",
    "remote_user": "william",
    "type": "add"
}

	 Terminations:
{
    "accnt": 123456,
    "date": "0000-01-01 00:00:00",
    "id": 100000001,
    "message": "Removed subaccount [12345678]. Domain [example.com], type [Akamai], main IP [127.0.0.1], uniq_id [FFFHHH], location [none].",
    "remote_addr": "10.0.0.0",
    "remote_user": "william",
    "type": "remove"
}

Report completed in 2.84 second(s)
```

The issue this solves is sometimes the Network team is not notified for configuration adjustments.

* In cases of missed additions this has the potential of giving the customer a bad experience with the product.
* In cases of terminations this leaves configurations in place potentially unnoticed for years. 

