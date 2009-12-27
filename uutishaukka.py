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

# Käy läpi annetussa rss-itemissä viitatun jutun ja tallentaa jutulle
# uuden version, ellei kyseinen versio ole jo tallessa
def processItem(channelTitle, itemElement):
    itemTitle = itemElement.getElementsByTagName("title")[0].firstChild.data
    itemDir = channelTitle + os.sep + itemTitle
    latestVersionHtml = None
    print "**"
    if not os.path.exists(itemDir):
        os.mkdir(itemDir)
        print "Uusi uutisjuttu: " + itemDir
    else:
        versionNames = os.listdir(itemDir)
        if len(versionNames) > 0: 
#            print "Uutisjutun '" + itemDir + "' versiot: "
#            for versionName in versionNames: 
#                print " " + versionName
            versionNames.sort(); versionNames.reverse()
            print "Uutisjutun '" + itemDir + "' viimeisin versio: " + versionNames[0]
            latestVersionFile = open(itemDir + os.sep + versionNames[0], 'r');
            latestVersionHtml = latestVersionFile.read()
        
    itemLink = itemElement.getElementsByTagName("link")[0].firstChild.data
    storyHtml = urllib2.urlopen(itemLink).read()
    saveVersion = True

    if latestVersionHtml is not None:
        print "Vertaillaan viimeista versiota tamanhetkiseen: " + itemLink
        if latestVersionHtml == storyHtml:
            saveVersion = False
            print "Ei muutoksia edellisen ajon jalkeen"
        else:
            print "Tallennetaan uusi versio"
        
    if saveVersion:
        storyFilename = datetime.now().isoformat() + ".html"
        storyPath = itemDir + os.sep + storyFilename
        if latestVersionHtml is not None:
            print "Ensimmainen versio:" + storyPath
        else:
            print "Uusi versio: " + storyPath
        storyFile = open(storyPath, 'w');
        storyFile.write(storyHtml);
        storyFile.close();
        

# Käy läpi syötteen jutu ja päivittää niiden tiedot syötedokumentin
# elementin channel->title mukaisiin hakemistoihin
# processItem-funktion avulla
def processChannel(rssDocument):
#    print rssDocument.toxml()
    channelNode = rssDocument.getElementsByTagName("channel")[0]
    channelTitle = channelNode.getElementsByTagName("title")[0].firstChild.data
    if not os.path.exists(channelTitle):
        os.mkdir(channelTitle)
        print "Uusi uutissyote: " + channelTitle
    itemElements = channelNode.getElementsByTagName("item");
    for itemElement in itemElements:
        processItem(channelTitle, itemElement)



# Luetaan sisään syötteet, joita halutaan seurata
feedfile = open('feeds.list', 'r')
feeds = feedfile.readlines()
feedfile.close()

# käsitellään kaikki syötelistassa mainitut rss-syötteet
for feed in feeds:
    print "*** Syote: " + feed
    file = urllib2.urlopen(feed)
    rssString = file.read()
    rssDocument = minidom.parseString(rssString);
    processChannel(rssDocument)
    file.close()


