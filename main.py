# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QColor
from skimage.io import imread
from skimage.transform import SimilarityTransform
from apps import documentation

# Need to be able to find mplwidget.py
custom_app_path = f"{os.path.dirname(os.path.realpath(__file__))}/apps/"
if custom_app_path not in sys.path:
    sys.path.append(custom_app_path)

# Need to scale to screen resolution - this handles 4k scaling
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

# Load Qt Designer file
qt_designer_file = os.path.abspath('apps/interface.ui')
Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_designer_file)


class CIMApp(QtWidgets.QMainWindow, Ui_MainWindow):
 
    def __init__(self):
        
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Need some variables to hold information throughout the apps
        self.images = {
            'reference': {
                'directory': '',
                'filename': '',
                'ref_image': 'N/A',
                'ref_landmarks': 'N/A',
                'mov_landmarks': 'N/A',
                'registered': 'N/A',
                'scale': 'N/A',
                'rotation': 'N/A',
                'translation': 'N/A'
            }
        }
        self.moving_count = 0
        self.reference_data = ''
        self.moving_data = ''
        self.script_path = ''
        self.ref_lm_color = QColor(219, 121, 108)
        self.mov_lm_color = QColor(108, 206, 219)
        self.refresh_landmark_colors()

        # Initialize the table
        table_headers = ['Filename', 'Scale', 'Rotation', 'Translation']
        self.tableCurrentFiles.setColumnCount(len(table_headers))
        self.tableCurrentFiles.setHorizontalHeaderLabels(table_headers)
        
        # Connect methods to buttons
        self.buttonOpenReferenceImage.clicked.connect(self.open_reference_image)
        self.buttonOpenMovingImages.clicked.connect(self.open_moving_images)
        self.buttonClearAllImages.clicked.connect(self.clear_images)
        self.buttonSaveScript.clicked.connect(self.save_script)
        self.buttonClearReference.clicked.connect(self.clear_reference_landmarks)
        self.buttonClearMoving.clicked.connect(self.clear_moving_landmarks)
        self.buttonRegister.clicked.connect(self.register_images)
        self.toolLandmarkColorReference.clicked.connect(self.choose_reference_color)
        self.toolLandmarkColorMoving.clicked.connect(self.choose_moving_color)
        self.buttonHelp.clicked.connect(self.show_documentation)

        # Connect methods to double clicks within matplotlib canvases
        self.mplReferenceImage.canvas.mpl_connect('button_press_event', self.reference_image_dbl_clicked)
        self.mplMovingImage.canvas.mpl_connect('button_press_event', self.moving_image_dbl_clicked)

    def refresh_landmark_colors(self):
        """
        Updates the tool buttons to choose landmark colors with the currently selected landmark colors.
        """
        self.toolLandmarkColorReference.setStyleSheet(f"background-color : {self.ref_lm_color.name()}")
        self.toolLandmarkColorMoving.setStyleSheet(f"background-color : {self.mov_lm_color.name()}")

    def keyPressEvent(self, event):
        """
        Changes between maximized and default size using F11.
        """
        if event.key() == QtCore.Qt.Key_F11:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()

    def open_reference_image(self):
        """
        When the "Open reference image..." button is pressed, this runs to allow choosing a file.

        The image is shown upon opening, and the table is updated.
        """
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose reference image', '',
                                                        'Images (*jpg *png *tif *tiff);;All Files (*)')
        if file:
            self.images['reference']['directory'] = os.path.dirname(file)
            self.images['reference']['filename'] = os.path.basename(file)
            self.buttonOpenMovingImages.setEnabled(True)
            self.buttonClearAllImages.setEnabled(True)
            self.update_table()
            self.comboSelectReference.addItem(f"{os.path.basename(file)}")
            self.comboSelectReference.currentIndexChanged.connect(self.show_reference_image)
            self.show_reference_image()

    def open_moving_images(self):
        """
        When the "Open moving images..." button is pressed, this runs to allow choosing mutliple files.

        The first selected image is shown upon opening, and the table is updated.
        """
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'Choose moving images', '',
                                                          'Images (*jpg *png *tif *tiff);;All Files (*)')
        if files:
            for f in files:
                self.moving_count += 1
                self.images[f"moving{self.moving_count}"] = {'directory': os.path.dirname(f),
                                                             'filename': os.path.basename(f),
                                                             'ref_image': None,
                                                             'ref_landmarks': [],
                                                             'mov_landmarks': [],
                                                             'registered': False,
                                                             'scale': 'N/A',
                                                             'rotation': 'N/A',
                                                             'translation': 'N/A'
                                                             }
                self.comboSelectMoving.addItem(f"{os.path.basename(f)}")
            self.update_table()
            self.comboSelectMoving.currentIndexChanged.connect(self.show_moving_image)
            self.show_moving_image()

    def clear_images(self):
        """
        Clears the images and resets the project. All current data is lost.
        """
        self.images = {
            'reference': {
                'directory': '',
                'filename': '',
                'ref_image': 'N/A',
                'ref_landmarks': 'N/A',
                'mov_landmarks': 'N/A',
                'registered': 'N/A',
                'scale': 'N/A',
                'rotation': 'N/A',
                'translation': 'N/A'
            }
        }
        self.comboSelectReference.currentIndexChanged.disconnect()
        self.comboSelectMoving.currentIndexChanged.disconnect()
        self.moving_count = 0
        self.tableCurrentFiles.setRowCount(0)
        self.buttonOpenMovingImages.setEnabled(False)
        self.buttonClearAllImages.setEnabled(False)
        self.comboSelectReference.clear()
        self.comboSelectMoving.clear()

        self.mplReferenceImage.canvas.ax.clear()
        self.mplReferenceImage.canvas.draw()
        self.mplMovingImage.canvas.ax.clear()
        self.mplMovingImage.canvas.draw()
    
    def update_table(self):
        """
        Updates the table with information stored in the current dictionary.
        """
        self.tableCurrentFiles.setRowCount(0)
        self.tableCurrentFiles.setRowCount(len(self.images))
        for r, f in enumerate(self.images):
            self.tableCurrentFiles.setItem(r, 0, QtWidgets.QTableWidgetItem(f"{self.images[f]['filename']}"))
            self.tableCurrentFiles.setItem(r, 1, QtWidgets.QTableWidgetItem(f"{self.images[f]['scale']}"))
            self.tableCurrentFiles.setItem(r, 2, QtWidgets.QTableWidgetItem(f"{self.images[f]['translation']}"))
            self.tableCurrentFiles.setItem(r, 3, QtWidgets.QTableWidgetItem(f"{self.images[f]['rotation']}"))
        self.tableCurrentFiles.resizeColumnsToContents()

    def show_reference_image(self):
        """
        Displays the reference image and any landmarks associated with it for the corresponding moving image.
        """
        mov_id = f"moving{self.comboSelectMoving.currentIndex() + 1}"
        ref_path = os.path.join(self.images['reference']['directory'], self.images['reference']['filename'])
        self.reference_data = imread(ref_path)
        self.mplReferenceImage.canvas.ax.clear()
        self.mplReferenceImage.canvas.ax.imshow(self.reference_data)
        if mov_id in self.images and self.images[mov_id]['ref_landmarks']:
            for i, p in enumerate(self.images[mov_id]['ref_landmarks']):
                self.mplReferenceImage.canvas.ax.annotate(f"{i+1}", xy=(p[1], p[0]))
                self.mplReferenceImage.canvas.ax.plot(p[1], p[0], marker='o',
                                                      color=self.ref_lm_color.name())
        self.mplReferenceImage.canvas.draw()
        
    def show_moving_image(self):
        """
        Displays the moving image and any landmarks associated with it for the corresponding moving image. Also redraws
        the reference image with any landmarks already made to associate the moving image to it.
        """
        mov_id = f"moving{self.comboSelectMoving.currentIndex() + 1}"
        mov_path = os.path.join(self.images[mov_id]['directory'], self.images[mov_id]['filename'])
        self.moving_data = imread(mov_path)
        self.mplMovingImage.canvas.ax.clear()
        self.mplMovingImage.canvas.ax.imshow(self.moving_data)
        if (mov_id in self.images) and (len(self.images[mov_id]['mov_landmarks']) > 0):
            for i, p in enumerate(self.images[mov_id]['mov_landmarks']):
                self.mplMovingImage.canvas.ax.annotate(f"{i+1}", xy=(p[1], p[0]))
                self.mplMovingImage.canvas.ax.plot(p[1], p[0], marker='o',
                                                   color=self.mov_lm_color.name())
        self.mplMovingImage.canvas.draw()
        self.show_reference_image()
    
    def reference_image_dbl_clicked(self, event):
        """
        Handles double-clicking of the reference image. A red dot and a black text label are added where the double-
        click occurs.
        """
        if event.xdata is None or event.ydata is None:
            return
        mov_id = f"moving{self.comboSelectMoving.currentIndex() + 1}"
        if mov_id == 'moving0':
            return
        if event.dblclick and event.inaxes is not None:
            x = event.xdata
            y = event.ydata
            self.images[mov_id]['ref_landmarks'].append((y, x))
            n_ref_landmarks = len(self.images[mov_id]['ref_landmarks'])
            self.mplReferenceImage.canvas.ax.annotate(f"{n_ref_landmarks}", xy=(x, y))
            self.mplReferenceImage.canvas.ax.plot(x, y, marker='o',
                                                  color=self.ref_lm_color.name())
            self.mplReferenceImage.canvas.draw()
            self.update_table()

    def moving_image_dbl_clicked(self, event):
        """
        Handles double-clicking of the moving image. A red dot and a black text label are added where the double-
        click occurs.
        """
        if event.xdata is None or event.ydata is None:
            return
        mov_id = f"moving{self.comboSelectMoving.currentIndex() + 1}"
        if event.dblclick and event.inaxes is not None:
            x = event.xdata
            y = event.ydata
            self.images[mov_id]['mov_landmarks'].append((y, x))
            n_mov_landmarks = len(self.images[mov_id]['mov_landmarks'])
            self.mplMovingImage.canvas.ax.annotate(f"{n_mov_landmarks}", xy=(x, y))
            self.mplMovingImage.canvas.ax.plot(x, y, marker='o',
                                               color=self.mov_lm_color.name())
            self.mplMovingImage.canvas.draw()
            self.update_table()

    def clear_reference_landmarks(self):
        """
        Clears all landmarks on the reference image that are associated with the currently selected moving image. Does
        not erase the registration matrix.
        """
        mov_id = f"moving{self.comboSelectMoving.currentIndex() + 1}"
        self.images[mov_id]['ref_landmarks'] = []
        self.show_reference_image()
        self.update_table()

    def clear_moving_landmarks(self):
        """
        Clears all landmarks on the currently selected moving image. Does not erase the registration matrix.
        """
        mov_id = f"moving{self.comboSelectMoving.currentIndex() + 1}"
        self.images[mov_id]['mov_landmarks'] = []
        self.show_moving_image()
        self.update_table()

    def save_script(self):
        """
        Opens a dialogue to save a script where the user chooses. When executed in a Python interpreter, the script
        will open napari, then open all of the files as new layers and transform them according the the transform
        calculated in CIM. If no transform has been calculated for an image, it skips that image.
        """
        script_file, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save napari script as...", "",
                                                               "Python (*.py);;Text Files (*.txt);; All Files (*)")
        f = open(script_file, 'w')
        if not f:
            return
        f.write('import os\nimport napari\nfrom skimage.io import imread\n\n')
        f.write('with napari.gui_qt():\n')
        f.write('\tviewer = napari.Viewer()\n')
        for i in self.images:
            p = f"{self.images[i]['directory']}\\{self.images[i]['filename']}".replace('\\', '/')
            if i == 'reference':
                f.write(f"\t{i} = viewer.add_image(imread('{p}'), name='{self.images[i]['filename']}')\n")
                f.write(f"\t{i}.scale = (1.0, 1.0)\n")
                f.write(f"\t{i}.rotate = 0.0\n")
                f.write(f"\t{i}.translate = (0.0, 0.0)\n")
            if self.images[i]['registered'] is True:
                f.write(f"\t{i} = viewer.add_image(imread('{p}'), name='{self.images[i]['filename']}')\n")
                f.write(f"\t{i}.scale = {self.images[i]['scale']}\n")
                f.write(f"\t{i}.rotate = {self.images[i]['rotation']}\n")
                f.write(f"\t{i}.translate = {self.images[i]['translation']}\n")
        f.close()
        self.statusbar.showMessage(f"Script written to {script_file}.", 5000)
        return script_file

    def register_images(self):
        """
        Computes a similarity transform (scaling, rotation, and translation; no shearing) to register the currently
        selected moving image to the reference image, then updates the table with that registration matrix. If there
        are not equal numbers of reference and moving landmarks (a req. for skimage.transform.SimilarityTransform),
        reports that to the user via the status bar of the main window and halts the computation, returning nothing.
        """
        mov_id = f"moving{self.comboSelectMoving.currentIndex() + 1}"
        ml = self.images[mov_id]['mov_landmarks']
        rl = self.images[mov_id]['ref_landmarks']
        if (len(ml)*len(rl)) == 0 or (len(ml) != len(rl)):
            message = f"There are {len(ml)} moving and {len(rl)} reference landmarks -these need to be equal."
            self.statusbar.showMessage(message, 5000)
        else:
            transform = SimilarityTransform()
            transform.estimate(np.asarray(ml), np.asarray(rl))
            self.images[mov_id]['scale'] = (transform.scale, transform.scale)
            self.images[mov_id]['rotation'] = np.rad2deg(transform.rotation)
            self.images[mov_id]['translation'] = (transform.translation[0], transform.translation[1])
            self.images[mov_id]['registered'] = True
            self.update_table()
            self.buttonSaveScript.setEnabled(True)

    def choose_reference_color(self):
        """
        Lets the user choose a color to use for reference landmarks.
        """
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.ref_lm_color = color
        self.refresh_landmark_colors()

    def choose_moving_color(self):
        """
        Lets the user choose a color to use for moving landmarks.
        """
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.mov_lm_color = color
        self.refresh_landmark_colors()

    def show_documentation(self):
        """
        Loads and displays simple HTML documentation.
        """
        self.docs = documentation.Documentation()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    cim = CIMApp()
    cim.showMaximized()
    sys.exit(app.exec())
