from flask import Flask, render_template, request
from waitress import serve
from functions import names_and_photos, get_QR_filename, get_photo_filename, list_of_seeds, list_of_generics, list_of_companies
from functions import update_database_list

app = Flask(__name__)

@app.route('/')
@app.route('/homepage')
def index():
    return render_template('homepage.html',seeds=list_of_seeds())

@app.route('/seed-info-page')
def seed_info_page():
    seed_type = request.args.get('seed-type').lower()

    matches = []
    file_names = []
    with open('static/seedList.txt', 'r') as file:
        for line in file:
            if line.split(":")[0] in seed_type:
                if len(line.split(":")) > 1:
                    varieties = line.split(":")[1]
                    varieties = varieties.split(",")

                    for variety in varieties:
                        item = variety + " " + line.split(":")[0]
                        matches.append(item)
                else:
                    matches.append(line)


    return render_template('seed-info-page.html', seed=seed_type.capitalize(), matches = names_and_photos(matches))

@app.route('/pdf-viewer')
def pdf_viewer():
    variety = request.args.get('variety').title() 
    pic_filename = get_photo_filename(variety)
    company = "Johnny's Seeds"
    date = "12/2024"

    return render_template('pdf-viewer.html', rows=10, columns=3, picture=pic_filename, variety=variety, company=company, date=date)

@app.route('/add-seed')
def add_seed_page():
    return render_template('add-seed.html',seeds=list_of_seeds(), generics=list_of_generics(), companies=list_of_companies())

@app.route('/confirm-new-entry')
def confirm_entry_page():
    #get info
    generic_seed = request.args.get('generic-seed').lower()
    specific_seed = request.args.get('specific-seed').lower()
    company = request.args.get('company').title()
    QR_link = request.args.get('QR-link')
    plant_image = request.args.get('fileUpload')

    #add entry to database
    update_database_list(generic_seed,specific_seed,company,QR_link,plant_image)

    seed_name = (specific_seed + generic_seed).title()

    #render template
    return render_template('confirm-new-entry.html',seed_name=seed_name)

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 8000)
    #serve(app, host="0.0.0.0", port=8000)