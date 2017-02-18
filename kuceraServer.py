#!/usr/bin/env python
# encoding: utf-8
'''kuceraServer is the server side application to support the kucera website. 
@author:     oggo
@copyright:  1998 c ivanov Consulting Inc.'''

import sys
import json
from datetime import datetime
from flask import Flask, flash, render_template, redirect, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth

app= Flask(__name__)
app.secret_key = 'kucera_very_secret_key_zzzhghrtebrr87011'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://adminqpXQxYv:C5yZDCjUwZaU@127.8.30.2/python'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:e6kobe6ko@localhost/python'
app.config['BASIC_AUTH_USERNAME'] = 'kucera'
app.config['BASIC_AUTH_PASSWORD'] = 'kucera'
db= SQLAlchemy(app)
basicAuth= BasicAuth(app)
reload(sys)
sys.setdefaultencoding('utf-8')

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
  headers['Access-Control-Allow-Origin'] = '*'
  #TODO: shrink the number of the sites having access to the API functions
  #headers['Access-Control-Allow-Origin'] = 'dddd.de'
  return resp

#get the current date time as string
def __getDateTimeAsString():
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#Controllers
#Admin
@app.route("/api/article/create", methods=["GET", "POST"])
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
def findArticleForUpdate(pId):
  print "INFO: {}: api/article/findForUpdate/{} function called!".format(__getDateTimeAsString(), pId)
  article= Article.query.get(pId)
  article.body= article.body.replace('<br/>', '\n')
  return render_template("updateArticle.html", article=article)

@app.route("/api/article/findForUpdateFull/<int:pId>")
def findArticleForUpdateFull(pId):
  print "INFO: {}: api/article/findForUpdateFull/{} function called!".format(__getDateTimeAsString(), pId)
  article= Article.query.get(pId)
  article.body= article.body.replace('<br/>', '\n')
  return render_template("updateArticleFull.html", article=article)

@app.route("/api/article/update", methods=["GET", "POST"])
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
@basicAuth.required
def deleteArticleById(pId):
  print "INFO: {}: api/article/article/deleteById/{} function called!".format(__getDateTimeAsString(), pId)
  # show the post with the given id, the id is an integer
  Article.query.filter_by(id=pId).delete()
  db.session.commit()
  return redirect("/")

@app.route("/api/article/viewAll", methods=['GET'])
def viewAllArticle():
  print "INFO: {}: api/article/viewAll function called!".format(__getDateTimeAsString())
  '''Lists all the articles'''
  #allArticle= Article.query.all()
  allArticle= Article.query.order_by(Article.id)
  #print "DEBUG: allArticle size: {}".format(len(allArticle))
  return render_template("viewAllArticle.html", allArticle=allArticle)

@app.route('/')
def home():
  #return 'Hello, World!'
  return render_template("home.html")

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
  # show the post with the given id, the id is an integer
  allArticle= Article.query
  resp= "{\"articles\" : ["
  #print "DEBUG: resp is: {}".format(resp)
  if allArticle:
    for article in allArticle:
      #print "DEBUG: current article is: {}".format(str(article))
      resp+= "{\"htmlId\" : \"%s\", \"body\" : \"%s\"}, " % (article.htmlId, article.body)
      #print "DEBUG: resp is: {}".format(resp)

    resp= resp[:-2] + "]}"
    #print "DEBUG: resp will be: %s" % (str(resp))
    return __getResponse(resp, 200)
  else:
    return Response("Not found", status=404)

if __name__ == "__main__":
    app.run(debug=True)