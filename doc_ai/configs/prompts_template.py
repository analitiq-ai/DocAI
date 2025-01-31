COMMON_INSTRUCTIONS = """
When the document contains a date on it to which the information in the document relates, rather than the date of issue of the document, use the date to which the document relates in tags and also in the new directory name.
Tag files that mention on the of the following companies with company name: Acme1, Acme2,.
Many documents could relate to the following companies Acme1, Acme2, it is important to note this in tags and directory name.
When organising the documents into folders, first split by company or personal and then use category as the next level directory name.

"""
IMG_PROMPT = """
I would like you to extract all the text in the provided image.
You are not to summarise the text, but to provide it back to me as it is on the image.
Do not skip or shorten the text.
Do not add any of your own comments or observations.
I want you to also guess the language of the document.
Your response should be in json format without any extra text.
Follow these instructions for formating your response:
{format_instructions}
"""


PROCESS_DOC_TEXT_PROMPT = """
I would like you to examine the following document carefully.
This document has text in the following languages: {document_languages}.
The users language is also {user_language}.
You will be required to:
 - create a summary of the document
 - create tags for the document
 - categorise the document into one of the following categories: {categories}. If document does not fit into any of these categories, create a new category for it.
 - fit the document into the following directory structure: {dir_tree}. Creating new directories is allowed.
The response format instructions specify how you should return your response, follow them carefully.

# Important Notes:
{common_instructions}

# Document:
```
{document_text}
```

# Response format instructions:
Provide back your response according to the format instructions that follow.
You must provide response in json format without any extra text.
{format_instructions}
"""

PROCESS_TRANSLATE_DOC_TEXT_PROMPT = """
I would like you to examine the following document carefully.
This document has text in the following languages: {document_languages}.
The users language is {user_language}.
You will be required to:
 - translate it into {user_language}
 - create a summary of the document in {user_language}
 - create tags in {user_language}
 - categorise the document into one of the following categories: {categories}. If document does not fit into any of these categories, create a new category for it.
 - fit the document into the following directory structure: {dir_tree}. Creating new directories is allowed.
The response format instructions specify how you should return your response, follow them carefully.

# Important Notes:
{common_instructions}

# Document:
```
{document_text}
```

# Response format instructions:
Provide back your response according to the format instructions that follow.
You must provide response in json format without any extra text.
{format_instructions}
"""
