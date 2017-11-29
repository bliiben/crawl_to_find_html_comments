from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
import re
from urllib.parse import urlparse
import json

# The parser will handle the html pages
class LinkParser(HTMLParser):

	def handle_comment(self, data):
		# Save comments that are on the page
		self.comments = self.comments + [data]

	def handle_starttag(self, tag, attrs):
		# With the tag a, we get new urls from the page
		if tag == 'a':
			for (key, value) in attrs:
				if key == 'href':
					newUrl = parse.urljoin(self.baseUrl, value)
					if( newUrl[-1] == "/"):
						newUrl = newUrl[:-1]
					self.links = self.links + [newUrl]

	def getLinks(self, url):
		self.links = []
		self.comments = []
		self.baseUrl = url
		
		response = urlopen(url)
		
		if response.getheader('Content-Type').find('text/html') != -1:
			htmlBytes = response.read()
			htmlString = htmlBytes.decode("utf-8")

			# Get into the class functions
			self.feed(htmlString)
			return htmlString, self.links, self.comments
		else:
			return "",[]

# If the url is in the filter list
def inFilter( filterOff, url ):
	for f in filterOff:
		if( len(f)>0 and url.find(f) != -1):
			return True
	return False


# Crawling Spider
def spider(url, word, maxPages):
	# Save domains names, so we stop visiting them
	domains = {}
	# Visited page that we don't want to visit again
	visited = []
	# Page visited that are left to visit
	pagesToVisit = []

	if( url !=None ) :
		pagesToVisit = [url]
	else:

		# Loads the files if the algorithms was started before
		print("Loading files...")
		with open("pagesToVisit","r") as f:
			data = f.read()
			if( len(data) > 0):
				pagesToVisit = data.split("\n")
			else:
				raise Exception("No input in file to visit")

		with open("visited","r") as f:
			data= f.read()
			if( len(data) > 0):
				visited = data.split("\n")

		with open("domains.json","r") as f:
			domains = json.loads(f.read())

	numberVisited = 0
	foundWord = False
	filterOff = []

	# Exclude domain from the filter
	with open("filter","r") as f:
		data = f.read()
		if( len(data) > 0 ):
			filterOff = data.split("\n")
		else:
			filterOff = []

	# Loop through urls
	while numberVisited < maxPages and pagesToVisit != [] :

		# Save our current status
		with open("visited","w") as f:
			f.write("\n".join(visited))
		with open("pagesToVisit","w") as f:
			f.write("\n".join(pagesToVisit))

		# Start from the beginning of our collection of pages to visit:
		url = pagesToVisit[0]
		pagesToVisit = pagesToVisit[1:]
		
		domain_ = urlparse(url)
		domain=domain_.netloc
		
		# Ignore the domains if we visited them 10 times before
		if( domain in domains and domains[domain] >= 10 ):
			print ("Ignoring "+domain)
			continue
		else:
			if( not domain in domains):
				domains[domain] = 0
			else:
				domains[domain] +=1

			with open("domains.json","w") as f:
				f.write(json.dumps(domains))

		# Filter off
		if( url in visited or inFilter(filterOff, url)):
			continue
		else:
			visited.append(url)

		numberVisited = numberVisited +1

		# Download
		try:
			print(numberVisited, "Visiting:", url)
			parser = LinkParser()
			data, links, comments = parser.getLinks(url)

			# If word we seek is in the HTML comment of the website we write this in the result.txt
			aMatch= False
			for c in comments:
				if( c.find(word) != -1):
					aMatch = True
			
			if aMatch:
				with open("result.txt","a+") as file:
					file.write("The word " + word + " was found in comments of " + url+"\n")
					print ("I found something in " + url)
			pagesToVisit = pagesToVisit + links
			pagesToVisit=list(set(pagesToVisit))
			print ("Continuing... links : "+str(len( pagesToVisit)))

		except Exception as e:
			print(" **Failed!**")
	
#Start from somewhere
if __name__ == '__main__':
	spider("http://www.level39.co","entry-header",50)