import io, json, math, pprint, copy, os

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
		else:
			print "i guess we are the root!!"

	def get_size_and_area(self, element):
		top = self.get_number_setting(element, "Top", 0)
		left = self.get_number_setting(element, "Left", 0)
		width = self.get_number_setting(element, "BubbleWidth", 0)
		height = self.get_number_setting(element, "BubbleHeight", 0)
		
		area = height * width
		
		return {
			"top": top, "left": left, "bottom": top + height, "right": left + width, "width": width, "height": height, "area": area 
		}

	def set_child_positions(self, element, parent_element):
		if parent_element != None:
			element["position"] = {
				"top": element["positioning"]["top"] - parent_element["positioning"]["top"],
				"left": element["positioning"]["left"] - parent_element["positioning"]["left"]
			}
			element["size"] = {
				"width": element["positioning"]["width"],
				"height": element["positioning"]["height"]
			}
		
		for child_element in element["children"]:
			self.set_child_positions(child_element, element)
			
		element.pop("positioning", 0)

	input_page_elements = None
	output_page_elements = None
	output_page_root = None
	def parse_page(self, page_json):
		print "in parse page"
		
		# get page elements 
		self.input_page_elements = page_json["ObjectDataModels"]
		
		# calculate element positions and sizes
		self.output_page_elements = []
		element_number = 1
		for element in self.input_page_elements:
			self.output_page_elements.append(
				{
					"type": "BublView",
					"id": "element%s" % element_number,
					"cssClass": "box element%s" % element_number,
					"positioning": self.get_size_and_area(element),
					"children": []
				}
			)
			element_number = element_number +1
	
		# sort elements by size	
		self.output_page_elements = sorted(self.output_page_elements, cmp = area_cmp)
	
		self.output_page_root = self.output_page_elements[0]
		for element in self.output_page_elements:
			self.add_to_smallest_parent(element)		
	
		self.set_child_positions(self.output_page_root, None)
		return self.output_page_root
	
	def parse_pages(self):
		print "in parse pages"
	
		return self.parse_page(self.input_bubl_json["Pages"][0])

	bubl = None
	input_bubl_json = None
	
	def parse(self, file_name):
		json_file = open(file_name, "r")
		json_file_contents = json_file.read()
		json_file.close()
		
		self.input_bubl_json = json.loads(json_file_contents)
		
		self.bubl = {
			"type": "Application",
			"id": "BublApp",
			"children": []		
		}
		self.bubl["children"].append(
			{
				"type": "BublView",
				"size": { "width": 1366, "height": 768 },
				"position": { "top": "middle", "left": "middle" },
				"show": True,		
				"children": [
					self.parse_pages()
				]
			}		
		)
		
		return self.bubl
		
	def save_bubl(self):
		pprint.pprint(self.bubl)
		self.save_bubl_definition()
		self.save_bubl_css()
		
	def save_bubl_definition(self):
		demo_filename = "../bubl/www/demo.json"
		
		if os.path.exists(demo_filename):
			os.remove(demo_filename)
		
		data = json.dumps(self.bubl, indent=4, separators=(',',':'))
		
		f = open(demo_filename, "w")
		f.write(data)
		f.close()
		
	def save_bubl_css(self):
		pass

translate = Translate()

translate.parse("../bublexamples/example1.json")
translate.save_bubl()

print "done"