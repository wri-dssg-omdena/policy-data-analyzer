## Sentence splitting evaluation

----------------------------------
#### Some general evaluation criteria:

- "/" means good sentence
- "-/" means good sentence with a little bit of unnecessary additions
- "~/" means that it's understandable why this was considered (or not) a sentence, but it shouldn't have been because of how it works in the domain... in theory this is not bad, not taking points away for this
- "-" means not all the sentence was parsed/more than one sentences were parsed
- For non-clear sentences, we guide ourselves by the new line character
----------------------------------
### Chile

*Chile1.txt*

-> Evaluation substring:from the beginning until "Párrafo II"

- NLTK
	- Total identified sentences: 77
	- Identifies bullet points well, except the first one, if it comes after a heading like "Titulo I" or "Parrafo I", then the heading + the bullet point get processed
	- Overall gets everything right 
	- IMPORTANT: We should take a look at why the bullet points like "a)" got parsed correctly here but NOT in other document
	- Score: 21/21 

- Manual
	- Total identified sentces: 127
	- Gets rid of bullet points and letter/numbers (like a) or 1.) 
	- Also gets rid of words that appear a customizable stopwords list (such as "Decreto").
	- Score: 21/21

- SpaCy
	- Total identified sentences: 94
	- Similar to NLTK, the first bullets (like a)) can be appended to the heading, unnecessarily
	- Score: 21/21

*Chile2.txt*

-> Evaluation substring:from the beginning until "Lote 4 (b) de 1.171,08 hectáreas."

- NLTK
	- Total identified sentences: 192
	- Many badly split sentences here --> this time one sentence got split into multiple ones because of things like "ord." and "Sra." and "Corp." and "U.T.M."
	- Also that weird sentence with the V48 and V50... coordinates?
	- Score: 20/26
	- Error sentences:
		- Half:
			- Sentence_1
			- Sentence_14
			- Sentence_15
			- Sentence_16 
		- Full:
			- Sentence_2
			- Sentence_3
			- Sentence_20
			- Sentence_26
- Manual
	- Total identified sentences: 201
	- A bit of confusion between phrases ending in ";", and abreviations that use "."
	- Score: 23/26
	- Error sentences:
		- Half:
			- Sentence_3
			- Sentence_10
		- Full:
			- Sentence_20
			- Sentence_26
- Spacy
	- Total identified sentences: 88
	- Similar errors to NLTK
	- Score: 24.5/26
	- Error sentences:
		- Half:
			- Sentence_2
		- Full:
			- Sentence_3
			- Sentence_26

*Chile3.txt*

-> Evaluation substring:from the beginning until "(vi) panaderías que operen con combustible sólido y/o combustibles líquidos."

- NLTK
	- Total identified sentences: 59
	- Sentences 3-30 get put under the same one... because of a lack of period
	- Score: 3/61??????
	- Error sentences:
		- Sentence_3-Sentence_30?
		- Sentence_30-Sentence_56
		- Sentence_56-Sentence_61 
- Manual
	- Total identified sentences: 104
	- Most of the sentences got separated properly, except the ones that got separated by "S.A."
	- Error sentences:
		- Sentence_31-Sentence_33
		- Sentence_57-Sentence_61
- Spacy
	- Total identified sentences: 64
	- Random splits up to Sentence_10
	- Error sentences:
		- Sentence_10-Sentence_19
		- Sentence_22-Sentence-26
		- Sentence_26-Sentence_30
		- The rest...? There are bulet points that are joint together until sentence 9), Sentence_57-61


*General patterns to take in account for preprocessing*:
- Get rid of law numbers (Ley No 12.345) - splitting by space, identifying element next to No. and replacing with "Numero" and a random number.
- (PRIORITY) We need to do something about the bullet points like "a)"... Maybe we add a new line to the back, so it gets considered as a new sentence? Or we deal with them after the initial sentence splitting 
- Get rid of patterns like ".-" which are only confusing
- We can maybe get rid of periods that have a character with no space after them ("U.M" or "629.144" or "m.,", or ".(")
- Stopwords... are they useful? like "Articulo 7.-" or "Decreto:"... so far, they seem to not mess up with the sentence splitting system.
- (PRIORITY) Semicolons:
	- Get rid of semicolons? or replace them by periods? or replace them by spaces, or replace them by commas? 
	- When considering ";", we should check whether the next character is lowercase or not

----------------------------------
### USA

*USA_Sept302020.txt*

-> Evaluation substring:from the beginning until "Final Rule Issued Under Section 4(d) of the Act"

- NLTK
	- Total identified sentences: 244
	- Total sentences for evaluation extract: 51
	- Main errors come from confuesing docket numbers: "inspection at http://www.regulations.gov under Docket No. FWS-R4-ES-2018-0074."
	- Score: 41/43
	- Error sentences:
		- Half:
			- Sentence_7
			- Sentence_8
			- Sentence_9
			- Sentence_24

- Spacy
	- Total identified sentences: 277
	- Total sentences for evaluation extract: 78
	- Main errors also come from links AND docker numbers. Small errors from not properly identifying bullet points?
	- Score: 39.5/43
	- Error sentences:
		- Half:
			- Sentence_1
			- Sentence_2
			- Sentence_7
			- Sentence_8
			- Sentence_10
		- Full
			- Sentence_6
			- Sentence_7
			- Sentence_14
			- Sentence_24

- Manual
	- Total identified sentences: 135
	- Total sentences for evaluation extract: 27
	- Main issue here is that the text is read through lines and that mixes and cuts sentences in an undesirable way, as some sentences are separated by a new line in the middle.
	- Score: too low
	- Error sentences:
		- Sentence_13-Sentence_17 together
		- Sentence_18-Sentence_22 together
		- Sentence_22-Sentence_30 are both cut and mixed together


*General patterns to take in account for preprocessing:*
- Can filter out anything up to "ACTION: Final rule." or "-------------------" 
- We need to figure out how laws and docket numbers are represented, congressmen ("Cong."), sessions ("Sess."), district ("Dist.") numbers, etc.
- To figure out common patterns, we should grab everyting that comes before a "." and see if we can build them

----------------------------------
### El Salvador

*ElSalvador1.txt*


----------------------------------

INDIA

