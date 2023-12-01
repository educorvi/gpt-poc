searchQueryPromptMistral = ("[INST] Generate keywords for a search in a search index for the following question: '{question}'. The keywords MUST be in German! Return ONLY the keywords, formatted as JSON array! Do not generate more than 5 keywords. Return ONLY valid JSON, nothing else. Do NOT wrap it in markdown quotes! [/INST]")
mainTemplateMistral = ("{history}\n[INST] Use these sources for information: \n{context}\n-------\n-------\nAnswer the following question in german: {"
                       "question}. [/INST]\n")

searchQueryPromptSolar = ("### User:\n Generate keywords for a search in a search index for the following question: '{question}'. The keywords MUST be in German! Return ONLY the keywords, formatted as JSON array! Do not generate more than 5 keywords. Return ONLY valid JSON, nothing else. Do NOT wrap it in markdown quotes!")
mainTemplateSolar = ("{history}\n\n### User:\nUse these sources for information: \n{context}\n-------\n-------\nAnswer the following question in german: {"
                       "question}.\n")