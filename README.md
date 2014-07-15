good-talk
=========

An experimental chatroom server with all communication AES-encrypted in the browser via (crypto-js)[crypto-js.googlecode.com].
The idea is to allow private and free association on the internet without the website operator being put in the
regrettable position where they have to give up any useful information (i.e. content) from your conversations should they be
'compelled' to do so.
It requires no session-cookies or other persistent state, allowing greater scalability and simpler assertions about how your
conversations may be recorded by the operator.
Server-side, it utilizes zero-mq in a very simple django application for realtime, database-free message delivery, 

For a demo of the current master, see https://rtps.co.

To get started just enter your shared-secret (get this to your friends over the sneakernet), name your chatroom, and provide a personal alias.

What's encrypted?
================
Both your alias and your message are encrypted in-browser before your message is sent.

What's not encrypted?
=====================
The name of your chatroom.  Don't call this something that may identify you (such as "OMGALICEANDBOBARETOtallYGONNATAKEOVERTHEWORLD")

Is this actually secure?
========================
TL;DR It's an experiment, I'm not a cryptographer, an doing this in JavaScript is so probably not.

Performing encryption in a language like JavaScript - while technically feasible - has many pitfalls that allow your 
key/plaintext to be leaked through all sorts of side channels.  It is impossible to say how your particular browser/OS combination 
will store your secrets at runtime or whether it will be suitably amnesiac when you close the window.  For example, if your
system is low on memory, some things (including your passphrase) may be paged to disk.  
JavaScript provides no native mechanism to prevent this.  In C, on a POSIX system, we could call `mlock()`  after we allocate
the string, and then use something like FreeBSD's `explicit_bzero()` when we're done, but this is impossible with the current
implementation.
Therefore, you *can* do encryption with Javascript, but before you do you should take note of the possible attack surfaces.
As such if you want to ensure real privacy, you should use something more trustworthy such as GPG.

All that said, this application provides a "better than nothing" solution for proper OTR web chat, so you may find it useful.
