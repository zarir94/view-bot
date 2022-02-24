from requests.exceptions import ConnectionError, ConnectTimeout
from flask import Flask, render_template, jsonify, request
from requests.structures import CaseInsensitiveDict
from validators import url as validate_url
from fake_useragent import UserAgent
from urllib.parse import unquote
from requests import get
import threading

ua = UserAgent()

app=Flask(__name__)

threadid=10000
all_threads={}

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
	headers["User-Agent"] = ua.random
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

@app.route('/', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/add', methods=['POST'])
def addwork():
	global all_threads
	global threadid

	url=unquote(request.form.get('url', '', str))
	amount=request.form.get('amount', '', int)
	maxamount=5000
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
	all_threads[threadid]=Views_Thread(url, amount)
	all_threads[threadid].setDaemon(True)
	all_threads[threadid].start()
	return jsonify({'success':True, 'message':'URL added to thread', 'category':'success', 'id':threadid})

@app.route('/work/<threadid>', methods=['GET', 'POST'])
def showwork(threadid):
	try:
		threadid=int(threadid)
	except:
		return render_template('404.html'), 404
	if not (threadid in all_threads):
		return render_template('404.html'), 404
	return render_template('showwork.html', threadid=threadid)

@app.route('/getwork/<threadid>', methods=['POST'])
def getwork(threadid):
	try:
		threadid=int(threadid)
	except:
		return render_template('404.html'), 404
	if not (threadid in all_threads):
		return render_template('404.html'), 404
	thread=all_threads[threadid]
	percent=thread.percent
	views=thread.views
	running=thread.running
	done=thread.done
	url=thread.url
	amount=thread.amount
	return jsonify({'id':threadid, 'percent':percent, 'views':views, 'running':running, 'done':done, 'url':url, 'amount':amount})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=False)
