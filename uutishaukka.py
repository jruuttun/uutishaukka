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


# Uutisjuttujen vertailufunktio;
# toistaiseksi vain tutkitaan, onko annettu html-tiedosto
# täsmälleen sama kuin uusi versio
def equal(oldVersion, newVersion):
    return oldVersion == newVersion

# Komentoriviargumentit (sys.argv)
import sys


# Ääkkösiä sisältävien nimien käsittelyä
# merkkikoodausongelmien väistämiseksi
import unicodedata

def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

# Käy läpi annetussa rss-itemissä viitatun jutun ja tallentaa jutulle
# uuden version, ellei kyseinen versio ole jo tallessa
def processItem(itemElement):
    itemTitle = itemElement.getElementsByTagName("title")[0].firstChild.data
    itemTitle = strip_accents(itemTitle)
    latestVersion = None
    print "**"
    if not os.path.exists(itemTitle):
        os.mkdir(itemTitle)
        print "Uusi uutisjuttu: " + itemTitle.encode('utf-8')
    else:
        versionNames = os.listdir(itemTitle)
        if len(versionNames) > 0: 
            versionNames.sort(); versionNames.reverse()
            print "Uutisjutun '" + itemTitle.encode('utf-8') + "' viimeisin versio: " + versionNames[0].encode('utf-8')
            latestVersion = versionNames[0]
    
    os.chdir(itemTitle)
    itemLink = itemElement.getElementsByTagName("link")[0].firstChild.data
    newVersion = datetime.now().isoformat()
    print "Haetaan juttu: " + itemLink
    versionDir = newVersion
    os.mkdir(versionDir)
    os.chdir(versionDir)
    os.system('wget --page-requisites --convert-links "' + itemLink + '"')
    os.chdir("..")
    os.chdir("..")


# Käy läpi syötteen jutut ja päivittää niiden tiedot syötedokumentin
# elementin channel->title mukaisiin hakemistoihin
# processItem-funktion avulla
def processChannel(path, rssDocument):
    os.chdir(path)
    channelNode = rssDocument.getElementsByTagName("channel")[0]
    channelTitle = channelNode.getElementsByTagName("title")[0].firstChild.data
    channelDir = channelTitle
    if not os.path.exists(channelDir):
        os.mkdir(channelDir)
        print "Uusi uutiskanava: " + channelDir
    os.chdir(channelDir)
    rssFile = open('rss.xml', 'w')
    rssFile.write(rssDocument.toxml().encode('utf-8'))
    rssFile.close()
    itemElements = channelNode.getElementsByTagName("item");
    for itemElement in itemElements:
        processItem(itemElement)


#### Pääohjelma #######
# Luetaan sisään syötteet, joita halutaan seurata
feedfile = open('feeds.list', 'r')
feeds = feedfile.readlines()
feedfile.close()

newsPath = '.'
if(len(sys.argv) > 1):
    newsPath = sys.argv[1]
    print "Uutiset viedään hakemistoon " + newsPath.encode('utf-8')
    os.chdir(newsPath)
else:
    print "Uutiset tallennetaan työhakemistoon"

newsPath = os.getcwd()


# käsitellään kaikki syötelistassa mainitut rss-syötteet
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
 

