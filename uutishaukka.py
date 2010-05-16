#!/usr/bin/env python
# -*- coding: utf-8 -*-

# HTTP-liikennöinti
import urllib2

# XML-dokumentin simppeli DOM-api
from xml.dom import minidom

# Tiedostojärjestelmän käyttö
import os

# Päivämäärien ja kellonaikojen käsittly
from datetime import datetime

# Komentoriviargumentit (sys.argv)
import sys

# Ääkkösiä sisältävien nimien käsittelyä
# merkkikoodausongelmien väistämiseksi
import unicodedata
import string

safeChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
def makeSafeFilename(filename):
    unaccented = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in unaccented if c in safeChars)

encoding = 'utf-8'

# Hakee ja tallentaa anntussa rss-itemissä viitatun jutun tiedostojärjestelmään
def processItem(itemElement):
    titleElement = itemElement.getElementsByTagName("title")[0]
    if titleElement is None or titleElement.firstChild is None:
        print "Otsikkoa ei voitu lukea!"
        return
    itemTitle = titleElement.firstChild.data
    itemTitle = makeSafeFilename(itemTitle)
    latestVersion = None
    print "**"
    if not os.path.exists(itemTitle):
        os.mkdir(itemTitle)
        print "Uusi uutisjuttu: " + itemTitle.encode(encoding)
    else:
        versionNames = os.listdir(itemTitle)
        if len(versionNames) > 0: 
            versionNames.sort(); versionNames.reverse()
            print "Uutisjutun '" + itemTitle.encode(encoding) + "' viimeisin versio: " + versionNames[0].encode(encoding)
            latestVersion = versionNames[0]
    
    os.chdir(itemTitle)
    itemLink = itemElement.getElementsByTagName("link")[0].firstChild.data
    newVersion = datetime.now().isoformat()
    print "Haetaan juttu: " + itemLink
    versionDir = newVersion
    os.mkdir(versionDir)
    os.chdir(versionDir)
    os.system('wget -q --page-requisites --convert-links "' + itemLink + '"')
    os.chdir("..")
    os.chdir("..")


# Käy läpi syötteen jutut ja vie niiden tiedot syötedokumentin
# elementin channel->title mukaisiin hakemistoihin
# processItem-funktion avulla
def processChannel(path, rssDocument):
    os.chdir(path)
    channelNode = rssDocument.getElementsByTagName("channel")[0]
    titleElement = channelNode.getElementsByTagName("title")[0]
    channelTitle = unicode('no-channel-title')
    if titleElement.firstChild is not None:
        channelTitle = titleElement.firstChild.data
    channelDir = makeSafeFilename(channelTitle)
    if not os.path.exists(channelDir):
        os.mkdir(channelDir)
        print "Uusi uutiskanava: " + channelDir
    os.chdir(channelDir)
    rssFile = open('rss.xml', 'w')
    rssFile.write(rssDocument.toxml().encode(encoding))
    rssFile.close()
    itemElements = channelNode.getElementsByTagName("item");
    for itemElement in itemElements:
        processItem(itemElement)


#### Pääohjelma #######
# Luetaan sisään syötteet, joita halutaan seurata
feedfile = open('feeds.list', 'r')
feeds = feedfile.readlines()
feedfile.close()

newsPath = './data'
if(len(sys.argv) > 1):
    newsPath = sys.argv[1]
print "Uutiset viedään hakemistoon " + newsPath.encode(encoding)
if not os.path.isdir(newsPath):
    print "Hakemistoa " + newsPath + " ei ole, se luodaan."
    os.mkdir(newsPath)

os.chdir(newsPath)
newsPath = os.getcwd()


# Käsitellään kaikki syötelistassa mainitut rss-syötteet
for feed in feeds:
    print "*** Syote: " + feed
    try:
        file = urllib2.urlopen(feed)
        rssString = file.read()
        rssDocument = minidom.parseString(rssString);
        processChannel(newsPath, rssDocument)
        file.close()
    except urllib2.URLError:
        print "Syöte ei saatavilla, jatketaan seuraavaan"
 

