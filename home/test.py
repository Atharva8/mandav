from PIL import Image

basewidth = 400
img = Image.open('media/images/sdf.jpg')
wpercent = (basewidth / float(img.size[0]))
hsize = int((float(img.size[1]) * float(wpercent)))
img = img.resize((basewidth, hsize), Image.ANTIALIAS)
img.save('media/images/sdf.jpg')