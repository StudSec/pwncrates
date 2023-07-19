Welcome to the StudSec CTF Challenges!

## Getting Started
Some of these challenges can be quite overwhelming, especially as a beginner. So here are some quick pointers for each 
category as well as some general tips and tricks.

- Often, a challenge can require you to encode or decode data in a certain way. One excellent tool for this is CyberChef (https://gchq.github.io/CyberChef/)
- The Challenge name is often an indirect hint towards its contents. If your stuck it might be worth googling the name and related terms.

If your stuck, don't hesitate to ask. We all have to start somewhere, a simple question like "Hey, I'm currently 
looking at X, I've tried y and z. However, it doesn't seem to work." Allows others to nudge you on the right path 
(though don't expect others to solve the challenges for you).

Keep in mind however that this type of questioning is generally banned in competitive CTF play.

#### Web
Web challenges generally come in two flavors, client-side attacks and server side attacks.

For client side attacks you'll generally be attacking a different browser. For example, with xss you try to exploit 
other users logged into the website. These challenges can be solved by crafting a malicious website of your own and 
having `StudBot` visit it, you can do this by dming `!visit <url>` to the bot.

For more information about client side attacks check the following list,
  - https://portswigger.net/web-security/csrf
  - https://www.youtube.com/watch?v=EoaDgUgS6QA

For server side attacks your directly attacking the server, for this It's important to identify what's running on the 
server, is there a database? If so what kind? What is the server running? Php? Javascript? Answering these questions can
help you target your research.

For example, if you know the server is running Flask you can look up `Flask exploit` or `Flask exploit ctf`, which might 
lead you to this https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/flask . Additionally, 
looking a bit deeper into flask we see it uses the Jinja2 templating engine, which could prompt you 
to look up `Jinja2 template injection`.

For more information about server side attacks check the following list,
  - https://www.youtube.com/c/ippsec
  - https://www.youtube.com/watch?v=WWJTsKaJT_g
  - https://book.hacktricks.xyz

#### Reversing
While not exclusively the case, most reversing challenges contain a flag which you must recover. Either by passing the 
checks restricted or by bypassing these checks (or the flag is the check). You can use binary patching to bypass some
 of these checks but keep in mind the flag is intended to work on the original binary.

The best way to get started with these challenges is to throw them in a decompiler (Ghidra is recommended) and start 
labeling functions and variables based on their behavior. This allows you to slowly build up a picture of the binary 
and lets you figure out the flag.

For more information and tools check the following list,
  - https://ghidra-sre.org/
  - https://www.youtube.com/watch?v=fTGTnrgjuGA
  - objdump
  - gdb
  - https://www.youtube.com/watch?v=VroEiMOJPm8
  - Honorable mention: gdb gef extention

#### Crypto
Crypto challenges are generally an exceptionally difficult CTF category. They either incorporate 'made up' crypto 
systems or introduce a deliberate flaw in an established crypto system. In the first case your best bet is to use your 
imagination, check if the crypto system is similar to/matches existing ciphers (google is your friend here). In the 
second case, try to identify the crypto system used, generally this is given, and then do some research into it. 
For most major systems there will be a computerphile or live overflow video on the topic. In high level CTFs it is 
not uncommon to implement attacks based on research papers.

For more information check the following list,
  - cryptohack.org
  - https://www.youtube.com/watch?v=sYCzu04ftaY
  - https://www.youtube.com/watch?v=Rk0NIQfEXBA

 #### PWN
PWN challenges generally require you to gain arbitrary code execution (or, in beginner challenges, change code flow). 
For this you nearly always get the binary (or source code), it is recommended to first reverse engineer the binary to
see how it works. From there you can look for the vulnerability, for example a buffer overflow, or a use-after-free. 
One good first step is to run `checksec` on a binary to see what protections are in place.

Once you've identified your vulnerability you can start exploiting, this itself is generally a challenge, requiring 
you to chain code fragments and manipulate the memory to execute code.

This segment is unfortunately brief, as I am not really qualified to give advice on the topic.

For more information check the following list,
  - https://www.youtube.com/watch?v=iyAyN3GFM7A&list=PLhixgUqwRTjxglIswKp9mpkfPNfHkzyeN
  - pwntools
  - gdb
  - pwngdb or gef

#### Forensics
Forensics challenges are quite akin to mysteries. You get a piece of information, be it a network capture, memory dump, 
image or something else, and you'll need to understand what happened to recover the flag.

In this case it's a good skill to be able to filter out the noise (are the ARP requests really relevant in this 
network dump?), so look at filters and other items. Als make note of how information relates to each other, if you 
find an encrypted zip file you can probably find the password in the same email chain.

For more information check the following list,
  - wireshark
  - https://www.youtube.com/watch?v=A4_DOr7Eiqo
  - https://github.com/volatilityfoundation/volatility3

## Bot
For client side web ctfs (XSS, CSRF, etc) we have a discord bot called StudBot. The bot will attempt to visit *any* 
link you send it in dms via `!visit <url>`. 

StudBot is using a Firefox browser, the exact version may vary, but it will generally be close to the latest version. 
If you want to test your exploit locally you can grab the current live version by opening a listener using `nc -lvnp 
1337` and pointing the bot to this listener.
   
For more information on the bot you can view the source code on our github: https://github.com/StudSec/Bot/blob/main/Modules/browser.py
   
Its worth noting the challenge use *dns*, so if your exploit uses direct IP access, and it's not working you might want to 
switch to using dns instead. For example, cookies stored with IP access do not transfer if the website is later visited
via dns.