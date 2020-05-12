# -*- coding: utf-8 -*-
# Copyright: Kyle Hwang <feathered.hwang@hotmail.com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# To import lines
#


import json
import logging
import random
import re
import time
import unicodedata
from pathlib import Path
from shutil import copyfile

# import the main window object (mw) from aqt
from aqt import mw, editor
# import the "show info" tool from utils.py
from aqt.utils import showInfo, askUser
# import all of the Qt GUI library
from aqt.qt import *
# import anki notes library
from anki import notes

# import ui
from . import settingsDialog


# Support the same media types as the Editor
AUDIO_TYPES = editor.audio
IMAGE_TYPES = editor.pics
# Support lyric files as subtitles for now
# TODO Add support to other lyric types
SUB_TYPES = ("lrc", "txt",)

# Field Map Choices
FILL_NOTHING = ''
FILL_FILENAME = 'File Name'
FILL_PROV = 'Provenance'
FILL_AUDIO = 'Audio'
FILL_LINE = 'Subtitle'
FILL_IMAGE = 'Random Image'
FILLING_OPTIONS = [FILL_NOTHING,
                   FILL_FILENAME,
                   FILL_PROV,
                   FILL_AUDIO,
                   FILL_LINE,
                   FILL_IMAGE]


def do_import():
    """
    Get the user settings from settingsForm, then do importing
    """
    # Raise the settings window for the add-on and retrieve its result when closed.
    (dir_path, prov, deck_name, model_name, field_map, tags, ok) = SettingsDialog().get_result()
    if not ok:
        return

    deck = mw.col.decks.byName(deck_name)
    model = mw.col.models.byName(model_name)

    # Initialize
    audio_files, std_image_files, sub_files = [], [], []
    is_import_failed = False
    card_count = 0
    # Locate work directory
    os.chdir(dir_path)
    # Firstly, get new file name standard prefix according to provenance
    std_prefix = prov.replace(' ', '.')
    # We won't walk the path - we only want the top-level files.
    file_names = os.listdir(dir_path)

    # Start importing progress
    mw.progress.start(max=len(file_names), parent=mw)
    p = 0

    # To classify files
    for f in file_names:
        file_root, ext = os.path.splitext(f)
        _ext = ext[1:].lower()
        if _ext in AUDIO_TYPES:
            audio_files.append((file_root, ext))
        elif _ext in SUB_TYPES:
            sub_files.append((file_root, ext))
        elif _ext in IMAGE_TYPES:
            # Copy image files to collection.media with standardized name
            std_name = std_prefix + '.image-' + str(time.time()) + ext
            copyfile(f, std_name)
            std_image_files.append(std_name)
            p += 1
        else:
            p += 1
        # Update progress
        mw.progress.update(value=p)

    # Create a note for each audio file, and add it to Anki collection
    for i, (root, ext) in enumerate(audio_files):
        std_root = std_prefix + '.audio' + '(' + str(i + 1) + ')' + '-' + str(time.time())
        std_name = std_root + ext
        copyfile(root + ext, std_name)
        mw.col.media.addFile(std_name)
        os.remove(std_name)

        # Create a new note
        note = notes.Note(mw.col, model)
        note.model()['did'] = deck['id']

        # Get subtitle file content
        try:
            # Find the corespondent sub file
            sub_ext = sub_files[[r[0] for r in sub_files].index(root)][1]
            # Opening with utf-8-sig encoding, which will remove BOM (Byte order mark) if it exists
            with open(root + sub_ext, mode='r', encoding='utf-8-sig') as f:
                line = re.sub(r'\[[0-9:.]+\]', '', f.read())
                line = re.sub(r'\n+', r'<br>', line)
            # Update progress
            p += 1
        # If sub file not found, index(root) will raise ValueError
        except ValueError:
            line = ''

        # Fill fields
        for field, option_idx in field_map.items():
            data = ''
            option = FILLING_OPTIONS[option_idx]
            if option == FILL_NOTHING:
                continue
            elif option == FILL_FILENAME:
                data = std_root
            elif option == FILL_PROV:
                data = prov
            elif option == FILL_AUDIO:
                data = u'[sound:%s]' % std_name
            elif option == FILL_LINE:
                data = line
            elif option == FILL_IMAGE:
                if std_image_files:
                    image = random.choice(std_image_files)
                    mw.col.media.addFile(image)
                    data = u'<img src="%s">' % image
            # Assign value to field
            note[field] = data

        # Add Tags
        for tag in tags:
            note.tags.append(tag)

        # Add to collection
        if not mw.col.addNote(note):
            # No cards were generated - probably bad template. No point to import anymore.
            is_import_failed = True
            break
        card_count += 1
        p += 1

        # Update progress
        mw.progress.update(value=p)

    # Delete std_image_files
    for image in std_image_files:
        os.remove(image)

    # At the end
    mw.progress.finish()
    mw.deckBrowser.refresh()
    if is_import_failed:
        show_failure_dialog()
    else:
        show_completion_dialog(card_count, deck_name)


def show_failure_dialog():
    """
    Show this dialog when one or more cards failed to import.
    """
    QMessageBox.about(mw, "Lines Import Failure", """
<p>
Failed to generate one or more notes and no media files were imported. 
Please ensure the note type you selected is able to generate cards by using a valid card template.
</p>
""")


def show_completion_dialog(new_cards_count, deck_name):
    """
    Show this dialog when cards-import succeed.
    """
    # noinspection PyTypeChecker
    QMessageBox.about(mw, "Lines Import Complete",
                      """
<p>
Importing is complete and %s new notes were created. 
All generated cards are put into the <b>%s</b> deck.
</p>
""" % (new_cards_count, deck_name))


class SettingsDialog(QDialog):
    """
    User's configuration of lines importing.
    To get the user configuration, call get_result().
    """

    def __init__(self):
        # noinspection PyTypeChecker
        QDialog.__init__(self, mw)

        # keys of json settings dictionary
        self.DIR_PATH_KEY = 'dirPath'
        self.PROV_KEY = 'prov'
        self.DECK_NAME_KEY = 'deckName'
        self.MODEL_NAME_KEY = 'modelName'
        self.FIELD_MAP_KEY = 'fieldMap'
        self.TAGS_TXT_KEY = 'tagsTxt'

        self.form = settingsDialog.Ui_settingsDialog()
        self.form.setupUi(self)
        self.form.buttonBox.accepted.connect(self.accept)
        self.form.buttonBox.rejected.connect(self.reject)

        # Import previous settings
        self.SETTINGS_JSON_PATH = \
            os.path.dirname(sys.modules[__name__].__file__) \
            + '/settings@%s.json' % mw.pm.name.replace(' ', '.')
        settings_dict = {}
        try:
            with open(self.SETTINGS_JSON_PATH) as f:
                settings_dict = json.load(f)
        except EnvironmentError:
            logging.warning('Settings File Not Found.')
        logging.info('The earlier settings: \n' + json.dumps(settings_dict))
        # dirPath (directory path, default: home path)
        self.dirPath = settings_dict.get(self.DIR_PATH_KEY, '')
        if not os.path.exists(self.dirPath):
            self.dirPath = str(Path.home())
        self.form.dirInput.setText(self.dirPath)
        self.form.dirButton.clicked.connect(self.browse_dir)
        # prov (provenance, default: ''/Unknown)
        self.prov = settings_dict.get(self.PROV_KEY, '')
        self.form.provInput.setText(self.prov)
        self.form.provInput.editingFinished.connect(self.prov_updated)
        # deck (default: current deck)
        deck_list = [d['name'] for d in mw.col.decks.all()]
        self.form.deckCombo.addItems(deck_list)
        self.deckName = settings_dict.get(self.DECK_NAME_KEY, '')
        if self.deckName not in deck_list:
            self.deckName = mw.col.decks.current()['name']
        self.form.deckCombo.setCurrentIndex(self.form.deckCombo.findText(self.deckName))
        self.form.deckCombo.currentIndexChanged.connect(self.deck_updated)
        # model (default: current model)
        model_list = [m['name'] for m in mw.col.models.all()]
        self.form.modelCombo.addItems(model_list)
        self.modelName = settings_dict.get(self.MODEL_NAME_KEY, '')
        if self.modelName not in model_list:
            self.modelName = mw.col.models.current()['name']
        self.form.modelCombo.setCurrentIndex(self.form.modelCombo.findText(self.modelName))
        self.form.modelCombo.currentIndexChanged.connect(self.model_updated)
        # fieldMap (field map, default: empty)
        self.fieldMap = settings_dict.get(self.FIELD_MAP_KEY, {})
        self.create_field_grid()
        # tags (default: [])
        self.tags = []
        self.tagsTxt = settings_dict.get(self.TAGS_TXT_KEY, '')
        self.form.tagsInput.setText(self.tagsTxt)
        self.tags_updated()
        self.form.tagsInput.editingFinished.connect(self.tags_updated)
        # help label
        self.form.helpLabel.setText("""
<p>
For how to use this add-on, please refer to 
<a href="https://github.com/feathered-hwang/lines2anki/blob/master/README.md">README.md</a>.
</p>
""")

        self.exec_()

    def browse_dir(self):
        """
        Browse File Explorer, which will change dirPath and prov as well
        """
        path = QFileDialog.getExistingDirectory(mw, caption='Open', directory=str(Path(self.dirPath).parent))

        if not path:
            return
        self.dirPath = path
        self.form.dirInput.setText(self.dirPath)
        logging.info('dirPath =         ' + self.dirPath)
        self.prov = os.path.basename(self.dirPath)
        self.form.provInput.setText(self.prov)

    def prov_updated(self):
        """
        If user edit the content of provenance QLineEdit, change self.prov
        """
        self.prov = self.form.provInput.text()
        logging.info('prov =            ' + self.prov)

    def deck_updated(self):
        """
        If user select another deck in combobox, change self.deckName
        """
        self.deckName = self.form.deckCombo.currentText()
        logging.info('deckName =        ' + self.deckName)

    def model_updated(self):
        """
        If user select another model in combobox, change self.modelName
        """
        self.modelName = self.form.modelCombo.currentText()
        logging.info('modelName =       ' + self.modelName)
        self.create_field_grid()

    def tags_updated(self):
        """
        If user edit the tags QLineEdit, change self.tags
        """
        self.tagsTxt = unicodedata.normalize("NFC", self.form.tagsInput.text())
        self.tags = mw.col.tags.canonify(mw.col.tags.split(self.tagsTxt))
        self.tagsTxt = mw.col.tags.join(self.tags).strip()
        self.form.tagsInput.setText(self.tagsTxt)
        logging.info('tags =            ' + self.tagsTxt)

    def create_field_grid(self):
        """
        Fill in the fieldMapGrid QGridLayout.

        Each row in the grid contains two columns:
        Column 0 = QLabel with name of field
        Column 1 = QComboBox with selection of mappings ("actions")
        """
        # Clear Grid layout
        self.clear_layout(self.form.fieldMapGrid)
        if not self.modelName:
            return

        # Add Combinations of QLabel (with field name) and QComboBox (with FILLING_OPTIONS) to QGridLayout
        row = 0
        for field in mw.col.models.byName(self.modelName)['flds']:
            lbl = QLabel(field['name'])
            cmb = QComboBox()
            cmb.addItems(FILLING_OPTIONS)
            cmb.setCurrentIndex(self.fieldMap.get(field['name'], -1))
            # piggy-back the special flag on QLabel
            self.form.fieldMapGrid.addWidget(lbl, row, 0)
            self.form.fieldMapGrid.addWidget(cmb, row, 1)

            row += 1
        self.form.fieldMapGrid.addItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), row, 0)
        logging.info("Fields Map of ** " + self.modelName + " ** are generated.")

    def clear_layout(self, layout):
        """
        A recursive function, convenient for removing child widgets from a layout.
        """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())

    def accept(self):
        """
        If user accept the settings (commit the settings)
        """
        # validate directory
        if not os.path.exists(self.dirPath):
            showInfo("Directory not found.\n"
                     "The resource you're looking for might have been removed, "
                     "had its name changed, or is temporary unavailable. \n"
                     "Please select another directory.")
            self.browse_dir()
            return
        # validate provenance
        try:
            # Test if a string is filename-ok by creating a file
            with open(self.prov, 'w'):
                pass
            os.remove(self.prov)
        except (FileNotFoundError, OSError):
            _prov = 'Unknown'
            if askUser("""
Provenance will be used to rename files, so it cannot be empty or contain any of the following characters:\n
/\\:*?"<>|\n
If you choose 'Yes', you'll return to edit the provenance.\n
If you choose 'No', provenance will be '%s'.
""" % _prov):
                self.form.provInput.setFocus()
                self.form.provInput.selectAll()
                return
            else:
                self.prov = _prov
        # validate deck
        if not self.deckName:
            self.deckName = mw.col.decks.current()['name']
        # validate model
        if not self.modelName:
            self.modelName = mw.col.models.current()['name']
        # get field map
        self.fieldMap = {}
        for row in range(len(mw.col.models.byName(self.modelName)['flds'])):
            # QLabel with field name
            field = self.form.fieldMapGrid.itemAtPosition(row, 0).widget().text()
            # QComboBox with index from the FILLING_OPTIONS list
            option_idx = self.form.fieldMapGrid.itemAtPosition(row, 1).widget().currentIndex()
            self.fieldMap[field] = option_idx

        # logging
        logging.info("Final dirPath   =     " + self.dirPath)
        logging.info("Final prov      =     " + self.prov)
        logging.info("Final deckName  =     " + self.deckName)
        logging.info("Final modelName =     " + self.modelName)
        logging.info('fieldMap = \n' + json.dumps(self.fieldMap, indent=4))
        logging.info("Final tags =          " + self.tagsTxt)

        # save user settings
        settings_dict = {
            self.DIR_PATH_KEY: self.dirPath,
            self.PROV_KEY: self.prov,
            self.DECK_NAME_KEY: self.deckName,
            self.MODEL_NAME_KEY: self.modelName,
            self.FIELD_MAP_KEY: self.fieldMap,
            self.TAGS_TXT_KEY: self.tagsTxt
        }
        with open(self.SETTINGS_JSON_PATH, 'w') as f:
            f.write(json.dumps(settings_dict, indent=4))

        QDialog.accept(self)

    def get_result(self):
        """
        Return a tuple containing the user-defined settings to follow
        for an import. The tuple contains seven items (in order):
         - Path of chosen media directory
         - The imported lines' provenance
         - The deck name
         - The model (note type) name
         - A dictionary that maps each of the fields in the model to an
           integer index from the ACTIONS list
         - The tags list
         - True/False indicating whether the user clicked OK/Cancel
        """
        if self.result() == QDialog.Rejected:
            return None, None, None, None, None, None, False
        return self.dirPath, self.prov, self.deckName, self.modelName, self.fieldMap, self.tags, True


# create a new menu item,
action = QAction("Lines Import...", mw)
# set it to call what function when it's clicked
action.triggered.connect(do_import)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
