# Lab 1: Username enumeration via different responses

## Objective
Enumerate a valid username, brute-force this user's password, then access their account page.

## Steps
1. Go to My Account, login with random usename/password, and catch request by Burp.
2. See the http request `/login`, and form data include username, password.
3. Set username as a variable, and brute force a list candidate user, and see the username has response "Invalid password". It's a username we need to find (For my lab, username is `ec2-user`)
4. Do the same for the password. However, replace the username with the username that was found. See the password return status code 302 -> redirect to page my-account (For my lab, password is `mobilemail`)
5. Login with found username, password -> solved lab