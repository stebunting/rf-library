#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import Python Modules
import requests
from lxml import html
import os
import datetime
import xml.etree.ElementTree as ET

class LoginError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

################################################################################
##########                     PMSE LOOKUP OBJECT                     ##########
################################################################################

# Define PMSE Lookup class
class PMSELookup(object):

    # Initialise class
    def __init__(self, account_name, username, password):
        self.account_name = account_name
        self.username = username
        self.password = password
        self.request_session = None
        self.viewstate = '/wEPDwULLTE3NDg5MjE3MTUPZBYCZg9kFgICAQ9kFgICBQ9kFgICAg8PFgIeB1Zpc2libGVoZGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFGGN0bDAwJG1jcGgkbXlMb2dvbiRjdGwwMSG/qFz0Dd2NuKGYWg6Ip1M9J0yi'
        self.viewstategenerator = '0E9A1EEB'

        self.date = datetime.datetime.utcnow()
        self.datenum = self.date.day
        self.monthyear = self.date.strftime("%b %Y")
        self.datemonthyear = self.date.strftime("%d %b, %Y")
        self.monthdateyear = self.date.strftime("%b %d, %Y")
        self.hdupper = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%b %d, %Y %H:%M")

    # Login to PMSE site
    def login(self):
        #return True
        url = 'https://pmse.ofcom.org.uk/Pmse/Ecom/loginpage.aspx'

        # Define data payload
        payload = {
            '__VIEWSTATE': self.viewstate,
            '__VIEWSTATEGENERATOR': self.viewstategenerator,
            'strClientCompanyLogon': self.account_name,
            'strClientUserLogon': self.username,
            'strClientPassword': self.password,
            'rememberMe': 'false',
            'ctl00$mcph$myLogon': 'ctl00$mcph$myLogon',
            'ctl00$mcph$btnContinueLogon': 'Continue'
        }
        # POST data for main Login button
        # payload['ctl00$mcph$myLogon$ctl00' = 'Login'

        # Start session
        self.request_session = requests.session()
        #result = self.request_session.get(url)

        # Return false if login page get unsuccessful
        #if not 200 <= result.status_code < 300:
        #    return False

        # Get data from login page form
        #tree = html.fromstring(result.text)
        #self.viewstate = tree.xpath("//*[@id=\"__VIEWSTATE\"]/@value")[0]
        #self.viewstategenerator = tree.xpath("//*[@id=\"__VIEWSTATEGENERATOR\"]/@value")[0]
        #payload['__VIEWSTATE'] = self.viewstate
        #payload['__VIEWSTATEGENERATOR'] = self.viewstategenerator
        
        # Define headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
            'Referer': url
        }

        # Log-in to PMSE site
        try:
            result = self.request_session.post(
                url, 
                data=payload,
                headers=headers
            )
        except ConnectionError as e:
            return e

        # Check page
        tree = html.fromstring(result.text)
        title = tree.xpath("//title/text()")[0].strip()

        if title == "PMSE Login":
            raise LoginError('Login Error')

        # Return true if login successful else false
        if 200 <= result.status_code < 300:
            return True
        else:
            return False

    # Method to logout
    def logout(self):
        url = 'https://pmse.ofcom.org.uk/pmse/ecom/private/logoutpage.aspx'

        # Define data payload
        payload = {
            'ctl00$mcph$btnContinue': 'Click here to complete'
        }

        # Start session
        result = self.request_session.get(url)

        # Return false if logout page get unsuccessful
        if not 200 <= result.status_code < 300:
            return False

        # Get data from login page form
        tree = html.fromstring(result.text)
        payload['__VIEWSTATE'] = tree.xpath("//*[@id=\"__VIEWSTATE\"]/@value")[0]
        payload['__VIEWSTATEGENERATOR'] = tree.xpath("//*[@id=\"__VIEWSTATEGENERATOR\"]/@value")[0]
        
        # Define headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
            'Referer': url
        }

        # Log-in to PMSE site
        result = self.request_session.post(
            url, 
            data=payload,
            headers=headers
        )

        # Check page
        tree = html.fromstring(result.text)
        title = tree.xpath("//title/text()")[0].strip()
        self.request_session = None
        
        # Return true if login successful else false
        if not 200 <= result.status_code < 300 or title != "PMSE Login":
            return False
        else:
            return True

    # Method to return data from PMSE database
    def getList(self, location):
        url = 'https://pmse.ofcom.org.uk/pmse/wireless/private/microphonedate.aspx'

        payload = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            'ctl00$hdnJavaPostback': '',
            'ctl00$mcph$When$dtStart$ddlDay': self.datenum,
            'ctl00$mcph$When$dtStart$ddlMonthYear': self.monthyear,
            'ctl00$mcph$When$dtStart$ddlHour': 0,
            'ctl00$mcph$When$dtStart$ddlMinute': 0,
            'ctl00$mcph$When$dtStart$hdDateTime': self.datemonthyear + " 00:00",
            'ctl00$mcph$When$dtStart$hdLower': self.monthdateyear + " 00:00",
            'ctl00$mcph$When$dtStart$hdUpper': self.hdupper,
            'ctl00$mcph$When$dtFinish$ddlDay': self.date,
            'ctl00$mcph$When$dtFinish$ddlMonthYear': self.monthyear,
            'ctl00$mcph$When$dtFinish$ddlHour': 23,
            'ctl00$mcph$When$dtFinish$ddlMinute': 59,
            'ctl00$mcph$When$dtFinish$hdDateTime': self.datemonthyear + " 23:59",
            'ctl00$mcph$When$dtFinish$hdLower': self.monthdateyear + " 00:00",
            'ctl00$mcph$When$dtFinish$hdUpper': self.hdupper,
            'ctl00_mcph_Where_radLocation3': 'radLocation3',
            'ctl00$mcph$Where$LocationListName': location,
            'ctl00$mcph$Where$btnSearch': 'Find >'
        }

        result = self.request_session.get(url)

        # Return false if login page get unsuccessful
        if not 200 <= result.status_code < 300:
            return False

        # Get data from login page form
        tree = html.fromstring(result.text)
        self.viewstate = tree.xpath("//*[@id=\"__VIEWSTATE\"]/@value")[0]
        self.viewstategenerator = tree.xpath("//*[@id=\"__VIEWSTATEGENERATOR\"]/@value")[0]
        payload['__VIEWSTATE'] = self.viewstate
        payload['__VIEWSTATEGENERATOR'] = self.viewstategenerator
        
        # Define headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
            'Referer': url
        }

        # Get result
        result = self.request_session.post(
            url, 
            data=payload,
            headers=headers
        )

        # Check page
        tree = html.fromstring(result.text)
        locations = tree.xpath("//*[@id=\"ctl00_mcph_Where_LocationList\"]/option/text()")
        locationIDs = tree.xpath("//*[@id=\"ctl00_mcph_Where_LocationList\"]/option/@value")
        locations.pop(0)
        locationIDs.pop(0)

        print([locations, locationIDs])
        return [locations, locationIDs]

    # Method to return data from PMSE database
    def getData(self, id):
        #return {60: {'IndoorQuality': 4, 'OutdoorExclude': False}, 59: {'IndoorQuality': 4, 'OutdoorExclude': False}, 58: {'IndoorQuality': 4, 'OutdoorExclude': False}, 57: {'IndoorQuality': 4, 'OutdoorExclude': False}, 56: {'IndoorQuality': 4, 'OutdoorExclude': False}, 55: {'IndoorQuality': 4, 'OutdoorExclude': False}, 54: {'IndoorQuality': 4, 'OutdoorExclude': False}, 53: {'IndoorQuality': 4, 'OutdoorExclude': False}, 52: {'IndoorQuality': 4, 'OutdoorExclude': False}, 51: {'IndoorQuality': 4, 'OutdoorExclude': False}, 50: {'IndoorQuality': 4, 'OutdoorExclude': False}, 49: {'IndoorQuality': 4, 'OutdoorExclude': False}, 48: {'IndoorQuality': 4, 'OutdoorExclude': False}, 47: {'IndoorQuality': 1, 'OutdoorExclude': True}, 46: {'IndoorQuality': 4, 'OutdoorExclude': False}, 45: {'IndoorQuality': 4, 'OutdoorExclude': False}, 44: {'IndoorQuality': 1, 'OutdoorExclude': True}, 43: {'IndoorQuality': 4, 'OutdoorExclude': False}, 42: {'IndoorQuality': 4, 'OutdoorExclude': False}, 41: {'IndoorQuality': 1, 'OutdoorExclude': True}, 40: {'IndoorQuality': 4, 'OutdoorExclude': False}, 39: {'IndoorQuality': 4, 'OutdoorExclude': False}, 37: {'IndoorQuality': 1, 'OutdoorExclude': True}, 36: {'IndoorQuality': 4, 'OutdoorExclude': False}, 35: {'IndoorQuality': 4, 'OutdoorExclude': False}, 34: {'IndoorQuality': 4, 'OutdoorExclude': False}, 33: {'IndoorQuality': 4, 'OutdoorExclude': False}, 32: {'IndoorQuality': 4, 'OutdoorExclude': False}, 31: {'IndoorQuality': 1, 'OutdoorExclude': True}, 30: {'IndoorQuality': 4, 'OutdoorExclude': False}, 29: {'IndoorQuality': 1, 'OutdoorExclude': True}, 28: {'IndoorQuality': 3, 'OutdoorExclude': True}, 27: {'IndoorQuality': 3, 'OutdoorExclude': True}, 26: {'IndoorQuality': 4, 'OutdoorExclude': False}, 25: {'IndoorQuality': 3, 'OutdoorExclude': True}, 24: {'IndoorQuality': 2, 'OutdoorExclude': True}, 23: {'IndoorQuality': 1, 'OutdoorExclude': True}, 22: {'IndoorQuality': 2, 'OutdoorExclude': True}, 21: {'IndoorQuality': 2, 'OutdoorExclude': True}, 61: {'IndoorQuality': 1, 'OutdoorExclude': True}, 62: {'IndoorQuality': 1, 'OutdoorExclude': True}, 63: {'IndoorQuality': 1, 'OutdoorExclude': True}, 64: {'IndoorQuality': 1, 'OutdoorExclude': True}, 65: {'IndoorQuality': 1, 'OutdoorExclude': True}, 66: {'IndoorQuality': 1, 'OutdoorExclude': True}, 67: {'IndoorQuality': 1, 'OutdoorExclude': True}, 68: {'IndoorQuality': 1, 'OutdoorExclude': True}, 69: {'IndoorQuality': 1, 'OutdoorExclude': True}, 38: {'IndoorQuality': 4, 'OutdoorExclude': False}}

        url = 'https://pmse.ofcom.org.uk/pmse/wireless/private/microphonedate.aspx'

        payload = {
            '__EVENTTARGET': id,
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': self.viewstate,
            '__VIEWSTATEGENERATOR': self.viewstategenerator,
            'ctl00$hdnJavaPostback': '',
            'ctl00$mcph$When$dtStart$ddlDay': self.date,
            'ctl00$mcph$When$dtStart$ddlMonthYear': self.monthyear,
            'ctl00$mcph$When$dtStart$ddlHour': 0,
            'ctl00$mcph$When$dtStart$ddlMinute': 0,
            'ctl00$mcph$When$dtStart$hdDateTime': self.datemonthyear + " 00:00",
            'ctl00$mcph$When$dtStart$hdLower': self.monthdateyear + " 00:00",
            'ctl00$mcph$When$dtStart$hdUpper': self.hdupper,
            'ctl00$mcph$When$dtFinish$ddlDay': self.date,
            'ctl00$mcph$When$dtFinish$ddlMonthYear': self.monthyear,
            'ctl00$mcph$When$dtFinish$ddlHour': 23,
            'ctl00$mcph$When$dtFinish$ddlMinute': 59,
            'ctl00$mcph$When$dtFinish$hdDateTime': self.datemonthyear + " 23:59",
            'ctl00$mcph$When$dtFinish$hdLower': self.monthdateyear + " 00:00",
            'ctl00$mcph$When$dtFinish$hdUpper': self.hdupper,
            'ctl00$mcph$Where$LocationGroup': 'radLocation3',
            'ctl00$mcph$Where$PostCode': '',
            'ctl00$mcph$Where$Square': 'CA',
            'ctl00$mcph$Where$Easting': '',
            'ctl00$mcph$Where$Northing': '',
            'ctl00$mcph$Where$LocationList': id
        }

        # Define headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
            'Referer': url
        }

        # Get result
        result = self.request_session.post(
            url, 
            data=payload,
            headers=headers
        )

        # Scrape information
        tree = html.fromstring(result.text)
        data = dict()
        channels = tree.xpath("//table[@id=\"ctl00_mcph_grdAvailabilities\"]/tr/td[1]/text()")
        indoor = tree.xpath("//table[@id=\"ctl00_mcph_grdAvailabilities\"]/tr/td[2]/div/img/@src")
        outdoor = tree.xpath("//table[@id=\"ctl00_mcph_grdAvailabilities\"]/tr/td[3]/div/span/text()")

        # Combine data into a dictionary
        for (ch, inside, outside) in zip(channels, indoor, outdoor):
            ch = int(ch)
            data[ch] = dict()
            data[ch]['IndoorQuality'] = int(os.path.basename(inside)[12:13])
            if outside == "Not available":
                data[ch]['OutdoorExclude'] = True
            else:
                data[ch]['OutdoorExclude'] = False

        for i in range(61, 70):
            data[i] = {
                'IndoorQuality': 1,
                'OutdoorExclude': True
            }
        data[38] = {
            'IndoorQuality': 4,
            'OutdoorExclude': False
        }

        return data
    
    # Method to generate exclusions file
    def xmlGenerate(self, data, io, filename):
        threshold = 3

        root = ET.Element('channel_exclusions',
            date=self.date.strftime("%a %b %d %Y"),
            time=self.date.strftime("%H:%M:%S"),
            appl_version="6.12.2.35",
            version="1.1",
            source="RF Library")
        location_info = ET.SubElement(root, 'location_info')
        search_type = ET.SubElement(location_info, 'search_type').text = "city based"
        country = ET.SubElement(location_info, 'country').text = "United Kingdom"
        state = ET.SubElement(location_info, 'state')
        city = ET.SubElement(location_info, 'city')
        zipcode = ET.SubElement(location_info, 'zipcode')

        channel_avoidance_info = ET.SubElement(location_info, 'channel_avoidance_info')

        for ch in sorted(data):
            channel = ET.SubElement(channel_avoidance_info, 'channel')
            ET.SubElement(channel, 'number').text = str(ch)
            ET.SubElement(channel, 'call_sign')
            ET.SubElement(channel, 'tv_station_country').text = "United Kingdom"
            ET.SubElement(channel, 'tv_station_latitude')
            ET.SubElement(channel, 'tv_station_longitude')
            ET.SubElement(channel, 'distance')
            ch_type = ET.SubElement(channel, 'type')
            db_source = ET.SubElement(channel, 'db_source')
            exclude = ET.SubElement(channel, 'exclude')
            if io == 'Outside':
                exclude.text = str(data[ch]['OutdoorExclude']).lower()
            elif io == 'Inside':
                if data[ch]['IndoorQuality'] >= threshold:
                    exclude.text = 'false'
                else:
                    exclude.text = 'true'
            if exclude.text == 'true' and ch < 61:
                ch_type.text = '1'
                db_source.text = '2'
            else:
                ch_type.text = '4'

        tree = ET.ElementTree(root)
        tree.write(filename)