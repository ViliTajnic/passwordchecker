# passwordchecker
Python script to check your password security through API on pwnedpasswords.com.

Script is sending only first FIVE characters of SHA1 generated from your password to API and downloads the list which includes that string. 
API returns list of comprmised passowrds starting with SHA1 string sent and then the script locally matches if your password in on that list.
Advatage is that passord is never sent throgh internet for checking but it does that locally on your computer.

Next version will have oprion to use local text file for bulk passwords checking. 
