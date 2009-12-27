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

# Käy läpi annetussa rss-itemissä viitatun jutun ja tallentaa jutulle
# uuden version, ellei kyseinen versio ole jo tallessa
def processItem(channelDir, itemElement):
    itemTitle = itemElement.getElementsByTagName("title")[0].firstChild.data
    itemDir = channelDir + os.sep + itemTitle
    latestVersionHtml = None
    print "**"
    if not os.path.exists(itemDir):
        os.mkdir(itemDir)
        print "Uusi uutisjuttu: " + itemDir.encode('utf-8')
    else:
        versionNames = os.listdir(itemDir)
        if len(versionNames) > 0: 
            versionNames.sort(); versionNames.reverse()
            print "Uutisjutun '" + itemDir.encode('utf-8') + "' viimeisin versio: " + versionNames[0].encode('utf-8')
            latestVersionFile = open(itemDir + os.sep + versionNames[0], 'r');
            latestVersionHtml = latestVersionFile.read()
            latestVersionFile.close()
        
    itemLink = itemElement.getElementsByTagName("link")[0].firstChild.data
    print "Haetaan juttu: " + itemLink
    try:
        storyHtml = urllib2.urlopen(itemLink).read()
        saveVersion = True
        
        if latestVersionHtml is not None:
            print "Vertaillaan juttua viimeisimpään versioon..."
            if equal(latestVersionHtml, storyHtml):
                saveVersion = False
                print "Ei muutoksia edellisen ajon jalkeen"
            else:
                print "Juttu muuttunut, tallennetaan uusi versio"
                
                if saveVersion:
                    storyFilename = datetime.now().isoformat() + ".html"
                    storyPath = itemDir + os.sep + storyFilename
                    if latestVersionHtml is None:
                        print "Ensimmäinen versio:" + storyPath.encode('utf-8')
                    else:
                        print "Uusi versio: " + storyPath.encode('utf-8')
                        storyFile = open(storyPath, 'w');
                        storyFile.write(storyHtml);
                        storyFile.close();
    except urllib2.URLError, urlError:
        print "Juttu ei ole saatavilla: ", urlError 


# Käy läpi syötteen jutut ja päivittää niiden tiedot syötedokumentin
# elementin channel->title mukaisiin hakemistoihin
# processItem-funktion avulla
def processChannel(path, rssDocument):
    channelNode = rssDocument.getElementsByTagName("channel")[0]
    channelTitle = channelNode.getElementsByTagName("title")[0].firstChild.data
    channelDir = path + os.sep + channelTitle
    if not os.path.exists(channelDir):
        os.mkdir(channelDir)
        print "Tallennetaan uusi uutiskanava: " + channelDir
    itemElements = channelNode.getElementsByTagName("item");
    for itemElement in itemElements:
        processItem(channelDir, itemElement)


#### Pääohjelma #######
newsPath = '.'
if(len(sys.argv) > 1):
    newsPath = sys.argv[1]
    print "Uutiset viedään hakemistoon " + newsPath.encode('utf-8')
else:
    print "Uutiset tallennetaan työhakemistoon"


# Luetaan sisään syötteet, joita halutaan seurata
feedfile = open('feeds.list', 'r')
feeds = feedfile.readlines()
feedfile.close()

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
 

