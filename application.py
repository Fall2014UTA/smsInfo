from flask import Flask, request, redirect, Response
import twilio.twiml
import urllib2
import os.path
import flask
from xml.dom import minidom
import urllib2
import StringIO
import wolframalpha
import json
 
application = Flask(__name__)
#application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']
#app = Flask(__name__)
#TEMP_PATH="/tmp/"
# Try adding your own number to this list!
callers = {
    "+16825832250": "Mr Riby",
    "+14089871135": "Mr Bansal",
    "+13474817269": "Mr Sadhoo",
}

def getWfdata(pr):
	print pr
	client = wolframalpha.Client('WEGRWY-7TKAYKK42E')
	res = client.query(pr)
	print res
	msg=""
	lst=[]
	for pod in res.pods:
		lst.append(next(res.results).text)
		msg=msg+next(res.results).text
		print next(res.results).text
		print msg
	return msg
	
def getDataw(reqs):
	url="http://api.wolframalpha.com/v2/query?appid=WEGRWY-7TKAYKK42E&input="+reqs.upper()+"&format=plaintext"

	data=urllib2.urlopen(url)
	db=data.read()
	print "data"
	d=minidom.parse(StringIO.StringIO(db))
	podList=[]
	subpodList=[]
	x=d.getElementsByTagName("pod")
	for i in x:
		podList.append(i.getAttribute("title"))
	y=d.getElementsByTagName("subpod")
	for j in y:
		subpodList.append(j.getElementsByTagName("plaintext")[0].firstChild.data)
	msg=""
	
	for i in range(0,len(podList)):
		if "conversions" in podList[i]:
			msg=podList[i] + " "+subpodList[i]
			print type(msg)
			msg=json.dumps(msg)
			print type(msg)
			return msg
	return msg

def pullData(stock):
	fileLine=stock+".txt"
	urltoget='http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=1m/csv'
	data=urllib2.urlopen(urltoget)
	dblock=data.read().decode('utf-8')
	splitdblock=dblock.split('\n')
	
	for eachLine in splitdblock:
		splitLine=eachLine.split(',')
		if 'values' not in eachLine:
			saveFile=open(fileLine,'a')
			linetoWrite=eachLine+'\n'
			saveFile.write(linetoWrite)

def printData(stock):
	if(os.path.isfile(stock+".txt")==False):
		pullData(stock)
	f=open(stock+".txt",'r')
	l=f.readlines()
	last=l[-2]
	last=last.replace('\n','')
	last=last.split(',')
	#DATE,CLOSE,HIGH,LOW,OPEN,VOLUME
	msg="Last Close:"+last[1]+" High:"+last[2]+" Low:"+last[3]
	return msg

@application.route("/", methods=['GET', 'POST'])
def mob_con():
	"""Respond and greet the caller by name."""
	stock="AMD"
	msg=""
	req=request.values.get('Body',None).decode('utf-8')
	if "stock" in req.lower():
		req=req.split()
		stock=req[1]
		stock=stock.upper()
		msg=printData(stock)
	
	elif "temperature" in req.lower():
		msg=getWfdata(req)
	elif "currency" in req.lower():
		req=req.split()
		cur=req[1]
		cur=cur.upper()
		msg=getDataw(cur)		
	else:
		#stock="GOOG"
		msg="Invalid Choice"#printData(stock)
	from_number = request.values.get('From', None)
	if from_number in callers:
		message = callers[from_number] + ", requested quotes!"+msg
	else:
		message = "Riby, thanks for the message!"+msg
	resp = twilio.twiml.Response()
	resp.message(message)
	return str(resp)

@application.route("/stock/<string:stock>", methods=['GET', 'POST'])
def web_con(stock):
	"""Respond and greet the caller by name."""
		
	msg=printData(stock)
	from_number = request.values.get('From', None)
	if from_number in callers:
		message = callers[from_number] + ", requested quotes!"+msg
	else:
		message = "Riby, thanks for the message!"+msg
	resp = twilio.twiml.Response()
	resp.message(message)
	return str(resp)

@application.route("/reqs/<string:req>", methods=['GET', 'POST'])
def web_con2(req):
	
	req=req.replace("%20"," ")
	msg=getDataw(req)
	from_number = request.values.get('From', None)
	if from_number in callers:
		message = callers[from_number] + ", requested quotes!"+msg
	else:
		message = "Riby, thanks for the message!"+msg
	resp = twilio.twiml.Response()
	resp.message(message)
	return str(resp)
	
if __name__ == '__main__':
	application.run(host='0.0.0.0')
