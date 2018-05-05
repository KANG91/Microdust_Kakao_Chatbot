﻿# Microdust KaKao chatbot project

## Synopsis
Many Koreans have been suffering from microdust which might cause serious damage to human body.  Therefore, It is absolutely important for Koreans to check how clean air it is when they are outside. One of the closest things we always have is a smartphone, and we use messenger app to talk with friends every day. so, I thought It would be convinient If there was a chatbot in messenger app that let me know how much microdust in air whenever I want, wherever I am. 

## How to make..
Step 1. using Kakao talk Plus friend to make chatbot - **Done** 
> - sign up to Kakao talk plus friend site to get allowance to make a chatbot 
> - make a server on Amazon ec2 using Python Flask to use it for 24 hours

Step 2. get microdust information instantly - **Done**
> - get microdust information from internet.

Step 3. save messages from users - **Done**
> - use pymongo to deliver all message from users to mongoDB

Step 4. correct users's word - working
> - sometimes, two words that have same meaning are written different form. ex)충청북도 -> 충북
> - by using word2vec, have chatbot understand those words.
> - (still working to make it) 


