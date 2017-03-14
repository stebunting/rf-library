# rf-library
App for converting, merging and organising RF scans from various sources for use in IM calculation software.

This app started as a personal project for me to expedite the process of taking multiple RF scans, copying them to my computer, opening each one up to remove the headers, combining them all into one file, removing the duplicates and then saving them into a master file, before opening up the file in Shure Wireless Workbench 6 and doing a co-ordination. This all happened during the load-in where there is almost never an abundance of time!

It started as a command line script, but then I started adding new features in order to organise my library of scans, format the files in such a way that they were quick to upload to http://www.bestaudio.com/spectrum-scans/ (an international scan repository maintained by Pete Erskine) and recognise more file types. Then I realised that this might be of use to other people, so here we are.

Written in Python 2.7 on OS X.
