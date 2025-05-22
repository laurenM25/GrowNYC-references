from PIL import Image
from werkzeug.utils import secure_filename
import boto3
import qrcode
import os
from datetime import datetime, timezone, timedelta
import requests
import pandas as pd
import warnings

# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

#checking time drift - DEBUGGING
# Local server time
print("Local UTC:", datetime.now(timezone.utc))

# AWS server time via HTTP Date header
response = requests.head('https://s3.amazonaws.com')
print("AWS Server time:", response.headers['Date'])


# Initialize boto3 S3 client (for remote storage of photos)
session = boto3.session.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

#check if properly fetched on Render
print(session.get_credentials().get_frozen_credentials())

s3 = session.client('s3')
BUCKET_NAME = 'grownyc-app-assets'

def generate_presigned_url(key, content_type, expiration=3600): #Not using - use presigned url 
    return s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': key,
            'ContentType': content_type
        },
        ExpiresIn=expiration
    )

def matches(seed_type, find_index_generic = False): #checking matches between user input and list 
    ornamental_generic = check_if_ornamental(seed_type)

    if isinstance(ornamental_generic,list):
        print("showing results for all ornamentals")
        all_specifics = []
        len_specifics = []
        for generic in ornamental_generic:
            all_specifics.extend(list_of_specifics(generic))
            len_specifics.append(len(list_of_specifics(generic)))
        return (all_specifics, ornamental_generic, len_specifics)
    elif ornamental_generic not in "" and isinstance(ornamental_generic,str):
        print(f"{seed_type} is ornamental, called '{ornamental_generic}'")
        if find_index_generic == True:
            return ornamental_generic, index_of_generic(ornamental_generic,use_full_name=True)
        return (list_of_specifics(ornamental_generic),ornamental_generic) #also return generic name
    
    #otherwise, check regular list of generics
    print("not considered ornamental")
    for generic in list_of_generics():
        if generic.lower() in seed_type.lower():
            #success
            if find_index_generic == True:
                return generic, index_of_generic(generic)
            return list_of_specifics(generic)
    else:
        print(f"Could not find the generic seed variety in the inputted name '{seed_type}'")
        #check for keyword in literally any of the varieties
        if desperate_match_check(seed_type) != []:
            print("Desperate match successful")
            print(desperate_match_check(seed_type))
            return desperate_match_check(seed_type)
        print("Desperate match check unsuccessful. Returning None.")
        return None

def desperate_match_check(keyword): #check for keyword in literally any of the varieties
    desperate_list = []
    for variety in list_of_seeds():
        print(f"comparing {keyword} with {variety}")
        if keyword.lower().strip() in variety.lower():
            print(f"yes, {keyword} is in '{variety}")
            desperate_list.append(variety)
    return desperate_list

def check_if_ornamental(seed):
    all_ornamentals = ["Kale, Ornamental", "Grasses, Ornamental", "Cress, Ornamental", "Basil, Ornamental"]
    if "ornamental" in seed.lower():
        print("yup, it's ornamental")
        ornamentals = ["kale", "grasses", "cress", "basil"]
        return next((f"{orn_type.capitalize()}, Ornamental" for orn_type in ornamentals if orn_type in seed.lower()), all_ornamentals) 
    else:
        print(f"nope, {seed} is not ornamental")
        return ""

def index_of_generic(string, use_full_name = False):
    for i,generic in enumerate(list_of_generics()):
        if use_full_name == True:
            if generic.lower() == string.lower(): #only accept an exact match
                return i
        elif generic.lower() in string.lower():
            return i
        
def index_of_specific(generic, specific):
    for i,string in enumerate(list_of_specifics(generic)):
        if string.lower() in specific.lower():
            return i
        
    print(f"'{string}' not found in the specific varieties of '{generic}'")
        
def locate_generic_specific_coords(string): #from just its full name -- returns (generic, specific)
    generic, generic_index = matches(string, find_index_generic=True)
    print("Line 74:", generic)
    specific_index = index_of_specific(generic, string)

    print("indices: ", generic_index, "and", specific_index)
    return generic_index,specific_index
    
def names_and_photos(matches, specified_generic = None, len_multi_speci_lists = None): # -> {"plant-name": [QR, photo]}
    my_dict = {}
    if matches == []:
        print("no matches, so returning None for photos")
        return None
    print("names_and_photos() def, type:",type(matches)) 
    print(matches)
    if not isinstance(matches, list):
        print("Incorrect: the matches variable must be type list.")
        return

    if specified_generic is not None:
        if isinstance(specified_generic,list): #if I have multiple generic varieties, get multiple indices
            generic_index = [index_of_generic(gen1,use_full_name=True) for gen1 in specified_generic]
            #special multi indicies, iterate through matches paying attential to various indicies
            specific_index = 0
            threshold = 0
            for i,match in enumerate(matches):
                #obtain QR and photo
                if specific_index >= len_multi_speci_lists[threshold]:
                    threshold += 1
                    specific_index = 0
                g_index = generic_index[threshold]
                my_dict[match] = [retrieve_photo(g_index,specific_index,"QR-url"),retrieve_photo(g_index,specific_index,"plant-photo-url")]
                specific_index += 1
            return my_dict
        else:
            generic_index = index_of_generic(specified_generic,use_full_name=True)
    else:
        generic_index = index_of_generic(matches[0])

    #just one generic index
    specific_index = 0
    for match in matches:
        #obtain QR and photo
        my_dict[match] = [retrieve_photo(generic_index,specific_index,"QR-url"),retrieve_photo(generic_index,specific_index,"plant-photo-url")]
        specific_index += 1
    return my_dict

def get_QR_filename(variety_name): #not in use rn - input a string, output a string
    variety_name = variety_name.strip().lower()
    return variety_name.replace(" ", "-") + "-QR.png"

def create_qr_code(data, filename):
    if not data.startswith("http://") and not data.startswith("https://"):
        raise ValueError("Invalid link — must start with http:// or https://")
    
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # Add data to the QR code
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Make sure the directory exists
    save_path = os.path.join('static', 'icons')
    os.makedirs(save_path, exist_ok=True)

    #save to AWS
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    s3_key = f'icons/{filename}'
    presigned_url = generate_presigned_url(s3_key, 'image/png')

    # Upload via HTTP PUT
    response = requests.put(
        presigned_url,
        data=buf,
        headers={'Content-Type': 'image/png'}
    )

    if response.status_code != 200:
        raise Exception(f"Failed to upload QR code: {response.text}")

    return f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/icons/{filename}"

def get_photo_filename(variety_name):
    variety_name = variety_name.strip().lower()
    return variety_name.replace(" ", "-") + ".jpg"

def list_of_seeds(): #for the drop-down list on homepage, all seed varieties
    seeds = []

    for generic in list_of_generics():
        specifics = list_of_specifics(generic)
        seeds.extend(specifics)

    return seeds

def list_of_generics():
    seed_df = add_scraped_to_seed_list()
    return seed_df["name"]

def row_generic(generic):
    seed_df = add_scraped_to_seed_list()
    seed_df = seed_df.set_index("name")
    return seed_df.loc[generic]

def list_of_specifics(generic):
    row = row_generic(generic)
    l = []
    for i,dict in enumerate(row["specific-varieties"]):
        if isinstance(dict, list):
            dict = dict[0]
        variety = dict["variety-name"].replace(generic,"").strip()
        variety = variety + " " + generic
        l.append(variety)
    return l

def list_of_companies():
    companies = ["Johnny's Seeds", "Hudson Valley Seed"]

    return companies

def save_feedback(str):
    with open("static/feedback.txt", 'w') as f:
        f.write(str)
    with open("static/feedback.txt", 'rb') as f:
        s3_key = f'feedback/feedback-{datetime.now(timezone.utc)}.txt'
        presigned_url = generate_presigned_url(s3_key, 'text/plain')
        response = requests.put(
            presigned_url,
            data=f,
            headers={'Content-Type': 'text/plain'}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to upload text file: {response.text}")

def update_database_list(generic, specific, company, QR_link, image): #not in use
    name = specific + " " + generic
    image_name = get_photo_filename(name)
    QR_name = get_QR_filename(name)

    #create QR 
    create_qr_code(QR_link,QR_name)

    save = save_user_input_img(image_name,image)

    #now save name to file
    with open('static/seedList.txt', 'r+') as file:
        lines = file.readlines()  # Read all lines from the file

        matching_line = next((line for line in lines if line.split(":")[0].strip().lower() == generic.lower()), None)

        if matching_line:
            parts = matching_line.strip().split(":")
            varieties = parts[1].strip()
            # If the specific variety isn't already in the list, append it
            if specific.lower() not in varieties.lower():
                if len(varieties) > 1:
                    parts[1] = varieties + ", " + specific
                else:
                    parts[1] = specific
                # Update the line in the list
                updated_line = ":".join(parts) + "\n"
                lines[lines.index(matching_line)] = updated_line
        else:
            #  no matching line is found --> create a new line and append it
            lines.append(f"{generic}: {specific}\n")
        
        #update file with new lines
        file.seek(0)  # cursor moves back to the start of the file
        file.writelines(lines)  #add modified content back
        upload_txt_to_s3('static/seedList.txt')

    #DEAL WITH COMPANY LATER --> johnny default, but if Hudson, need that to reflect in filename

def save_user_input_img(filepath, file): #not in use

    if file:
        filename = secure_filename(filepath)
        s3_key = f'icons/{filename}'
        presigned_url = generate_presigned_url(s3_key, file.content_type)
        response = requests.put(
            presigned_url,
            data=file,
            headers={'Content-Type': file.content_type}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to upload image: {response.text}")
        return f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/icons/{filename}"
    return None

def upload_txt_to_s3(local_path): # not in use. update txt file in S3 bucket
    with open(local_path, 'rb') as f:
        s3_key = 'seedList.txt'
        presigned_url = generate_presigned_url(s3_key, 'text/plain')
        response = requests.put(
            presigned_url,
            data=f,
            headers={'Content-Type': 'text/plain'}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to upload text file: {response.text}")

def retrieve_photo(generic_i,specific_i,photo_type):
    if photo_type != "QR-url" and photo_type != "plant-photo-url":
        return f"Error retrieving photo: Incorrect photo_type was specified. You said {photo_type} but it needs to be QR-url or plant-photo-url"
    seed_df = add_scraped_to_seed_list()

#QR code won't work right now. It is just a link.
    return seed_df["specific-varieties"][generic_i][specific_i][photo_type]

def add_scraped_to_seed_list():
    # convert to table
    seed_df = pd.read_csv("scraped_seeds.csv")
    seed_df["name"] = seed_df["name"].str.replace(r'\s*\(.*?\)', '', regex=True)

    seed_df["specific-varieties"] = [eval(variety) for variety in seed_df["specific-varieties"]]
    #remove duplicate specifics
    for i, row in enumerate(seed_df["specific-varieties"]):
        running_list = []
        list_dicts = []
        for d in row:
            d["variety-name"] = strip_punctuation(d["variety-name"],"'")
            if d["variety-name"] not in running_list:
                running_list.append(d["variety-name"])
                list_dicts.append(d)
        seed_df["specific-varieties"][i] = list_dicts
    return seed_df

def strip_punctuation(str, regex):
    return str.strip(f"{regex}")
#print(list_of_generics().to_list())
#print(list_of_seeds())