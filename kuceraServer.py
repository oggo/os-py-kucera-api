#!/usr/bin/env python
# encoding: utf-8
'''kuceraServer is the server side application to support the kucera website. 
@author:     oggo
@copyright:  1998 c ivanov Consulting Inc.'''

import sys
import json
import os
from functools import wraps
from datetime import datetime
from flask import Flask, flash, render_template, redirect, request, Response
from flask_sqlalchemy import SQLAlchemy
from _ast import TryExcept
from symbol import try_stmt

app= Flask(__name__)
app.secret_key = 'kucera_very_secret_key_zzzhghrtebrr87011'
mysqlUri= 'mysql://oggo:taini4ka@oggo.mysql.pythonanywhere-services.com/oggo$kuceradb'
#mysqlUri= 'mysql://kucera_tech_1:taini4ka@{}/kuceradb'.format(os.environ.get('MYSQL_SERVICE_HOST'))
#mysqlUri= 'mysql://kucera_tech_1:taini4ka@{}:{}/kuceradb'.format(os.environ.get('MYSQL_SERVICE_HOST'), os.environ.get('MYSQL_SERVICE_PORT'))
print 'DEBUG: mysqlUri is: {}'.format(mysqlUri)
app.config['SQLALCHEMY_DATABASE_URI'] = mysqlUri
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://adminqpXQxYv:C5yZDCjUwZaU@127.8.30.2/python'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:<put the right one>@localhost/python'
db= SQLAlchemy(app)
reload(sys)
sys.setdefaultencoding('utf-8')

users = {
    "kucera": "kucera",
    "admin": "dianka"
}

def checkAuth(pUsername, pPwd):
  """This function is called to check if a username / password combination is valid."""
  if pUsername in users:
    return pPwd == users.get(pUsername)

  return False


def authenticate(pReason):
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    , 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requiresAuth(pUsername=None):
  def decorator(f):
    @wraps(f)
    def decorated(*args, **kwargs):
      auth = request.authorization
      if not auth:
        return authenticate('You have to login')
      if None != pUsername and auth.username != pUsername:
        return authenticate('You have to login with proper user')
      if not checkAuth(auth.username, auth.password):
        return authenticate('You have to login with proper credentials')
      return f(*args, **kwargs)
    return decorated
  return decorator

#Models
class Article(db.Model):
  id= db.Column(db.Integer, primary_key=True)
  htmlId= db.Column(db.String(100))
  title = db.Column(db.String(80))
  body = db.Column(db.Text)
  created= db.Column(db.DateTime, default=datetime.utcnow)
  lastUpdated= db.Column(db.DateTime, default=datetime.utcnow)

  def __init__(self, pTitle, pHtmlId, pBody, pCreated, pLastUpdated, pId= None):
    self.id = pId
    self.title = pTitle
    self.htmlId= pHtmlId
    self.body = pBody
    self.created= pCreated
    self.lastUpdated= pLastUpdated

#internal utils
def __getResponse(pBase, pStatus):
  resp= Response(pBase, pStatus)
  headers= resp.headers
  try:
    print "DEBUG: request.environ['HTTP_ORIGIN'] is: {}".format(request.environ['HTTP_ORIGIN'])
  except:
    print "DEBUG: http origin unknown!"
    headers['Access-Control-Allow-Origin'] = 'https://www.kucera.biz'
    return resp

  #print "DEBUG: request.http_origin is: {}".format(request.http_origin)
  if request.environ['HTTP_ORIGIN'] in ['http://kucera.biz', 'http://www.kucera.biz', 'https://www.kucera.biz', 'http://www.dddd.de', 'https://www.dddd.de', 'http://dddd.de', 'http://geekline.org']:
    headers['Access-Control-Allow-Origin'] = '*'
    print "DEBUG: request.environ['HTTP_ORIGIN'] is IN: ".format(request.environ['HTTP_ORIGIN'])
  else:
    headers['Access-Control-Allow-Origin'] = 'https://www.kucera.biz'
    print "DEBUG: request.http_origin is OUT: ".format(request.environ['HTTP_ORIGIN'])

#  headers['Access-Control-Allow-Origin'] = '*'
#   if request.path[:11] in ['http://kucera.biz', 'http://www.kucera.biz', 'www.dddd.de']:
#     headers['Access-Control-Allow-Origin'] = '*'
#   else:
#     headers['Access-Control-Allow-Origin'] = 'http://kucera.biz'
  #headers.add('Access-Control-Allow-Origin', 'http://www.kucera.biz')
  #headers['Access-Control-Allow-Origin'] = '*kucera.biz'
  #headers.extend([("Access-Control-Allow-Origin", orig) for orig in ['http://kucera.biz', 'http://www.kucera.biz', \
  #                                                                   'http://dddd.de', 'http://geekline.de']])
  #headers.add('Access-Control-Allow-Origin', 'http://dddd.de')
  #headers.extend('Access-Control-Allow-Origin', 'http://geekline.org')
  #headers['Access-Control-Allow-Origin']= 'http://kuzera.biz, http://www.kuzera.biz'
  #headers.append('Access-Control-Allow-Origin', 'http://www.kuzera.biz')
  #TODO: shrink the number of the sites having access to the API functions
  #headers['Access-Control-Allow-Origin'] = 'dddd.de'
  return resp

#get the current date time as string
def __getDateTimeAsString():
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#Controllers
#Admin
@app.route("/api/article/create", methods=["GET", "POST"])
@requiresAuth('admin')
def createArticle():
  if request.method == "GET":
    print "INFO: {}: api/article/create GET function called!".format(__getDateTimeAsString())
    return render_template("createArticle.html")
  else:
    title= request.form["title"]
    htmlId= request.form["htmlId"]
    body= request.form["body"].replace('\n', '<br/>').replace('\r', '').replace('"', '\\"')
    created= datetime.now()
    lastUpdated= datetime.now()
    print "INFO: {}: api/article/create POST function called for the htmlId: {}!".format(__getDateTimeAsString(), htmlId)
    article= Article(pTitle=title, pHtmlId=htmlId, pBody=body, pCreated=created, pLastUpdated=lastUpdated)
    db.session.add(article)
    db.session.commit()
    flash("Article successfully created!")
    return redirect("/")

@app.route("/api/article/findForUpdate/<int:pId>")
@requiresAuth()
def findArticleForUpdate(pId):
  print "INFO: {}: api/article/findForUpdate/{} function called!".format(__getDateTimeAsString(), pId)
  article= Article.query.get(pId)
  article.body= article.body.replace('<br/>', '\n')
  return render_template("updateArticle.html", article=article)

@app.route("/api/article/findForUpdateFull/<int:pId>")
@requiresAuth('admin')
def findArticleForUpdateFull(pId):
  print "INFO: {}: api/article/findForUpdateFull/{} function called!".format(__getDateTimeAsString(), pId)
  article= Article.query.get(pId)
  article.body= article.body.replace('<br/>', '\n')
  return render_template("updateArticleFull.html", article=article)

@app.route("/api/article/update", methods=["GET", "POST"])
@requiresAuth()
def updateArticle():
  print "INFO: {}: api/article/update function called!".format(__getDateTimeAsString())
  localId= request.form["id"]
  article= Article.query.filter_by(id=localId).first()
  article.title= request.form["title"]
  article.htmlId= request.form["htmlId"]
  article.body= request.form["body"].replace('\n', '<br/>').replace('\r', '').replace('"', '\\"')
  article.lastUpdated= datetime.now()
  db.session.commit()
  flash("Die Daten wurden erfolgreich hochgeladen!")
  #return redirect("/")
  return render_template("updateArticle.html", article=article)

@app.route('/api/article/deleteById/<int:pId>')
@requiresAuth('admin')
def deleteArticleById(pId):
  print "INFO: {}: api/article/article/deleteById/{} function called!".format(__getDateTimeAsString(), pId)
  # show the post with the given id, the id is an integer
  Article.query.filter_by(id=pId).delete()
  db.session.commit()
  return redirect("/")

@app.route("/api/article/viewAll", methods=['GET'])
@requiresAuth('admin')
def viewAllArticle():
  print "INFO: {}: api/article/viewAll function called!".format(__getDateTimeAsString())
  '''Lists all the articles'''
  #allArticle= Article.query.all()
  allArticle= None
  try:
    allArticle= Article.query.order_by(Article.id)
  except Exception as e:
    print "ERROR: Error getting the Articles: {}".format(e)
  #print "DEBUG: allArticle size: {}".format(len(allArticle))
  return render_template("viewAllArticle.html", allArticle=allArticle)

@app.route('/')
@requiresAuth('admin')
def home():
  #return 'Hello, World!'
  return render_template("home.html")

@app.route('/test')
@requiresAuth('admin')
def test():
  #return 'Hello, World!'
  return render_template("test.html")

#API
@app.route('/api/article/title/findById/<int:pId>')
def findArticleTitleById(pId):
  print "INFO: {}: api/article/title/findById/{} function called!".format(__getDateTimeAsString(), pId)
  # show the post with the given id, the id is an integer
  article= Article.query.filter_by(id=pId).first()
  if article:
    return article.title
  else:
    return Response("Not found", status=404)

@app.route('/api/article/title/findByHtmlId/<string:pHtmlId>')
def findArticleTitleByHtmlId(pHtmlId):
  print "INFO: {}: api/article/title/findByHtmlId/{} function called!".format(__getDateTimeAsString(), pHtmlId)
  # show the post with the given id, the id is an integer
  article= Article.query.filter_by(htmlId=pHtmlId).first()
  if article:
    resp= Response(article.title, status=200)
    headers= resp.headers
    headers['Access-Control-Allow-Origin'] = '*'
    return resp
  else:
    return Response("Not found", status=404)

@app.route('/api/article/body/findById/<int:pId>')
def findArticleBodyById(pId):
  print "INFO: {}: api/article/body/findById/{} function called!".format(__getDateTimeAsString(), pId)
  # show the post with the given id, the id is an integer
  article= Article.query.filter_by(id=pId).first()
  if article:
    return __getResponse(article.body, 200)
  else:
    return Response("Not found", status=404)

@app.route('/api/article/body/findByHtmlId/<string:pHtmlId>')
def findArticleBodyByHtmlId(pHtmlId):
  print "INFO: {}: api/article/body/findByHtmlId/{} function called!".format(__getDateTimeAsString(), pHtmlId)
  # show the post with the given id, the id is an integer
  article= Article.query.filter_by(htmlId=pHtmlId).first()
  
  if article:
    return __getResponse("{\"articles\" : [\"dzhhhh\", \"brom\"]}", 200)
  else:
    return Response("Not found", status=404)

@app.route('/api/article/body/getAll')
def getAllArticleBody():
  print "INFO: {}: api/article/body/getAll function called!".format(__getDateTimeAsString())
  allArticle= Article.query
  resp= "{\"articles\" : ["
  if allArticle:
    for article in allArticle:
      resp+= "{\"htmlId\" : \"%s\", \"body\" : \"%s\"}, " % (article.htmlId, article.body)

    resp= resp[:-2] + "]}"
    return __getResponse(resp, 200)
  else:
    return Response("Not found", status=404)

if __name__ == "__main__":
    app.run(debug=True)
