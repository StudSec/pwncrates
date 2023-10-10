# Contributing
StudSec is community driven, because of this we want anyone to be able to help out!

## "Getting started" page
The getting started page is aimed at helping beginners get started with CTF's, found an amazing resource you want to add?
See something that can be improved? Spot a Typo? You can contribute to it by going to https://github.com/StudSec/pwncrates
and make a pull request with the proposed changes to `data/pages/getting_started.md`.

For more information on pull requests see here: https://www.youtube.com/watch?v=8lGpZkjnkt4

### New challenge
Anyone is free to submit a new challenge, and we will gladly credit you for your hard work.
However, do keep in mind the challenges are tested before being deployed, and they might be
rejected or asked to be reworked.

But we don't want that! You lose the time you spent designing the challenge, and we lose the opportunity to expand our 
challenge roster. So, here are a couple of things to keep in mind when designing a challenge.

1) The flow of information.

    Make sure a CTF player has all the information needed to solve a challenge. If your challenge has a blind injection,
    give them the source code, so they can test it locally. There are times were you want to deny this type of information
    but make sure you have a good reason.


2) Real world application

    A good CTF walks the line between being realistic, and being educational. A trap a lot of CTF designers walk into is
    wanting to make 'realistic' challenges. While this is not a bad mindset, it can often lead to dull and boring 
    challenges. CTFs and the real world differ on two fronts, time and education. Let me explain.

    Time. In the real world you'll be spending a lot of time on meaningless items. Consider the hours of code scrolling
    an exploit developer has to do before finding a vulnerability. Or the amount of fuzzing an attacker may do before
    finding a vulnerable endpoint. This is fine in the real world, as the aim is to be secure. However, in a CTF this can
    create a very frustrating experience, realise that your players don't have an endless amount of time to try every
    possible string on your black box input (this leads back into point 1), or go through thousands of lines of code. Most
    of the time should be spent focusing on the vulnerability, not looking for it*. This is not to say the vulnerability 
    should be obvious, but a very hard to spot bug might benefit from a severely limited scope.

    Education. Unlike the real world we *want* players to solve the challenge, break into our system, hijack our database.
    But in the process we also want them to learn something. In the real world you'll find that most exploits are re-using
    known bugs in existing software (often called CVE's). Be careful when using a CVE in your challenge, don't make it
    as simple as downloading and running a script on exploitdb. You could, for example, give it a unique twist, or choose
    an exploit that has no public exploit available.


3) Simulating vulnerabilities

    Be very, **very**, careful when simulating vulnerabilities within your CTF. Say, for example you want to make an
    LFI challenge, where you extract a secrets file for a JsonWebToken. So you can forge a new token and read the
    authenticated flag. Great, but you don't want players to gain code execution through log poisoning, so you implement the
    following snippet:
    
    ```php
    if ($_GET['file'] === "/var/www/html/jwt.secret") {
        echo $SECRET;
       }
    ```
    
    This works, the challenge will play out as you intended, and the threat of RCE has been thwarted (though it's still
    PHP so who knows). However, say a player suspects your challenge is LFI, so they try to read a world-readable file, for
    example `/etc/passwd`. Now, when they make a request `?file=/etc/passwd` they will get an error, and the player will
    rightly assume the application is not vulnerable to LFI and move on, getting completely stuck.

### Challenge submission guidelines
Please include the following when submitting a challenge:
+ Source code (so no compiled code, even if it's a reversing challenge)
+ Build instructions
+ A detailed writeup, possibly with explanations _why_ you made certain design decisions.

If the challenge is hosted it should be put in a Docker container, we can do this for you if you're not familiar
with docker, but please keep it in mind.

Try to keep the file size to a minimum, we are on a STORM budget :)

You can send your submissions to any of our staff (not STORM) members in discord.

### Fixes in existing challenges
If you have found an unintended in a challenge you can submit a fix or ask Staff/the challenge creator to do so
for you. However, only do this if the unintended hurts the overall challenge. If it is a genuine mistake it makes
the challenge that much more realistic, however in some cases it can also completely derail the educational aim behind
the challenge. If this is the case you are justified in fixing the unintended approach, but consider making a second
challenge focusing on this unintended solution.
