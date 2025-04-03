from PIL import Image

def names_and_photos(matches):
    my_dict = {}

    for match in matches:
        match = match.strip()
        f1 = match.replace(" ", "-") + "-QR.png"
        f2 = match.replace(" ", "-") + ".jpg"
        my_dict[match] = [f1,f2]

    #my_dict = {"black cherry tomato": ["black-cherry-tomato-QR.png", "black-cherry-tomato.jpg"], "chiba green soybean": ["chiba-green-soybean-QR.png", "chiba-green-soybean.jpg"]}
    return my_dict

def get_QR_filename(variety_name): #input a string, output a string
    variety_name = variety_name.strip().lower()
    return "static/icons/" + variety_name.replace(" ", "-") + "-QR.png"

def get_photo_filename(variety_name):
    variety_name = variety_name.strip().lower()
    return "static/icons/" + variety_name.replace(" ", "-") + ".jpg"

def list_of_seeds(): #for the drop-down list on homepage
    seeds = []

    with open('static/seedList.txt', 'r') as file:
        for line in file:
            if len(line.split(":")) > 1:
                varieties = line.split(":")[1]
                varieties = varieties.split(",")

                for variety in varieties:
                    item = variety.strip() + " " + line.split(":")[0]
                    seeds.append(item)
            else:
                seeds.append(line)

    return seeds

def list_of_generics():
    seeds = []

    with open('static/seedList.txt', 'r') as file:
        for line in file:
            seeds.append(line.split(":")[0])

    return seeds

def list_of_companies():
    companies = ["Johnny's Seeds", "Hudson Valley Seed"]

    return companies

def update_database_list(generic, specific, company, QR, image): 
    name = specific + generic
    image_name = get_photo_filename(name)
    QR_name = get_QR_filename(name)

    save = save_user_input_img(image_name,image)
    if isinstance(save,str):
        if save == "Error":
            return "General Error"
        else:
            return "File Not Found Error"
    #DEAL WITH COMPANY LATER --> johnny default, but if Hudson, need that to reflect in filename


def create_QR(link_for_QR):
    #create QR, save to icons
    return

def save_user_input_img(filepath, content):

    try:
        img = Image.open(content)
        img.save(filepath)
    except FileNotFoundError:
        return "FileNotFoundError"
    except:
        return "Error"

    #fix later, need POST, etc.