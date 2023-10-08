from flask import Flask, render_template, request, redirect, send_file
import os
import pandas as pd
from verification_dict import create_verification_dict, import_csv
import edit_firebase
import time
import datetime
import json
import shutil
edit_firebase.firebase_init()

"----------"

def epoch_to_datetime(epoch):
    # Convert epoch to datetime
    dt = datetime.datetime.fromtimestamp(epoch)

    # Set the time zone to GMT+8
    gmt8 = datetime.timezone(datetime.timedelta(hours=8))
    dt_with_timezone = dt.replace(tzinfo=gmt8)

    # Convert to GMT+8 and remove time zone offset
    dt_without_timezone = dt_with_timezone.astimezone(datetime.timezone.utc).replace(tzinfo=None)

    return dt_without_timezone

def check_csv_format(file_path, file_name, unique_column):
    data = import_csv(file_path, file_name)
    s = set()
    for recod in data:
        s.add(recod[unique_column])
    return len(s) == len(data)

def check_duplicated_item(table, uniqle_column):
    unique_items = set()
    duplicate_items = []

    for record in table:
        if record[uniqle_column] in unique_items:
            duplicate_items.append(record[uniqle_column])
        else:
            unique_items.add(record[uniqle_column])
    
    return duplicate_items

def check_event_name_unique(event_name):
    with open(f"events/events_list.json", mode="r", encoding="utf-8") as file:
        content = json.loads(file.read())
    unique = True
    for record in content:
        if record["name"] == event_name:
            unique = False
    return unique

def update_firebase(file_path, file_name, event_name):
    with open(f"{file_path}/{file_name}", mode="r", encoding="utf-8") as file:
        content = json.loads(file.read())
    edit_firebase.save(f"/{event_name}", content)

def update_events_list(new_event_name):
    with open(f"events/events_list.json", mode="r", encoding="utf-8") as file:
        content = json.loads(file.read())

    content.append({"name": new_event_name, "time": time.time()})
    print(json.dumps(content))

    with open(f"events/events_list.json", mode="w", encoding="utf-8") as file:
        file.write(json.dumps(content))


"----------"

app = Flask(__name__)


@app.route('/test')
def test():
    return render_template('/upload_test2.html')

@app.route('/')
def index():
    return redirect('/home')

@app.route('/home')
def home():
    with open(f"events/events_list.json", mode="r", encoding="utf-8") as file:
        data = json.loads(file.read())

    sorted_data = sorted(data, key=lambda x: x['time'], reverse=True)

    for i in range(len(sorted_data)):
        sorted_data[i]["time"] = epoch_to_datetime(sorted_data[i]["time"])

    return render_template('home.html', data=sorted_data)

@app.route('/download')
def download():
    event_name = request.args.get('event')
    file_path = f"events/{event_name}/mail_merge_csv.csv"
    return send_file(file_path, as_attachment=True)



@app.route('/delete_confirm')
def delete_confirm():
    event_name = request.args.get('event')
    return render_template('delete_confirm.html', event=event_name)


@app.route('/delete')
def delete():
    event_name = request.args.get('event')

    # delete event list

    with open(f"events/events_list.json", mode="r", encoding="utf-8") as file:
        content = json.loads(file.read())

    for i in range(len(content)):
        if content[i]["name"] == event_name:
            content.pop(i)
    
    with open(f"events/events_list.json", mode="w", encoding="utf-8") as file:
        file.write(json.dumps(content))

    # delete foler
    shutil.rmtree(f"events/{event_name}")

    # delete firebase
    edit_firebase.delete("/", event_name)

    
    
    return redirect('/home')


@app.route('/upload', methods=['GET'])
def upload_get():
    return render_template('upload.html', valid="---", table=None, duplicated_item=None)

@app.route('/upload', methods=['POST'])
def upload_post():
    event_name = request.form['TextInput']
    file = request.files['FileInput']

    if not check_event_name_unique(event_name):
        return render_template('upload.html', valid="Event name used", table=None, duplicated_item=None)
    elif not file:
        return render_template('upload.html', valid="No file uploaded", table=None, duplicated_item=None)
    else:
        
        hashed_file_name = f"{hash(str(time.time()))}.csv"
        
        file.save(os.path.join("uploaded_files", f"{hashed_file_name}"))
        if not check_csv_format("uploaded_files", hashed_file_name, 0):
            table = import_csv("uploaded_files", hashed_file_name)
            duplicated_item = check_duplicated_item(table, 0)
            print(table)
            return render_template('upload.html', valid="File not in valid format", table=table, duplicated_item=duplicated_item)
        else:
            file_name = "raw.csv"
            file_path = f"events/{event_name}"

            # update events_list.json
            update_events_list(event_name)

            # create event folder with event name
            os.mkdir(file_path)
            with open(f"uploaded_files/{hashed_file_name}", encoding="utf-8") as file_old:
                with open(f"{file_path}/{file_name}", mode="w", encoding="utf-8") as file_new:
                    file_new.write(file_old.read())

            # save csv for mail merge AND verificario dict (for firebase)
            create_verification_dict(file_path, file_name, 0, 1, 2, "verification_dict", "mail_merge_csv")

            # upload verificario dict (for firebase)
            update_firebase(file_path, "verification_dict.json", event_name)

            return redirect('/home')


if __name__ == '__main__':
    app.run(debug=True)