# Ruckus-API
Ruckus SmartZone (vSZ or SZ) API Scripts

* getHistoricalClient.py
  * This script grabs recent clients and dumps them into a PostgreSQL database due to the storage limitation of 3 days within SZ/vSZ.
  * Users wanting to run this script will need to update variable values on lines 12, 20, 50, and 51.
