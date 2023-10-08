import csv
import json

def import_csv(file_path, file_name):
    with open(f"{file_path}/{file_name}", encoding="utf-8") as f:
        result = list(csv.reader(f))
    return result

def create_hash_dict(l, unique_column, name_column, number_column):
    hash_dict = {}
    for i in l:
        string = i[unique_column]
        hash_dict[hash(string)] = {"name": i[name_column], "number": i[number_column], "unique": i[unique_column]}
    return hash_dict

def check_unique(hash_dict):
    s = set()
    for keys, values in hash_dict.items():
        s.add(keys)
    return len(s) == len(hash_dict)


def create_verification_dict_from_hash_dict(hash_dict, file_path, saved_file_name):
    verification_dict = {} 
    for keys, values in hash_dict.items():
        verification_dict[keys] = {"name":values["name"], "number":values["number"], "count":0}
    
    with open(f"{file_path}/{saved_file_name}.json", "w") as f:
        f.write(json.dumps(verification_dict))



def create_mail_merge_csv_from_hash_dict(info, unique_column, hash_dict, file_path, saved_file_name):
    mail_merge_csv = info

    mail_merge_csv[0].append("qrcode")
    
    for i in range(1, len(mail_merge_csv)):
      for keys, values in hash_dict.items():
            if mail_merge_csv[i][unique_column] == values["unique"]:
                mail_merge_csv[i].append(f"https://chart.googleapis.com/chart?cht=qr&chs=500x500&chl={keys}") # https://chart.googleapis.com/chart?cht=qr&chs=500x500&chl=07b3ff19a2be2d7162f2af620770edab0819889e    
    
    with open(f"{file_path}/{saved_file_name}.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(mail_merge_csv) 


def create_verification_dict(file_path, file_name, unique_column, name_column, number_column, saved_verification_dict_name, saved_mail_merge_csv_name):
    info = import_csv(file_path, file_name)
    hash_dict = create_hash_dict(info, unique_column, name_column, number_column)
    
    if not check_unique(hash_dict):
        return "The hashing has repeted, try again"
    
    vd = create_verification_dict_from_hash_dict(hash_dict, file_path, saved_verification_dict_name)
    vd = create_mail_merge_csv_from_hash_dict(info, unique_column, hash_dict, file_path, saved_mail_merge_csv_name)

