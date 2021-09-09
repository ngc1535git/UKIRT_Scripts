# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 09:44:16 2021

@author: ablock
"""

#!python
#
#Usage:
#Scans a directory to find Dark frames (CDS ReadMode)
#Takes median of darks to create a master dark
#Header information from a example dark is used to populate the new MaserDark
#Dark frame is written to the Master Darks directory


from astropy.io import fits
import sys
import os
import numpy as  np
import shutil

filekey ='y'   #the starting string common to the data file names
endkey = '.fits'
dark_masters_directory = '/mnt/d/UKRIT_2021/Masters/Darks/'
search_num = 200


def main():


	cwd = os.getcwd()
	#Set directory variable to be the type (bytes) read by os system 
	directory = os.fsencode(cwd)
	#change working directory
	os.chdir(directory)
	#FileList stores the Entire contents of directory- FitsList will be the data files
	FileList,FitsList,DarksList,Darks_Data_Stack = [],[],[],[]

	#create FileList and a list of Fits files
	for file in os.listdir(directory):
			filename = os.fsdecode(file)
			FileList.append(filename)
			if filename.startswith(filekey) and filename.endswith(endkey):
				FitsList.append(filename)
	if not FitsList:
		sys.exit("No files found in this directory that match your command line file listing. The file list is empty.")
		
	print('There are {} files to check for darks in {}.'.format(len(FitsList),(cwd)))
	print('In this version of script, we are only going to examine the first {} files.'.format(search_num))
	FitsList.sort()
				
	for i in range(search_num):
		hdul = fits.open(FitsList[i])
		hdr = hdul[0].header
		data = hdul[0].data
		data.astype(np.float32)
		if hdr['OBSTYPE'].strip()=='DARK' and hdr['EXP_TIME']== 5 and hdr['READMODE']=='CDS': 
			DarksList.append(FitsList[i])
			Darks_Data_Stack.append(data)
		hdul.close()	
	print('OK, found {} dark frames that are 5 second exposures.'.format(len(DarksList)))
	exemplar_hdul = fits.open(DarksList[0])
	exemplar_dark = exemplar_hdul[0].header
	print('Taking the median of the data to create the Master Dark frame...')
	master_dark = np.median(Darks_Data_Stack,axis=0)
	std = np.std(master_dark)
	mean = np.mean(master_dark)
	median = np.median(master_dark)
	variance = np.var(master_dark)
	print('Copying some information from the Fits header of the first dark frame.')
	darkhead = fits.Header()
	darkhead['IMAGETYP'] = 'Master Dark'
	darkhead['OBSTYPE'] = 'DARK'
	darkhead['DATE-OBS'] = exemplar_dark['DATE-OBS']
	darkhead['EXP_TIME'] = exemplar_dark['EXP_TIME']
	darkhead['FILTER'] = exemplar_dark['FILTER']
	darkhead['GAIN'] = exemplar_dark['GAIN']
	darkhead['INSTRUME'] = exemplar_dark['INSTRUME']
	darkhead['TELESCOP'] = exemplar_dark['TELESCOP']
	darkhead['CAMNUM'] = exemplar_dark['CAMNUM']
	darkhead['MEAN'] = (mean, 'mean')
	darkhead['MEDIAN'] = (median, 'median')
	darkhead['STD'] = (std, 'standard dev')
	darkhead['VAR'] = (variance, 'variance')
	darkhead['NAXIS'] = 2
	darkhead['NAXIS1'] = master_dark.shape[0]
	darkhead['NAXIS2'] = master_dark.shape[1]
	masterdarkfits = fits.PrimaryHDU(master_dark, header=darkhead)

	masterdarkname = DarksList[0].split('_')
	masterdarkname = masterdarkname[0].split('y')
	masterdarkname = 'Dark Master_'+ masterdarkname[1]+'.fits'
	print('Saving master Dark ----> {}'.format(dark_masters_directory+ masterdarkname))
	masterdarkfits.writeto(masterdarkname, overwrite=True)
	shutil.copyfile(os.path.join(directory, os.fsencode(masterdarkname)), os.path.join(os.fsencode(dark_masters_directory), os.fsencode(masterdarkname)))

	
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
	main()
