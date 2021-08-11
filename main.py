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
                PREFIX ngbo: <http://purl.obolibrary.org/obo/ngbo.owl#> """
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


@app.route('/speciman')
def Speciman():
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
    return render_template("speciman.html", data=results)


@app.route('/SearchBySpeciman')
def SearchBySpeciman():
    select = str(request.args.get('speciman_name'))
    speciman_code = select.rsplit('/', 1)[-1]
    print("===> Speciman Code:", speciman_code)
    user = session['user']
    if user == 'GUEST':
        sparql.setQuery(prefixquery + """
                            SELECT (COUNT(?label) AS ?total) 
                            WHERE {
                                ?entity a <http://purl.obolibrary.org/obo/""" + str(speciman_code) + """> .
                                ?entity rdfs:label ?label .
                            } """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        # r = requests.get(url, params={'format': 'json', 'query': query})
        # results = r.json()
        print(results)
        return render_template("countspecimanbysearch.html", data=results)

    else:
        sparql.setQuery(prefixquery + """
                                SELECT ?entity ?label
                                WHERE {
                                    ?entity a <http://purl.obolibrary.org/obo/""" + str(speciman_code) + """> .
                                    ?entity rdfs:label ?label .
                                } """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        # r = requests.get(url, params={'format': 'json', 'query': query})
        # results = r.json()
        print(results)
        return render_template("specimanbysearch.html", data=results)


@app.route('/checkguest')
def checkguest():
    session['user'] = 'GUEST'
    print(session['user'])
    return redirect('/speciman')

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
                ?x ngbo:userEmailId ?email
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
            return redirect('/speciman')
        else:
            message = "Invalid username and password"
            return render_template("login.html", message = message)


@app.route('/MoreInfoOfSpeciman')
def MoreInfoOfSpeciman():
    select = str(request.args.get('speciman_name'))
    speciman_code = select.rsplit('/', 1)[-1]
    print("===> Speciman Code:", speciman_code)
    sparql.setQuery(prefixquery + """
                    SELECT ?predicate ?label ?object
                    WHERE {
                       ?predicate ?object <http://purl.obolibrary.org/obo/""" + str(speciman_code) + """> .
                       ?predicate rdfs:label ?label .
                    } """)

    #r = requests.get(url, params={'format': 'json', 'query': query})
    #results = r.json()
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    return render_template("more_info_of_speciman.html", data=results)


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