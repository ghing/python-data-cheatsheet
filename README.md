# Python data cheatsheet

Things in Python, Pandas, GeoPandas and Jupyter that I've had to look up or weren't obvious in the documentation.

## Loading and creating data

- [Converting multiple columns to categories](notebooks/converting_multiple_columns_to_categories.ipynb)
- [Creating DataFrames from lists and dictionaries](notebooks/create_dataframes_from_lists_and_dictionaries.ipynb)
- [Parsing date values](notebooks/parse_dates.ipynb)

### Read Shapefile from zip

```
import geopandas as gpd
from zipfile import ZipFile

zipfile_url = "zip://{0}".format(os.path.join(DATA_DIR_SRC, 'tl_2017_13_tabblock10.zip'))
blocks_ga = gpd.read_file(
    '/tl_2017_13_tabblock10.shp',
    vfs=zipfile_url,
) 

```

## Examining data

- [Count null values in any column](notebooks/count_null_values_in_any_column.ipynb)
- [Select a single item by index](notebooks/select_single_item_by_index.ipynb)

### Length of a DataFrame

To get the number of rows in a DataFrame, you can use `len(df.index)`.

However, `df.shape[0]` is faster.

### Check if a column exists in a `DataFrame`

```
if 'A' in df:
    ...
```

or

```
if 'A' in df.columns:
```

### Show all columns in a DataFrame

Use the `display.max_columns`
```
with pd.option_context('display.max_columns', None):
    display(df)
```

### Format values in a DataFrame

Use `Style.format`.

See the [styling docs](https://pandas.pydata.org/pandas-docs/stable/style.html) especially, [this section](https://pandas.pydata.org/pandas-docs/stable/style.html#Finer-Control:-Display-Values).

### List the columns in a DataFrame

I like to use the `DataFrane.dtypes` attribute because it also shows the data type of each column.

## Filtering data

- [Find rows with null values in any column](notebooks/find_null_values_in_any_column.ipynb)
- [Find all cells with zero values](notebooks/find_all_cells_with_zero_value.ipynb)

### Filter a Series

```
s = s[s != 1]
```

or in a more chainable way:

```
s.where(lambda x : x != 1)
```

### Filter a DataFrame using a function

Use `DataFrame.apply`.

```
df = pandas.DataFrame(np.random.randn(5, 3), columns=['a', 'b', 'c'])
df[df.apply(lambda x: x['b'] > x['c'], axis=1)]
```

via [pandas: complex filter on rows of DataFrame](https://stackoverflow.com/questions/11418192/pandas-complex-filter-on-rows-of-dataframe)

### Filtering DataFrame based on whether a column's value is in a list

Use [`pandas.Series.isin`](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.isin.html).

```
df = DataFrame({'A' : [5,6,3,4], 'B' : [1,2,3, 5]})

df[df['A'].isin([3, 6])]
```

via [Use a list of values to select rows from a pandas dataframe [duplicate]](https://stackoverflow.com/a/12098586/386210).

### Invert a boolean Series

Use the `~` operator. See [Boolean indexing](http://pandas.pydata.org/pandas-docs/stable/indexing.html#boolean-indexing) in the docs.

via [How can I obtain the element-wise logical NOT of a pandas Series?](https://stackoverflow.com/questions/15998188/how-can-i-obtain-the-element-wise-logical-not-of-a-pandas-series)


### Filter a DataFrame column based on a string property

Use the [Vectorized string functions for Series](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.str.html).

For example, using `len`:

```
In [1]: import pandas as pd

In [2]: df = pd.DataFrame({'a': ['1234', '12345', '123', '12']})

In [3]: df
Out[3]:
       a
0   1234
1  12345
2    123
3     12

In [4]: df[df['a'].str.len() > 3]
Out[4]:
       a
0   1234
1  12345
``` 


## Manipulating data

### Change types of columns

[This StackOverflow answer](https://stackoverflow.com/a/28648923/386210) offers a good rundown of options.

### Find and replace across an entire dataframe

Use `pandas.DataFrame.replace()`

### Add a rank column to a DataFrame

Use `Series.rank`.

via [Ranking Rows Of Pandas Dataframes](https://chrisalbon.com/python/data_wrangling/pandas_dataframe_ranking_rows/)

### Summing values across columns

Use [`pandas.DataFrame.sum`](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.sum.html).

It seems easy to just use the `+` operator to add values across columns:

```
In [1]: import pandas as pd

In [2]: d = {'one' : pd.Series([1., 2., 3.], index=['a', 'b', 'c']),
   ...:      'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])}
   ...:

In [3]: df = pd.DataFrame(d)

In [4]: df
Out[4]:
   one  two
a  1.0  1.0
b  2.0  2.0
c  3.0  3.0
d  NaN  4.0

In [5]: df['sum'] = df['one'] + df['two']

In [6]: df
Out[6]:
   one  two  sum
a  1.0  1.0  2.0
b  2.0  2.0  4.0
c  3.0  3.0  6.0
d  NaN  4.0  NaN
```

But this gives us `NaN` whenever one of the values is `NaN`. In many, but not all cases, we want to treat `NaN` as `0`.

To get around this we can use [`pandas.DataFrame.sum`](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.sum.html) on a slice of the columns we want to sum:

```
In [7]: df['sum'] = df[['one', 'two']].sum(axis=1)

In [8]: df
Out[8]:
   one  two  sum
a  1.0  1.0  2.0
b  2.0  2.0  4.0
c  3.0  3.0  6.0
d  NaN  4.0  4.0
```

Note that the `axis=1` argument makes `sum` operate across columns. Also, if you want to not skip the `NaN` values, you can specify `skipna=False`.

h/t [Pandas sum two columns, skipping NaN](https://stackoverflow.com/questions/24386638/pandas-sum-two-columns-skipping-nan)

### Flatten MultiIndex columns into one

```
grouped.columns = ['%s%s' % (a, '|%s' % b if b else '') for a, b in grouped.columns]
```

via [python - Pandas dataframe with multiindex column - merge levels - Stack Overflow](https://stackoverflow.com/questions/24290297/pandas-dataframe-with-multiindex-column-merge-levels)

### Adding a quartile column

```
removals_inactive_migration['removed_inactive_rate_q'] = pd.qcut(
    removals_inactive_migration['removed_inactive_rate'],
    4,
    labels=[1, 2, 3, 4]
)
```

### Add a column and return a new DataFrame

Use `DataFrame.assign()`


## Aggregating data

### Count number of items in a group

```
df.groupby(['col1','col2']).size()
```

## Jupyter notebooks

### Render a Python variable in a Markdown cell

Use the [Python Markdown](http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/python-markdown/readme.html) extension which is part of the [Unofficial Jupyter Notebook Extensions](http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/index.html)

### Showing lower-level logging messages 

```
%config Application.log_level="INFO"
```

TODO: Check if this actually works.

via [Get Output From the logging Module in IPython Notebook](https://stackoverflow.com/questions/18786912/get-output-from-the-logging-module-in-ipython-notebook)
