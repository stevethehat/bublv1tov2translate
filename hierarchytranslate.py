import io, json, math, pprint, copy, os, sys

def area_cmp(item1, item2):
	item1_positioning = item1["positioning"]
	item2_positioning = item2["positioning"]
	
	if "area" in item1_positioning and "area" in item2_positioning:
		if int(item1_positioning["area"]) > int(item2_positioning["area"]):
			return -1
		else:
			return 1
	else:
		return 0
	
class Translate:
	def get_number_setting(self, element, key, default):
		if key in element:
			return int(math.ceil(float(element[key])))
		else:
			return default

	def is_inside(self, element, possible_parent):
		result = False
		element_positioning = element["positioning"]
		possible_parent_positioning = possible_parent["positioning"]
	
		if element_positioning["top"] > possible_parent_positioning["top"]:
			if element_positioning["left"] > possible_parent_positioning["left"]:
				if element_positioning["bottom"] < possible_parent_positioning["bottom"]:
					if element_positioning["right"] < possible_parent_positioning["right"]: 
						result = True
		return result
		
	def add_to_smallest_parent(self, element):
		smallest_parent = None
		
		for possible_parent in self.output_page_elements:
			if self.is_inside(element, possible_parent):
				if smallest_parent == None:
					smallest_parent = possible_parent
				else:
					if possible_parent["positioning"]["area"] < smallest_parent["positioning"]["area"]:
						smallest_parent = possible_parent 
		if smallest_parent != None:
			smallest_parent["children"].append(element)
			
	def update_text_details(self, span, result):
		result["text"] = "%s<p>%s</p>" % (result["text"], span["Text"])
		
		if "ForeColor" in span:
			result["css"]["color"] = self.fix_colour_RGB(span["ForeColor"])
	
		if "FontFamily" in span:
			result["css"]["font-family"] = span["FontFamily"]
			
		if "FontSize" in span:
			result["css"]["font-size"] = "%spx" % span["FontSize"]

	
	def get_text_details(self, element):
		result = {
			"text": "",
			"css": {} 
		}
		xaml_text = element["XamlText"]
		section = xaml_text["Section"]
		
		# look for span..
		if "Span" in section:
			span = section["Span"]
			self.update_text_details(span, result)
		else:
			paragraph = section["Paragraph"]
			
			if type(paragraph) == dict:
				if "Span" in paragraph:
					span = paragraph["Span"]
					if "Text" in span:
						self.update_text_details(span, result)
			else:
				result["text"] = ""
				for paragraph_bit in paragraph:
					if "Span" in paragraph_bit:
						span = paragraph_bit["Span"]
						self.update_text_details(span, result)
				#text = "process list %s" % element["Title"]
				
	
		#print "\n\n\nget_text result!!! details %s " % result
		return result	
			
	colors = {
		"#002050": "ms-blue",
		"#EB3C00": "ms-red",
		"#BA141A": "ms-dk-red",
		"#FF8C00": "ms-orange",
		"#6C38A7": "ms-purple",
		"#00B294": "ms-teal",
		"#009E49": "ms-green",
		"#442359": "ms-dk-purple"			
	}
	
	def set_bgcolor(self, element):
		color = None
		try:
			if "BubbleBackgroundColor" in element["data"]:
				old_color = element["data"]["BubbleBackgroundColor"] 
				if old_color != "#00000000":
					color = "#%s" % old_color[3:]
					if color in self.colors:
						color_class = self.colors[color]
						element["cssClass"] = "%s %s" % (element["cssClass"], color_class)
					else:
						element["bgColour"] = color
		except Exception, e:
			print " color error '%s'" % e.message
			
		if "BubbleOpacity" in element["data"]:
			element["opacity"] = float(element["data"]["BubbleOpacity"]) / 100
		
	asset_index = 0
	def download_asset(self, url):
		print "downloading '%s" % url
		self.asset_index = self.asset_index +1
		file_name = "assets/%s_asset%s.png" % (self.file_name, self.asset_index) 
			
		"""
		import urllib2
		try:
			print "downloading '%s" % url
			self.asset_index = self.asset_index +1 
			
			asset = urllib2.urlopen(url)
			asset = open("assets/%s_asset%s.png" % (self.file_name, self.asset_index), "wb")
			asset.write(asset.read())
			asset.close()		
		except:
			pass
		"""
		import urllib
		asset = urllib.URLopener()
		asset.retrieve(url, file_name)
		
	id_count = 0						
	def setup_control(self, element):
		element.pop("positioning", 0)
		old_type = element["data"]["BubbleControlType"]
		element["id"] = "id%s" % self.id_count
		self.id_count += 1
					 
		style_element = element
		
		if "AssetUrl" in element["data"]:
			element["image"] = element["data"]["AssetUrl"] 
		
		if old_type == "BubbleText":
			element["type"] = "ContentEditable"
			element["cssClass"] = "%s text" % element["cssClass"]

			"""
			if "AssetUrl" in element["data"]:
				element["css"] = {
					"background-image": "url(%s)" % element["data"]["AssetUrl"]
				}
			"""
			
			if int(element["size"]["width"] == 196) and int(element["size"]["height"]) == 95:
				print ""
				print "we have a ms-menuControl"
				print ""
				
				#self.download_asset(element["data"]["AssetUrl"])
				
				element["type"] = "msMenuBox"
				element["cssClass"] = "%s ms-menuControl" % element["cssClass"]
				
				print "top %s left %s" % (element["data"]["BGImagePositionLeft"], element["data"]["BGImagePositionLeft"])
				print "%s x %s" % (element["data"]["BGImagePositionWidth"], element["data"]["BGImagePositionHeight"])

			#element["type"] = "msMenuBox"
			#element["cssClass"] = "%s ms-menuControl" % element["cssClass"]
			#output_element["label"] = 'text'
			try:
				element["label"] = self.get_text_details(element["data"])["text"]
			except:
				element["label"] = 'text'

		if old_type == "BubbleImage" and len(element["children"]) == 0:
			element["type"] = "BublImage"
			element.pop("image", 0)
			element["content"] = {
				"url": element["data"]["AssetUrl"]
			}
		else:
			pass

		if old_type == "BubbleVideo":
			element["type"] = "BublVideo"
			element["content"] = {
				"url": element["data"]["AssetUrl"]
			}

		if element["type"] == "BublView":
			print ""
			print "we just have a view '%s'" % old_type	
			
			import copy
			new_control = copy.deepcopy(element)
			new_control["type"] = "BublControl"
			new_control.pop("children", 0)
			new_control.pop("position", 0)
			#new_control.pop("size", 0)
			new_control["auto added control"] = True
			
			#pprint.pprint(new_control["data"])
			
			self.set_bgcolor(new_control)
			new_control.pop("data", 0)
			
			#print "adding default control %s " % new_control			
			element["children"] = [new_control] + element["children"]
			#print "added %s" % element["children"][0]
			
		else:
			self.set_bgcolor(element)
			
	unique_sizes = {}
	def get_size_and_area(self, element):
		top = self.get_number_setting(element, "Top", 0)
		left = self.get_number_setting(element, "Left", 0)
		width = self.get_number_setting(element, "BubbleWidth", 0)
		height = self.get_number_setting(element, "BubbleHeight", 0)
		
		size = "%s - %s" % (width, height)
		print size
		if size in self.unique_sizes:
			self.unique_sizes[size] = self.unique_sizes[size] +1
		else:
			self.unique_sizes[size] = 1
		
		if top < 0:
			top = 0
			
		if left < 0:
			left = 0
		
		area = height * width
		
		return {
			"top": top, "left": left, "bottom": top + height, "right": left + width, "width": width, "height": height, "area": area, "visibility": element["BubbleVisibility"], "guid": element["BubbleId"]  
		}
		
	def fix_colour_RGB(self, hex_rgba):
		result = "rgba(%s,%s,%s,%s)" % (int("0x%s" % hex_rgba[3:5], 0), int("0x%s" % hex_rgba[5:7], 0), int("0x%s" % hex_rgba[7:9], 0), int("0x%s" % hex_rgba[1:3], 0))
		return result
		
	def set_basic_stylings(self, input_element, output_element, output_element_css):
		# BubbleBackgroundColor
		output_element_css["background-color"] = self.fix_colour_RGB(input_element["BubbleBackgroundColor"])
		
		

	def setup_children(self, element, parent_element):
		if parent_element != None:
			element["position"] = {
				"top": element["positioning"]["top"] - parent_element["positioning"]["top"],
				"left": element["positioning"]["left"] - parent_element["positioning"]["left"]
			}
			element["size"] = {
				"width": element["positioning"]["width"],
				"height": element["positioning"]["height"]
			}
		else:
			element["position"] = {
				"top": element["positioning"]["top"],
				"left": element["positioning"]["left"]
			}
			element["size"] = {
				"width": element["positioning"]["width"],
				"height": element["positioning"]["height"]
			}
		for child_element in element["children"]:
			self.setup_children(child_element, element)
						
		self.setup_control(element)
		
		if len(element["children"]) == 0:
			element.pop("children", 0)
		
		element.pop("positioning", 0)
		element.pop("data", 0)

	input_page_elements = None
	output_page_elements = None
	output_page_root = None
	def parse_page(self, page_json):
		print "in parse page"
		
		# get page elements 
		self.input_page_elements = page_json["ObjectDataModels"]
		self.input_page_elements.append(
			{
				"BubbleHeight":768.0,
				"BubbleWidth":1366.0,
				"Top": 0,
				"Left": 0,
				"BubbleControlType": "BubbleRectangle",
				"BubbleVisibility": True,
				"Title": "Fake Bubble Root",
				"BubbleId": 1,
				"BubbleBackgroundColor": page_json["BubbleBackgroundColor"]
			}
		)
		
		# calculate element positions and sizes
		self.output_page_elements = []
		element_number = 1
		for element in self.input_page_elements:
			do_it = element["BubbleVisibility"]
			
			if self.force_visibility:
				do_it = True
			"""	
			if element["BubbleId"] == "6e0d7fb7-9b68-43d5-8b2e-ba58ae91709d":
				do_it = True
			"""
				
			if do_it == True:
				title = element["Title"]
				print "processing %s - %s" % (element["BubbleControlType"], element["Title"])
				
				happy_title = "".join(ch for ch in title if ch.isalnum()) 
				element_id = "%s-%s" % (happy_title, element_number)
				print happy_title
				output_element = {
						"type": "BublView",
						"cssClass": "%s" % element_id,
						"positioning": self.get_size_and_area(element),
						"children": [],
						"oldtype": element["BubbleControlType"],
						"oldid": element["Title"],
						"data": element
					} 
				#output_element = self.setup_control(element, output_element)
				output_element_css = {
						"class": "box .%s" % element_id,
						"styles": {
						}
					}

				#self.set_basic_stylings(element, output_element, output_element_css)
				
				self.output_page_elements.append(output_element)
				self.bubl_css.append(output_element_css)
				element_number = element_number +1
			else:
				print "discarded %s - %s" % (element["BubbleControlType"], element["Title"])
		# sort elements by size	
		self.output_page_elements = sorted(self.output_page_elements, cmp = area_cmp)
	
		self.output_page_root = self.output_page_elements[0]
		for element in self.output_page_elements:
			print "%s" % (element["positioning"])
			self.add_to_smallest_parent(element)		
	
		self.setup_children(self.output_page_root, None)
		return self.output_page_root
	
	def parse_pages(self):
		print "in parse pages - %s of %s" % (self.page, len(self.input_bubl_json["Pages"])) 
	
		return self.parse_page(self.input_bubl_json["Pages"][int(self.page) -1])

	bubl = None
	input_bubl_json = None
	bubl_css = []
	
	def flatten_pages(self):
		pass
							   
	flat_pages = []
	def find_pages(self, element):
		if isinstance(element, dict):
			for k in element:
				if k == "Pages":
					pages = element[k]
					for page in pages:
						print "found page"
						self.flat_pages.append(page)
						self.find_pages(page)
				
	
	current_search_page = 0
	found_page = None
	def find_page(self, search):
		print "find page containing '%s'" % search
		result = False
		for page in self.input_bubl_json["Pages"]:
			print "search page %s" % self.current_search_page
			self.search_element(page, search)
			self.current_search_page = self.current_search_page + 1
			print "updating current search page %s" % self.current_search_page

		print type(self.found_page)
		print "on page %s" % (self.found_page +1)
		
		self.page = self.found_page +1
		
	def search_element(self, json_element, search):
		if isinstance(json_element, dict):
			for element in json_element:
				self.search_element(json_element[element], search)
		else:
			if isinstance(json_element, list):
				for element in json_element:
					self.search_element(element, search)
			else:
				try:
					if json_element.find(search) != -1:
						print "found '%s' = '%s on %s" % (json_element, search, self.current_search_page)
						self.found_page = self.current_search_page
						#pprint.pprint(self.input_bubl_json["Pages"][self.found_page]["Actions"])
						
						try:
							page = open("found_page.json", "w")
							page.write(json.dumps(self.input_bubl_json["Pages"][self.found_page], indent=4, separators=(',',':')))
							page.close()
							print "WRITTEN PAGE"
						except Exception, e:
							print e.message
				except Exception, e:
					pass
		"""
		for element in json:
			print "element %s" % type(element)
			value = element
			if value == search:
				print "FOUND"
			else:
				if isinstance(value, dict) or isinstance(value, list):
					self.search_element(json[element], search)
		"""
		 	
	def parse(self, file_name, page, search):
		self.file_name = file_name
					
		json_file = open("../bublexamples/%s.json" % file_name, "r")
		json_file_contents = json_file.read()
		json_file.close()
		
		print "parsing '%s'" % file_name
		
		self.input_bubl_json = json.loads(json_file_contents)
		
		self.find_pages(self.input_bubl_json)
		self.input_bubl_json["Pages"] = self.flat_pages
		
		if page == None and not(search == None):
			self.find_page(search)			
		else:
			self.page = page

		self.bubl = {
			"type": "Application",
			"id": "BublApp",
			"children": []		
		}
		root = 	{
			"type": "BublView",
			"id": "rootView",
			"size": { "width": 1366, "height": 768 },
			"position": { "top": "middle", "left": "middle" },
			"show": True,		
			"children": [
				self.parse_pages()
			]
		}	
		root["data"] = self.input_bubl_json
		self.set_bgcolor(root)	
		root.pop("data", 0)

		self.bubl["children"].append(root)
		
		return self.bubl
		
	def save_bubl(self):
		#pprint.pprint(self.bubl)
		self.save_bubl_definition()
		self.save_bubl_css()
		
	def save_bubl_definition(self):
		definition_filename = "../bubl/www/demo.json"
		
		if os.path.exists(definition_filename):
			os.remove(definition_filename)
		
		data = json.dumps(self.bubl, indent=4, separators=(',',':'))
		
		print data
		
		f = open(definition_filename, "w")
		f.write(data)
		f.close()
		
		print "unique sizes"
		#pprint.pprint(self.unique_sizes)
		
		print "no pages = %s" % len(self.input_bubl_json["Pages"])
		print "processed '%s'" % self.file_name
		print "page %s" % self.page
		
		
	def save_bubl_css(self):
		definition_filename = "../bubl/www/app/css/demo_bubl.css"
		
		if os.path.exists(definition_filename):
			os.remove(definition_filename)
		
		f = open(definition_filename, "w")
		f.write("/* demo bubl css */")
		for css_class in self.bubl_css:
			f.write("\n.%s{" % css_class["class"])
			
			for style in css_class["styles"]:
				f.write("\n\t%s:%s;" % (style, css_class["styles"][style]))
			
			f.write("\n}\n")
		f.close()

translate = Translate()

example_number = 1
page = 1
search = None

if len(sys.argv) >= 2:
	example_number = sys.argv[1]
if len(sys.argv) == 3:
	if isinstance(sys.argv[2], int):
		page = sys.argv[2]
	else:
		page = None
		search = sys.argv[2]
	
translate.force_visibility = False
translate.parse("example%s" % example_number, page, search)
translate.save_bubl()

print "done"

# change to test git