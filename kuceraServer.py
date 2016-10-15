#!/usr/bin/env python
# encoding: utf-8
'''kuceraServer is the server side application to support the kucera website. 
@author:     oggo
@copyright:  1998 c ivanov Consulting Inc.'''

import sys
import datetime
import json
from flask import Flask, flash, render_template, redirect, request, Response
from flask_sqlalchemy import SQLAlchemy

app= Flask(__name__)
app.secret_key = 'kucera_very_secret_key_zzzhghrtebrr87011'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://adminqpXQxYv:C5yZDCjUwZaU@127.8.30.2/python'
db= SQLAlchemy(app)
reload(sys)
sys.setdefaultencoding('utf-8')

#Models
class Article(db.Model):
  id= db.Column(db.Integer, primary_key=True)
  htmlId= db.Column(db.String(100))
  title = db.Column(db.String(80))
  body = db.Column(db.Text)
  created= db.Column(db.DateTime, default=datetime.datetime.utcnow)
  lastUpdated= db.Column(db.DateTime, default=datetime.datetime.utcnow)

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
  return resp

#Controllers
#Admin
@app.route("/api/article/create", methods=["GET", "POST"])
def createArticle():
  if request.method == "GET":
    return render_template("createArticle.html")
  else:
    title= request.form["title"]
    htmlId= request.form["htmlId"]
    body= request.form["body"].replace('\n', '<br/>').replace('\r', '').replace('"', '\\"')
    created= datetime.datetime.now()
    lastUpdated= datetime.datetime.now()
    article= Article(pTitle=title, pHtmlId=htmlId, pBody=body, pCreated=created, pLastUpdated=lastUpdated)
    db.session.add(article)
    db.session.commit()
    flash("Article successfully created!")
    return redirect("/")

@app.route("/api/article/findForUpdate/<int:pId>")
def findArticleForUpdate(pId):
  article= Article.query.get(pId)
  article.body= article.body.replace('<br/>', '\n')
  return render_template("updateArticle.html", article=article)

@app.route("/api/article/findForUpdateFull/<int:pId>")
def findArticleForUpdateFull(pId):
  article= Article.query.get(pId)
  article.body= article.body.replace('<br/>', '\n')
  return render_template("updateArticleFull.html", article=article)

@app.route("/api/article/update", methods=["GET", "POST"])
def updateArticle():
  localId= request.form["id"]
  article= Article.query.filter_by(id=localId).first()
  article.title= request.form["title"]
  article.htmlId= request.form["htmlId"]
  article.body= request.form["body"].replace('\n', '<br/>').replace('\r', '').replace('"', '\\"')
  article.lastUpdated= datetime.datetime.now()
  db.session.commit()
  flash("Die Daten wurden erfolgreich hochgeladen!")
  #return redirect("/")
  return render_template("updateArticle.html", article=article)

@app.route('/api/article/deleteById/<int:pId>')
def deleteArticleTitleById(pId):
  # show the post with the given id, the id is an integer
  Article.query.filter_by(id=pId).delete()
  db.session.commit()
  return redirect("/")

@app.route("/api/article/viewAll", methods=['GET'])
def viewAllArticle():
  '''Lists all the articles'''
  allArticle= Article.query.all()
  print "DEBUG: allArticle size: {}".format(len(allArticle))
  return render_template("viewAllArticle.html", allArticle=allArticle)

@app.route('/')
def home():
  #return 'Hello, World!'
  return render_template("home.html")

#API
@app.route('/api/article/title/findById/<int:pId>')
def findArticleTitleById(pId):
    # show the post with the given id, the id is an integer
    article= Article.query.filter_by(id=pId).first()
    if article:
      return article.title
    else:
      return Response("Not found", status=404)
  
@app.route('/api/article/title/findByHtmlId/<string:pHtmlId>')
def findArticleTitleByHtmlId(pHtmlId):
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
    # show the post with the given id, the id is an integer
    article= Article.query.filter_by(id=pId).first()
    if article:
      return __getResponse(article.body, 200)
    else:
      return Response("Not found", status=404)
  
@app.route('/api/article/body/findByHtmlId/<string:pHtmlId>')
def findArticleBodyByHtmlId(pHtmlId):
    # show the post with the given id, the id is an integer
    article= Article.query.filter_by(htmlId=pHtmlId).first()
    
    if article:
      return __getResponse("{\"articles\" : [\"dzhhhh\", \"brom\"]}", 200)
    else:
      return Response("Not found", status=404)
  
@app.route('/api/article/body/getAll')
def getAllArticleBody():
    # show the post with the given id, the id is an integer
    allArticle= Article.query
    resp= "{\"articles\" : ["
    print "DEBUG: resp is: {}".format(resp)
    if allArticle:
      for article in allArticle:
        print "DEBUG: current article is: {}".format(str(article))
        resp+= "{\"htmlId\" : \"%s\", \"body\" : \"%s\"}, " % (article.htmlId, article.body)
        print "DEBUG: resp is: {}".format(resp)
  
      resp= resp[:-2] + "]}"
      print "DEBUG: resp will be: %s" % (str(resp))
      return __getResponse(resp, 200)
    else:
      return Response("Not found", status=404)
  
if __name__ == "__main__":
    app.run(debug=True)