# Python data cheatsheet

Things in Python, Pandas, GeoPandas and Jupyter that I've had to look up or weren't obvious in the documentation.

TODO: Break quick inline examples into individual notebooks.

## Loading and creating data

- [Converting multiple columns to categories](notebooks/converting_multiple_columns_to_categories.ipynb)
- [Creating DataFrames from lists and dictionaries](notebooks/create_dataframes_from_lists_and_dictionaries.ipynb)
- [Parsing date values](notebooks/parse_dates.ipynb)
- [Querying a SQL database in a Jupyter notebook](notebooks/sql_query_in_jupyter_notebook.ipynb)
- [Loading a DataFrame into a temporary table of a SQL database](notebooks/sql_temporary_table.ipynb)
- [Read shapefile from zip](notebooks/read_shapefile_from_zip.ipynb)
- Create spatial data (a Geopandas GeoDataFrame) from a CSV with coordinates: [From CSV to GeoDataFrame in two lines](https://anitagraser.com/2019/01/23/from-csv-to-geodataframe-in-two-lines/)

### Loading the results of a Spatialite spatial query

You need to make sure you have Python compiled with the ability to load extensions:

```
CONFIGURE_OPTS=--enable-loadable-sqlite-extensions pyenv install 3.9.4
```

If you installed sqlite3 on a Mac using Homebrew, you might also have to point to the Homebrew versions of the libraries:

```
LDFLAGS="-L/usr/local/opt/sqlite/lib" CPPFLAGS="-I/usr/local/opt/sqlite/include" CONFIGURE_OPTS=--enable-loadable-sqlite-extensions pyenv install 3.9.4
```

After making your database connection, you need to load the spatialite extension:

```
import sqlite3

con = sqlite3.connect("spatial_data.db")
con.enable_load_extension(True)
con.load_extension('mod_spatialite')
```

Once you've created the connection object like this, you can [`geopandas.GeoDataFrame.from_postgis()`](https://geopandas.org/docs/reference/api/geopandas.GeoDataFrame.from_postgis.html#geopandas.GeoDataFrame.from_postgis) to query the database.

Note that you have to do some conversion on the data in the geometry column. Geopandas also expects the column to be named `geom` (though you can override this). You may also need to specify the coordinate reference system (CRS) using the `crs` argument.

```
gpd.read_postgis("SELECT name, Hex(ST_AsBinary(geometry)) as geom FROM parcels LIMIT 5", con=con)
```

Sources: [Python sqlite3.Connection object has no attribute 'enable_load_extension](https://code.luasoftware.com/tutorials/python/python-sqlite3-connection-objecthas-no-attribute-enable-load-extension/) (Lua Software Code), [Loading spatialite tables into GeoPandas GeoDataFrames](https://gist.github.com/perrygeo/868135514d2518257bbb)


### Geocoding addresses

I usually first pass the addresses through the Census Geocoder Batch API and then geocode the addresses that it can't handle using Geocodio. 

Helpful packages:

- [datadesk/python-censusbatchgeocoder: A simple Python wrapper for U.S. Census Geocoding Services API batch service](https://github.com/datadesk/python-censusbatchgeocoder)

I put a sample script in `scripts/geocode_data.py`. Note that I haven't tried to run this script. It's a quick and dirty combination of code from a project, but it should provide an idea of how to do this.

## Examining data

- [Count null values in any column](notebooks/count_null_values_in_any_column.ipynb)
- [Calculate percentages of a group](notebooks/percentages_of_group.ipynb)
- [Length of a DataFrame](notebooks/length_of_dataframe.ipynb)
- [Check if column exists](notebooks/column_exists.ipynb)
- [Show all columns](notebooks/show_all_columns.ipynb)
- [Format values in a DataFrame](noteboos/format_values.ipynb)
- [List columns](notebooks/list_columns.ipynb)

## Filtering, subsetting and indexing data

- [Find rows with null values in any column](notebooks/find_null_values_in_any_column.ipynb)
- [Find all cells with zero values](notebooks/find_all_cells_with_zero_value.ipynb)
- [Select all the contents of a MultiIndex level](notebooks/multiindex_slice.ipynb)
- [Select a single item by index](notebooks/select_single_item_by_index.ipynb)
- [Get consecutive pairs from an interable](notebooks/consecutive_pairs_iterable.ipynb)
- [Select a set of items by a list of index values](notebooks/select_multiple_items_by_index.ipynb)

### Filter a Series

```
s = s[s != 1]
```

or in a more chainable way:

```
s.where(lambda x : x != 1)
```

### Filter a DataFrame using a function

You can specify a function inside `[]`:

```
df = pd.DataFrame(np.random.randn(5, 3), columns=['a', 'b', 'c'])
df[lambda x: x['b'] > x['c']]
```

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

## Cleaning, transforming and manipulating data

- [Combine records when information is split across rows](notebooks/combine_record_rows.ipynb)
- [Split a DataFrame into chunks](notebooks/chunk_dataframe.ipynb)

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

## Visualizing data

- [Coloring a choropleth based on an explicit color value in a GeoDataFrame](notebooks/color_choropleth_explicitly.ipynb)

## Jupyter notebooks

- [Hide cells in HTML output of notebook](notebooks/hide_cells_jupyter_html.ipynb)

### Render a Python variable in a Markdown cell

Use the [Python Markdown](http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/nbextensions/python-markdown/readme.html) extension which is part of the [Unofficial Jupyter Notebook Extensions](http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/index.html)

### Showing lower-level logging messages 

```
%config Application.log_level="INFO"
```

TODO: Check if this actually works.

via [Get Output From the logging Module in IPython Notebook](https://stackoverflow.com/questions/18786912/get-output-from-the-logging-module-in-ipython-notebook)

### Avoiding having to manually reimport modules when you change code in them.

Use the [autoreload](https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html) extension.

```
%load_ext autoreload

%autoreload 2

from foo import some_function

some_function()

# open foo.py in an editor and change some_function to return 43

some_function()
```

## Python environment

### Installing Python in a good way

[My Python Development Environment, 2020 Edition](https://jacobian.org/2019/nov/11/python-environment-2020/) is a good guide. I prefer to use Pipenv instead of Poetry because `pipenv run` automatically sources `.env` files.

### Use a particular Python version with Pipenv

```
pipenv install --python=/path/to/your/python
```

### Running a script and dropping to the debugger on an exception

```
python -m pdb -c continue myscript.py arg1 arg2 
```

Source: [Starting python debugger automatically on error](https://stackoverflow.com/a/2438834)

### Create a kernel for use with Jupyter

This makes it possible to have a single Jupyter Lab installation with separate kernels for the virtualenvs for each project. 

```
pipenv run python -m ipykernel install --user --name=your-project-slug
```

Source: [associatedpress/cookiecutter-python-project](https://github.com/associatedpress/cookiecutter-python-project/blob/master/hooks/post_gen_project.sh)

### Integrating code formatters and linters into your coding workflow

In many projects, I use [Black](https://black.readthedocs.io/en/stable/) to format my source code and [pylint](https://www.pylint.org/) to check my code for both formatting issues and things that could cause errors or make my code more difficult to read and update.

There are ways to integrate these tools into your editor, such as [vim](https://github.com/dense-analysis/ale/blob/master/supported-tools.md) or Visual Studio Code. However, I've found a good universal way to approach this is to install them as git hooks that run when trying to commit code. To do this, I use the [pre-commit](https://pre-commit.com/) framework.

I've put an example [`.pre-commit-config.yml`](.pre-commit-config.yml) file that runs Black and pylint in this repo.

### Listing the path to a virtual environment created with Pipenv

```pipenv --venv```

### Specifying the Python environment used by Visual Studio code

This is important if you're running pylint on a particular project using VS Code integration and want to make sure it detects the packages installed in your project virtual environment.

To select a specific environment, use the Python: Select Interpreter command from the Command Palette (⇧⌘P on Mac). If the environment you want isn't listed, you can enter a full path to the Python executable.

Source: [Using Python Environments in Visual Studio Code](https://code.visualstudio.com/docs/python/environments)

## Data sources

These are the data sources used as example data in this project.

This will be for examples of working with GeoPandas and Spatialite.

- Table B02001, American Community Survey, 5-year estimates, 2019 for Chicago Tracts
  - Agency: U.S. Census Bureau
  - URL: https://censusreporter.org/data/table/?table=B02001&geo_ids=16000US1714000,140|16000US1714000&primary_geo_id=16000US1714000

- Chicago Neighborhood Boundaries
  - Agency: City of Chicago
  - URL: https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Neighborhoods/bbvz-uum9

## Installation of this project for local development

I've used the [Jupytext](https://github.com/mwouts/jupytext/) Jupyter Lab extension to create "paired" .Rmd versions of the notebooks in this repository.

This was mostly because the git diffs for the Rmd files more clearly show the changes between versions. There may be other, potentially preferable ways to do this in 2021. I also just wanted to experiment with Jupytext.

You'll need to install this extension in the same environment as your Jupyter lab.

For me, since I installed Jupyter Lab using pipx, this looks like:

```
pipx inject jupyterlab jupytext
```
