#Goes through a protein FASTA file and replaces the header with the NCBI taxonomy ID for
#the originating organism using NCBI's E utilities.  MUST be given a protein FASTA file
#as an input, does not work for DNA.  Requires and internet connection.  Written to make
#FASTA files compatible with the assign taxonomy function of the Interactive Tree of Life.

#This process may be faster through the use of an NCBI API key.  If you don't have one you
#can get one for free by registering an account with NCBI.  The script will ask for a file
#containing the API key: this should be a plain text file which ONLY contains the key in a
#single contiguous string.

import urllib.request
import xml.etree.ElementTree as ET
import time
import sys
import datetime

#https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=protein&id=YP_004144438.1

#Delay between API requests, 0.35s if no API key, 0.11s if API key is present
requestDelay = 350000

#Basic URL for accessing the E Utilities
urlBase = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=protein&id="

if __name__ == "__main__":
    #Stuff for file selection dialogue boxes:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()


    #Get a file to open
    gettingLocation = True
    while (gettingLocation == True):
        print("\nPlease choose an input file: ")
        inputFileLocation = filedialog.askopenfilename()
        #Try to open the input FASTA file.  If successful, set as inputData and continue
        try:
            inputFile = open(inputFileLocation,"r")
            inputData = inputFile.read()
            gettingLocation = False
        #If opening the input file fails inform the user and retry.
        except IOError:
            print("Sorry, I'm unable to open that file location.")


    #Ask for an api key
    gettingKey = True
    while (gettingKey == True):
        apiInput = input("\nDo you have an NCBI eTools API key?  This is not\
 required but speeds up the rate at which requests can be made.  If you have one\
 type 'y', otherwise type 'n' to skip.")
        #If the user indicated no API key, continue
        if (apiInput == "n"):
            gettingKey = False
        #If the user has an API key ask for the file location
        elif (apiInput == "y"):
            print("\nPlease select a file containing your API key: it should be\
 a plain text document with any name containing ONLY your key.")
            apiKeyLocation = filedialog.askopenfilename()
            try:
                #Try opening the file.  If successful, adjust the requestDelay and continue
                if (apiKeyLocation != ""):
                    file = open(apiKeyLocation,"r")
                    apiKey = file.read()
                    print("Using API key = " + apiKey)
                    requestDelay = 110000
                    gettingKey = False
                #If opening the file fails or no location is given wanr the user and retry
                else:
                    print("Sorry, I'm unable to open that file.")
            except IOError:
                print("Sorry, I'm unable to open that file.")
                pass
        else:
            print("\nSorry, I didn't recognise that.  Please type 'y' if you\
 have an API key or 'n' if you don't.")


    
    #Get a file location to save the output data
    gettingLocation = True
    while (gettingLocation == True):
        print("\nPlease choose an output file location and file name: ")
        outputFileLocation = filedialog.asksaveasfilename()
        #Try to open the output file location, if successful set as gettingLocation and continue
        try:
            file = open(outputFileLocation,"w")
            gettingLocation = False
        #If opening the location fails warn the user and retry
        except IOError:
            print("Sorry, I'm unable to open that file location.")
           
    
    #Count the number of ">" chars to figure out how many sequences are in the file
    numberOfSeqs = inputData.count(">")
    print("There are " + str(numberOfSeqs) + " sequences in this file")
    
    #Create a list to read sequences into
    seqsList = []

    #Find sequences and append them to the seqsList list:
    #For every ">" char (which denotes the start of a sequence)
    for x in range (0, numberOfSeqs):

        #Find the end of the header by finding the next return
        headerEnd = inputData.find("\n")
        #Find the *NEXT* ">" char (i.e. the start of the next sequence)
        secondSeqStart = inputData.find(">", 1)
        #Create a dictionary with the header and sequence under separate items
        dictionary = {"header":inputData[:headerEnd],"sequence":inputData[headerEnd:secondSeqStart]}
        #Append this dictionary to the seqsList list
        seqsList.append(dictionary)
        #Scrub the processed sequence from the input data
        inputData = inputData[secondSeqStart:]

    print("Starting request process")

    #Log the last time a web request was made (none for the first one so start the clock now)
    lastRequest = datetime.datetime.now()
    
    for seq in seqsList:
        #Find the space char in a header, everything before that except ">" is the accession
        endOfAccession = seq["header"].find(" ")
        accession = seq["header"][1:endOfAccession]

        #Append the accession to the URL request
        url = urlBase + accession

        #Log the time the current request is made
        currentTime =  datetime.datetime.now()
        #Check if more than requestDelay milliseconds have elapsed, if not wait.
        #This prevents overloading of the NCBI website which may result in you
        #getting IP blocked.
        timeDelta = currentTime - lastRequest
        if ((timeDelta.microseconds + (timeDelta.seconds * 1000000)) < requestDelay):
            time.sleep(0.05)
            currentTime =  datetime.datetime.now()
            timeDelta = currentTime - lastRequest

        #Open the request URL
        with urllib.request.urlopen(url) as response:
            #Log this as the last time a request was made
            lastRequest = datetime.datetime.now()
            print("Fetched page at " + str(lastRequest))
            #Process the web request to something comprehensible
            xmlOutput = response.read().decode("utf-8")
            #Use the XML parser to find the root of the XML tree
            root = ET.fromstring(xmlOutput)
            #Find the value containing the taxonomy ID number
            taxid = root[0][8].text
            #Set the sequences header in seqsList as the tax ID number
            seq["header"] = ">" + taxid
        time.sleep(1)

    #Once all headers have been processed, dump the processed list to the output file
    with open(outputFileLocation, "a") as file:
        for seq in seqsList:
            file.write(seq["header"] + " " + seq["sequence"])

print("Done!")


