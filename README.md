# kortextanalyzer

Korta is a tool that parses and analyzes texts written in Korean. The list of grammar and vocabulary are based on: 
* Cho et al., (2020). *Integrated Korean: Intermediate 1* (3rd edition). University of Hawaii Press.
* Cho et al., (2020). *Integrated Korean: Intermediate 2* (3rd edition). University of Hawaii Press.


## Grammar Use:
A list of grammar from a specific level that you target will show in the report. If the list does not show the sentence where you used the grammar, it is probable that 1) there are grammatical errors in the text that resulted in incorrect parsing, or 2) the sentence structure is too complex with many modifications for the analyzer to correctly handle. Please contact the developer to help increase accuracy!

## Vocabulary Use:
A list of all vocabulary that you used from the specific level(s) that you selected will show in the report. If the list does not show when you used a word that is supposed to be on the list, it is likely that you have typos and/or conjugation errors that caused incorrect tagging. 

## Diversity and complexity metrics:

**Word diversity**: This measure indicates the level of diversity in your vocabulary use, that is, if you have a variety of words or you use words repetitively. For instance, if your score is 0.5, it means half of your words out of all are unique. 

**Number of clauses per sentence**: This measure indicates the average number of clauses per sentence. For instance, if your score is 1.0, that means each sentence has one clause (subject + predicate).

**Number of noun-modifying forms per sentence**: Complex sentences include relative clauses, and/or modifications (complex noun phrases) that provide more information. This measure indicates the average number of noun-modifying forms per sentence.


## Wordcloud:
Korta automatically generates a wordcloud based on the text. The image will be saved as a separate file in the output folder.

## Font: 
You can choose a specific font to create wordcloud. The font must support Korean or Unicode -- otherwise you will just see a lot of squares in your image!

## Important Note:
Keep in mind that linguistic aspects of your writing is just part of what makes your writing good or bad. This report only evaluates the extent of linguistic variety and complexity you attempted to achieve. It does not speak to the content or organization and tells little about the accuracy and effectiveness of your language use. 

*Currently only available for MacOS with Python 3.9 installed. 

## Troubleshooting:
Coming soon
