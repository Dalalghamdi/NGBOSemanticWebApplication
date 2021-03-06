from functools import wraps

from flask import Flask, render_template, request, redirect, session, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON
from flask_mail import Mail, Message
import requests
import re

app = Flask(__name__)
app.secret_key = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'biobankingportal@gmail.com'
app.config['MAIL_PASSWORD'] = 'NGBO121212!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

prefixquery = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX obo: <http://purl.obolibrary.org/obo/>
                PREFIX ngbo: <http://purl.obolibrary.org/obo/ngbo.owl/> """


url = 'http://localhost:3030/NGBO/sparql'

sparql = SPARQLWrapper("http://localhost:7200/repositories/NGBO")


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap

def start_session(user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    return jsonify(user), 200


@app.route('/index')
def Index():
    sparql.setQuery(prefixquery + """
            SELECT (COUNT(?specimen) AS ?triple)
            WHERE { ?specimen rdfs:subClassOf <http://purl.obolibrary.org/obo/OBI_0001479>}
            """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #r = requests.get(url, params={'format': 'json', 'query': query})
    #results = r.json()
    return render_template("index.html", data=results)

@app.route('/RequestPage')
def RequestPage():
    return render_template("requestpage.html")


@app.route('/specimen')
def Specimen():
    sparql.setQuery(prefixquery + """ 
                SELECT ?entity ?label
                WHERE {
                    ?entity rdfs:subClassOf obo:OBI_0001479 .
                    ?entity rdfs:label ?label .
                } """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #r = requests.get(url, params={'format': 'json', 'query': query})
    #results = r.json()
    #print(results)
    return render_template("specimen.html", data=results)


@app.route('/SearchBySpecimen')
def SearchBySpecimen():
    select = str(request.args.get('specimen_name'))
    specimen_code = select.rsplit('/', 1)[-1]
    print("===1> Specimen Code:", specimen_code)
    user = session['user']
    if user == 'GUEST':
        sparql.setQuery(prefixquery + """
                            SELECT (COUNT(?label) AS ?total) 
                            WHERE {
                                ?entity a <http://purl.obolibrary.org/obo/""" + str(specimen_code) + """> .
                                ?entity rdfs:label ?label .
                            } """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        # r = requests.get(url, params={'format': 'json', 'query': query})
        # results = r.json()
        print(results)
        return render_template("countspecimenbysearch.html", data=results)

    else:
        sparql.setQuery(prefixquery + """
                                SELECT ?entity ?label
                                WHERE {
                                    ?entity a <http://purl.obolibrary.org/obo/""" + str(specimen_code) + """> .
                                    ?entity rdfs:label ?label .
                                } """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        # r = requests.get(url, params={'format': 'json', 'query': query})
        # results = r.json()
        #print(results)
        return render_template("specimenbysearch.html", data=results)


@app.route('/checkguest')
def checkguest():
    session['user'] = 'GUEST'
    print(session['user'])
    return redirect('/specimen')

# SELECT ?predicate ?label ?object
# WHERE {
#    ?predicate ?object <http://purl.obolibrary.org/obo/OBI_0000070> .
#    ?predicate rdfs:label ?label .
# }
@app.route('/')
def Login():
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username',None)
    session.clear()
    return redirect('/')


@app.route('/auth', methods=['POST'])
def Auth():
    if request.method == 'POST':
        uname = request.form['username']
        upass = request.form['password']

        print(uname,upass)
        sparql.setQuery(prefixquery + """
            select (count(?uid) as ?id)
            where
            {
                ?x a ngbo:User .
                ?x ngbo:userId ?uid .
                ?x ngbo:userName ?uname .
                ?x ngbo:userPassword ?upwd .
                ?x ngbo:userEmailId ?email .
                Filter(?uname = '""" + uname + """' && ?upwd = '""" + upass + """')
            }""")
        #r = requests.get(url, params={'format': 'json', 'query': query})
        #results = r.json()
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for row in results['results']['bindings']:
            count = row['id']['value']

        if int(count) > 0:
            session['user'] = uname
            return redirect('/specimen')
        else:
            message = "Invalid username and password"
            return render_template("login.html", message = message)


@app.route('/DetailsOfSpecimen')
def DetailsOfSpecimen():
    sparql.setQuery(prefixquery + """ 
            SELECT ?bloodspecimenlabel ?biobanklabel ?libraryPreprationlabel ?LibraryPreprationProtocollabel
            ?LibraryPreprationKitlabel ?Sequencingdevicelabel ?availableSequencingDatalabel ?FileFormatlabel
            WHERE{
            
            ?bloodspecimen a obo:OBI_0000655 .
            ?bloodspecimen rdfs:label ?bloodspecimenlabel .
            
            ?biobank a obo:OMIABIS_0000000 .
            ?biobank rdfs:label ?biobanklabel .
                
            ?libraryPrepration a obo:OBI_0000711 .   
            ?libraryPrepration rdfs:label ?libraryPreprationlabel . 
                
            ?LibraryPreprationProtocol a ngbo:NGBO_6000276 .   
            ?LibraryPreprationProtocol rdfs:label ?LibraryPreprationProtocollabel .
                
            ?LibraryPreprationKit a ngbo:NGBO_6000255 .
            ?LibraryPreprationKit rdfs:label ?LibraryPreprationKitlabel .
                
            ?Sequencingdevice a obo:OBI_0400103 .
            ?Sequencingdevice rdfs:label ?Sequencingdevicelabel .
                
            ?availableSequencingData a obo:OBI_0001573 .
            ?availableSequencingData rdfs:label ?availableSequencingDatalabel .
                
            ?FileFormat a ngbo:NGBO_6000003 .
            ?FileFormat rdfs:label ?FileFormatlabel .
                
            ?bloodspecimen obo:BFO_0000050 ?biobank .
            ?libraryPrepration obo:OBI_0000293 ?bloodspecimen .
            ?libraryPrepration obo:STATO_0000102 ?LibraryPreprationProtocol .
            ?libraryPrepration obo:OBI_0000293 ?LibraryPreprationKit .
            ?availableSequencingData obo:IAO_0000136 ?bloodspecimen .
            ?FileFormat obo:IAO_0000136 ?availableSequencingData .
            
            }
            """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # r = requests.get(url, params={'format': 'json', 'query': query})
    # results = r.json()
    print("Detail Relationship===>",results)
    return render_template("details_of_specimen.html", data=results)


@app.route('/MoreInfoOfSpecimen')
def MoreInfoOfSpecimen():
    print(request.args.get('chkbloodspecimen'))
    select = str(request.args.get('chkbloodspecimen'))
    specimen_code = select[-4:]
    print("===> Specimen Code:", specimen_code)
    sparql.setQuery(prefixquery + """
                     SELECT ?bloodspecimenlabel ?biobanklabel ?libraryPreprationlabel ?LibraryPreprationProtocollabel
            ?LibraryPreprationKitlabel ?Sequencingdevicelabel ?availableSequencingDatalabel ?FileFormatlabel
            WHERE{
            
            ?bloodspecimen a obo:OBI_0000655 .
            ?bloodspecimen rdfs:label ?bloodspecimenlabel .
            
            ?biobank a obo:OMIABIS_0000000 .
            ?biobank rdfs:label ?biobanklabel .
                
            ?libraryPrepration a obo:OBI_0000711 .   
            ?libraryPrepration rdfs:label ?libraryPreprationlabel . 
                
            ?LibraryPreprationProtocol a ngbo:NGBO_6000276 .   
            ?LibraryPreprationProtocol rdfs:label ?LibraryPreprationProtocollabel .
                
            ?LibraryPreprationKit a ngbo:NGBO_6000255 .
            ?LibraryPreprationKit rdfs:label ?LibraryPreprationKitlabel .
                
            ?Sequencingdevice a obo:OBI_0400103 .
            ?Sequencingdevice rdfs:label ?Sequencingdevicelabel .
                
            ?availableSequencingData a obo:OBI_0001573 .
            ?availableSequencingData rdfs:label ?availableSequencingDatalabel .
                
            ?FileFormat a ngbo:NGBO_6000003 .
            ?FileFormat rdfs:label ?FileFormatlabel .
                
            ?bloodspecimen obo:BFO_0000050 ?biobank .
            ?libraryPrepration obo:OBI_0000293 ?bloodspecimen .
            ?libraryPrepration obo:STATO_0000102 ?LibraryPreprationProtocol .
            ?libraryPrepration obo:OBI_0000293 ?LibraryPreprationKit .
            ?availableSequencingData obo:IAO_0000136 ?bloodspecimen .
            ?FileFormat obo:IAO_0000136 ?availableSequencingData .
            FILTER regex(?bloodspecimenlabel, '"""+ specimen_code +"""', "i")
            } """)

    #r = requests.get(url, params={'format': 'json', 'query': query})
    #results = r.json()
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    return render_template("more_info_of_specimen.html", data=results)


@app.route("/EmailSent", methods=['POST', 'GET'])
def EmailSent():
    if request.method == 'POST':
        print("==> Hi")
        name = request.form['name']
        institute = request.form['institute']
        email = request.form['email']
        summary = request.form['summary']
        question = request.form['question']
        print(name,email,institute,summary,question)
        msg = Message('Hello', sender = 'biobankingportal@gmail.com', recipients = [email])
        msg.body = """Name: """ +name+"\nInstitute: """+institute+"""\nEmail: """+email+"""\nSummary: """+summary+"""Question: """+question+"""."""
        mail.send(msg)
    return "Sent"


if __name__=="__main__":
     app.run(debug=True)