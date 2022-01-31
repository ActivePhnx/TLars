import requests
import zipfile
import datetime as dt
import io
import lxml.html as html
import sqlite3
import time


#D = dt.date.today() - dt.timedelta(days=2)


def get_html_text(date):
    print(date)
    thing = "https://www.govinfo.gov/link/crec/latest?link-type=zip&publishdate=" + date
    print(thing.format(date))
    r = requests.get(thing.format(date)) #Don't think I need .format() clause
    print(r.status_code)
    if r.status_code == 404 or r.status_code == 400:
        r.raise_for_status()
    elif r.status_code == 503 or r.status_code == 502:
        print("Adding to error")
        add_to_error(date)
        r.raise_for_status()
    else:
        zip_content = io.BytesIO(r.content)
        try:
            zip_list = zipfile.ZipFile(zip_content).namelist()
        except zipfile.BadZipFile:
            add_to_error(date)
            r.raise_for_status()
        zip_read = []
        for i in zip_list:
            if ".htm" in i:
                zip_read.append(zipfile.ZipFile(zip_content).read(str(i)))
        for i in range(len(zip_read)):
            html_data = html.fromstring(zip_read[i]).text_content()
            add_to_db(html_data, date)


def add_to_db(html_data, date):
    conn = sqlite3.connect('crec.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE if not exists crec
                (id INTEGER PRIMARY KEY, html_data TEXT UNIQUE,
                 UTC DATE)''')

    cur.execute('''
              INSERT or IGNORE INTO crec VALUES
              (?, ?, ?)''', (None, html_data, date))


    conn.commit()
    conn.close()

def add_to_error(date):
    conn = sqlite3.connect('error.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE if not exists error
                (id INTEGER PRIMARY KEY,
                 UTC DATE)''')

    cur.execute('''
              INSERT or IGNORE INTO error VALUES
              (?, ?)''', (None, date))
    print("Added " + date)
    conn.commit()
    conn.close()



for y in range(6):
    for m in range(12):
        for d in range(31):
            try:
                year = str(2016 + y)
                month = str(1 + m)
                day = str(1 + d)
                if m < 9:
                    month = "0" + month
                if d < 9:
                    day = "0" + day

                get_html_text(year + "-" + month + "-" + day)
                time.sleep(.1)
            except requests.HTTPError:
               pass



""" Testing Error db
for y in range(6):
    for m in range(12):
        for d in range(31):
            year = str(2016 + y)
            month = str(1 + m)
            day = str(1 + d)
            if m < 9:
                month = "0" + month
            if d < 9:
                day = "0" + day
                
            add_to_503(year + "-" + month + "-" + day)
"""
                
