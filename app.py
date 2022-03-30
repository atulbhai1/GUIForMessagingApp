from flask import Flask, render_template, request, url_for, flash, redirect
import requests
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import *
from dominate.tags import img
from requests.structures import CaseInsensitiveDict
from requests_oauthlib import OAuth2
rootAPIURL = 'https://messagingappfastapi-atul.herokuapp.com'
logo = img(src="./static/img/logo.png" , height="50", width="200", style="margin-top:-15px")
topbar = Navbar(logo,
                View('View All Posts', 'showAllPosts'),
                View('Login', 'login'),
                View('Most Recent Message', 'latest'),
                View('Find a specific post by the ID', 'getAPost'),
                View('Vote', 'vote'))
nav = Nav()
nav.register_element('top', topbar)
app = Flask(__name__)
app.config['SECRET_KEY'] = '17bb05ad20765f49322692652f2bf6d761bf9wn29dm39aso'
Bootstrap(app)
security_auth_code = ''
postsToDisplay = []
postFilters = None
auth = None
@app.route('/', methods=('GET', 'POST'))
def showAllPosts():
    global postFilters
    if request.method == 'POST' and request.form.get('submit') == 'submit':
        try:
            limit = int(request.form['limit'])
        except Exception:
            flash('Please Ensure that the limit is an INTEGER!!!')
            return redirect(url_for('showAllPosts'))
        try:
            skip = int(request.form['skip'])
        except Exception:
            flash('Please ensure that skip is an INTEGER')
            return redirect(url_for('showAllPosts'))
        search = request.form['search']
        postFilters = {'limit': limit, 'skip': skip, 'search': search}
        return redirect(url_for('showAllPosts'))
    if postFilters is None:
        notFormattedPostsToDisplay = requests.get(url=rootAPIURL+'/posts')
    else:
        notFormattedPostsToDisplay = requests.get(url=rootAPIURL+'/posts', params=postFilters)
        postFilters = None
    ThePostsToDisplay = notFormattedPostsToDisplay.json()
    data=ThePostsToDisplay
    return render_template('showAllPosts.html', data=data)

@app.route('/login', methods=('GET', 'POST'))
def login():
    global security_auth_code, auth
    print('hi')
    print(request.method)
    if request.method == 'POST':
        print('hi')
        email = request.form['email']
        password = request.form['password']
        session = requests.Session()
        response = session.post(url=rootAPIURL+'/login', data={"username": email, "password":password})
        session.close()
        try:
            if not(int(response.status_code) - 200 < 100): raise Exception('This credential is not good')
            #auth = OAuth2(token=response.json())
            security_auth_code = response.json()['access_token']
            print(response.json())
            print('hello')
            flash('Logged in successfully')
            return redirect(url_for('showAllPosts'))
        except:
            flash('Check if your credentials are correct')
    return render_template('login.html')

@app.route('/latest', methods=['GET'])
def latest():
    result = requests.get(url=rootAPIURL+'/posts/latest')
    return render_template('latestPost.html', data=[result.json()])

@app.route('/aPost', methods=('GET', 'POST'))
def getAPost():
    global postsToDisplay
    if request.method == 'POST':
        try:
            THEid = int(request.form['ID'])
            returned = requests.get(url=rootAPIURL+f"/posts/{THEid}")
            if returned.status_code != 200:
                flash('A post with this ID could not be found')
                return redirect(url_for('getAPost'))
            postsToDisplay = returned.json()
            return redirect(url_for('getAPost'))
        except Exception:
            flash('Make sure the id is an integer')
    data = postsToDisplay
    postsToDisplay = None
    if not data:
        data = requests.get(url=rootAPIURL+'/posts/2').json()
    print([data])
    return render_template('showAPost.html', data=[data])

@app.route('/vote', methods=('GET', 'POST'))
def vote():
    global security_auth_code, auth
    if request.method == 'POST':
        if security_auth_code == '':
            flash('You have to be logged in to vote')
            return redirect(url_for('vote'))
        try:
            vote_dir = int(request.form['dir'])
            post_ID = int(request.form['id'])
        except Exception:
            flash('Please ensure that the vote direction is an integer and that the post ID is an integer!!!')
            return redirect(url_for('vote'))
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorize"] = f"Bearer {security_auth_code}"
        headers["Authenticate"] = f"Bearer {security_auth_code}"
        headers["Token"] = f"Bearer {security_auth_code}"
        session = requests.Session()
        returned = session.post(url=rootAPIURL+'/vote', params={"post_id": post_ID, "dir": vote_dir, "token": security_auth_code}, headers=headers, data={"token": security_auth_code, 'bearer': security_auth_code, "authorize": security_auth_code, "authenticate": security_auth_code}, )#auth=auth)
        print(returned.status_code, headers, returned.json(), security_auth_code)
        if int(returned.status_code) == 201:
            flash('Voted successfully!')
            return redirect(url_for('showAllPosts'))
        elif int(returned.status_code) == 401:
            flash('You have to be logged in to vote')
        elif returned:
            flash('A post with that ID wasn\'t found')
        else:
            flash('THIS SHOULD NOT BE SEEN!!!!')
    return render_template('vote.html')
nav.init_app(app)
app.run()