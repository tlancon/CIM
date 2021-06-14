import os
import napari
from skimage.io import imread

with napari.gui_qt():
	viewer = napari.Viewer()
	reference = viewer.add_image(imread('C:/Users/lancon/Documents/GitHub/CIM/docs/example/led_photograph_1.jpg'), name='led_photograph_1.jpg')
	reference.scale = (1.0, 1.0)
	reference.rotate = 0.0
	reference.translate = (0.0, 0.0)
	moving1 = viewer.add_image(imread('C:/Users/lancon/Documents/GitHub/CIM/docs/example/led_micrograph_1.jpg'), name='led_micrograph_1.jpg')
	moving1.scale = (0.06620473023384621, 0.06620473023384621)
	moving1.rotate = -2.667902396758369
	moving1.translate = (353.113107047931, 930.8959890457373)
	moving2 = viewer.add_image(imread('C:/Users/lancon/Documents/GitHub/CIM/docs/example/led_xray_2.jpg'), name='led_xray_2.jpg')
	moving2.scale = (0.15874186598992301, 0.15874186598992301)
	moving2.rotate = 0.2940480079357866
	moving2.translate = (325.73990289545736, 933.5170923835777)
