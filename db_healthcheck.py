import requests
from bs4 import BeautifulSoup
import json
import getpass
 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import date, time
from datetime import datetime

 

# set up session for auth
s = requests.Session()
login_form = s.get("http://35.174.4.215/login")

 
# get Cross-Site Request Forgery protection token
soup = BeautifulSoup(login_form.text, 'html.parser')
csrf_token = soup.find('input',{'id':'csrf_token'})['value']

 

# login the given session
s.post('http://35.174.4.215/login/',data=dict(username='admin', password='admin',csrf_token=csrf_token))
headers = {'Content-type': 'application/json; charset=utf-8', 'Accept': 'text/json'}
url='http://35.174.4.215/api/v1/database/'
result_db_names=(s.get(url).json())


#database_name
result_extracted=result_db_names['result']
all_db_names=[]
all_db_ids=[]


dict_for_name_id = {}

#creating a couter loop to organize db names
counter=0



db_name_id_uri={}
for items in result_extracted:

                all_db_names.append(items['database_name'])
                all_db_ids.append(items['id'])
                dict_for_name_id['db_name']=items['database_name']
                dict_for_name_id['id']=items['id']

                db_name_id_uri[counter]=dict_for_name_id
                counter=counter+1




all_db_uris=[]

print(db_name_id_uri)

headers = {'Content-type': 'application/json; charset=utf-8', 'Accept': 'text/json'}

print(db_name_id_uri[0]['db_name'])



for i in range(0,len(db_name_id_uri)):

    url='http://35.174.4.215/api/v1/database/' + str(db_name_id_uri[i]['id'])

    result_dbs=(s.get(url).json())
    result_extracted2=result_dbs['result']
    print(result_dbs)
    print(result_extracted2)

    db_name_id_uri[i]['uri']=result_extracted2['sqlalchemy_uri']
   

# base url to ping
url_test='http://35.174.4.215/api/v1/database/test_connection'

headers = {'Content-type': 'application/json', 'Accept': 'text/plain',
        "X-CSRFToken": csrf_token }


# looping through all the fields we got and replacing below
errors_check=""


dict_for_name_id2={}

dict_for_name_id2['db_name']="test"
dict_for_name_id2['id']=3
dict_for_name_id2['uri']="postgresql://superset:XXXXXXXXXX@db:5432/superset"

db_name_id_uri[1]=dict_for_name_id2



today = date.today()
now = datetime.now()

current_time = now.strftime("%H:%M:%S")

# Textual month, day and year   
d2 = today.strftime("%B %d, %Y")



            # Create the body of the message (a plain-text and an HTML version).
html = """\
<html>
    <head>
    <style>
        #db_test {
        font-family: Arial, Helvetica, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }

        #db_test td, #customers th {
        border: 1px solid #ddd;
        padding: 8px;
        }

        #db_test tr:nth-child(even){background-color: #f2f2f2;}

        #db_test tr:hover {background-color: #ddd;}

        #db_test th {
        padding-top: 12px;
        border: 1px solid #ddd;
        padding-bottom: 12px;
        text-align: left;
        background-color: #04AA6D;
        color: white;
        }
        </style>
    </head>
    <body>
    <h1>Database Automation HealthCheck Created On """+d2+""" """+current_time+"""</h1>
        <table id="db_test">
        <tr>
        <th>#</th>
        <th>Database Name</th>
        <th>Running Status</th>
        </tr>"""

for i in range(0,len(db_name_id_uri)):

    params={
    "configuration_method": "sqlalchemy_form",
    "database_name": str(db_name_id_uri[i]['db_name']),
    "sqlalchemy_uri": str(db_name_id_uri[i]['uri'])
    }
    data=json.dumps(params) 

    result_db_names_test=(s.post(url=url_test,data=data,headers=headers))

    result_check=result_db_names_test.json()

    
    if('message' in result_check):

        if(result_check['message'])=='OK':

            errors_check=errors_check+"The database "+db_name_id_uri[i]['db_name']+" is working\n"
            html=html+"""
            <tr>
            <td>"""+str(i+1)+"""</td>
            <td>"""+db_name_id_uri[i]['db_name']+"""</td>
            <td>"""+"Working Perfectly!"+"""</td>

            </tr>"""






    else:
        if('errors' in (result_check)):
            errors_check=errors_check+"The database "+db_name_id_uri[i]['db_name']+" is not working error = "+str(result_check['errors'][0]['message']) + "\n"
            html=html+"""
            <tr>
            <td>"""+str(i+1)+"""</td>
            <td>"""+db_name_id_uri[i]['db_name']+"""</td>
            <td>"""+"is not working error = "+str(result_check['errors'][0]['message'])+"""</td>

            </tr>"""



html=html+"""
        </table>
    </body>
</html>
"""

print(db_name_id_uri)
print(errors_check)

# create message object instance


msg = MIMEMultipart('alternative')


message = errors_check
 
# setup the parameters of the message
password = "alienwarem15X"
msg['From'] = "siddharthdani10@gmail.com"
msg['To'] = "siddharthdani10@gmail.com"
msg['Subject'] = "DB_Healthcheck"
 
# add in the message body
msg.attach(MIMEText(message, 'plain'))
 
#create server
server = smtplib.SMTP('smtp.gmail.com: 587')
 
server.starttls()
 
# Login Credentials for sending the mail
server.login(msg['From'], password)
 
 
# send the message via the server.
#server.sendmail(msg['From'], msg['To'], msg.as_string())
 
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part2)

server.sendmail(msg['From'], msg['To'], msg.as_string())

server.quit()
 
print ("successfully sent email to %s:" % (msg['To']))