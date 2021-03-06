# -*- coding: utf-8 -*-
"""book-data.ipynb
Automatically generated by Colaboratory.

"""# 2. Preprocessing"""

import numpy as np
import pandas as pd
import json
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

"""## 1. Helper Function"""

def resetIndex(df):
    df.reset_index(inplace=True)
    df.drop('index', axis=1, inplace=True)

"""### 1. Publisher"""

def findPublishersContainString(df, string):
    result = df.loc[df.publisher.str.contains(string), 'publisher'].unique()
    return result

def replacePublisher(df, findName, replaceName):
    temp = findPublishersContainString(df, findName.strip())
    df.publisher.replace(temp, replaceName.strip(), inplace=True)

def preprocessPublisher(df, listName): #[{findname: , replacename:}]
    for item in listName:
        replacePublisher(df, item['findName'], item['replaceName'])

"""### 2. Isbn"""

def getIsbnValue(df, col, value):
    try: 
        return df.loc[df[col] == value, 'isbn13'].values[0]
    except:
        return None

# isbn of two row is the same, condition is where we want to find row to drop it
def dropDuplicatedIsbn(df, condition): #condition = {}
    for col, value in condition.items():
        isbn = getIsbnValue(df, col, value)
        if (isbn != None):
            df.drop(df.loc[(df[col] == value) & (df['isbn13'] == isbn)].index, inplace=True)
        
def processDuplicatedIsbn(df, conditions): # conditions = [{}, {}, ...]:
    for condition in conditions:
        dropDuplicatedIsbn(df, condition)

"""### 3. Genre"""

def preprocessGenre(text):
    temp = text.split(',')[0]
    result = temp.split('\\\\')[1]
    return result.strip()

"""## 2. Main - read dataFrame at this position"""
df = pd.read_json('./new_book_1667.json', orient="table")


df.replace('Null', np.NaN, inplace=True)
df.dropna(subset=['isbn13'], inplace=True)
df.drop(['page'], axis=1, inplace=True)
resetIndex(df)

df['genre'] = df['genre'].apply(lambda text: preprocessGenre(text))
df.drop(df[df['genre'] == 'Accounting'].index, inplace=True)
df.genre.replace('Programming', 'Programming: Games', inplace=True)
df.genre.replace('Cybernetics', 'Cybernetics: Artificial Intelligence', inplace=True)

df.publisher = df.publisher.fillna('nopublisher')


df.isbn13 = df.isbn13.apply(lambda isbn: isbn.replace('-', '').strip())
df.isbn13 = df.isbn13.apply(lambda isbn: isbn.replace('.', '').strip())
wrongIsbnIndex = df.loc[df.isbn13.apply(len) != 13, 'isbn13'].index
for i in wrongIsbnIndex:
    temp = df.loc[i, 'isbn13'].split(' ')
    df.loc[i, 'isbn13'] = temp[0]

for col in ['author', 'name', 'publisher', 'genre']:
    df.loc[:, col] = df.loc[:, col].apply(lambda text: text.replace('/n', '').strip())
df = df.drop_duplicates()
if (type(df) == pd.core.frame.DataFrame): print('done')

# hand process duplicated isbn13
deleteIsbn = ['9781591402398', '9780201316636', '9781591408000', 
              '9781540422651', '9781847194060', '9781847198501', '9781946442949', '0807060504765']
df.drop(df[df['isbn13'].isin(deleteIsbn)].index, inplace=True)

conditions = [ # conditions for book that will be dropped
    # 9781593278274
    {'author': 'DeBarros Anthony'},
    #9781617294945
    {'name': 'Spring in Action'},
    # 9781848000704
    {'author': 'Steven S. Skiena (auth.)'},
    # 9781904811510
    {'name': 'Mastering Mambo: E-commerce, Templates, Module Development, Seo, Security, And Performance'},
    # 9783540205005
    {'author': 'Daniel J. Veit (auth.),Khosrow-Pour M.'},
    # 9780070131514
    {'name': 'Introduction to algorithms. Instructor’s manual'},
    # 9780071592086
    {'author': 'Clayton M. Christensen,Jerome H. Grossman,Jason Hwang,Jerri L. Ledford,Mary E. Tyler,Clayton M. Christensen,Clayton M. Christensen,Michael E. Raynor,Michael B. Horn,Heather Staker,Clayton M. Christensen,Clayton M. Christensen,Karen Dillon,Taddy Hall,David S. Duncan'},
    # 9780201316636
    {'name': 'Algorithms in C, Part 5: Graph Algorithmsl'},  
    # 9780316380508
    {'author': 'Kevin D. Mitnick,Robert Vamosi'},  
    # 9780321573513
    {'name': 'Algorithms (part 2, electronic edition)'},  
    # 9780471180906
    {'author': 'Gordon E. Smith,Steven M. Bragg,P. Candace Deans'},    
    # 9780980232776
    {'name': 'Introduction to Linear Algebra'},    
    # 9780981519401
    {'name': 'The Analysis of Biological Data: Solutions Manual'},    
    # 9781492032649
    {'name': 'Hands-On Machine Learning with Scikit-Learn, Keras, and Tensorflow: Concepts, Tools, and Techniques to Build Intelligent Systems'},    
    # 9781492040347
    {'name': 'Database Internals: A deep-dive into how distributed data systems work'},    
    # 9781590597507
    {'name': "Pro PayPal E-Commerce (Expert's Voice)"},
    # 
    {'name': 'Django 3 Web Development Cookbook'},
    #
    {'author': 'William Rice'},
    #
    {'author': 'Daniel J. Veit ,Khosrow-Pour M.'}
]
processDuplicatedIsbn(df, conditions)
resetIndex(df)


publisherNameToProcess = [
    { 'findName': 'Wiley', 'replaceName': 'Wiley'},
    { 'findName': 'Packt', 'replaceName': 'Packt'},
    { 'findName': 'Springer', 'replaceName': 'Springer'},
    { 'findName': 'Reilly', 'replaceName': "O'Reilly"},
    { 'findName': 'Apress', 'replaceName': 'Apress'},
    { 'findName': 'Manning', 'replaceName': 'Manning'},
    { 'findName': 'Pearson', 'replaceName': 'Pearson'},
    { 'findName': 'Chapman', 'replaceName': 'Chapman and Hall'},
    { 'findName': "McGraw-Hill", 'replaceName': "McGraw-Hill"},
    { 'findName': 'Mcgraw-Hill', 'replaceName': 'McGraw-Hill'},
    { 'findName': 'McGraw Hill', 'replaceName': 'McGraw-Hill'},  
    { 'findName': 'Cambridge Uni', 'replaceName': 'Cambridge University Press'},
    { 'findName': 'CRC', 'replaceName': 'CRC Press'},
    { 'findName': 'Wesley', 'replaceName': 'Addison-Wesley Professional'},
    { 'findName': 'Morgan', 'replaceName': 'Morgan Kaufmann'},
    { 'findName': 'Oxford', 'replaceName': 'Oxford University Press'},
    { 'findName': 'Routledge', 'replaceName': 'Routledge'},
    { 'findName': "PTR", 'replaceName': "Course Technology PTR "},
    { 'findName': 'Cengage', 'replaceName': 'Cengage Learning'},
    { 'findName': 'Academic Press', 'replaceName': 'Academic Press'},
    { 'findName': 'Independently', 'replaceName': 'Independently Published'},
    { 'findName': "CreateSpace'", 'replaceName': 'CreateSpace IPP'},
    { 'findName': 'Osprey', 'replaceName': 'Osprey'},
    { 'findName': 'Elsevier', 'replaceName': 'Elsevier'},
    { 'findName': 'Jones & Bartlett', 'replaceName': 'Jones & Bartlett Publishers'},
    { 'findName': 'Penguin', 'replaceName': 'Penguin Books'},
    { 'findName': 'World', 'replaceName': 'World Scientific Publishing'},
    { 'findName': 'Project Management', 'replaceName': 'Project Management Institute Inc'},
    { 'findName': 'W. W.', 'replaceName': 'W. W. Norton Company'},
    { 'findName': 'Simon', 'replaceName': 'Simon Schuster'},
    { 'findName': 'Harper', 'replaceName': 'HarperCollins'},
    { 'findName': 'Random', 'replaceName': 'Random House'},
    { 'findName': 'Dorling', 'replaceName': 'Dorling Kindersley'},
    { 'findName': 'Portfolio', 'replaceName': 'Portfolio'},
    { 'findName': 'Sams', 'replaceName': 'Sams Publishing'},
    { 'findName': 'Active', 'replaceName': 'Active Learning Publisher'},
    { 'findName': 'APRESS', 'replaceName': 'Apress'},
    { 'findName': 'Greate', 'replaceName': 'Great Little Book Publishing'},
    { 'findName': 'SAGE', 'replaceName': 'SAGE Publications'},
    { 'findName': 'Taylor', 'replaceName': 'Taylor & Francis Group'},
    { 'findName': 'Wordware', 'replaceName': 'Wordware Publishing'},
    { 'findName': 'Bloom', 'replaceName': 'Bloomsbury'},
    { 'findName': 'Brooks', 'replaceName': 'Brooks Cole'},
    { 'findName': 'Printice Hall', 'replaceName': 'Prentice Hall'},
    { 'findName': 'Harvard', 'replaceName': 'Harvard University Press'},
    { 'findName': 'Crown', 'replaceName': 'Crown Publishers'},
    { 'findName': 'Sage', 'replaceName': 'SAGE Publications'},
    # { 'findName': 'Thomson Course Technology', 'replaceName': 'Thomson Course Technology'},
    { 'findName': 'A K PETERS', 'replaceName': 'A K Peters'},
    { 'findName': 'Createspace Independent Publishing Platform', 'replaceName': 'CreateSpace Independent Publishing Platform'},
    { 'findName': 'PALGRAVE MACMILLAN', 'replaceName': 'Palgrave Macmillan'},
    { 'findName': 'pen & sword', 'replaceName': 'Pen & Sword'},
]

preprocessPublisher(df, publisherNameToProcess)

publisherNameToDrop = ['人民邮电出版社', '社会科学文献出版社', '人民邮电出版社', 
                       'Universo dos Livros', 'EUG, Editorial Universidad de Granada',
                       'Companhia das Letras', '中信出版社', 'Питер', '西安电子科技大学出版社', 'CASA DO CODIGO',
                       '上海人民出版社', 'БХВ-Петербург', '生活·读书·新知三联书店 ', 'ООО "Альфа-книга"', 
                       '人民邮电出版社 = Post & Telecom Press','Манн, Иванов и Фербер ', '中信出版集团股份有限公司 ']
for item in publisherNameToDrop:
    df.drop(df[df.publisher == item.strip()].index, inplace=True)
df.drop_duplicates(inplace=True)
resetIndex(df)


def handProcessAuthor(df, processType, condition, field):
    indexes = df[df['author'] == condition].index
    for index in indexes:
        if processType == "assign":
            df.loc[index, 'author'] = field
        elif processType == "replace":
            for item in field:
                text = str(df.loc[index, 'author'])
                df.loc[index, 'author'] = text.replace(item['find'], item['replaceto'])

for t in [' (editors)', ' (Auth.)', ' (Editor)', ' (Editors)', ' (Author)', ' (eds.)']:
    df.loc[:, 'author'] = df.loc[:, 'author'].apply(lambda text: text.replace(t, ''))


authorArrayToProcess = [
    {'type': 'assign', 
     'condition': 'Readtrepreneur Publishing,summarizing a book by Michael E. Gerber', 
     'field': 'Michael E. Gerber'},
    
    {'type': 'assign', 
     'condition': 'Aggarwal,Charu C.,Reddy,Chandan K', 
     'field': 'Charu C. Aggarwal,Chandan K. Reddy'},
    
    {'type': 'replace',
     'condition': 'Manzur,A.,Marques,G.,Ariel Manzur,Chris Bradfield,Chris Bradfield [Chris Bradfield]', 
     'field': [{'find': ',Chris Bradfield [Chris Bradfield]', 'replaceto': ''},
               {'find': 'Manzur,A.,Marques,G.,', 'replaceto': ''}]},

    {'type': 'assign',
     'condition': 'Chris Bradfield,Ariel Manzur,Chris Bradfield,Chris Bradfield [Chris Bradfield]', 
     'field': 'Ariel Manzur,Chris Bradfield'},
    
    {'type': 'replace', 
     'condition': 'Shiv Aroor,Rahul Singh,Tanushree Podder [Podder,Tanushree]', 
     'field': [{'find': ' [Podder,Tanushree]', 'replaceto': ''}]},

    {'type': 'assign',
     'condition': 'Taylor,Allen G,Allen G. Taylor',
     'field': 'Allen G. Taylor'},

    {'type': 'assign',
    'condition': 'Krohn,J.,Beyleveld,G.,Bassens,A.',
    'field': 'Jon Krohn,Grant Beyleveld,Aglae Bassens'},

    {'type': 'assign',
    'condition': 'Ian Goodfellow and Yoshua Bengio and Aaron Courville.',
    'field': 'Ian Goodfellow,Yoshua Bengio,Aaron Courville'},

    {'type': 'assign',
    'condition': 'Ian Goodfellow and Yoshua Bengio and Aaron Courville',
    'field': 'Ian Goodfellow,Yoshua Bengio,Aaron Courville'},

    {'type': 'assign',
    'condition': 'Lee (Lee Sheldon) Sheldon',
    'field': 'Lee Sheldon'},

    {'type': 'replace', 
     'condition': 'Nicola Valcasara,Lauren S. Ferro [Lauren S. Ferro]', 
     'field': [{'find': ' [Lauren S. Ferro]', 'replaceto': ''}]},

    {'type': 'assign',
    'condition': 'Allen (Allen Sherrod) Sherrod',
    'field': 'Allen Sherrod'},
    
    {'type': 'assign',
    'condition': 'Mike (Mike Dickheiser) Dickheiser',
    'field': 'Mike Dickheiser'},
    
    {'type': 'assign',
    'condition': 'Bob (Bob Bates) Bates',
    'field': 'Bob Bates'},
    
    {'type': 'assign',
    'condition': 'Maneesh (Maneesh Sethi) Sethi',
    'field': 'Maneesh Sethi'},
    
    {'type': 'replace', 
    'condition': 'Albert Anthony,Anthony Sequeira [Anthony Sequeira],Anthony Sequeira [Anthony Sequeira]', 
    'field': [{'find': 'Anthony Sequeira [Anthony Sequeira],Anthony Sequeira [Anthony Sequeira]', 'replaceto': 'Anthony Sequeira'}]},
    
    {'type': 'assign',
    'condition': 'R. Keith Mobley President and CEO of Integrated Systems  Inc.',
    'field': 'R. Keith Mobley'},

    {'type': 'assign',
    'condition': 'RHJ,R.H. Jarrett',
    'field': 'R.H. Jarrett'},

    {'type': 'replace', 
     'condition': 'Jack R. Meredith,Scott M. Shafer,Samuel J. Mantel,Jr.', 
     'field': [{'find': 'Samuel J. Mantel,Jr.', 'replaceto': 'Samuel J. Mantel Jr'}]},

    {'type': 'replace', 
    'condition': 'Frank K. Reilly,Keith C. Brown,Reilly and Brown', 
    'field': [{'find': ',Reilly and Brown', 'replaceto': ''}]},

    {'type': 'replace', 
    'condition': 'Edward H. Shortliffe MD,PhD ,Edward H. Shortliffe,James J. Cimino', 
    'field': [{'find': ',PhD ', 'replaceto': ''}]},

    {'type': 'assign',
    'condition': 'Balakrishnan,N',
    'field': 'N. Balakrishnan'},

    {'type': 'assign',
    'condition': 'Nabil R. Adam,Yelena Yesha ,Nabil R. Adam,Yelena Yesha',
    'field': 'Nabil R. Adam,Yelena Yesha'},

    {'type': 'replace', 
    'condition': 'Carles Sierra,Frank Dignum ,Frank Dignum,Carles Sierra', 
    'field': [{'find': 'Frank Dignum ,', 'replaceto': ''}]},

    {'type': 'replace', 
    'condition': 'Jiming Liu,Yiming Ye ,Jiming Liu,Yiming Ye,Steven M. Bragg,P. Candace Deans', 
    'field': [{'find': 'Jiming Liu,Yiming Ye ,', 'replaceto': ''}]},

    {'type': 'assign',
    'condition': 'Jon Kleinberg,Éva Tardos',
    'field': 'Jon Kleinberg,Eva Tardos'},

    {'type': 'assign',
    'condition': 'In Lee,In Lee',
    'field': 'In Lee'},

    {'type': 'replace', 
    'condition': 'Steve Street,Mehdi Khosrow-Pour,Mehdi Khosrowpour,Vesna Hassler,Mehdi Khosrow-Pour', 
    'field': [{'find': ',Mehdi Khosrow-Pour', 'replaceto': ''}]},

    {'type': 'replace', 
    'condition': 'Carles Sierra,Frank Dignum,Carles Sierra', 
    'field': [{'find': ',Carles Sierra', 'replaceto': ''}]},

    {'type': 'replace', 
    'condition': 'William Rice,Khosrow-Pour M.,William Rice,Fernando J. Miguel,Robert Kent,Andrea Sacca', 
    'field': [{'find': 'William Rice,Khosrow-Pour M.,William Rice', 'replaceto': 'William Rice,Mehdi Khosrowpour'}]},

    {'type': 'replace', 
    'condition': 'Adam Higginbotham,Barry Kevin,Phillips Julia,Lerner Ben,Adam Higginbotham', 
    'field': [{'find': ',Adam Higginbotham', 'replaceto': ''}]},

    {'type': 'assign',
    'condition': 'Tim Marshall,Tim Marshall',
    'field': 'Tim Marshall'},

    {'type': 'assign',
    'condition': 'James Holland,James Holland',
    'field': 'James Holland'},

    {'type': 'assign',
    'condition': 'Martin Gilbert,Martin Gilbert',
    'field': 'Martin Gilbert'},

    {'type': 'replace', 
    'condition': 'Rick Atkinson,Verble Margaret,Rick Atkinson', 
    'field': [{'find': ',Rick Atkinson', 'replaceto': ''}]},

    {'type': 'assign',
    'condition': 'Mary Beard,Mary Beard',
    'field': 'Mary Beard'},

    {'type': 'assign',
    'condition': 'Pat Contri,Pat Contri',
    'field': 'Pat Contri'},

     {'type': 'assign',
    'condition': 'Darril Gibson,Darril Gibson',
    'field': 'Darril Gibson'},

     {'type': 'assign',
    'condition': 'Artiom Dashinsky,Artiom Dashinsky',
    'field': 'Artiom Dashinsky'},

    {'type': 'assign',
    'condition': 'Shankar IAS Academy,Prasad Rajendra,Publishers Rainbow,Prasad Rajendra',
    'field': 'Prasad Rajendra'},

    {'type': 'assign',
    'condition': 'David Icke,David Icke',
    'field': 'David Icke'},
]

for item in authorArrayToProcess:
    handProcessAuthor(df, item['type'], item['condition'], item['field'])
df

"""# 3. Modeling"""

from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

traindf = df.copy()
traindf

def makeLowerCase(text):
    return text.lower()

def removeWhiteSpace(text):
    return text.replace(' ', '')

for col in traindf.columns:
    traindf[col] = traindf[col].apply(removeWhiteSpace)
    traindf[col] = traindf[col].apply(makeLowerCase)

def createSoup(item):
    return " ".join([item[col] for col in traindf.columns if col in ['name', 'author', 'publisher', 'genre']])

traindf['soup'] = traindf.apply(createSoup, axis=1)
traindf.isbn13 = traindf.isbn13.apply(str)

isbnIndex = pd.Series(traindf.index, traindf.isbn13)

count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(traindf['soup'])
cosine_similarity_score = cosine_similarity(count_matrix, count_matrix)


pickle.dump(count_matrix, open('wordcountmatrix.pkl', 'wb'))


def get_recommendations_with_isbn_index(isbn, index, cosine_sim=cosine_similarity_score):
    idx = index[isbn]

    # Get similarity score
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort similarity scores in descending order
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get top 10 scores
    sim_scores = sim_scores[1:11]

    # Get the book indices
    book_indices = [i[0] for i in sim_scores]

    # Return most similar book
    return df.loc[book_indices, :]

get_recommendations_with_isbn_index('9780262028189', isbnIndex)