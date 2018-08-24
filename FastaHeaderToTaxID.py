import urllib.request
import xml.etree.ElementTree as ET
import time
import sys
import datetime

#https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=protein&id=YP_004144438.1

#Delay between API requests, 0.35s if no API key, 0.11s if API key is present
requestDelay = 350000


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
        try:
            inputFile = open(inputFileLocation,"r")
            inputData = inputFile.read()
            gettingLocation = False
        except IOError:
            print("Sorry, I'm unable to open that file location.")


    #Ask for an api key
    gettingKey = True
    while (gettingKey == True):
        apiInput = input("\nDo you have an NCBI eTools API key?  This is not\
 required but speeds up the rate at which requests can be made.  If you have one\
 type 'y', otherwise type 'n' to skip.")
        if (apiInput == "n"):
            gettingKey = False
        elif (apiInput == "y"):
            print("\nPlease select a file containing your API key: it should be\
 a plain text document with any name containing ONLY your key.")
            apiKeyLocation = filedialog.askopenfilename()
            try:
                if (apiKeyLocation != ""):
                    file = open(apiKeyLocation,"r")
                    apiKey = file.read()
                    print("Using API key = " + apiKey)
                    requestDelay = 110000
                    gettingKey = False
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
        try:
            file = open(outputFileLocation,"w")
            gettingLocation = False
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
    #for seq in seqsList:
    #    print(seq["header"])
    lastRequest = datetime.datetime.now()
    
    for seq in seqsList:
        endOfAccession = seq["header"].find(" ")
        accession = seq["header"][1:endOfAccession]

        url = urlBase + accession

        currentTime =  datetime.datetime.now()
        timeDelta = currentTime - lastRequest
        if ((timeDelta.microseconds + (timeDelta.seconds * 1000000)) < requestDelay):
            time.sleep(0.05)
            currentTime =  datetime.datetime.now()
            timeDelta = currentTime - lastRequest


        with urllib.request.urlopen(url) as response:
            lastRequest = datetime.datetime.now()
            print("Fetched page at " + str(lastRequest))
            xmlOutput = response.read().decode("utf-8")
            #Use the XML parser to find the root of the XML tree
            root = ET.fromstring(xmlOutput)
            taxid = root[0][8].text
            seq["header"] = ">" + taxid
        time.sleep(1)

    with open(outputFileLocation, "a") as file:
        for seq in seqsList:
            file.write(seq["header"] + " " + seq["sequence"])

    print("Done!")

    


 

