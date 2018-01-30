# Comment Search Engine

## Project Structure

| Folder/File       | Description                        |
| :---------------- | :--------------------------------- |
| `cse`             | source code for this project       |
| `searchengine.py` | start script for the search engine |
| `deployment`      | Needed for Vagrant setup           |
| `Vagrant`         | Vagrant file                       |
| `setup.py`        | Setup file                         |
| `setup.cfg`, `MANIFEST.in` | Manifest files            |
| `License`         | License file                       |

<!-- | `data` | downloaded data of the web crawler | -->

## Submodules

This project uses submodules to build the Vagrant box (used for development). Use `git clone --recursive https://github.com/CodeLionX/CommentSearchEngine.git` when cloning the project or `git submodule update --init` if you've already cloned the repo.

## Get the development environment running

This project uses vagrant for environment setup and testing. Use `vagrant up` to start the testing environment.

- Install VirtualBox 5.1.x from [Oracles download site](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
- Install Vagrant 2.0.x following [this guide](https://www.vagrantup.com/intro/getting-started/index.html)
- Use the following commands to bring up the vagrant box:

```bash
vagrant up
vagrant ssh
```

- install the project in the vagrant box

```bash
python setup.py sdist
sudo pip install --upgrade dist/CommentSearchEngine-0.1.0.tar.gz
```

Now you are able to use the Comment Search Engine inside of Vagrant.


## Get it running

This project is build for `python3`. You can install all requirements using pip:

```bash
sudo pip install --upgrade -r requirements.txt
```

We are using `nltk` for preprocessing the comment text. Therefore you need to install the porter stemmer and nltk's stopword list. Follow these steps:

```bash
python -m nltk.downloader -d /<your_path>/data/nltk_data punkt stopwords wordnet
```

For `nltk` to recognize your downloaded data you have to make the path to it available inside an environment variable. With `export NLTK_DATA="/<your_path>/data/nltk_data"` the variable is set for the current session. To make it available in shells even after restarting them, you can add this environment variable to your `environment` file:

```bash
echo "NLTK_DATA=\"/<your_path>/data/nltk_data\"" >> /etc/environment
```

After that you are ready to run the search engine on your machine:

### Indexing Phase

The following command starts the indexing process: `python searchengine.py Index:comments.csv`

> Please make sure all three files are available in the project's root directory:
> - `comments.csv`
> - `articles.csv`
> - `authors.csv`
>
> You can adjust the directory and file names in the source code of the file `searchengine.py`.

The indexer will create the following files:

- `postingLists.index`
- `postingDict.index`
- `replyToLists.index`
- `replyToDict.index`
- `documentMap.index`


Please do not delete any of these files. Depending on your document collection, the index files can get pretty huge (up to 1.5 times of the source file size).

### Querying Phase

Please create a new file `query.txt` in the project's root folder to use the search engine after a successfull index creation. Each line in this file represents a separate query to the search engine. The results are printed to new files, named `query<n>.txt` with ascending `n`.

```bash
python searchengine.py query.txt --printIdsOnly --topN 10
```

## Supported Query Types and Syntax

| Query Type | Example                            | Annotations                                                                                                                                       |
| :--------: | :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------ |
| Keyword    | `christmas` or `donald trump`      | Use one or more keywords                                                                                                                          |
| Prefix     | `christ*`                          |                                                                                                                                                   |
| Phrase     | `'christmas market'`               | Search for contiguous words                                                                                                                       |
| Boolean    | `christmas NOT 'christmas market'` | Each term can be either a keyword, prefix or phrase. You can only use one operator kind at a time. Supported operators: `AND`, `OR`, `NOT` |
