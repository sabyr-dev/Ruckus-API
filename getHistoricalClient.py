import requests
import json
import pprint
import psycopg2
import datetime

import urllib3
urllib3.disable_warnings()


def get_db_connection():
	return psycopg2.connect(host='', user='', password='', dbname='')


def get_db_cursor(conn):
	return conn.cursor()


def send_post(uri, body, cookie, session):
	sz_host_api = 'https://' + '' + ':8443/wsg/api/public/v9_0'
	return session.post(
		url=sz_host_api + uri,
		data=json.dumps(body),
		headers={
			'content-type': 'application/json:charset=UTF-8'
		},
		cookies={
			'JSESSIONID': cookie
		},
		verify=False
	)


def get_tuples_for_insertion(array, client_list):
	for client in client_list:
		array.append((
			client['apMac'],
			client['clientMac'],
			client['hostname'],
			client['ipAddress'],
			client['modelName'],
			int(client['sessionStartTime'] / 1000),
			int(client['sessionEndTime'] / 1000),
			client['ssid']
		))
	return array


pp = pprint.PrettyPrinter(indent=4)
sz_user = ''
sz_pw = ''
s = requests.Session()

r = send_post(
	'/session',
	{
		'username': sz_user,
		'password': sz_pw
	},
	'JSESSIONCOOKIE',
	s
)

check = True
page = 1
insert_records = []
while check == True:
	t = send_post(
		'/query/historicalclient',
		{
			"extraTimeRange": {
				"start": int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000),
				"end": int((datetime.datetime.now().timestamp() + 200) * 1000)
			},
			"sortInfo": {
				"sortColumn": "sessionStartTime",
				"dir": "ASC"
			},
			"limit": 1000,
			"page": page
		},
		r.cookies['JSESSIONID'],
		s
	)
	t_json = json.loads(t.text)
	insert_records = get_tuples_for_insertion(insert_records, t_json['list'])
	page += 1
	check = t_json['hasMore']

insert_query = "INSERT INTO wireless_data.public.ruckus_sessions (apmac, clientmac, hostname, ipaddress, modelname, sessionstarttime, sessionendtime, ssid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) on conflict do nothing"
connection = get_db_connection()
cursor = get_db_cursor(connection)
cursor.executemany(insert_query, insert_records)
connection.commit()
pp.pprint(str(cursor.rowcount) + " records inserted successfully")
cursor.close()
connection.close()