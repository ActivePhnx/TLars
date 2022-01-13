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
    r = requests.get(thing.format(date))
    print(r.status_code)
    if r.status_code == 404 or r.status_code == 400 or r.status_code == 503:
        r.raise_for_status()
    else:
        zip_content = io.BytesIO(r.content)
        zip_list = zipfile.ZipFile(zip_content).namelist()
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



for y in range(5):
    for m in range(11):
        for d in range(31):
            try:
                year = str(2016 + y)
                month = str(1 + m)
                day = str(1 + d)
                if m < 9:
                    month = "0" + month
                if d < 9:
                    day = "0" + day

                print("trying day" + day)
                get_html_text(year + "-" + month + "-" + day)
                time.sleep(.05)
            except requests.HTTPError:
               pass

