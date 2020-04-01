Steam Price Checker
======
A project to manage prices and deals for steam games through the cli. For now it can show free games and more features are coming.
***

Requirements
------
The application is written using python3 and requires python3

Installation
------
install the dependencies `$ pip3 install -r requirements.txt`

Usage
------
**Simple Usage**
 * Default mode will store the steamapp data in the same directory as the script
 * `$ python3 checker.py`
 * You can specify a path to your own database using the db flag
 * `$ python3 checker.py --db ~/downloads/prices.db`
 * You can specify a minimum discount using the min_discount flag
 * `$ python3 checker.py --min_discount 80`
 * You can specify a minimum base (non discounted) price using the min_initial flag 
 * `$ python3 checker.py --min_initial 1000`
 * You can specify a maximum discounted price using the max_current flag
 * `$ python3 checker.py --max_current 225`