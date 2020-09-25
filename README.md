# passwordchecker
Python script to check your password security through API on pwnedpasswords.com.

Script is sending only first FIVE characters of SHA1 generated from your password to API and downloads the list which includes that string. 
API returns list of compromised passwords starting with SHA1 string sent and then the script locally matches if your password is on that list.
Advantage is that password is never sent/passed through the internet for checking, but it runs all the checks on your computer locally.

Next version will have option to use local text file for bulk passwords checking.

To run the password checker you should have at least Python verson 3. It runs on Windows and MACs.

example of usage:
> python .\checkmypass.py password1 password2 password3 passwordn (and so)

Program returns checks like this:

password1 was found 2418984 times... you should probably change your password!

password2 was found 185754 times... you should probably change your password!

password3 was found 79754 times... you should probably change your password!

passwordn was found 119 times... you should probably change your password!

Check completed succesfuly!

I hope you like it and it will help you stay more secure!
