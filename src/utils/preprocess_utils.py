import re
import emoji
import numpy as np

import torch
from torchtext.legacy.data import Field, LabelField, TabularDataset, BucketIterator
from torchtext.vocab import build_vocab_from_iterator
from torch.utils.data import Dataset

import nltk
nltk.download('stopwords')

import spacy
import pandas as pd

from sklearn.model_selection import train_test_split

import transformers


dict_dataset_name = {'offenseval': {'train': 'data/offenseval_train.csv',\
     'val': 'data/offenseval_val.csv', 'test': 'data/offenseval_test.csv'}, 
     'covidhate' : {'train': 'data/covidhate_train.csv',\
     'val': 'data/covidhate_val.csv', 'test': 'data/covidhate_test.csv'},
     'SBF' : {'train': 'data/SBF_train.csv',\
     'val': 'data/SBF_val.csv', 'test': 'data/SBF_test.csv'},
     'implicithate' : {'train': 'data/implicithate_train.csv',\
     'val': 'data/implicithate_val.csv', 'test': 'data/implicithate_test.csv'}
     }

def format_training_file(text_file, module_path='', dataset_name=''):
    tweets = []
    classes = []
    if dataset_name == 'offenseval':
        for line in open(module_path+text_file,'r',encoding='utf-8'):
            line = re.sub(r'#([^ ]*)', r'\1', line)
            line = re.sub(r'https.*[^ ]', 'URL', line)
            line = re.sub(r'http.*[^ ]', 'URL', line)
            line = emoji.demojize(line)
            line = re.sub(r'(:.*?:)', r' \1 ', line)
            line = re.sub(' +', ' ', line)
            line = line.rstrip('\n').split('\t')
            tweets.append(line[1])
            classes.append(int(line[2]=='OFF'))

    elif dataset_name == 'covidhate':
        pass

    elif dataset_name == 'SBF':
        for line in open(module_path+text_file,'r',encoding='utf-8'):
            line = re.sub(r'#([^ ]*)', r'\1', line)
            line = re.sub(r'https.*[^ ]', 'URL', line)
            line = re.sub(r'http.*[^ ]', 'URL', line)
            line = emoji.demojize(line)
            line = re.sub(r'(:.*?:)', r' \1 ', line)
            line = re.sub(' +', ' ', line)
            line = line.rstrip('\n').split(',')
            offensive = set(['1', '1.0', '0', '0.0'])
            if len(line) >= 18 and line[4] in offensive:
                message = ""
                for i in range(14, len(line) - 3):
                    message += line[i]
                tweets.append(message)
                classes.append(line[4])

    else:
        for line in open(module_path+text_file,'r',encoding='utf-8'):
            line = re.sub(r'#([^ ]*)', r'\1', line)
            line = re.sub(r'https.*[^ ]', 'URL', line)
            line = re.sub(r'http.*[^ ]', 'URL', line)
            line = emoji.demojize(line)
            line = re.sub(r'(:.*?:)', r' \1 ', line)
            line = re.sub(' +', ' ', line)
            line = line.rstrip('\n').split('\t')
            hate_labels = set(['implicit_hate', 'explicit_hate'])
            if len(line) >= 3:
                tweets.append(line[1])
                classes.append(int(line[2] in hate_labels))
            
    
    # print(len(tweets), len(classes))
    return tweets[1:], classes[1:]

def train_val_split_tocsv(tweets, classes, val_size=0.2, module_path='', dataset_name=''):
    tweets_train, tweets_val, y_train, y_val = train_test_split(tweets, classes, test_size=val_size, random_state=42)

    df_train = pd.DataFrame({'text': tweets_train, 'label': y_train})
    df_val = pd.DataFrame({'text': tweets_val, 'label': y_val})

    df_train.to_csv(module_path+dict_dataset_name[dataset_name]['train'], index=False)
    df_val.to_csv(module_path+dict_dataset_name[dataset_name]['val'], index=False)

def format_test_file(text_file_testset, text_file_labels, module_path='', dataset_name=''):
    tweets_test = []
    y_test = []
    
    if dataset_name == 'offenseval':
        for line in open(module_path+text_file_testset,'r',encoding='utf-8'):
            line = re.sub(r'#([^ ]*)', r'\1', line)
            line = re.sub(r'https.*[^ ]', 'URL', line)
            line = re.sub(r'http.*[^ ]', 'URL', line)
            line = emoji.demojize(line)
            line = re.sub(r'(:.*?:)', r' \1 ', line)
            line = re.sub(' +', ' ', line)
            line = line.rstrip('\n').split('\t')
            tweets_test.append(line[1])
        for line in open(module_path+text_file_labels,'r',encoding='utf-8'):
            line = line.rstrip('\n').split('\t')
            y_test.append(int(line[0][-3:]=='OFF'))

    elif dataset_name == 'covidhate':
        pass

    elif dataset_name == 'SBF':
        for line in open(module_path+text_file_testset,'r',encoding='utf-8'):
            line = re.sub(r'#([^ ]*)', r'\1', line)
            line = re.sub(r'https.*[^ ]', 'URL', line)
            line = re.sub(r'http.*[^ ]', 'URL', line)
            line = emoji.demojize(line)
            line = re.sub(r'(:.*?:)', r' \1 ', line)
            line = re.sub(' +', ' ', line)
            line = line.rstrip('\n').split(',')
            offensive = set(['1', '1.0', '0', '0.0'])
            if len(line) >= 18 and line[4] in offensive:
                message = ""
                for i in range(14, len(line) - 3):
                    message += line[i]
                tweets_test.append(message)
                y_test.append(line[4])
        for line in open(module_path+text_file_labels,'r',encoding='utf-8'):
            line = re.sub(r'#([^ ]*)', r'\1', line)
            line = re.sub(r'https.*[^ ]', 'URL', line)
            line = re.sub(r'http.*[^ ]', 'URL', line)
            line = emoji.demojize(line)
            line = re.sub(r'(:.*?:)', r' \1 ', line)
            line = re.sub(' +', ' ', line)
            line = line.rstrip('\n').split(',')
            offensive = set(['1', '1.0', '0', '0.0'])
            if len(line) >= 18 and line[4] in offensive:
                message = ""
                for i in range(14, len(line) - 3):
                    message += line[i]
                tweets_test.append(message)
                y_test.append(line[4])
        return tweets_test[1:], y_test[1:]
            

    else:
        for line in open(module_path+text_file_testset,'r',encoding='utf-8'):
            line = re.sub(r'#([^ ]*)', r'\1', line)
            line = re.sub(r'https.*[^ ]', 'URL', line)
            line = re.sub(r'http.*[^ ]', 'URL', line)
            line = emoji.demojize(line)
            line = re.sub(r'(:.*?:)', r' \1 ', line)
            line = re.sub(' +', ' ', line)
            line = line.rstrip('\n').split('\t')
            hate_labels = set(['implicit_hate', 'explicit_hate'])
            if len(line) >= 3:
                tweets_test.append(line[1])
                y_test.append(int(line[2] in hate_labels))
        return tweets_test[1:], y_test[1:]

    # print(len(tweets_test), len(y_test))
    return tweets_test[1:], y_test

def test_tocsv(tweets_test, y_test, module_path='', dataset_name = ''):
    df_test = pd.DataFrame({'text': tweets_test, 'label': y_test})
    df_test.to_csv(module_path+dict_dataset_name[dataset_name]['test'], index=False)

def create_fields_dataset(model_type, fix_length=None, module_path='', dataset_name = ''):
    tokenizer = None
    if model_type == "DistillBert":
        tokenizer = transformers.DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
        pad_index = tokenizer.convert_tokens_to_ids(tokenizer.pad_token)
        print('pad_index', pad_index)
        field = Field(use_vocab=False, tokenize=tokenizer.encode, pad_token=pad_index, fix_length=fix_length)
    elif model_type == "DistillBertEmotion":
        tokenizer = transformers.DistilBertTokenizer.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
        pad_index = tokenizer.convert_tokens_to_ids(tokenizer.pad_token)
        print('pad_index', pad_index)
        field = Field(use_vocab=False, tokenize=tokenizer.encode, pad_token=pad_index, fix_length=fix_length)
    else:
        spacy_en = spacy.load("en_core_web_sm")
        def tokenizer_func(text):
            return [tok.text for tok in spacy_en.tokenizer(text)]

        field = Field(sequential=True, use_vocab=True, tokenize=tokenizer_func, lower=True, fix_length=fix_length,
                      stop_words = nltk.corpus.stopwords.words('english'))

    label = LabelField(dtype=torch.long, batch_first=True, sequential=False)
    fields = [('text', field), ('label', label)]
    print("field objects created")
    train_data, val_data = TabularDataset.splits(
        path = '',
        train=module_path+dict_dataset_name[dataset_name]['train'],
        test=module_path+dict_dataset_name[dataset_name]['test'],
        format='csv',
        fields=fields,
        skip_header=True,
    )
    _, test_data = TabularDataset.splits(
        path = '',
        train=module_path+dict_dataset_name[dataset_name]['train'],
        test=module_path+dict_dataset_name[dataset_name]['test'],
        format='csv',
        fields=fields,
        skip_header=True,
    )

    return (field, tokenizer, label, train_data, val_data, test_data)

#Create train and test iterators to use during the training loop
def create_iterators(train_data, test_data, batch_size, dev, shuffle=False):
    train_iterator, test_iterator = BucketIterator.splits(
        (train_data, test_data),
        shuffle=shuffle,
        device=dev,
        batch_size=batch_size,
        sort = False,
        )
    return train_iterator, test_iterator

def get_vocab_stoi_itos(field, tokenizer=None):
    if tokenizer is not None:
        vocab_stoi = tokenizer.encode
        vocab_itos = tokenizer.decode
    else:
        vocab_stoi = field.vocab.stoi
        vocab_itos = field.vocab.itos
    return (vocab_stoi, vocab_itos)

def get_datasets(training_data, testset_data, test_labels_data, model_type, fix_length=None, module_path='', dataset_name=''):
    # preprocessing of the train/validation tweets, then test tweets
    tweets, classes = format_training_file(training_data, module_path=module_path, dataset_name=dataset_name)
    tweets_test, y_test = format_test_file(testset_data, test_labels_data, module_path=module_path, dataset_name=dataset_name)
    print("file loaded and formatted..")
    train_val_split_tocsv(tweets, classes, val_size=0.2, module_path=module_path, dataset_name=dataset_name)
    test_tocsv(tweets_test, y_test, module_path=module_path, dataset_name=dataset_name)
    print("data split into train/val/test")

    field, tokenizer, label, train_data, val_data, test_data = create_fields_dataset(model_type, fix_length, 
                                                                                     module_path=module_path, dataset_name=dataset_name)

    # build vocabularies using training set
    print("fields and dataset object created")
    field.build_vocab(train_data, max_size=10000, min_freq=2)
    label.build_vocab(train_data)
    print("vocabulary built..")

    return (field, tokenizer, train_data, val_data, test_data)

def get_dataloaders(train_data, val_data, test_data, batch_size, device):
    train_iterator, val_iterator = create_iterators(train_data, val_data, batch_size, device, shuffle=True)
    _, test_iterator = create_iterators(train_data, test_data, 1, device, shuffle=False)
    print("dataloaders created..")

    dataloaders = {}
    dataloaders['train'] = train_iterator
    dataloaders['val'] = val_iterator
    dataloaders['test'] = test_iterator

    return dataloaders
