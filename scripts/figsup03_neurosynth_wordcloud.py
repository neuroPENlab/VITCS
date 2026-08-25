#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
figsup03_neurosynth_wordcloud.py
@author: Angels Calvet-Mirabent
"""
from os.path import join
import pandas as pd
from wordcloud import WordCloud

# Create WordCloud object
wc = WordCloud(
    background_color='white',
    width=800,
    height=150,
    margin=2,
    prefer_horizontal=1,
    relative_scaling=0.6,
    colormap='viridis'
)
# Define text based on Neurosynth terms from the decoding
basedir = '<PATH_TO_PROJECT>'  # <-- EDIT THIS, same as other scripts

figdir = join(basedir, 'figures')
path_excel = '<PATH_TO_NEUROSYNTH_EXCEL>'  # <-- EDIT THIS, same as other scripts
excel = pd.read_excel(path_excel, sheet_name='NEGATIVE_ABS') # ALL POSITIVE NEGATIVE_ABS NEGATIVE

# Generate the word cloud ANATOMIC from the text data
text_anat = excel.loc[:,['Anatomic','Correlation_S']].set_index('Anatomic').to_dict()['Correlation_S']
wc.fit_words(text_anat)
# Save the word cloud to an image file
wc.to_file(join(figdir, 'figsup03a_neurosynth_WC_anatomic.png'))

# Generate the word cloud FUNCTIONAL from the text data
text_func = excel.loc[:,['Functional','Correlation_F']].set_index('Functional').to_dict()['Correlation_F']
wc.fit_words(text_func)
# Save the word cloud to an image file
wc.to_file(join(figdir, 'figsup03b_WC_functional.png'))