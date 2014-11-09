'''
    Box XBMC Plugin
    Copyright (C) 2013-2014 ddurdle

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''

import os
import re
import urllib, urllib2
import cookielib
#from resources.lib import authorization
from cloudservice import cloudservice
#from resources.lib import folder
#from resources.lib import file
#from resources.lib import package
#from resources.lib import mediaurl
import unicodedata


import xbmc, xbmcaddon, xbmcgui, xbmcplugin

addon = xbmcaddon.Addon(id='plugin.video.box')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

import os
import sys

sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )

import authorization
#import cloudservice
import folder
import file
import package
import mediaurl

#
#
#
class box(cloudservice):


    AUDIO = 1
    VIDEO = 2
    PICTURE = 3

    MEDIA_TYPE_MUSIC = 1
    MEDIA_TYPE_VIDEO = 2
    MEDIA_TYPE_PICTURE = 3

    MEDIA_TYPE_FOLDER = 0

    CACHE_TYPE_MEMORY = 0
    CACHE_TYPE_DISK = 1
    CACHE_TYPE_AJAX = 2

    ##
    # initialize (save addon, instance name, user agent)
    ##
    def __init__(self, PLUGIN_URL, addon, instanceName, user_agent):
        self.PLUGIN_URL = PLUGIN_URL
        self.addon = addon
        self.instanceName = instanceName

        try:
            username = self.addon.getSetting(self.instanceName+'_username')
        except:
            username = ''
        self.authorization = authorization.authorization(username)


        self.cookiejar = cookielib.CookieJar()

        self.user_agent = user_agent


        self.login();



    ##
    # perform login
    ##
    def login(self):

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), MyHTTPErrorProcessor)
        opener.addheaders = [('User-Agent', self.user_agent)]

        url = 'https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=12&checkda=1&ct=1414903461&rver=6.4.6456.0&wp=MBI_SSL_SHARED&wreply=https:%2F%2Fonedrive.live.com%2Fabout%2Fauth%2F&lc=1033&id=250206&cbcxt=sky'


        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()

        for cookie in self.cookiejar:
            for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                cookieType,cookieValue = r.groups()
                if cookieType == 'MSPRequ':
                    self.authorization.setToken(cookieType,cookieValue)

        MSPRequ = self.authorization.getToken('MSPRequ')
        opener.addheaders = [('User-Agent', self.user_agent),('Cookie', 'MSPRequ='+MSPRequ + ';')]


        if (MSPRequ == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049)+ 'MSPRequ')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30049)+ 'MSPRequ', xbmc.LOGERROR)
            return


        url = 'https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=12&ct=1414903461&rver=6.4.6456.0&wp=MBI_SSL_SHARED&wreply=https:%2F%2Fonedrive.live.com%3Fgologin%3D1%26mkt%3Den-US&lc=1033&id=250206&cbcxt=sky&mkt=en-US&ODABID=1&ODABBKT=1&username='+self.authorization.username


        request = urllib2.Request(url)
        self.cookiejar.add_cookie_header(request)

        # try login
        try:
            response = opener.open(request)

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()

        PPFTValue=''
        for r in re.finditer('name\=\"PPFT\" id\=\"([^\"]+)\" value\=\"([^\"]+)\"',
                             response_data, re.DOTALL):
            PPFTID,PPFTValue = r.groups()

        for r in re.finditer('(uaid)\=([^\&]+)\&',
                             response_data, re.DOTALL):
            uaid,uaidValue = r.groups()
        PPFTValue = re.sub('\$', '%24', PPFTValue)
        PPFTValue = re.sub('!', '%21', PPFTValue)

        if (PPFTValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049)+ 'PPFTValue')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30049)+ 'PPFTValue', xbmc.LOGERROR)
            return


        for cookie in self.cookiejar:
            for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                cookieType,cookieValue = r.groups()
                if cookieType == 'MSPOK':
                    self.authorization.setToken(cookieType,cookieValue)



        url = 'https://login.live.com/ppsecure/post.srf?wa=wsignin1.0&rpsnv=12&ct=1414903462&rver=6.4.6456.0&wp=MBI_SSL_SHARED&wreply=https:%2F%2Fonedrive.live.com%3Fgologin%3D1%26mkt%3Den-US&lc=1033&id=250206&cbcxt=sky&mkt=en-US&ODABID=1&ODABBKT=1&username='+self.authorization.username+'&bk=1414903494&uaid='+uaidValue

        request = urllib2.Request(url)
#        self.cookiejar.add_cookie_header(request)

        MSPOK = self.authorization.getToken('MSPOK')
        opener.addheaders = [('Cookie', 'MSPOK='+MSPOK + ';')]

        if (MSPOK == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049)+ 'MSPOK')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30049)+ 'MSPOK', xbmc.LOGERROR)
            return

        # try login
        try:
#            response = opener.open(request,urllib.urlencode(values)+'&PPFT='+PPFTValue)
            response = opener.open(request,'login='+self.authorization.username+'&passwd='+self.addon.getSetting(self.instanceName+'_password')+'&KMSI=1&SI=Sign+in&type=11&PPFT='+PPFTValue+'&PPSX=Pass&idsbho=1&sso=0&NewUser=1&LoginOptions=1&i1=0&i2=1&i3=52992&i4=0&i7=0&i12=1&i13=1&i14=735&i15=5115&i17=0&i18=__Login_Strings%7C1%2C__Login_Core%7C1%2C')

        except urllib2.URLError, e:
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
            return
        response_data = response.read()
        response.close()


        for cookie in self.cookiejar:
            for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                cookieType,cookieValue = r.groups()
                if cookieType == 'WLSSC':
                    self.authorization.setToken(cookieType,cookieValue)
        return


    ##
    # return the appropriate "headers" for onedrive requests that include 1) user agent, 2) authorization cookie
    #   returns: list containing the header
    ##
    def getHeadersList(self):
        auth = self.authorization.getToken('auth_token')
        session = self.authorization.getToken('auth_session')
        if (auth != '' or session != ''):
            return [('User-Agent', self.user_agent), ('Cookie', session+'; oc_username='+self.authorization.username+'; oc_token='+auth+'; oc_remember_login=1')]
        else:
            return [('User-Agent', self.user_agent )]



    ##
    # return the appropriate "headers" for onedrive requests that include 1) user agent, 2) authorization cookie
    #   returns: URL-encoded header string
    ##
    def getHeadersEncoded(self):
        auth = self.authorization.getToken('auth_token')
        session = self.authorization.getToken('auth_session')

        if (auth != '' or session != ''):
            return urllib.urlencode({ 'User-Agent' : self.user_agent, 'Cookie' : session+'; oc_username='+self.authorization.username+'; oc_token='+auth+'; oc_remember_login=1' })
        else:
            return urllib.urlencode({ 'User-Agent' : self.user_agent })

    ##
    # retrieve a list of videos, using playback type stream
    #   parameters: prompt for video quality (optional), cache type (optional)
    #   returns: list of videos
    ##
    def getMediaList(self, folderName='', cacheType=CACHE_TYPE_MEMORY):

        if folderName == '':
            folderName = 'root'

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', self.user_agent)]

        WLSSC = self.authorization.getToken('WLSSC')

        if (WLSSC == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30050))
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30050), xbmc.LOGERROR)
            return


        url = 'https://onedrive.live.com/?gologin=1&mkt=en-US'

        opener.addheaders = [('User-Agent', self.user_agent),('Cookie', 'WLSSC='+WLSSC+';')]
        request = urllib2.Request(url)

        # if action fails, validate login

        try:
            response = opener.open(request)

        except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                return

        response_data = response.read()
        response.close()


        canaryValue=''
        for r in re.finditer('\"(canary)\"\:\"([^\"]+)\"' ,response_data, re.DOTALL):
            canaryID,canaryValue = r.groups()

        cidValue=''
        for r in re.finditer('profile\.live\.com\/(cid)\-([^\/]+)\/' ,response_data, re.DOTALL):
            cidID,cidValue = r.groups()




        canaryValue = re.sub('\\\\u003d\d', '=1', canaryValue)
        canaryValue = re.sub('\\\\u002b', '+', canaryValue)
        canaryValue = re.sub('\\\\u002f', '/', canaryValue)

        if (canaryValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049)+ 'canaryValue')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30049)+ 'canaryValue', xbmc.LOGERROR)
            return

        if (cidValue == ''):
            xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049)+ 'canaryValue')
            xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30049)+ 'canaryValue', xbmc.LOGERROR)
            return

        url = 'https://skyapi.onedrive.live.com/API/2/GetItems?id='+folderName+'&cid='+cidValue+'&group=0&qt=&ft=&sb=0&sd=0&gb=0%2C1%2C2&rif=0&d=1&iabch=1&caller='+cidValue+'&path=1&si=0&ps=100&pi=5&m=en-US&rset=skyweb&lct=1&v=0.8593795660417527'

        opener.addheaders = [('User-Agent', self.user_agent), ('Canary', canaryValue),('AppId','1141147648'),('Accept','application/json'),('Cookie', 'WLSSC='+WLSSC+';')]
        request = urllib2.Request(url)

        # if action fails, validate login

        try:
            response = opener.open(request)

        except urllib2.URLError, e:
                xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                return

        response_data = response.read()
        response_data = re.sub("\n", '', response_data)
        response.close()


        mediaFiles = []
        # parsing page for files
        for r in re.finditer('\{\"audio\"\:.*?\"userRole\"\:0\}' ,response_data, re.DOTALL):
                entry = r.group()
                for q in re.finditer('\"(download)\"\:\"([^\"]+)\",' ,entry, re.DOTALL):
                    downloadID,downloadURL = q.groups()
                for q in re.finditer('\"(title)\"\:\"([^\"]+)\",' ,entry, re.DOTALL):
                    titleID,title = q.groups()

                downloadURL = re.sub('\\\\', '', downloadURL)
                downloadURL = re.sub('\%20', '+', downloadURL)

                media = package.package(file.file(title, title, title, self.AUDIO, '', ''),folder.folder('',''))
                media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                mediaFiles.append(media)

        for r in re.finditer('\"mimeType\"\:\"video.*?\"userRole\"\:0' ,response_data, re.DOTALL):
                entry = r.group()
                for q in re.finditer('\"(download)\"\:\"([^\"]+)\",' ,entry, re.DOTALL):
                    downloadID,downloadURL = q.groups()
                for q in re.finditer('\"(name)\"\:\"([^\"]+)\",\"orderedFriendlyName\"' ,entry, re.DOTALL):
                    titleID,title = q.groups()

                downloadURL = re.sub('\\\\', '', downloadURL)
                downloadURL = re.sub('\%20', '+', downloadURL)

                media = package.package(file.file(title, title, title, self.VIDEO, '', ''),folder.folder('',''))
                media.setMediaURL(mediaurl.mediaurl(downloadURL, '','',''))
                mediaFiles.append(media)

        for r in re.finditer('\{\"commands\"\:.*?\"userRole\"\:0\}' ,response_data, re.DOTALL):
                entry = r.group()
                for q in re.finditer('\"(id)\"\:\"([^\"]+)\",' ,entry, re.DOTALL):
                    folderID,folderIDName = q.groups()
                for q in re.finditer('\"(name)\"\:\"([^\"]+)\",\"orderedFriendlyName\"' ,entry, re.DOTALL):
                    titleID,title = q.groups()
                folderIDName = re.sub('!', '%21', folderIDName)

                media = package.package(0,folder.folder(folderIDName,title))
                mediaFiles.append(media)


        return mediaFiles


    ##
    # retrieve a playback url
    #   returns: url
    ##
    def getPlaybackCall(self, playbackType, package):

                downloadURL = package.getMediaURL()
                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
                opener.addheaders = [('User-Agent', self.user_agent)]
                downloadURL = re.sub(' ', '+', downloadURL)
                request = urllib2.Request(downloadURL)

                # if action fails, validate login

                try:
                    response2 = opener.open(request)

                except urllib2.URLError, e:
                        xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                        return

                response2_data = response2.read()
                response2.close()

                formSubmission = {}
                for t in re.finditer('id\=\"([^\"]+)\" value\=\"([^\"]+)\"' ,response2_data, re.DOTALL):
                    formItemName,formItemValue = t.groups()
                    formSubmission[formItemName] = formItemValue

                submitURL=''
                for t in re.finditer('id\=\"(fmHF)\" action\=\"([^\"]+)\"' ,response2_data, re.DOTALL):
                    submitName,submitURL = t.groups()

                if (submitURL == ''):
                    xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049)+ 'submitURL')
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30049)+ 'submitURL', xbmc.LOGERROR)
                    return


                MSPOK = self.authorization.getToken('MSPOK')
                opener.addheaders = [('User-Agent', self.user_agent), ('Cookie', 'MSPOK='+MSPOK + ';')]


                if (MSPOK == ''):
                    xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049)+ 'MSPOK')
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30049)+ 'MSPOK', xbmc.LOGERROR)
                    return

                try:

                    response2 = opener.open(submitURL,urllib.urlencode(formSubmission))

                except urllib2.URLError, e:
                        xbmc.log(self.addon.getAddonInfo('name') + ': ' + str(e), xbmc.LOGERROR)
                        return

                response2_data = response2.read()
                response2.close()

                cookieString = ''
                for cookie in self.cookiejar:
                    for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                        cookieType,cookieValue = r.groups()
                        cookieString = cookieString + cookieType + '='+ cookieValue + ';'

                if (cookieString == ''):
                    xbmcgui.Dialog().ok(self.addon.getLocalizedString(30000), self.addon.getLocalizedString(30049)+ 'cookieString')
                    xbmc.log(self.addon.getAddonInfo('name') + ': ' + self.addon.getLocalizedString(30049)+ 'cookieString', xbmc.LOGERROR)
                    return

                return downloadURL + '|' + urllib.urlencode({ 'User-Agent' : self.user_agent, 'Cookie' : cookieString })


    ##
    # retrieve a media url
    #   returns: url
    ##
    def getMediaCall(self, package):
        return #not implemented

    ##
    # retrieve a directory url
    #   returns: url
    ##
    def getDirectoryCall(self, folder):
        return self.PLUGIN_URL+'?mode=folder&instance='+self.instanceName+'&directory='+folder.id



class MyHTTPErrorProcessor(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        # only add this line to stop 302 redirection.
        if code == 302: return response

        if not (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)
        return response

    https_response = http_response

