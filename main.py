from flask import Flask, render_template, request
from flask_mail import Mail, Message
import requests
import re

app = Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'dal.alghamdi92@gmail.com'
app.config['MAIL_PASSWORD'] = 'Dalia280678'
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





@app.route('/')
def Index():
    query = prefixquery + """
            SELECT (COUNT(?specimen) AS ?triple)
            WHERE { ?specimen rdfs:subClassOf <http://purl.obolibrary.org/obo/OBI_0001479>}
            """
    r = requests.get(url, params={'format': 'json', 'query': query})
    results = r.json()
    return render_template("index.html", data=results)


@app.route('/speciman')
def Speciman():
    query = prefixquery + """ 
                SELECT ?entity ?label
                WHERE {
                    ?entity rdfs:subClassOf obo:OBI_0001479 .
                    ?entity rdfs:label ?label .
                } """
    r = requests.get(url, params={'format': 'json', 'query': query})
    results = r.json()
    #print(results)
    return render_template("speciman.html", data=results)

@app.route('/SearchBySpeciman')
def SearchBySpeciman():
    select = str(request.args.get('speciman_name'))
    speciman_code = select.rsplit('/', 1)[-1]
    print("===> Speciman Code:", speciman_code)
    query = prefixquery + """
                    SELECT ?entity ?label
                    WHERE {
                        ?entity rdfs:subClassOf <http://purl.obolibrary.org/obo/""" + str(speciman_code) + """> .
                        ?entity rdfs:label ?label .
                    } """
    r = requests.get(url, params={'format': 'json', 'query': query})
    results = r.json()
    print(results)
    return render_template("specimanbysearch.html", data=results)

# SELECT ?predicate ?label ?object
# WHERE {
#    ?predicate ?object <http://purl.obolibrary.org/obo/OBI_0000070> .
#    ?predicate rdfs:label ?label .
# }


@app.route('/MoreInfoOfSpeciman')
def MoreInfoOfSpeciman():
    select = str(request.args.get('speciman_name'))
    speciman_code = select.rsplit('/', 1)[-1]
    print("===> Speciman Code:", speciman_code)
    query = prefixquery + """
                    SELECT ?predicate ?label ?object
                    WHERE {
                       ?predicate ?object <http://purl.obolibrary.org/obo/""" + str(speciman_code) + """> .
                       ?predicate rdfs:label ?label .
                    } """
    r = requests.get(url, params={'format': 'json', 'query': query})
    results = r.json()
    print(results)
    return render_template("more_info_of_speciman.html", data=results)


@app.route("/EmailSent", methods=['POST', 'GET'])
def EmailSent():
    if request.method == 'POST':
        name = request.form['name']
        institute = request.form['institute']
        email = request.form['email']
        summary = request.form['summary']
        question = request.form['question']
        print(name,email,institute,summary,question)
        msg = Message('Hello', sender = 'dal.alghamdi92@gmail.com', recipients = [email])
        msg.body = """<table><tr><td>Name:</td><td>""" + name + "</td></tr><tr><td>Institute:</td><td>""" + institute + """</td></tr><tr><td>Email:</td><td>""" + email + """</td></tr><tr><td>Summary:</td><td>""" + summary + """</td></tr><tr><td>Question:</td><td>""" + question + """</td></tr></table>"""
        mail.send(msg)
        return "Sent"


if __name__=="__main__":
    app.run(debug=True)