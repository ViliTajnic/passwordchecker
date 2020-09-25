# passwordchecker
Python script to check your password security through API on pwnedpasswords.com.

Script is sending only first FIVE characters of SHA1 generated from your password to API and downloads the list which includes that string. 
API returns list of compromised passwords starting with SHA1 string sent and then the script locally matches if your password in on that list.
Advantage is that password is never sent/passed through the internet for checking, but it runs all the checks on your computer locally.

Next version will have option to use local text file for bulk passwords checking.
