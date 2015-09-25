import io, json, math, pprint, copy, os
	
def get_number_setting(element, key, default):
	if key in element:
		return int(math.ceil(float(element[key])))
	else:
		return default

def get_size_and_area(element):
	top = get_number_setting(element, "Top", 0)
	left = get_number_setting(element, "Left", 0)
	width = get_number_setting(element, "BubbleWidth", 0)
	height = get_number_setting(element, "BubbleHeight", 0)
	
	area = height * width
	
	print "position %s %s %s %s - %s" % (top, left, width, height, area)
	
	return {
		"top": top, "left": left, "bottom": top + height, "right": left + width, "width": width, "height": height, "area": area 
	}

def parse_page(page_json):
	print "in parse page"
	
	elements = page_json["ObjectDataModels"]
	for element in elements:
		control_type = element["BubbleControlType"]

		print "parse element %s" % control_type
		print get_size_and_area(element)
	
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