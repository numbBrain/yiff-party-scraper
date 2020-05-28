import os
import math
import socket
import requests
import argparse
from lxml import html
from time import sleep
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.exceptions import ReadTimeoutError
from requests.packages.urllib3.util.retry import Retry

def writeFiles(content, failedLogPath):

    with open(failedLogPath, "a") as logFile:

        if isinstance(content, list):
            for line in content:
                logFile.write(line+"\n")
        elif isinstance(content, str):
            logFile.write(content+"\n")

def formatBytes(bytes):

    if bytes == 0:
        return "0B"
    suffixes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    index = int(math.floor(math.log(bytes, 1024)))
    formatted = round(float(bytes)/(1024**index), 2)
    return f"{formatted} {suffixes[index]}"

def downloadFile(fileLink, directory, filenameCounter, fileCounter, delay):

    global TOTAL_SIZE
    filename = f"{filenameCounter}_{fileLink.strip('/').split('/')[-1]}"
    filepath = os.path.join(directory, filename)

    try:
        fileData = session.get(fileLink, headers=HEADERS, stream=True,timeout=TIMEOUT)
        
        try:
            fileSize = int(fileData.headers["Content-Length"])
        except KeyError:
            fileSize = 0
        if os.path.isfile(filepath):

            localFileSize = os.stat(filepath).st_size
            
            if localFileSize == fileSize:
                filenameCounter += 1
                sleep(2)
                return (filenameCounter, fileCounter)
            else:
                if fileSize == 0:
                    pass
                else:
                    diff = int(fileSize) - int(localFileSize)
                    HEADERS["Range"] = f"bytes={diff+1}-{fileSize-1}"

                fileResp = session.get(fileLink, headers=HEADERS, stream=True, timeout=TIMEOUT)
                fileResp.raise_for_status()
        else:
            fileResp = fileData

    except requests.exceptions.ConnectionError as connErr:
        writeFiles(fileLink, failedLogPath)
        filenameCounter += 1
        print(connErr)
        return (filenameCounter, fileCounter)

    except (socket.timeout, ReadTimeoutError, requests.Timeout) as timeErr:
        writeFiles(fileLink, failedLogPath)
        filenameCounter += 1
        print(timeErr)
        return (filenameCounter, fileCounter)


    except requests.exceptions.HTTPError as err:
        writeFiles(fileLink, failedLogPath)
        filenameCounter += 1
        print(err)
        return (filenameCounter, fileCounter)

    with open(filepath, "ab") as file:

        print(ERASE, end="\r", flush=True)
        print(f"[+] Downloading file: {filename}, have downloaded {fileCounter} files, {formatBytes(TOTAL_SIZE)}", end="\r", flush=True)

        for iterData in fileResp.iter_content(chunk_size=2**20): 
            if iterData:
                file.write(iterData) 
    fileCounter += 1
    filenameCounter += 1
    TOTAL_SIZE += os.stat(filepath).st_size
    sleep(delay)
    return (filenameCounter, fileCounter)
        
parser = argparse.ArgumentParser(description="scrape files from yiff.party posts")
groupsParser = parser.add_mutually_exclusive_group()
modeParser = parser.add_mutually_exclusive_group()
groupsParser.add_argument("--links", type=str, nargs="+", const=None, help="take links from STDI")
groupsParser.add_argument("--read", metavar="file.txt", type=argparse.FileType("r", encoding="UTF-8"), const=None, help="read links from file")
parser.add_argument("--dest", type=str, nargs="?", default=os.getcwd(), help="specify download directory")
parser.add_argument("--timeout", type=int, nargs="?", default=60, help="timeout in seconds for requests")
parser.add_argument("--delay", type=int, nargs="?", default=5, help="seconds to wait between downloads")
parser.add_argument("--continous", action="store_true", default=False, help="paginate automatically and scrap next pages")
modeParser.add_argument("--postsOnly", action="store_true", default=False, help="scrape patreon posts only")
modeParser.add_argument("--sharedOnly", action="store_true", default=False, help="scrape shared files posts only")
parser.add_argument("--version", action="version", version="yiff_scraper 1.0")
args = parser.parse_args()

SKIP = "https_www.dropbox.com_static_images_spectrum-icons_generated_content_content-folder_dropbox-large.png"
HEADERS = { "User-Agent" : "Opera/9.80 (Linux armv7l) Presto/2.12.407 Version/12.51 , D50u-D1-UHD/V1.5.16-UHD (Vizio, D50u-D1, Wireless)"}
RETRIES = Retry(total=10, backoff_factor=3)
ERASE = "\033[2K"
DOMAIN = "yiff.party"
TIMEOUT = args.timeout
SLEEP = args.delay
CONTINUE = args.continous
DESTINATION = os.path.abspath(args.dest)
POSTS_ONLY = args.postsOnly
SHARED_ONLY = args.sharedOnly
FILE_COUNTER = 0
SHARED_FILE_COUNTER = 0
FILENAME_COUNTER = 1
SHARED_FILENAME_COUNTER = 1
TOTAL_SIZE = 0

if not (args.read or args.links):
    print("[-] No options specified, use --help for available options")
    exit()

else:
    if args.links:

        suppliedLinks = list(dict.fromkeys(args.links)) 
    else:
        suppliedLinks = list(dict.fromkeys(list(args.read.read().splitlines())))
        args.read.close()

print(f"[+] Download folder: {DESTINATION}\n")

if not (POSTS_ONLY or SHARED_ONLY):
    print(f"[+] Both posts and shared files will be downloaded\n")
    POSTS_ONLY = True
    SHARED_ONLY = True

elif POSTS_ONLY:
    print(f"[+] Only patreon posts will be downloaded\n")


elif SHARED_ONLY:
    print(f"[+] Only shared files will be downloaded\n")

with requests.Session() as session:
    session.mount("https://", HTTPAdapter(max_retries=RETRIES)) 

    for suppliedLink in suppliedLinks:

        suppliedLink = suppliedLink.strip()
        if not urlparse(suppliedLink).netloc == DOMAIN: 
            print(f"[-] {suppliedLink} doesn't belong to {DOMAIN}, skipping it")
            continue

        print(f"[*] Getting page: {suppliedLink}", end="\r", flush=True)

        try:
            pageResp = session.get(suppliedLink, headers=HEADERS, timeout=TIMEOUT)
            pageResp.raise_for_status()

        except requests.exceptions.ConnectionError as connErr:
            print(connErr)
            continue
    
        except (socket.timeout, ReadTimeoutError, requests.Timeout) as timeoutErr:
            print(timeoutErr)
            continue

        except requests.exceptions.HTTPError as err:
            print(err)
            continue
        
        print(ERASE, end="\r", flush=True)
        print(f"[+] {suppliedLink}, page retrieved\n")

        pageTree = html.fromstring(pageResp.text)
        pageTree.make_links_absolute(suppliedLink)
        posts = pageTree.xpath("//div[@class='card large yp-post']")
        sharedFiles = pageTree.xpath("//div[@id='shared_files']//div[@class='card-action']/a/@href")
        name = pageTree.xpath("//span[@class='yp-info-name']/text()")[0].strip()
        patreonName = pageTree.xpath("//span[@class='yp-info-name']/small/text()")[0].strip()

        creatorName = name+patreonName
        creatorDirectory = os.path.join(DESTINATION, creatorName)
        sharedFilesDirectory = os.path.join(creatorDirectory, "shared_files")
        failedLogPath = os.path.join(creatorDirectory, "failed_links.txt")
        embededLogPath = os.path.join(creatorDirectory, "embeded_links.txt")
        os.makedirs(sharedFilesDirectory, exist_ok=True)

        if CONTINUE:
            nextPage = pageTree.xpath("//a[@class='btn pag-btn pag-btn-bottom'][1]/@href")
            if nextPage: 
                nextPage = nextPage[0]
                index = suppliedLinks.index(suppliedLink) + 1
                suppliedLinks.insert(index, nextPage)  

        if POSTS_ONLY:   
            for post in posts:

                cardAttachments = post.xpath(".//div[@class='card-attachments']//a/@href")
                cardAction = post.xpath(".//div[@class='card-action']//a/@href") 
                cardEmbed = post.xpath(".//div[@class='card-embed']//a/@href") 

                if cardAttachments:
                    allMedia = cardAttachments
                else:
                    allMedia = cardAction
                
                if cardEmbed:
                    writeFiles(cardEmbed, embededLogPath)

                for media in allMedia:
            
                    if SKIP in media:
                        continue

                    FILENAME_COUNTER, FILE_COUNTER = downloadFile(media, creatorDirectory, FILENAME_COUNTER, FILE_COUNTER, SLEEP)
                    
        if SHARED_ONLY:
            for sharedFile in sharedFiles:
                
                if SHARED_FILE_COUNTER < len(sharedFiles):
                    SHARED_FILENAME_COUNTER, SHARED_FILE_COUNTER = downloadFile(sharedFile, sharedFilesDirectory, SHARED_FILENAME_COUNTER, SHARED_FILE_COUNTER, SLEEP)

print(ERASE, end="\r", flush=True)
formattedSize = formatBytes(TOTAL_SIZE)
print(f"[+] {FILE_COUNTER} post files downloaded, {formattedSize}")
print(f"[+] {SHARED_FILE_COUNTER} shared files downloaded, {formattedSize}")
