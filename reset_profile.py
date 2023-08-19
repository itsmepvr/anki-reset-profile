import os
import shutil
from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, askUser, showText
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QAction, QProgressDialog
from anki import version as anki_version


class Ui_resetDialog(object):
    def setupUi(self, resetDialog):
        if not resetDialog.objectName():
            resetDialog.setObjectName(u"resetDialog")
        resetDialog.resize(291, 277)
        self.buttonBox = QDialogButtonBox(resetDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 230, 261, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.label = QLabel(resetDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(50, 10, 191, 41))
        self.label.setStyleSheet(u"font-size:30px;")
        self.decks = QCheckBox(resetDialog)
        self.decks.setObjectName(u"checkBox")
        self.decks.setGeometry(QRect(50, 60, 191, 31))
        self.decks.setStyleSheet(u"font-size:18px;")
        self.decks.setChecked(True)
        self.notetypes = QCheckBox(resetDialog)
        self.notetypes.setObjectName(u"checkBox_2")
        self.notetypes.setGeometry(QRect(50, 100, 201, 31))
        self.notetypes.setStyleSheet(u"font-size:18px;")
        self.notetypes.setChecked(True)
        self.tags = QCheckBox(resetDialog)
        self.tags.setObjectName(u"checkBox_3")
        self.tags.setGeometry(QRect(50, 140, 191, 31))
        self.tags.setStyleSheet(u"font-size:18px;")
        self.tags.setChecked(True)
        self.media = QCheckBox(resetDialog)
        self.media.setObjectName(u"checkBox_4")
        self.media.setGeometry(QRect(50, 180, 191, 31))
        self.media.setStyleSheet(u"font-size:18px;")
        self.media.setChecked(True)

        self.retranslateUi(resetDialog)
        self.r = resetDialog
        self.buttonBox.accepted.connect(self.reset_profile)
        self.buttonBox.rejected.connect(resetDialog.reject)

        QMetaObject.connectSlotsByName(resetDialog)

    def retranslateUi(self, resetDialog):
        resetDialog.setWindowTitle(QCoreApplication.translate(
            "resetDialog", u"Reset Profile", None))
        self.label.setText(QCoreApplication.translate(
            "resetDialog", u"Reset Profile", None))
        self.decks.setText(QCoreApplication.translate(
            "resetDialog", u"Remove Decks", None))
        self.notetypes.setText(QCoreApplication.translate(
            "resetDialog", u"Remove Notetypes", None))
        self.tags.setText(QCoreApplication.translate(
            "resetDialog", u"Remove Tags", None))
        self.media.setText(QCoreApplication.translate(
            "resetDialog", u"Remove Media", None))

    # reset profile
    def reset_profile(self):
        decks = self.decks.isChecked()
        notetypes = self.notetypes.isChecked()
        tags = self.tags.isChecked()
        media = self.media.isChecked()
        text = ''
        if decks:
            text = ' decks'
        if notetypes:
            text += ', notetypes'
        if tags:
            text += ', tags'
        if tags:
            text += ', media'

        if not askUser((_(f"Are you sure you wish to reset profile ? This removes {text} in current profile and cannot be undone."))):
            self.close()
            return
        mw.progress.start(immediate=True)
        self.decks = mw.col.decks
        self.collection_path = self.getCollectionPath()
        self.errors = []
        if decks:
            self.removeDecks()
        if notetypes:
            self.removeNotetypes()
        if tags:
            self.removeTags()
        if media:
            self.removeMedia()
        mw.maybeReset()
        mw.reset()
        mw.progress.finish()
        if len(self.errors) > 0:
            showText("\n".join(self.errors))
        else:
            showInfo('Profile reset done..')
        self.r.close()

    # remove decks
    def removeDecks(self):
        try:
            if anki_version.startswith('2.1.4'):
                self.deck_names = self.decks.allNames()
                while len(self.deck_names) > 1:
                    for deck in self.deck_names:
                        did = self.decks.id(deck)
                        self.decks.rem(did, True)
                        self.deck_names = self.decks.allNames()
            else:
                deck_names = self.decks.all_names_and_ids()
                deck_ids = []
                for deck in deck_names:
                    deck_ids.append(deck.id)
                self.decks.remove(deck_ids)
        except:
            self.errors.append('Unable to delete decks')

    # remove notetypes
    def removeNotetypes(self):
        try:
            mw.col.models.remove_all_notetypes()
        except:
            self.errors.append('Unable to delete notetypes')

    # remove tags
    def removeTags(self):
        try:
            mw.col.tags.clear_unused_tags()
        except:
            self.errors.append('Unable to delete tags')

    # remove media
    def removeMedia(self):
        try:
            if os.path.exists(self.collection_path):
                shutil.rmtree(self.collection_path)
                os.mkdir(self.collection_path)
        except:
            self.errors.append('Unable to delete media')

    # collection.media path
    def getCollectionPath(self):
        return os.path.join(
            mw.pm.base, mw.pm.name, 'collection.media')


# Main Dialog
class MyDialog(QDialog):
    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent, Qt.WindowType.Window)
        self.dialog = Ui_resetDialog()
        self.dialog.setupUi(self)


# Function to handle reset profile
def onResetProfile():
    dialog = MyDialog()
    if dialog.exec():
        showInfo('Dialog closed')


# Add action to menu
a = QAction(mw)
a.setText('Reset Profile')
mw.form.menuTools.addAction(a)
a.triggered.connect(onResetProfile)
