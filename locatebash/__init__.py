#!/usr/bin/env python3
# coding=utf-8
"""
Call mdfind to do a quick search

Usage:
  locate.py [options] <query>...

Options:
  -h --help       Show this screen.
  -f --folders    Show folders seperately

author  : rabshakeh (erik@a8.nl)
project : devenv
created : 09-06-15 / 09:35
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import super
from builtins import open
from future import standard_library
standard_library.install_aliases()
from past.builtins import cmp
from builtins import str
import time
import os
try:
        import pyzmail
        GOTPYZ = True
except:
        GOTPYZ = False

from arguments import Arguments
from consoleprinter import remove_colors, console
from functools import cmp_to_key
from fuzzywuzzy import fuzz
#from cmdssh import call_command
import subprocess
import hashlib
import stat

def call_command(command, cmdfolder=os.path.expanduser("~"), verbose=False, streamoutput=True, returnoutput=False, prefix=None, ret_and_code=False):
    """
    @type command: str, unicode
    @type cmdfolder: str, unicode
    @type verbose: bool
    @type streamoutput: bool
    @type returnoutput: bool
    @type prefix: str, None
    @type ret_and_code: bool
    @return: None
    """
    try:
        if ret_and_code is True:
            streamoutput = False
            returnoutput = True

        if verbose:
            console(cmdfolder, command, color="yellow")

        for prevfile in os.listdir(cmdfolder):
            if prevfile.startswith("callcommand_"):
                os.remove(os.path.join(cmdfolder, prevfile))

        commandfile = "callcommand_" + hashlib.md5(str(command).encode()).hexdigest() + ".sh"
        commandfilepath = os.path.join(cmdfolder, commandfile)
        open(commandfilepath, "w").write(command)

        if not os.path.exists(commandfilepath):
            raise ValueError("commandfile could not be made")

        try:
            os.chmod(commandfilepath, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

            proc = subprocess.Popen(commandfilepath, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cmdfolder, shell=True)
            retval = ""

            if streamoutput is True:
                while proc.poll() is None:
                    time.sleep(0.1)
                    output = proc.stdout.readline()

                    if isinstance(output, bytes):
                        output = output.decode()

                    if len(remove_escapecodes(output).strip()) > 0:
                        if returnoutput is True:
                            retval += str(output)

                        if prefix is None:
                            prefix = command

                        if len(prefix) > 50:
                            prefix = prefix.split()[0]

                        console(output.rstrip(), color="green", prefix=prefix)

                        if returnoutput is True:
                            retval += output

            so, se = proc.communicate()

            if ret_and_code is False and (proc.returncode != 0 or verbose):
                so = so.decode().strip()
                se = se.decode().strip()
                output = str(so + se).strip()

                if proc.returncode == 1:
                    if verbose:
                        console_error(command, CallCommandException("Exit on: " + command), errorplaintxt=output, line_num_only=9)
                    else:
                        raise CallCommandException("Exit on: " + command+" - "+output)

                else:
                    console("returncode: " + str(proc.returncode), command, color="red")

            if ret_and_code is True or returnoutput is True and streamoutput is False:
                retval = so
                retval += se

                if hasattr(retval, "decode"):
                    retval = retval.decode()

            if ret_and_code is True:
                returnoutput = False

            if returnoutput is True:
                return retval.strip()
            elif ret_and_code is True:
                return proc.returncode, retval.rstrip()
            else:
                return proc.returncode
        finally:
            if os.path.exists(commandfilepath):
                #if proc.returncode == 0:
                os.remove(commandfilepath)

    except ValueError as e:
        console_exception(e)
    except subprocess.CalledProcessError as e:
        console_exception(e)

class IArguments(Arguments):
    """
    IArguments
    """
    def __init__(self, doc):
        """
        __init__
        """
        self.help = False
        self.folders = False
        self.query = ""
        super().__init__(doc)


def cmp(x, y):
    """
    @type x: str
    @type y: str
    @return: None
    cmp(x, y) -> integer
    Return negative if x<y, zero if x==y, positive if x>y.
    """
    return (x > y) - (x < y)


def get_mdfind(cmd):
    """
    @type cmd: str
    @return: None
    """

    #console(cmd)
    return cmd


def locatequery(args):
    """
    @type args: IArguments
    @return: None
    """
    searchword = " ".join(args.query)
    query_display = ", ".join(args.query)
    mdfind_results = []
    textsearch = False

    if searchword.strip().endswith("*"):
        searchword = searchword.strip().strip("*")
        textsearch = True
    elif searchword.strip().endswith("+"):
        searchword = searchword.strip().strip("+")
        textsearch = True

    print("\033[91m[" + query_display + "]:\033[0m")
    sl = call_command(get_mdfind("mdfind -onlyin '" + os.path.expanduser("~") + "' -name '" + searchword + "'"), returnoutput=True, streamoutput=False)
    mdfind_results.extend(sl.split("\n"))
    mdfind_results = [x for x in mdfind_results if x]
    res = call_command(get_mdfind("mdfind -name '" + searchword + "'"), returnoutput=True, streamoutput=False)
    mdfind_results.extend(res.split("\n"))

    if textsearch:
        res = call_command(get_mdfind("mdfind -onlyin ~/workspace " + searchword), returnoutput=True, streamoutput=False)
        mdfind_results.extend(res.split("\n"))

    if len(mdfind_results) < 10:
        res = call_command(get_mdfind("mdfind " + searchword), verbose=False, returnoutput=True, streamoutput=False)
        mdfind_results.extend(res.split("\n"))

    return mdfind_results, searchword


def show_folders(folders, mdfind_results3, searchword, skiplist):
    """
    @type folders: list
    @type mdfind_results3: list
    @type searchword: str
    @type skiplist: list
    @return: None
    """
    folders2 = []

    if len(folders) > 0 and len(mdfind_results3) < 50:
        print()
        print("\033[91m[" + searchword + "] Folders:\033[0m")
        last = None
        nextcnt = 0

        for i in folders:
            nextcnt += 1
            skip = False
            skipi = i.lower()
            nexti = None
            try:
                nexti = folders[nextcnt]
            except IndexError:
                pass

            for item in skiplist:
                item = item.lower()

                if item in skipi:
                    skip = True

            if last and fuzz.ratio(i, last) > 85:
                skip = True

            if len(folders) < 10:
                skip = False

            if not skip:
                # if last and (pp(i) == pp(last) or fuzz.ratio(i, nexti) > 70):
                #    folders2.append("\033[90m" + str(i) + "\033[0m")
                # else:
                newi = ""

                if nexti:
                    if fuzz.ratio(i, nexti) > 90:
                        newi = "\033[90m" + str(os.path.dirname(i)) + "\033[34m/" + str(os.path.basename(i)) + "\033[0m"

                if newi == "":
                    newi = "\033[34m" + str(i) + "\033[0m"

                folders2.append(newi)

    folders2.sort(key=lambda x: (x.count("/"), len(x), x))
    folders2.reverse()

    for i in folders2:
        print(i)


def main():
    """
    main
    """
    args = IArguments(__doc__)
    mdfind_results, searchword = locatequery(args)
    osearchword = searchword
    mdfind_results = [x for x in mdfind_results if x]
    mdfind_results = set(mdfind_results)
    mdfind_results = [xs for xs in mdfind_results if xs]
    mdfind_results2 = []
    folders = []
    skiplist = ["Library/Caches"]
    mdfind_results.sort(key=lambda x: (x.count("/"), len(x), x))

    for i in mdfind_results:
        skip = False
        skipi = i.lower()

        for item in skiplist:
            item = item.lower()

            if item in skipi:
                skip = True

        if not skip:
            mdfind_results2.append(i)

    last = None

    def grandparentpath(apath):
        """
        @type apath: str
        @return: None
        """
        return os.path.dirname(os.path.dirname(apath))

    mdfind_results2 = sorted(mdfind_results2, key=cmp_to_key(lambda x, y: cmp(str(len(y)), str(len(x)))))
    mdfind_results2.reverse()

    if len(mdfind_results2) == 0:
        mdfind_results2.extend(os.popen("/usr/bin/locate " + searchword).read().split("\n"))

    mdfind_results3 = []

    for i in mdfind_results2:
        if last and (grandparentpath(i) == grandparentpath(last) or fuzz.ratio(i, last) > 70):
            mdfind_results3.append("\033[90m" + str(i) + "\033[0m")
        else:
            mdfind_results3.append("\033[34m" + str(os.path.dirname(i)) + "\033[34m/" + str(os.path.basename(i)) + "\033[0m")

        if os.path.isfile(i):
            folders.append(os.path.dirname(i))
        else:
            folders.append(i)

        last = i

    if len(mdfind_results3) > 0:
        mdfind_results3.reverse()

    for i in set(mdfind_results3):
        if i != osearchword:
            mdfind_results3.append(i)

    # folders = sorted(set(folders))
    # skiplist = ["Library/Mail"]
    # folders.sort(key=lambda x: (x.count("/"), len(x), x))
    # if args.folders is True:
    #    show_folders(folders, mdfind_results3, searchword, skiplist)

    if len(mdfind_results3) == 1 and len(folders) == 1:
        print("\033[90m")
        l = os.popen("glocate " + osearchword).read().split("\n")

        for i in l:
            if i != osearchword:
                print("~/" + str(i).lstrip("./"))
    else:
        mdfind_results3 = list(set(mdfind_results3))
        mdfind_results3.sort(key=lambda x: (-x.count("/"), len(x), x))

        for i in mdfind_results3:
            ipath = remove_colors(i)

            if ipath.strip().lower().endswith(".emlx"):
                sub = "-"
                if os.path.exists(ipath):

                     conts = open(ipath, "rb").read().decode("utf8", "ignore")
                     conts = conts.split("Content-Type:")
                #
                     if len(conts) > 1:
                        cont = "Content-Type:" + "Content-Type:".join(conts[1:])
                #
                        global GOTPYZ
                        if GOTPYZ:
                                msg = pyzmail.PyzMessage.factory(cont)
                #         aan = ", ".join(msg.get_address('from')) + ":"
                                sub2 = msg.get_subject().replace("\n", "").strip()
                                if sub2.split():
                                    sub = sub2

                print("\033[90mmail:" + os.path.basename(ipath), sub + "\033[0m")
            else:
                print(i)

    print("\033[0m")


if __name__ == "__main__":
    main()
