# -*- mode: python ; coding: utf-8 -*-
"""
Anki Add-on: Reset profile - remove all decks, notetypes, tags, media for version 2.1.x

Updated December 28, 2020

Reset profile to a new one. Removes all decks, notetypes, tags and also clear collection media. 

Copyright: (c) Venkata Ramana P 2020 <github/itsmepvr>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

Initializes add-on components.
"""

import os
import sys
import json
import time
import shutil
from aqt import mw
from aqt.deckbrowser import DeckBrowser
from aqt.utils import showInfo, askUser
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QAction, QProgressDialog
from anki.lang import _
import requests
from anki.hooks import wrap, addHook
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin


class Reset_Profile:
    def __init__(self):
        if askUser((_("Are you sure you wish to reset profile ? This removes everything in current profile and cannot be undone."))):
            mw.progress.start(immediate=True)
            self.collection_path = self.getCollectionPath()
            self.decks = mw.col.decks
            self.removeDecks()
            self.clearNoteTypes()
            self.clearTags()
            self.clearMedia()
            mw.progress.finish()
            mw.moveToState("deckBrowser")
            showInfo("Profile Reset Done.")

    def removeDecks(self):
        try:
            self.startEditing()
            self.deck_names = self.deckNames()
            while len(self.deck_names) > 1:
                for deck in self.deck_names:
                    did = self.decks.id(deck)
                    self.decks.rem(did, True)
                    self.deck_names = self.deckNames()
        finally:
            self.stopEditing()

    def clearNoteTypes(self):
        for model in mw.col.models.all():
            mw.col.models.rem(model)
        self.startEditing()

    def clearTags(self):
        mw.col.tags.registerNotes()

    def clearMedia(self):
        path = self.getCollectionPath()
        if os.path.exists(path):
            shutil.rmtree(path)
            os.mkdir(path)

    def startEditing(self):
        mw.requireReset()

    def stopEditing(self):
        if mw.col is not None:
            mw.maybeReset()

    def deckNames(self):
        return self.decks.allNames()

    def getCollectionPath(self):
        self.ankifolder = mw.pm._defaultBase()
        # Get to profile folder
        if not mw.pm.name:
            profs = mw.pm.profiles()
            mw.pm.load(profs[0])
        if not mw.pm.name:
            mw.showProfileManager()
        profilename = mw.pm.name
        collectionPath = os.path.join(
            self.ankifolder, profilename+"/collection.media")
        return collectionPath


# Adding download button on menubar in Anki browser
action = QAction("Reset Profile", mw)
action.triggered.connect(Reset_Profile)
mw.form.menuTools.addAction(action)


def checkState(*args):
    if mw.state == 'deckBrowser':
        action.setVisible(True)
    else:
        action.setVisible(False)


addHook('beforeStateChange', checkState)
