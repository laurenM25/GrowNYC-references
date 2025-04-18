from flask import Flask, render_template, request
from waitress import serve
from functions import names_and_photos, get_QR_filename, get_photo_filename, list_of_seeds, list_of_generics, list_of_companies
from functions import update_database_list

app = Flask(__name__)

@app.route('/')
@app.route('/homepage')
def index():
    return render_template('homepage.html',seeds=list_of_seeds(), companies=list_of_companies())

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


    return render_template('seed-info-page.html', seed=seed_type.capitalize(), matches = names_and_photos(matches),companies=list_of_companies())

@app.route('/pdf-viewer')
def pdf_viewer():
    variety = request.args.get('variety').title() 
    pic_filename = get_photo_filename(variety)
    company = request.args.get('company')
    date = request.args.get('month') + " " +  request.args.get("year")

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

    #confirm no blank inputs
    inputs = [generic_seed,specific_seed,company,QR_link]
    if any(len(ele)==0 for ele in inputs):
        expl="Missing an input. Make sure to fill out all areas on the form."
        return render_template('error.html', error="Missing value", expl=expl)

    plant_image = request.args.get('fileUpload')

    #add entry to database
    update = update_database_list(generic_seed,specific_seed,company,QR_link,plant_image)
    if isinstance(update,str):
        expl = "An error occured when updating the database list with the image. System error."
        return render_template('error.html', error=update, expl=expl)

    seed_name = (specific_seed + generic_seed).title()

    #render template
    return render_template('confirm-new-entry.html',seed_name=seed_name)

if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 8000)
    #serve(app, host="0.0.0.0", port=8000)