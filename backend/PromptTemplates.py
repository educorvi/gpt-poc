searchQueryPromptMistral = ("[INST] Generate keywords for a search in a search index for the following question: '{question}'. The keywords MUST be in German! Return ONLY the keywords, formatted as JSON array! Do not generate more than 5 keywords. Return ONLY valid JSON, no additional text! Do NOT wrap it in markdown quotes! [/INST]")
mainTemplateMistral = ("{history}\n[INST] Use these sources for information: \n{context}\n-------\n-------\nAnswer the following question in german: {"
                       "question}. [/INST]\n")
# mainTemplateMistral = (
#     "{history}\n[INST] Use these sources for information: \n{context}\n-------\n-------\nAnswer the following "
#     "question in german. Cite the source for your statements by adding the number of the source provided in "
#     "square brackets like so: This is a statement [n]. Do NOT list the sources at the and of the text! ONLY ADD THE SQUARE BRACKETS with the number behind the statement!\n"
#     "{question}. [/INST]\n")