# yiff.party scraper
python scraper to download media from yiff.party

### Requirements
Only **requests and lxml** packages are required. Do:
```
pip install -r requirements.txt
```

### Usage:

```
$ python yiff_scraper.py --help

optional arguments:
  -h, --help            show this help message and exit
  --links LINKS [LINKS ...]
                        take links from STDI
  --read file.txt       read links from file
  --dest [DEST]         specify download directory
  --timeout [TIMEOUT]   timeout in seconds for requests
  --delay [DELAY]       seconds to wait between downloads
  --continous           paginate automatically and scrap next pages
  --postsOnly           scrape patreon posts only
  --sharedOnly          scrape shared files posts only
  --version             show program's version number and exit

  ```
### Example
  ```
  $ python yiff_scraper.py --read links.txt 
  ```

  above command reads links from the file links.txt, one link each line. Downloads files from each link into the current folder. The **default timeout is 60 seconds** and **default wait time between requests is 5 seconds**

```
  $ python yiff_scraper.py --links link1 link2 --dest Downloads --timeout 120 --delay 10
```

  above command takes links(link1, link2,...) from the terminal and downloads files into the Downloads folder. Timeout for requests is set as 120 seconds and wait time between requests is set as 10 seconds

```
  $ python yiff_scraper.py --links link1 link2 --dest ~/Documents --timeout 120 --delay 10 --continous
```

  this command takes links from the terminal. Files are downloaded into the **Documents** folder of the current user **(in Linux)**. Timeout for requests is set as 120 seconds and wait time between requests is set as 10 seconds. **--continous option does pagination automatically, it enables you to scrape next pages until the last page is reached.**

  **--continous option is ideal for scraping creator's complete profile**

```
  $ python yiff_scraper.py --links link1 link2 --dest ~/Documents --timeout 120 --delay 10 --sharedOnly
```

  this command takes links from the terminal. Files are downloaded into the **Documents** folder of the current user **(in Linux)**. Timeout for requests is set as 120 seconds and wait time between requests is set as 10 seconds. **--continous option is not required if you're only scraping shared files.**

  **--sharedOnly and --postsOnly options cannot be used together, if you want to scrape everything don't use either options.**

### Note

* If scraping is interrupted, start the scraper again without altering the downloaded files. This will resume scraping instead of scraping from the start.

* Use proper timeout and sleep durations to avoid the script from crashing often.

* Failed URLs will be a displayed on the terminal without interupting scraping and are also added to  **failed_links.txt** file.

* Filenames of files are the same as uploaded by the creators. But, filenames are prefixed with a number(counter) to keep filenames unique.

## Limitaions

* Given the current situation, this scraper does not perform async requests, intentionally. `aiohttp` support shall be added in the future.

* Only Downloads files hosted at `data.yiff.party`. Does not download embeded videos, etc., but URLs are written to a file named **embeded_links.txt**