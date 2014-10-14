from bs4 import BeautifulSoup
from httpcache import CachingHTTPAdapter
import cPickle as pickle
import os
import requests
import time

BASE_URL = "http://senioren.voetbal.nl/clubs_comp/mijn-teams/{0}-club"


class Voetbal(object):
  """
  Voetbal class
  """
  def __init__(self,
               clubid="BBCC89Q",
               username="...",
               password="..."):
    """
    Initialize
    """
    uitslagenfile = r"./uitslagen/{0}.pk".format(clubid)
    programmafile = r"./programma/{0}.pk".format(clubid)

    self.delete_file(uitslagenfile)
    self.delete_file(programmafile)

    if os.path.exists(uitslagenfile) and os.path.exists(programmafile):
      self.uitslagen = self.open_object(uitslagenfile)
      self.programma = self.open_object(programmafile)
    else:
      content = self.get_voetbal_page(clubid, username, password)
      soup = BeautifulSoup(content)

      uitslagen_blok = soup.find(id="club-teams-uitslagen-blok")
      programma_blok = soup.find(id="club-teams-programma-blok")

      self.prepare_store()

      self.create_uitslagen(uitslagen_blok)
      self.save_object(self.uitslagen, uitslagenfile)
      self.create_programma(programma_blok)
      self.save_object(self.programma, programmafile)

  def prepare_store(self):
    """
    Prepare filesystem
    """
    if not os.path.exists("./uitslagen/"):
      os.makedirs("./uitslagen/")
    if not os.path.exists("./programma/"):
      os.makedirs("./programma/")

  def get_voetbal_page(self, clubid, username, password):
    """
    Do login/page request at voetbal.nl
    """
    s = requests.Session()
    s.mount("http://", CachingHTTPAdapter())
    s.mount("https://", CachingHTTPAdapter())

    user = {
      "name": username,
      "pass": password,
      "form_build_id": "automatic-login",
      "form_id": "login_block_v3_login_form",
    }

    s.post(BASE_URL.format(clubid), data=user)
    r = s.get(BASE_URL.format(clubid))
    return r.text.encode("utf-8")

  def create_uitslagen(self, uitslagen_blok):
    """
    Create 'uitslagen' object
    """
    self.uitslagen = {
      "thuis": [],
      "uit": [],
    }

    counter = 0
    for d in uitslagen_blok.find_all("div", class_="", recursive=False):
      for u in d.find_all("div", class_="club-teams-uitslagen-row"):
        self.uitslagen["thuis" if counter == 0 else "uit"].append({
          "datum": self.get_value(u, "div", "datum"),
          "wedstrijd": self.get_value(u, "div", "wedstrijd"),
          "uitslag": self.get_value(u, "div", "uitslag"),
        })
      counter += 1

  def create_programma(self, programma_blok):
    """
    Create 'programma' object
    """
    self.programma = {
      "thuis": [],
      "uit": [],
    }

    counter = 0
    for d in programma_blok.find_all("div", class_="club-programma-row", recursive=False):
      for p in d.find_all("div", class_="club-teams-programma-row"):
        self.programma["thuis" if counter == 0 else "uit"].append({
          "datum-tijd": self.get_value(p, "div", "datum-tijd"),
          "wedstrijd": self.get_value(p, "div", "wedstrijd"),
        })
      counter += 1

  def get_value(self, soupobj, elt, classname):
    """
    Helper-method: get_value
    """
    rv = " ".join(soupobj.find_all(elt, class_=classname)[0]
                         .get_text(strip=True)
                         .strip()
                         .split())
    return rv

  def save_object(self, obj, filename):
    """
    Helper-method: save_object
    """
    with open(filename, "wb") as output:
      pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

  def open_object(self, filename):
    """
    Helper-method: open_object
    """
    with open(filename, "rb") as input:
      obj = pickle.load(input)
    return obj

  def delete_file(self, filename):
    """
    If file is older then 1 hour => delete it
    """
    if os.path.exists(filename):
      age = time.time() - (60 * 60)
      st = os.stat(filename)
      mtime = st.st_mtime
      if mtime < age:
        os.unlink(filename)

  def get_uitslagen(self):
    """
    Get method for 'uitslagen'
    """
    if self.uitslagen is None:
      return {
        "error": "Geen uitslagen gevonden."
      }
    return self.uitslagen

  def get_programma(self):
    """
    Get method for 'uitslagen'
    """
    if self.programma is None:
      return {
        "error": "Geen programma gevonden."
      }
    return self.programma


"""
Flask appliction
"""
from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.route("/")
def index():
  """
  Homepage
  """
  return render_template("index.html")


@app.route("/<clubid>/all")
def all(clubid):
  """
  Get JSON object with 'all'
  """
  v = Voetbal(clubid=clubid)
  return jsonify(uitslagen=v.get_uitslagen(), programma=v.get_programma())


@app.route("/<clubid>/uitslagen")
def uitslagen(clubid):
  """
  Get JSON object with 'uitslagen'
  """
  v = Voetbal(clubid=clubid)
  return jsonify(uitslagen=v.get_uitslagen())


@app.route("/<clubid>/programma")
def programma(clubid):
  """
  Get JSON object with 'programma'
  """
  v = Voetbal(clubid=clubid)
  return jsonify(programma=v.get_programma())


@app.errorhandler(500)
def internal_error(error):
  """
  Error handling
  """
  errorObj = {
    "error": error
  }

  return jsonify(errorObj)

if __name__ == "__main__":
  app.run()
