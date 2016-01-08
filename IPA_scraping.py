# -*- coding: utf-8 -*-
# Scraping strategy is from here: http://docs.python-guide.org/en/latest/scenarios/scrape/

from lxml import html
from string import punctuation
import requests
import re

# ------------------------
# FUNCTION DEFINITIONS

def search_ipa(word):
# This function looks up a single word on Dictionary.com and returns the contents of all IPA fields.
    page = requests.get('http://dictionary.reference.com/browse/' + '%s' % word + '?s=t')
    tree = html.fromstring(page.content)
    ipa = tree.xpath('//span[@class="pron ipapron"]/text()')
    return ipa

# Looks up the word, dealing with punctuation if necessary.
def get_ipa(word):
    
    transcription = search_ipa(word)
    # If not found, remove punctuation (except hyphens) and try again.
    if (not transcription) and (any(char in word for char in punctuation)):
        no_punc = re.sub("[%s]" % punctuation.replace("-", ""), "", word)
        transcription = search_ipa(no_punc)
        # If not found, collapse a hyphenated word into one and try again
        if (not transcription) and ("-" in no_punc):
            no_punc_one_word = no_punc.replace("-", "")
            transcription = search_ipa(no_punc_one_word)
            # If not found, try it with a space instead of hyphen.
            if not transcription:
                no_punc_with_space = no_punc.replace("-", " ")
                transcription = search_ipa(no_punc_with_space)
                # If not found, split where the hyphens are and look up the words separately.
                if not transcription:
                    word_split = no_punc.split("-")
                    transcription = []
                    for item in word_split:
                        ipa = search_ipa(item)
                        # Add each part to the transcription. First chop each off at the comma if any.
                        if ipa[0].find(",") != -1:
                            transcription.append(ipa[0][0:ipa[0].index(",")] + " /")
                        else:
                            transcription.append(ipa[0])
                    transcription = ["".join(transcription)]

    return transcription

# ------------------------

print "Please input a sentence in English."
string = raw_input("> ")
wordlist = string.split()
ipalist = []
final = ""

# Find IPA for every word in the user input string, and add it to the list of results.
for word in wordlist:
    transcription = get_ipa(word)
    ipalist.append(transcription)

# For each sublist in the list of results, add its first item to the final output.
for sublist in ipalist:
    # If the IPA was found in the dictionary, add it to the output.
    if sublist:
        # If there are multiple pronunciations (indicated with comma), use only the first (up to the comma).
        if sublist[0].find(",") != -1:
            final += sublist[0][0:sublist[0].index(",")] + " /"
        else:
            final += sublist[0]
    # If no IPA was found for the word, give an error message. 
    else:
        final += "/[NOT FOUND] /"

# --------------------------------
# TRANSCRIPTION CONVENTIONS

# Dictionary.com uses <ər> for unstressed syllabic r and "ɜr" for stressed. Change to <ɹ̩>.
final = final.replace(u"ər", u"ɹ̩").replace(u"ɜr", u"ɹ̩")
# Change the <r> symbol that Dictionary.com uses to <ɹ>.
final = final.replace("r", u"ɹ")

# --------------------------------
# PUNCTUATION STUFF

# Dictionary.com uses spaces for breaks between unstressed syllables; change these to periods, as is standard in linguistics
final = re.sub("(?<![/]) (?!/)", ".", final)
# Also do so when a (primary or secondary) stress mark separates syllables. (These look like ' and , but they're not.)
final = re.sub(u"(?<!/)([\ˈ\ˌ])", r".\1", final)
# Remove commas, semicolons and slashes. (This must be ordered after the syllable thing.)
final = re.sub("[/;,]", "", final)
# Remove whitespace at the beginning or end.
final = final.strip(" ")
# Add a slash at the beginning and end.
final = "/" + final + "/"
# Fix the not-founds--those SHOULD have spaces.
final = final.replace("NOT.FOUND", "NOT FOUND")
# --------------------------------


print final

# TO-DO:

# 1. Give it other sites to try, e.g. Wiktionary, if it can't find it on Dictionary.com
# 2. Figure out the weird stuff that happens when there is non-IPA material in the IPA box on Dictionary.com.
#   - E.g., look up "the". I think an HTML italic tag is getting in the way.
# 3. Find other sites (e.g. Wiktionary) that have IPA, and have it check those if nothing on dictionary.com.
#   - Note: sometimes Wiktionary has a rhyme in IPA: https://en.wiktionary.org/wiki/furious#Pronunciation
#       Have to check if this is indicated differently than a full pronunciation.
# 4. When there are multiple IPA pronunciations, instead of throwing out all but the first, have the program offer
#   options to the user.
#   - Might have to work differently for alternates offered in the same definition vs. subsequent ones.
#   - Sometimes only a syllable or two of the alternative are indicated, the rest of the word assumed to be the same.
#       Look for a reliable way to handle this.
# 5. Looping: better to a) enclose the whole program in a while-loop, or b) make it a function, and enclose that
#   function in a while-loop at the end?