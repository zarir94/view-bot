from flask import Flask, render_template, jsonify, request, redirect, url_for, Blueprint
from requests.exceptions import ConnectionError, ConnectTimeout
from requests.structures import CaseInsensitiveDict
from validators import url as validate_url
from urllib.parse import unquote
from random import choice
from requests import get
from json import loads
import threading

with open('static/useragent.json', 'r') as file:
	all_useragent=loads(file.read())
	file.close()

app=Flask(__name__)
app.config['SECRET_KEY']='iureyu48783d#8*#^37489xnhkc'
url=Blueprint('urls',__name__)

threadid=10000
all_threads={}

def random_useragent():
	randua=choice(all_useragent[choice(list(all_useragent))])
	return randua

def calc_percent(minimum, maximum, current):
	return (((current - minimum) * 100) / (maximum - minimum))

class Views_Thread(threading.Thread):
	def __init__(self, url, amount):
		self.percent = 0
		self.views=0
		self.running=True
		self.done=False
		self.url=url
		self.amount=amount
		super().__init__()

	def run(self):
		for i in range(self.amount):
			resp = send_view(self.url)
			if resp=='error':
				self.running=False
				return
			self.views+=1
			self.percent=calc_percent(0, self.amount, self.views)
		self.done=True
		self.running=False

def send_view(url):
	headers = CaseInsensitiveDict()
	headers["User-Agent"] = random_useragent()
	fetched=False
	err=0
	while not fetched:
		if err>10:
			return 'error'
		try:
			resp = get(url, headers=headers)
			fetched=True
		except ConnectionError:
			err+=1
			continue
		except ConnectTimeout:
			err+=1
			continue
	return resp

@url.route('/', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@url.route('/add', methods=['POST'])
def addwork():
	global all_threads
	global threadid

	url=unquote(request.form.get('url', '', str))
	amount=request.form.get('amount', '', int)
	maxamount=50000
	if not validate_url(url)==True:
		return jsonify({'success':False, 'message':'Invalid URL', 'category':'error'})
	fetched=send_view(url)
	if fetched=='error':
		return jsonify({'success':False, 'message':'We could not fetch your URL', 'category':'error'})
	elif fetched.status_code!=200:
		return jsonify({'success':False, 'message':'We could not fetch your URL', 'category':'error'})
	if amount<1:
		return jsonify({'success':False, 'message':f'Please Enter amount between 1-{maxamount}', 'category':'error'})
	if maxamount<amount:
		return jsonify({'success':False, 'message':f'Please Enter amount between 1-{maxamount}', 'category':'error'})
	threadid+=1
	all_threads[str(threadid)]=Views_Thread(url, amount)
	all_threads[str(threadid)].setDaemon(True)
	all_threads[str(threadid)].start()
	return jsonify({'success':True, 'message':'URL added to thread', 'category':'success', 'id':threadid})

@url.route('/work', methods=['GET', 'POST'])
def showwork():
	thid=request.args.get('id')
	if not thid:
		return render_template('404.html'), 404		
	try:
		all_threads[thid]
	except:
		return render_template('404.html'), 404
	return render_template('showwork.html', threadid=thid)

@url.route('/getwork', methods=['POST'])
def getwork():
	thid=request.form.get('id')
	if not thid:
		return render_template('404.html'), 404		
	try:
		all_threads[thid]
	except:
		return render_template('404.html'), 404
	thread=all_threads[thid]
	percent=thread.percent
	views=thread.views
	running=thread.running
	done=thread.done
	url=thread.url
	amount=thread.amount
	return jsonify({'id':thid, 'percent':percent, 'views':views, 'running':running, 'done':done, 'url':url, 'amount':amount})

@url.route('/favicon.ico', methods=['GET', 'POST'])
def favicon():
	return redirect(url_for('static', filename='favicon.ico'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.register_blueprint(url,url_prefix='/')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=False)
