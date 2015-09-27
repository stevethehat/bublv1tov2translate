import io, json, math, pprint, copy, os
	
def get_number_setting(element, key, default):
	if key in element:
		return int(math.ceil(float(element[key])))
	else:
		return default

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

def is_inside(element, possible_parent):
	result = False
	element_positioning = element["positioning"]
	possible_parent_positioning = possible_parent["positioning"]

	if element_positioning["top"] > possible_parent_positioning["top"]:
		if element_positioning["left"] > possible_parent_positioning["left"]:
			if element_positioning["bottom"] < possible_parent_positioning["bottom"]:
				if element_positioning["right"] < possible_parent_positioning["right"]: 
					result = True
	return result
		
def add_to_smallest_parent(element, elements):
	smallest_parent = None
	
	for possible_parent in elements:
		if is_inside(element, possible_parent):
			if smallest_parent == None:
				smallest_parent = possible_parent
			else:
				if possible_parent["positioning"]["area"] < smallest_parent["positioning"]["area"]:
					smallest_parent = possible_parent 
	if smallest_parent != None:
		smallest_parent["children"].append(element)
	else:
		print "i guess we are the root!!"

def get_size_and_area(element):
	top = get_number_setting(element, "Top", 0)
	left = get_number_setting(element, "Left", 0)
	width = get_number_setting(element, "BubbleWidth", 0)
	height = get_number_setting(element, "BubbleHeight", 0)
	
	area = height * width
	
	return {
		"top": top, "left": left, "bottom": top + height, "right": left + width, "width": width, "height": height, "area": area 
	}

def parse_page(page_json):
	print "in parse page"
	
	# get page elements 
	elements = page_json["ObjectDataModels"]
	
	# calculate element positions and sizes
	output_elements = []
	for element in elements:
		output_elements.append(
			{
				"type": element["BubbleControlType"],
				"positioning": get_size_and_area(element),
				"children": []
			}
		)

	# sort elements by size	
	output_elements = sorted(output_elements, cmp = area_cmp)

	root = output_elements[0]
	for element in output_elements:
		#print "%s - %s" % (control_type, pprint.pformat(element["positioning"]))
		#print "%s - %s" % (control_type, element["positioning"])
		add_to_smallest_parent(element, output_elements)		

	pprint.pprint(root)
	
def parse_pages(bubl_json):
	print "in parse pages"
	
	parse_page(bubl_json["Pages"][0])

def parse(file_name):
	json_file = open(file_name, "r")
	json_file_contents = json_file.read()
	json_file.close()
	
	input_bubl_json = json.loads(json_file_contents)
	
	parse_pages(input_bubl_json)

parse("../bublexamples/example1.json")
print "done"