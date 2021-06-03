import os
import napari
from skimage.io import imread

with napari.gui_qt():
	viewer = napari.Viewer()
	reference = viewer.add_image(imread('C:/Users/lancon/Documents/GitHub/CIM/docs/images/led_photograph_1.jpg'), name='led_photograph_1.jpg')
	reference.scale = (1.0, 1.0)
	reference.rotate = 0.0
	reference.translate = (0.0, 0.0)
	moving1 = viewer.add_image(imread('C:/Users/lancon/Documents/GitHub/CIM/docs/images/led_xray_1.jpg'), name='led_xray_1.jpg')
	moving1.scale = (0.6750556940957996, 0.6750556940957996)
	moving1.rotate = 0.28827821902320655
	moving1.translate = (286.84713856699454, 312.03881723676216)
	moving2 = viewer.add_image(imread('C:/Users/lancon/Documents/GitHub/CIM/docs/images/led_micrograph_1.jpg'), name='led_micrograph_1.jpg')
	moving2.scale = (0.06702167479992088, 0.06702167479992088)
	moving2.rotate = -0.8050467017347441
	moving2.translate = (353.7324550308661, 927.9582324946447)
	moving3 = viewer.add_image(imread('C:/Users/lancon/Documents/GitHub/CIM/docs/images/led_xray_2.jpg'), name='led_xray_2.jpg')
	moving3.scale = (0.15568338107189866, 0.15568338107189866)
	moving3.rotate = 0.3951051917960021
	moving3.translate = (327.1747386431872, 935.133078025883)
	moving4 = viewer.add_image(imread('C:/Users/lancon/Documents/GitHub/CIM/docs/images/led_xray_3.jpg'), name='led_xray_3.jpg')
	moving4.scale = (0.07562171904384082, 0.07562171904384082)
	moving4.rotate = 0.33719975120085394
	moving4.translate = (340.1858354002664, 948.8138217715763)
