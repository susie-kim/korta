import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from tkinter import *
from tkinter import filedialog
import sys
import webbrowser
from docx2python import docx2python
import numpy
import pathlib
import re
import emoji
from konlpy import utils
from konlpy.tag import Komoran
import pandas as pd
from wordcloud import WordCloud

komoran = Komoran()

# reads the text and removes extra space
def read(input_file):
    file_extension = pathlib.Path(input_file).suffix
    if file_extension == '.txt':
        original_text = utils.read_txt(input_file)
        return original_text
    elif file_extension == '.docx':
        read_text = docx2python(input_file).body
        original_text = ' '.join(list(numpy.concatenate(read_text).flat))
        return original_text
    else:
        msgbox.showwarning("Warning", "Select a txt or docx file.")
        return

# removes emjois and corrects some spacing
def clean(original_text):
    clean_text = emoji.get_emoji_regexp().sub('', original_text)
    clean_text = re.sub('[.]+', '. ', clean_text)
    clean_text = re.sub('[!]+', '! ', clean_text)
    clean_text = re.sub('[?]+', '? ', clean_text)
    return clean_text

# reformats the tagged POS with correct lines
def format_tag(clean_text):
    text_tagged = komoran.pos(clean_text)
    text_formatted = ''
    for i in range(len(text_tagged)):
        text_formatted += ((text_tagged[i][0] + '/' + text_tagged[i][1] + ' '))
        i += 1
    text_lines = re.sub('SF', 'SF \\n', text_formatted)
    return text_lines

# finds line numbers of matching patterns in the tagged POS
def find_lineid(pattern, text_lines, flags=0):
    matches = list(re.finditer(pattern, text_lines, flags))
    if not matches:
        return []
    end = matches[-1].start()
    # -1 so a failed 'rfind' maps to the first line.
    newline_table = {-1: 0}
    for i, m in enumerate(re.finditer(r'\n', text_lines), 1):
        # don't find newlines past our last match
        offset = m.start()
        if offset > end:
            break
        newline_table[offset] = i

    # Failing to find the newline is OK, -1 maps to 0.
    for m in matches:
        newline_offset = text_lines.rfind('\n', 0, m.start())
        line_number = newline_table[newline_offset]
        yield line_number

# searches from a list of vocabulary and outputs the number of words used from the list
def search_vocab_message(formatted_text, vocab_df):
    vocab_list = {}
    for i in range(len(vocab_df['Pattern'])):
        pattern = re.compile(vocab_df['Pattern'].iloc[i])
        matches = pattern.findall(formatted_text)
        if len(matches) >= 1:
            vocab_list.update({vocab_df['Word'].iloc[i]: len(matches)})
        else:
            pass
    print('Vocabulary Use:\n You have used ' + str(len(vocab_list)) + ' new words:\n')

# searches from a list of vocabulary and outputs a list of words used from the list
def search_vocab_list(formatted_text, vocab_df):
    vocab_list = {}
    for i in range(len(vocab_df['Pattern'])):
        pattern = re.compile(vocab_df['Pattern'].iloc[i])
        matches = pattern.findall(formatted_text)
        if len(matches) >= 1:
            vocab_list.update({vocab_df['Word'].iloc[i] + ' (' + vocab_df['Lesson'].iloc[i] + ')': len(matches)})
        else:
            pass
    df_list = pd.DataFrame(vocab_list.items())
    df_list.columns = ['Word', 'Count']

    print(df_list.to_string(index=False))  # add df.to_html(index=False)

# searches from a list of vocabulary and outputs a list of grammar items used from the list
def search_grammar(clean_text, formatted_text, grammar_df):

    # clean the original text to show in the results
    original_lines = re.sub('[.]+', '.\\n', clean_text)
    original_lines = re.sub('[!]+', '!\\n', original_lines)
    original_lines = re.sub('[?]+', '?\\n', original_lines)

    print('Grammar Use:', end='')
    # iterate through the grammar patterns
    for i in range(len(grammar_df['Pattern'])):
        
        # line numbers in the tagged text
        lines_found = list(find_lineid(str(grammar_df.loc[i, 'Pattern']), formatted_text))
    
        if len(lines_found) >= 1:
            print('\n\n', str(grammar_df.loc[i, 'No']), '\"' + str(grammar_df.loc[i, 'Grammar']) + '\"' + ' was found', len(lines_found), 'times:', end='')
            line_list = []

            for ln in lines_found:
                line_list.append(original_lines.split(sep='\n')[ln])
            
            line_set = sorted(set(line_list), key=line_list.index)
        
            for id in line_set:
                print('\n   \u2022', id, end='')

        else:
            pass
    
# creates a wordcloud image
def text_wc(input_filename, filename_out):
    original_text = read(input_filename)
    text_clean = clean(original_text)
    text_tagged = komoran.pos(text_clean)

    df = pd.DataFrame(text_tagged, columns=['Word', 'Tag'])
    pd.options.mode.chained_assignment = None  # default='warn'

    df_1 = df[df['Tag'].isin(['NNG', 'NNP', 'NNB', 'MAG', 'MAJ'])]
    df_2 = df[df['Tag'].isin(['VV', 'VA'])]
    df_3 = df[df['Tag'] == 'XR']

    df_2['Word'] = df_2['Word'] + '다'
    df_3['Word'] = df_3['Word'] + '하다'
    dfs = [df_1, df_2, df_3]
    df_all = pd.concat(dfs)

    df_freq = df_all.groupby(['Word']).size().reset_index(name='n') #reset_index makes it a dataframe, not a series
    word_list = df_freq.values.tolist()

    if font_path.get() == '':
        wc = WordCloud(font_path='/System/Library/Fonts/AppleSDGothicNeo.ttc', background_color='white', margin = 20, width=1000, height=600, max_words=100, max_font_size=200)
    else:
        wc = WordCloud(font_path=font_path.get(), background_color='white', margin = 20, width=1000, height=600, max_words=100, max_font_size=200)
    
    wc.generate_from_frequencies(dict(word_list))
    wc.to_file(filename_out)


# statistics
def stats(input_filename):
    original_text = read(input_filename)
    text_clean = clean(original_text)
    text_tagged = komoran.pos(text_clean)
    text_lines = format_tag(text_clean)

    df = pd.DataFrame(text_tagged, columns=['Word', 'Tag'])
    pd.options.mode.chained_assignment = None  # default='warn'

    df_1 = df[df['Tag'].isin(['NNG', 'NNP', 'NNB', 'MAG', 'MAJ'])]
    df_2 = df[df['Tag'].isin(['VV', 'VA'])]
    df_3 = df[df['Tag'] == 'XR']

    df_2['Word'] = df_2['Word'] + '다'
    df_3['Word'] = df_3['Word'] + '하다'
    dfs = [df_1, df_2, df_3]
    df_all = pd.concat(dfs)
    no_total_words = len(df_all.index)
    # unique_words = pd.unique(df_all['Word'])
    no_unique_words = len(pd.unique(df_all['Word']))

    no_ec = len(re.compile('/EC').findall(text_lines))
    no_etm = len(re.compile('/ETM').findall(text_lines))
    no_sentences = len(re.compile('\\n').findall(text_lines))

    if no_sentences == 0:
        msgbox.showwarning("Warning", "Please enter more than one sentence.")
        return

    print('\n Total number of content words used:', no_total_words)
    print('\n Word diversity:', '\n \u2794', round(no_unique_words/no_total_words, 3),  ': number of unique words divided by the total number of words')
    print('\n Sentence complexity:', '\n \u2794', round(no_ec/no_sentences, 3), ': number of clauses per sentence', end='')
    print('\n \u2794', round(no_etm/no_sentences, 3), ': number of noun modifiers per sentence')

# GUI
root = Tk()
root.title("Korean Text Analyzer (Beta)")

# GUI functions
def add_file():
    files = filedialog.askopenfilenames(title="Select text files", filetypes=(("TXT", "*.txt"), ("DOCX", "*.docx"), ("All files", "*.*")))  # select files
    for n in files:  # list of selected files
        listbox.insert(END, n)

def delete_file():
    for f in reversed(listbox.curselection()): # make a reversed list to delete from the end
        listbox.delete(f)

def show_contact():
    msgbox.showinfo("Contact", "Susie Kim: susiek@princeton.edu\nBrian Zhen: bzhen@princeton.edu")

def open_web():
    webbrowser.open("https://github.com/susie-kim/korta", new=1)

# Menu
menu = Menu(root)

# File Menu
menu_file = Menu(menu, tearoff=0)
menu_file.add_command(label="Add file(s)", command=add_file)
menu_file.add_separator()
menu_file.add_command(label="Quit", command=root.quit)

menu.add_cascade(label="File", menu=menu_file)  # Menu bar, add cascade menu

# Info Menu
menu_info = Menu(menu, tearoff=0)
menu_info.add_command(label="Contact", command=show_contact)
menu_info.add_command(label="Go to website", command=open_web)

menu.add_cascade(label="Info", menu=menu_info)  # Menu bar, add cascade menu

# Top buttons
frame_top = Frame(root)
frame_top.pack(fill="x", padx=5, pady=5)

btn_add_file = Button(frame_top, text="Add files", command=add_file, padx=10, pady=4, width=15)
btn_del_file = Button(frame_top, text="Delete selected", command=delete_file, padx=10, pady=4, width=15)

btn_add_file.pack(side="left")
btn_del_file.pack(side="right")

# Listbox for files
frame_listbox = LabelFrame(root, text="Add text file(s) to process")
frame_listbox.pack(fill="both", padx=5, pady=5)

scrollbar = Scrollbar(frame_listbox)
scrollbar.pack(side="right", fill="y")

listbox = Listbox(frame_listbox, selectmode="extened", height=5, yscrollcommand=scrollbar.set)
listbox.pack(side="left", fill="both", expand=True)
scrollbar.config(command=listbox.yview)

# Textbox
frame_textbox = LabelFrame(root, text="Type in text to process")
frame_textbox.pack(fill="both", padx=5, pady=5)
txt = Text(frame_textbox, height=10, padx=5, pady=5)
txt.pack(fill="both", padx=5, pady=5)

def delete(): # Delete text
    txt.delete("1.0", END)

# btn_submit = Button(frame_textbox, text="Submit", command=submit, padx=10, pady=4)
btn_delete = Button(frame_textbox, text="Delete", command=delete, padx=10, pady=4)

# btn_submit.pack(side="right")
btn_delete.pack(side="right")

# Output path frame
frame_path = LabelFrame(root, text="Select a folder to save the report")
frame_path.pack(fill="x", padx=5, pady=5, ipady=5)

output_path = Entry(frame_path)
output_path.pack(side="left", fill="x", expand=True, ipady=4, padx=5, pady=5)    #ipady = change height

def find_path(): 
    folder_selected = filedialog.askdirectory()
    if folder_selected == "":   # when the user selects cancel
        return
    output_path.delete(0, END)
    output_path.insert(0, folder_selected)

btn_find = Button(frame_path, text="Find", command=find_path, padx=10, pady=5, width=5)
btn_find.pack(side="right")

# Font path frame
frame_font = LabelFrame(root, text="Select a font for your wordcloud (optional)")
frame_font.pack(fill="x", padx=5, pady=5, ipady=5)

font_path = Entry(frame_font)
font_path.pack(side="left", fill="x", expand=True, ipady=4, padx=5, pady=5)    #ipady = change height

def find_font(): 
    font_selected = filedialog.askopenfilenames(title="Select font", filetypes=(("ttf", "*.ttf"), ("ttc","*.ttc"), ("otf", "*.otf"), ("All files", "*.*")), initialdir='/System/Library/Fonts')
    if font_selected == "":   # when the user selects cancel
        return
    font_path.delete(0, END)
    font_path.insert(0, font_selected)

btn_font = Button(frame_font, text="Find", command=find_font, padx=10, pady=5, width=5)
btn_font.pack(side="right")

# Options frame
frame_option = LabelFrame(root, text="Select your target level")
frame_option.pack(fill="x", padx=5, pady=5, ipady=5)

## Level combobox
label_level = Label(frame_option, width=10)
label_level.pack(side="left", padx=5, pady=5)

opt_level = ['ALL', 'KOR105', 'KOR107']

cmb_level = ttk.Combobox(frame_option, state="readonly", values=opt_level, width=10)
cmb_level.current(0)
cmb_level.pack(side="left", padx=5, pady=5)

def textbox_wc(filename_out):
    clean_text = emoji.get_emoji_regexp().sub('', txt.get("1.0", END))
    clean_text = re.sub('[.]+', '. ', clean_text)
    clean_text = re.sub('[!]+', '! ', clean_text)
    clean_text = re.sub('[?]+', '? ', clean_text)
    clean_text = ' '.join(clean_text.split())
    text_tagged = komoran.pos(clean_text)

    df = pd.DataFrame(text_tagged, columns=['Word', 'Tag'])
    pd.options.mode.chained_assignment = None  # default='warn'

    df_1 = df[df['Tag'].isin(['NNG', 'NNP', 'NNB', 'MAG', 'MAJ'])]
    df_2 = df[df['Tag'].isin(['VV', 'VA'])]
    df_3 = df[df['Tag'] == 'XR']

    df_2['Word'] = df_2['Word'] + '다'
    df_3['Word'] = df_3['Word'] + '하다'
    dfs = [df_1, df_2, df_3]
    df_all = pd.concat(dfs)

    df_freq = df_all.groupby(['Word']).size().reset_index(name='n') #reset_index makes it a dataframe, not a series
    word_list = df_freq.values.tolist()

    if font_path.get() == '':
        wc = WordCloud(font_path='/System/Library/Fonts/AppleSDGothicNeo.ttc', background_color='white', margin = 20, width=1000, height=600, max_words=100, max_font_size=200)
    else:
        wc = WordCloud(font_path=font_path.get(), background_color='white', margin = 20, width=1000, height=600, max_words=100, max_font_size=200)

    wc.generate_from_frequencies(dict(word_list))
    wc.to_file(filename_out)

def textbox_stats():
    clean_text = emoji.get_emoji_regexp().sub('', txt.get("1.0", END))
    clean_text = re.sub('[.]+', '. ', clean_text)
    clean_text = re.sub('[!]+', '! ', clean_text)
    clean_text = re.sub('[?]+', '? ', clean_text)
    clean_text = ' '.join(clean_text.split())
    text_tagged = komoran.pos(clean_text)
    text_lines = format_tag(clean_text)

    df = pd.DataFrame(text_tagged, columns=['Word', 'Tag'])
    pd.options.mode.chained_assignment = None  # default='warn'

    df_1 = df[df['Tag'].isin(['NNG', 'NNP', 'NNB', 'MAG', 'MAJ'])]
    df_2 = df[df['Tag'].isin(['VV', 'VA'])]
    df_3 = df[df['Tag'] == 'XR']

    df_2['Word'] = df_2['Word'] + '다'
    df_3['Word'] = df_3['Word'] + '하다'
    dfs = [df_1, df_2, df_3]
    df_all = pd.concat(dfs)
    no_total_words = len(df_all.index)
    unique_words = pd.unique(df_all['Word'])
    no_unique_words = len(pd.unique(df_all['Word']))
    ttr = no_unique_words/no_total_words

    no_ec = len(re.compile('/EC').findall(text_lines))
    no_sentences = len(re.compile('\\n').findall(text_lines))
    no_etm = len(re.compile('/ETM').findall(text_lines))

    if no_sentences == 0:
        msgbox.showwarning("Warning", "Please enter more than one sentence.")
        return

    print('\n Total number of content words used:', no_total_words)
    print('\n Word diversity:', '\n \u2794', round(ttr, 3),  ': number of unique words divided by the total number of words')
    print('\n Sentence complexity:', '\n \u2794', round(no_ec/no_sentences, 3), ': number of clauses per sentence', end='')
    print('\n \u2794', round(no_etm/no_sentences, 3), ': number of noun modifiers per sentence')


def search_report(): 
    grammar_list = ['Level', 'No', 'Grammar', 'Pattern']
    url_grammar = r'https://raw.githubusercontent.com/susie-kim/korta/master/grammar_list.csv'
    grammar_df = pd.read_csv(url_grammar, usecols=grammar_list, sep=',', encoding='utf-8').dropna()
        
    # list of target vocabulary
    vocab_list = ['Level', 'Lesson', 'Word', 'Pattern']
    url_vocab = r'https://raw.githubusercontent.com/susie-kim/korta/master/vocab_list.csv'
    vocab_df = pd.read_csv(url_vocab, usecols=vocab_list, sep=',', encoding='utf-8').dropna()

    if listbox.size() != 0:
        for i in range(listbox.size()):
            current_file = listbox.get(i)
            print(current_file)
            file_name = pathlib.Path(current_file).stem
            original_text = read(current_file)
            clean_text = clean(original_text)
            formatted_text = format_tag(original_text)
            target_level = cmb_level.get()
            original_stdout = sys.stdout
            with open(output_path.get()+'/KTA_report_'+target_level+'_'+file_name+'.txt', 'w', encoding='utf8') as f:
                sys.stdout = f
                
                if target_level == 'KOR105':
                    # subset KOR105
                    grammar_i = grammar_df[grammar_df['Level'] == 'KOR105']
                    search_grammar(original_text, formatted_text, grammar_i)
                    print('\n')
                    vocab_i = vocab_df[vocab_df['Level'] == 'KOR105']
                    search_vocab_message(formatted_text, vocab_i)
                    search_vocab_list(formatted_text, vocab_i)

                elif target_level == 'KOR107':
                    # subset KOR107
                    grammar_ii = grammar_df[grammar_df['Level'] == 'KOR107']
                    grammar_ii = grammar_ii.reset_index(drop=TRUE)
                    search_grammar(original_text, formatted_text, grammar_ii)
                    print('\n')
                    vocab_ii = vocab_df[vocab_df['Level'] == 'KOR107']
                    vocab_ii = vocab_ii.reset_index(drop=TRUE)
                    search_vocab_message(formatted_text, vocab_ii)
                    search_vocab_list(formatted_text, vocab_ii)
            
                else: 
                    search_grammar(original_text, formatted_text, grammar_df)
                    print('\n')
                    search_vocab_message(formatted_text, vocab_df)
                    search_vocab_list(formatted_text, vocab_df)
                    stats(current_file)
                
                sys.stdout = original_stdout
            text_wc(current_file, output_path.get()+'/KTA_wc_'+file_name+'.png')
    
    elif len(txt.get("1.0", END)) >= 1:
        clean_text = emoji.get_emoji_regexp().sub('', txt.get("1.0", END))
        clean_text = re.sub('[.]+', '. ', clean_text)
        clean_text = re.sub('[!]+', '! ', clean_text)
        clean_text = re.sub('[?]+', '? ', clean_text)
        original_text = ' '.join(clean_text.split())
        formatted_text = format_tag(original_text)
        target_level = cmb_level.get()
        original_stdout = sys.stdout
        with open(output_path.get()+'/KTA_report_'+target_level+'.txt', 'w', encoding='utf8') as f:
            sys.stdout = f
            
            if target_level == 'KOR105':
                # subset KOR105
                grammar_i = grammar_df[grammar_df['Level'] == 'KOR105']
                search_grammar(original_text, formatted_text, grammar_i)
                print('\n')
                vocab_i = vocab_df[vocab_df['Level'] == 'KOR105']
                search_vocab_message(formatted_text, vocab_i)
                search_vocab_list(formatted_text, vocab_i)

            elif target_level == 'KOR107':
                # subset KOR107
                grammar_ii = grammar_df[grammar_df['Level'] == 'KOR107']
                grammar_ii = grammar_ii.reset_index(drop=TRUE)
                search_grammar(original_text, formatted_text, grammar_ii)
                print('\n')
                vocab_ii = vocab_df[vocab_df['Level'] == 'KOR107']
                vocab_ii = vocab_ii.reset_index(drop=TRUE)
                search_vocab_message(formatted_text, vocab_ii)
                search_vocab_list(formatted_text, vocab_ii)
        
            else: 
                search_grammar(original_text, formatted_text, grammar_df)
                print('\n')
                search_vocab_message(formatted_text, vocab_df)
                search_vocab_list(formatted_text, vocab_df)
                textbox_stats()
            
            sys.stdout = original_stdout
        textbox_wc(output_path.get()+'/KTA_wc.png')
    else:
        pass

def start():
    try:
        # check file list
        if listbox.size() == 0 and len(txt.get("1.0", END)) == 0:
            msgbox.showwarning("Warning", "Add text to analyze.")
            return

        # check output path
        if len(output_path.get()) == 0:
            msgbox.showwarning("Warning", "Select a folder to save the report.")
            return

    # run
        search_report()
        msgbox.showinfo("Success", "Your report has been saved.")

    except Exception as err:
        msgbox.showerror("Error", err)

# Execute buttons
frame_exe = Frame(root)
frame_exe.pack(fill="x", padx=5, pady=5)

btn_close = Button(frame_exe, text="Quit", command=root.quit, padx=5, pady=4, width=10)
btn_start = Button(frame_exe, text="Start", command=start, padx=5, pady=4, width=10)

btn_close.pack(side="right", padx=5, pady=5)
btn_start.pack(side="right", padx=5, pady=5)

root.config(menu=menu)
root.mainloop()