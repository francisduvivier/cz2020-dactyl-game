# 1.00 - Initial version
# 1.01 - Fixed loading and saving
# 1.02 - Fixed issue altering color 
#
#	Usage:
#		Click a button to color a pixel, use left and right navigate
#
import display, keypad, touchpads, appconfig, valuestore

MAX_PAGES=16

settings = appconfig.get("photoshop", {"colors": ["D0021B","F5A623","F8E71C","8B572A","7ED321","417505","BD10E0","9013FE","4A90E2","50E3C2","B8E986","4A4A4A"]})
global_page = 0
global_canvas = [[0] * 16 for i in range(16)]

colors = [0]
for color in settings["colors"]:
	if int(color,16)>0:
		colors.append(int(color,16))

def savepages():
	global global_canvas
	print("saving")
	allpages=""
	for p in range(0,16):
		allpages+=str(p)+":"
		for b in range(0,15):
			allpages+=hex(global_canvas[p][b]).split("x")[1]+","
		allpages+=hex(global_canvas[p][15]).split("x")[1]+"\r\n"
	print(allpages)
			
	valuestore.save("photoshop","pages",allpages)

def loadpages():
	global global_canvas
	print("loading")
	allpages = valuestore.load("photoshop","pages")
	print("allpages",allpages)
	if allpages == None:
		savepages()
		allpages = valuestore.load("photoshop","pages")
	for lines in allpages.split("\r\n"):
		items=lines.split(":")
		if len(items)==2:
			page=int(items[0])
			pixels=items[1].split(",")
			if len(pixels)==16:
				for i in range(0,16):
					global_canvas[page][i]=int(str(pixels[i]),16)

def drawpage():
	print("drawpage")
	for i in range(0,16):
		x = i %  4
		y = i // 4
		display.drawPixel(x, y, global_canvas[global_page][i])
	display.flush()

def on_touch(pressed):
	global global_page
	if pressed:
		if pressed == touchpads.CANCEL:
			global_page=0
		if pressed == touchpads.LEFT:
			if global_page>0:
				global_page=global_page-1
			else:
				global_page=(MAX_PAGES-1)
		if pressed == touchpads.RIGHT:
			if global_page<(MAX_PAGES-1):
				global_page=global_page+1
			else:
				global_page=0
		print("page:",global_page)
		savepages()
		drawpage()

def on_key(button, pressed):
	global global_canvas, global_page

	if pressed:
		x = button %  4
		y = button // 4

		if global_canvas[global_page][button] in colors:
			p = colors.index(global_canvas[global_page][button])+1
			if p>=len(colors):
				p=0
		else:
			p=0
		print(p,"/",len(colors),hex(colors[p]).split('x')[1])
		global_canvas[global_page][button]=colors[p]
		display.drawPixel(x, y, global_canvas[global_page][button])

		display.flush()

loadpages()
drawpage()

touchpads.on(touchpads.OK, on_touch)
touchpads.on(touchpads.LEFT, on_touch)
touchpads.on(touchpads.RIGHT, on_touch)
touchpads.on(touchpads.CANCEL, on_touch)

keypad.add_handler(on_key)