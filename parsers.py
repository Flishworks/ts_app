import base64
import io
import numpy as np
import pandas as pd


'''
Parse Router:
    Routes a file to the appropriate parser based on the filename
'''
def parse_router(fname, content):
    if content is None:
        return []
    if 'USD' in fname:
        return ohlc_parser(content)
    elif 'preprocessed' in fname:
        return preproc_parser(content)
    elif fname.endswith('.npy'):
        return numpy_parser(content)
    elif fname.endswith('.csv'):
        return generic_csv_parser(content)

    
'''
Parsers: 
    should return a list of dicts, each of format:
        {'df': <dataframe>, 'height': <height>}
        where df is the dataframe, where each column will be plotted on the same plot
        and height is the relative height of the subplot
'''
    
def generic_csv_parser(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    return [{'df': df, 'height': 1}]

def ohlc_parser(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    #set datetime as index
    df['dtime'] = pd.to_datetime(df['dtime'])
    df.set_index('dtime', inplace=True)
    
    df1 = df[['open', 'high', 'low', 'close']]
    df2 = df[['volume']]
    return [{'df': df1, 'height': 3}, {'df': df2, 'height': 1}]

def preproc_parser(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    arr = np.load(io.BytesIO(decoded))
    df = pd.DataFrame(arr.T)
    return [{'df': df, 'height': 1}]

def numpy_parser(content):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)
    arr = np.load(io.BytesIO(decoded))
    df = pd.DataFrame(arr)
    return [{'df': df, 'height': 1}]