import urllib2

n=input()
for i in range(n):
	response=urllib2.urlopen('http://stockinfo-env-bxppqy62s5.elasticbeanstalk.com/reqs/hkd')
	print response.read() 
