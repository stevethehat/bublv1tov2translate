import io, json, math, pprint, copy, os

element_parsers = {}
output = {
	"type": "Application",
	"id": "BublApp",
	"children": []		
}

def z_index_cmp(item1, item2):
	if "ZIndex" in item1 and "ZIndex" in item2:
		if int(item1["ZIndex"]) > int(item2["ZIndex"]):
			return -1
		else:
			return 1
	else:
		return 0
	

def get_number_setting(element, key, default):
	if key in element:
		return math.ceil(float(element[key]))
	else:
		return default

def get_setting(element, key, default):
	if key in element:
		return element[key]
	else:
		return default
		
def standard_process(element, element_output_json):
	top = get_number_setting(element, "Top", -1)
	left = get_number_setting(element, "Left", -1)
	width = get_number_setting(element, "BubbleWidth", -1)
	height = get_number_setting(element, "BubbleHeight", -1)
	
	print "position %s %s %s %s" % (top, left, width, height)
	
	element_output_json["position"] = { "top": top, "left": left }
	element_output_json["size"] = { "width": width, "height": height }
	#element_output_json["zIndex"] = get_number_setting(element, "ZIndex", -1)
	#element_output_json["css"] = {} 
	
	#if "BubbleBackgroundColor" in element:
	#	element_output_json["css"]["background-color"] = fix_colour_RGB(element["BubbleBackgroundColor"])
			
def process_image(element, element_output_json):
	standard_process(element, element_output_json)
	element_output_json["children"].append(
		{
			"type": "BublImage",
			"content": {
				"url": element["AssetUrl"]
			}
		}
	)
	
def process_background_image(element, css):
	top = get_number_setting(element, "BGImagePositionTop", 0)
	left = get_number_setting(element, "BGImagePositionLeft", 0)
	width = get_number_setting(element, "BGImagePositionWidth", 0)
	height = get_number_setting(element, "BGImagePositionHeight", 0)
	
	#BGImagePositionTop
	#BGImagePositionLeft 
	#BGImagePositionWidth 
	#BGImagePositionHeight
	#css["background-image"] = "url(%s)" % element["AssetUrl"]	
	#css["background-repeat"] = "no-repeat"
	#if top and left:
	#	css["background-position"] = "%s %s" % (top, left)
	#	print "setting css background '%s'" % css["background-position"] 
	
def process_text(element, element_output_json):
	standard_process(element, element_output_json)
	text_details = get_text_details(element)

	"""
	text_details = get_text_details(element)
	if "AssetUrl" in element:
		process_background_image(element, text_details["css"])	
	element_output_json["children"].append(
		{
			"type": "msMenuBox",
			"label": text_details["text"]			
		}
	)
	"""
	element_output_json["type"] = "msMenuBox"
	element_output_json["label"] = text_details["text"]			


def process_video(element, element_output_json):
	standard_process(element, element_output_json)
	element_output_json["children"].append(
		{
			"type": "BublVideo",
			"content": {
				"url": element["AssetUrl"]
			}
		}
	)

def fix_colour_RGB(hex_rgba):
	result = "rgba(%s,%s,%s,%s)" % (int("0x%s" % hex_rgba[3:5], 0), int("0x%s" % hex_rgba[5:7], 0), int("0x%s" % hex_rgba[7:9], 0), int("0x%s" % hex_rgba[1:3], 0))
	return result
	
def update_text_details(span, result):
	result["text"] = "%s<p>%s</p>" % (result["text"], span["Text"])
	
	if "ForeColor" in span:
		result["css"]["color"] = fix_colour_RGB(span["ForeColor"])

	if "FontFamily" in span:
		result["css"]["font-family"] = span["FontFamily"]
		
	if "FontSize" in span:
		result["css"]["font-size"] = "%spx" % span["FontSize"]

	
		
	
	
def get_text_details(element):
	result = {
		"text": "",
		"css": {} 
	}
	xaml_text = element["XamlText"]
	section = xaml_text["Section"]
	
	# look for span..
	if "Span" in section:
		span = section["Span"]
		update_text_details(span, result)
	else:
		paragraph = section["Paragraph"]
		
		if type(paragraph) == dict:
			span = paragraph["Span"]
			if "Text" in span:
				update_text_details(span, result)
		else:
			result["text"] = ""
			for paragraph_bit in paragraph:
				if "Span" in paragraph_bit:
					span = paragraph_bit["Span"]
					update_text_details(span, result)
			#text = "process list %s" % element["Title"]
			

	#print "\n\n\nget_text result!!! details %s " % result
	return result	
	
def process_fallback(element, element_output_json):
	standard_process(element, element_output_json)
	"""
	element_output_json["children"].append(
		{
			"type": "ContentEditable",
			"label": element["BubbleControlType"]
		}
	)
	"""
	

#element_parsers["BubbleImage"] = process_image
element_parsers["BubbleText"] = process_text
#element_parsers["BubbleVideo"] = process_video
element_parsers["Fallback"] = process_fallback

def parse(file_name):
	json_file = open(file_name, "r")
	json_file_contents = json_file.read()
	json_file.close()
	
	input_bubl_json = json.loads(json_file_contents)
	
	parse_pages(input_bubl_json)
	
def parse_pages(input_bubl_json):
	
	#for page in input_bubl_json['Pages']:
	#	parse_page(page)
	
	parse_page(input_bubl_json["Pages"][0])
	
def parse_page(page_json):
	demo_filename = "../bubl/www/demo_page1.json"
	
	if os.path.exists(demo_filename):
		os.remove(demo_filename)
	
	encoder = json.JSONEncoder()
	
	demo = open(demo_filename, "w")
	demo.write(encoder.encode(page_json))
	demo.close()


	page_output_json = {
		"type": "BublView",
		"size": { "width": 1366, "height": 768 },
		"position": { "top": "middle", "left": "middle" },
		"show": True,		
		"children": []
	}
	
	elements = page_json["ObjectDataModels"]
	sorted(elements, cmp = z_index_cmp)
	
	for element in elements:
		print element["ZIndex"]
	
	for element in elements:
		element_output_json = {}
		"""
		element_output_json = {
			"type": "BublView",
			"show": True,
			"children": []		
		}
		"""
		if "BubbleControlType" in element:
			control_type = element["BubbleControlType"]
			
			if control_type in element_parsers:
				element_parsers[control_type](element, element_output_json)
				page_output_json["children"].append(copy.deepcopy(element_output_json))
			else:
				print "no processor for %s" % control_type 
				element_parsers["Fallback"](element, element_output_json)
				page_output_json["children"].append(copy.deepcopy(element_output_json))
				
		else:
			print "no type"	

		print control_type		
		print element_output_json	
		print ""	

	output["children"].append(page_output_json)
	
parse("../bublexamples/example1.json")
#print pprint.pprint(output)

demo_filename = "../bubl/www/demo.json"

if os.path.exists(demo_filename):
	os.remove(demo_filename)

#encoder = json.JSONEncoder()

#demo = open(demo_filename, "w")
#demo.write(encoder.encode(output))
#demo.close()

data = json.dumps(output, indent=4, separators=(',',':'))

f = open(demo_filename, "w")
f.write(data)
f.close()




print "done"